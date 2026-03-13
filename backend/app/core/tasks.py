from fastapi import BackgroundTasks
from app.services.scan_executor import execute_scan

def run_scan_task(background_tasks: BackgroundTasks, scan_id, tool, target_value, user_id):
    """
    Abstraction layer for async tasks.
    Currently uses FastAPI BackgroundTasks.
    Can be swapped to Celery easily by changing this implementation.
    """
    background_tasks.add_task(
        execute_scan,
        scan_id,
        tool,
        target_value,
        user_id,
    )
