from datetime import datetime
from sqlalchemy.orm import Session
import tempfile
import os
import time
import subprocess
import socket
import json
from concurrent.futures import ThreadPoolExecutor

from app.db.session import SessionLocal
from app.services.passive_recon.runner import run_passive_recon
from app.services.threat_intel.runner import run_threat_intel 
from app.models.scan import Scan
from app.models.active_scan import ActiveScanResult
from app.models.recon_enhancement import ReconEnhancementResult
from app.services.risk_correlation.correlator import correlate
from app.services.parsers.nmap_parser import parse_nmap_xml
from app.services.parsers.whatweb_parser import parse_whatweb_json
from app.services.aggregation.scan_aggregator import aggregate_scan_results
from app.services.ai_explainer import generate_ai_summary
from app.services.tools import (
    get_os,
    is_tool_installed,
    build_nmap_command,
    build_whatweb_command,
    execute_command,
)

MAX_SCAN_DURATION = 600 # 10 minutes in seconds

from app.models.subdomain import Subdomain
from app.services.tools.manager import get_tool

def execute_scan(
    scan_id,
    tool: str,
    target_value: str,
    user_id,
):
    # Create fresh session for background task
    db = SessionLocal()

    try:
        # 1. Fetch scan record
        scan = db.query(Scan).filter(Scan.id == scan_id).first()

        if not scan:
            print(f"[SCAN_EXECUTOR] Scan ID {scan_id} not found in DB.")
            return

        # 2. Idempotency Guard (Inside Try)
        if scan.status == "completed":
            print(f"[SCAN_EXECUTOR] Scan {scan_id} already completed. Skipping.")
            return

        START_TIME = time.time()

        def check_timeout():
            if (time.time() - START_TIME) > MAX_SCAN_DURATION:
                raise TimeoutError(f"Scan duration exceeded {MAX_SCAN_DURATION}s")

        def log_transition(status: str, phase: str, progress: int):
            scan.status = status
            scan.current_phase = phase
            scan.progress = progress
            db.commit()
            print(f"[SCAN_EXECUTOR] STATUS: {status} | PHASE: {phase} | {progress}%")

        # 3. Cleanup existing results (for retries)
        db.query(ActiveScanResult).filter(ActiveScanResult.scan_id == scan_id).delete()
        db.query(Subdomain).filter(Subdomain.scan_id == scan_id).delete()
        db.commit()

        # --- INITIALIZING ---
        log_transition("running", "Initializing Engine", 5)
        scan.started_at = datetime.utcnow()
        
        # --- PARALLEL DISCOVERY & INTELLIGENCE (DEMO OPTIMIZATION) ---
        log_transition("running", "Initial Intelligence Gathering", 7)
        
        def task_subdomains():
            if scan.profile in ["full", "passive"]:
                subfinder = get_tool("subfinder", target_value)
                if subfinder and subfinder.is_installed():
                    sub_res = subfinder.execute()
                    # Use a fresh session for subdomain storage to avoid threading conflicts
                    with SessionLocal() as s_db:
                        for sub in sub_res.get("subdomains", []):
                            s_db.add(Subdomain(scan_id=scan.id, subdomain=sub))
                        s_db.commit()

        def task_osint():
            osint = get_tool("osint", target_value)
            return osint.execute()

        def task_passive_threat():
            if scan.profile in ["passive", "full"]:
                with SessionLocal() as p_db, SessionLocal() as t_db:
                    passive_data = run_passive_recon(target_value, p_db, user_id)
                    threat_result = run_threat_intel(target_value, t_db, user_id)
                    return {
                        "passive": passive_data["summary"],
                        "threat": {
                            "risk_score": threat_result["risk_score"],
                            "verdict": threat_result["verdict"],
                            "confidence": threat_result["confidence"],
                            "tags": threat_result.get("tags", []),
                            "signals": threat_result.get("signals", {})
                        }
                    }
            return None

        with ThreadPoolExecutor(max_workers=3) as discovery_executor:
            future_sub = discovery_executor.submit(task_subdomains)
            future_osint = discovery_executor.submit(task_osint)
            future_pt = discovery_executor.submit(task_passive_threat)

            osint_res = future_osint.result()
            pt_res = future_pt.result()

            # Merge results into the scan record
            scan.resolved_ip = osint_res.get("ip", "0.0.0.0")
            if pt_res:
                scan.passive_summary = pt_res["passive"]
                scan.threat_summary = pt_res["threat"]
            else:
                scan.threat_summary = {
                    "osint_data": osint_res,
                    "resolved_ip": osint_res.get("ip")
                }
            db.commit()

        # --- PHASE 2: ACTIVE ---
        check_timeout()
        if scan.profile in ["active", "full"]:
            log_transition("active", "Active Vulnerability Probing", 60)
            
            # Run both nmap and whatweb by default for active/full scans
            # Unless tool is explicitly something else that is not nmap/whatweb
            if tool in ["nmap", "whatweb"]:
                tools_to_run = ["nmap", "whatweb"]
            else:
                tools_to_run = [tool]
            
            def run_single_tool(current_tool):
                check_timeout()
                if not is_tool_installed(current_tool):
                    return None

                remaining_cmd = int(MAX_SCAN_DURATION - (time.time() - START_TIME))
                xml_path = None
                
                if current_tool == "nmap":
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as f:
                        xml_path = f.name
                    command = build_nmap_command(target_value, xml_path)
                else:
                    command = build_whatweb_command(target_value)

                result = execute_command(command, timeout=max(30, remaining_cmd))
                return {"tool": current_tool, "result": result, "xml_path": xml_path}

            # Run tools in parallel
            with ThreadPoolExecutor(max_workers=len(tools_to_run)) as executor:
                futures = {executor.submit(run_single_tool, t): t for t in tools_to_run}
                
                for future in futures:
                    current_tool_name = futures[future]
                    try:
                        tool_data = future.result()
                        if not tool_data: 
                            print(f"[SCAN_EXECUTOR] Tool {current_tool_name} returned no data (possibly not installed).")
                            continue
                        
                        current_tool = tool_data["tool"]
                        result = tool_data["result"]
                        xml_path = tool_data["xml_path"]

                        # Save raw output
                        header = f"\n\n--- {current_tool.upper()} OUTPUT ---\n"
                        if scan.output:
                            scan.output += header + (result.get("stdout") or "")
                        else:
                            scan.output = header + (result.get("stdout") or "")
                        
                        # Save parsed results
                        if current_tool == "nmap":
                            raw_xml = ""
                            if xml_path and os.path.exists(xml_path):
                                with open(xml_path, "r", encoding="utf-8") as f:
                                    raw_xml = f.read()
                            parsed = parse_nmap_xml(raw_xml or result.get("stdout") or "")
                            db.add(ActiveScanResult(
                                scan_id=scan.id, user_id=scan.user_id, tool="nmap",
                                raw_output=raw_xml, parsed_result=parsed,
                                severity=parsed["severity"], findings_count=str(parsed["findings_count"])
                            ))
                        elif current_tool == "whatweb":
                            parsed = parse_whatweb_json(result.get("stdout") or "")
                            db.add(ActiveScanResult(
                                scan_id=scan.id, user_id=scan.user_id, tool="whatweb",
                                raw_output=result.get("stdout") or "", parsed_result=parsed,
                                severity=parsed["severity"], findings_count=str(parsed["findings_count"])
                            ))
                        db.commit()
                        print(f"[SCAN_EXECUTOR] Tool {current_tool} finished and saved.")
                    except Exception as tool_err:
                        print(f"[SCAN_EXECUTOR] Tool {current_tool_name} failed: {tool_err}")
                        continue

        # --- PHASE 3: FINALIZATION ---
        check_timeout()
        log_transition("active", "Finalizing Intelligence", 95)
        
        all_res = db.query(ActiveScanResult).filter(ActiveScanResult.scan_id == scan.id).all()
        scan.aggregated_result = aggregate_scan_results(all_res)
        
        # Risk Correlation
        enhancements = db.query(ReconEnhancementResult).filter(
            ReconEnhancementResult.target == target_value,
            ReconEnhancementResult.user_id == user_id
        ).all()
        recon_data = {r.module: r.summary for r in enhancements}
        
        risk = correlate(scan, recon_data)
        
        # --- ENFORCE STRICT DATA CONTRACT (Option A/B hybrid for safety) ---
        if isinstance(risk, dict):
            scan.risk_summary = risk
            scan.risk_score = risk.get("overall_risk_score", 0)
            scan.risk_level = risk.get("risk_level", "info")
        else:
            # Emergency Fallback: If correlator violates contract, we don't crash
            print(f"[CRITICAL] Correlator returned {type(risk)} instead of dict. Enforcing fallback.")
            scan.risk_score = int(risk) if isinstance(risk, (int, float)) else 0
            scan.risk_level = "info"
            scan.risk_summary = {
                "overall_risk_score": scan.risk_score,
                "risk_level": scan.risk_level,
                "error": "Risk correlation returned unstructured data"
            }

        # --- PHASE 4: AI INTELLIGENCE REPORT ---
        try:
            log_transition("active", "Generating AI Intelligence Report", 98)
            ai_input = {
                "target": target_value,
                "aggregated_results": scan.aggregated_result,
                "passive_summary": scan.passive_summary,
                "threat_summary": scan.threat_summary,
                "risk_summary": scan.risk_summary
            }
            scan.ai_summary = generate_ai_summary(json.dumps(ai_input))
            print(f"[SCAN_EXECUTOR] AI Summary generated for {scan_id}")
        except Exception as ai_err:
            print(f"[SCAN_EXECUTOR] AI Report failed: {ai_err}")
            scan.ai_summary = "AI analysis was unable to complete for this scan."

        # TERMINAL SUCCESS
        scan.status = "completed"
        scan.progress = 100
        scan.current_phase = None
        scan.finished_at = datetime.utcnow()
        db.commit()
        print("[FINAL] Scan completed successfully")
        print(f"[SCAN_EXECUTOR] SUCCESS for scan {scan_id}")

    except Exception as e:
        print(f"[SCAN_EXECUTOR] ERROR: {e}")
        db.rollback()
        
        # Re-fetch or reuse scan to mark failed
        try:
            # Create a new session if the old one is closed or failed
            err_db = SessionLocal()
            scan = err_db.query(Scan).filter(Scan.id == scan_id).first()
            if scan:
                scan.status = "failed"
                scan.error = str(e)
                scan.current_phase = None
                scan.progress = 0 # Reset progress on failure
                scan.finished_at = datetime.utcnow()
                err_db.commit()
            err_db.close()
        except Exception as db_err:
            print(f"[SCAN_EXECUTOR] Critical DB error during failure logging: {db_err}")
            pass

    finally:
        db.close()
        print("SCAN EXECUTOR FINISHED")
