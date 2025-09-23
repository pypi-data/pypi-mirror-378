import requests

KEY_VALIDATION_URL = "http://localhost:8000/validate"

def is_valid_key(api_key: str) -> bool:
    try:
        response = requests.get(KEY_VALIDATION_URL, params={"key": api_key})
        response.raise_for_status()
        return response.json().get("valid", False)
    except requests.RequestException as e:
        print(f"[keyauth] Validation failed: {e}")
        return False