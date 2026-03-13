import os
import requests
import json
from google import genai
from app.config import settings

# Streamlined prioritized list for faster demo execution
OPENROUTER_FREE_CHAIN = [
    "deepseek/deepseek-r1:free",           # Top Reasoning (DeepSeek-R1)
    "meta-llama/llama-3.3-70b-instruct:free", # Powerful General
    "google/gemma-2-9b-it:free",           # Fast Alternative
]

def _load_prompt():
    prompt_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts", "ai_prompt.txt")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    return "You are a cybersecurity analyst. Analyze the following scan data in plain English:"

def _generate_with_gemini(prompt: str) -> str:
    """Uses Google's Native Gemini API for large context data."""
    if not settings.GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not configured")
    
    # Using the new google-genai SDK
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model='gemini-2.0-flash-exp',
        contents=prompt
    )
    return response.text

def _generate_with_openrouter(prompt: str, model_id: str) -> str:
    """Calls a specific model on OpenRouter."""
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")
        
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://reconxplorer.io",
            "X-Title": "ReconXplorer",
        },
        data=json.dumps({
            "model": model_id,
            "messages": [
                {"role": "user", "content": prompt}
            ],
        }),
        timeout=45
    )
    
    if response.status_code == 429:
        raise Exception(f"Rate limited (429)")
    
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")
        
    data = response.json()
    return data['choices'][0]['message']['content']

def _generate_with_ollama(prompt: str, model_id: str) -> str:
    """Uses local Ollama models as fallback."""
    try:
        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"
        response = requests.post(
            url=url,
            json={
                "model": model_id,
                "prompt": prompt,
                "stream": False
            },
            timeout=150 # Local models might be slow
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama Error {response.status_code}: {response.text}")
            
        data = response.json()
        return data.get('response', f"Ollama ({model_id}) returned empty response.")
    except requests.exceptions.ConnectionError:
        raise Exception("Ollama connection failed. Ensure OLLAMA_HOST=0.0.0.0 is set on the host.")
    except Exception as e:
        raise Exception(f"Ollama ({model_id}) failed: {str(e)}")

def generate_ai_summary(scan_json: str) -> str:
    base_prompt = _load_prompt()
    full_prompt = f"{base_prompt}\n\nTarget Scan Data (JSON):\n{scan_json}\n\nWrite a plain English report."

    # Logic:
    # 1. Try Gemini FIRST (Most reliable and user has a key)
    if settings.GEMINI_API_KEY:
        try:
            print(f"[AI_EXPLAINER] Attempting primary generation with Gemini...")
            return _generate_with_gemini(full_prompt)
        except Exception as e:
            print(f"[AI_EXPLAINER] Gemini failed: {e}. Falling back...")

    # 2. Try configured OpenRouter model
    if settings.OPENROUTER_API_KEY:
        try:
            model = settings.OPENROUTER_MODEL or "meta-llama/llama-3.1-8b-instruct:free"
            print(f"[AI_EXPLAINER] Attempting OpenRouter with {model}...")
            return _generate_with_openrouter(full_prompt, model)
        except Exception as e:
            print(f"[AI_EXPLAINER] OpenRouter failed: {e}. Trying local fallback...")

    # 3. Final Fallback: Local Ollama (With increased timeout for CPU inference)
    OLLAMA_FALLBACK_MODELS = ["phi3:mini", "llama3:8b"]
    for model_id in OLLAMA_FALLBACK_MODELS:
        try:
            print(f"[AI_EXPLAINER] All APIs failed. Attempting local Ollama ({model_id})...")
            return _generate_with_ollama(full_prompt, model_id)
        except Exception as e:
            print(f"[AI_EXPLAINER] Local Ollama ({model_id}) failed: {str(e)}")
            continue
            
    return f"AI Analysis failed. Data is stored technically below."
