"""
Ollama client for local AI model interaction.
Handles connection checking and text analysis requests.
"""

import requests
from ..config.settings import OLLAMA_BASE_URL, PROCESSING_MODES


def check_ollama_connection(model_name):
    """Check if Ollama server is running and specified model is available."""
    try:
        # Check if Ollama server is running
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [model.get('name', '') for model in models]
            
            if model_name in model_names:
                return True, f"Ollama server running with {model_name} model available"
            else:
                return False, f"Model {model_name} not found. Available models: {model_names}"
        else:
            return False, f"Ollama server responded with status {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, "Cannot connect to Ollama server. Please run 'ollama serve'"
    except Exception as e:
        return False, f"Error checking Ollama: {e}"


def analyze_with_ollama(prompt, model_name, processing_mode="enhanced"):
    """
    Perform analysis using local Ollama model.
    
    Args:
        prompt (str): The analysis prompt
        model_name (str): Model to use (e.g., "gpt-oss:20b", "gemma3:1b")
        processing_mode (str): "enhanced" or "statistical"
        
    Returns:
        str: Analysis result or error message
    """
    try:
        mode_config = PROCESSING_MODES[processing_mode]
        
        # Determine token count based on model and mode
        if "gpt-oss" in model_name:
            num_predict = mode_config["gpt_oss_tokens"]
        else:
            num_predict = mode_config["gemma_tokens"]
        
        mode_text = "statistical" if processing_mode == "statistical" else "enhanced"
        print(f"Sending request to local Ollama model ({model_name} - {mode_text} mode)...")
        
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": mode_config["temperature"],
                "top_p": 0.9,
                "top_k": 40,
                "num_predict": num_predict,
                "stop": ["Human:", "Assistant:"]
            }
        }
        
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=mode_config["timeout"]
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Deep analysis completed successfully!")
            return result.get('response', 'No response received')
        else:
            return f"Ollama Error: HTTP {response.status_code} - {response.text}"
            
    except requests.exceptions.Timeout:
        return "Timeout Error: Deep analysis took too long. Try with shorter text or cloud API."
    except Exception as e:
        return f"Ollama Error: {e}"