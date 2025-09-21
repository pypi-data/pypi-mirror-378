import streamlit as st
import requests

OLLAMA_URL = "http://localhost:11434"

TYPES = ["completion", "embedding"]
FUNCS = ["tools", "thinking"]

def get_model_capabilities(model_name="llama3"):
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/show",
            json={"name": model_name},
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        capabilities = data.get("capabilities", [])
        return capabilities
    except Exception as e:
        print(f"Error fetching capabilities for model '{model_name}': {e}")
        return []

def get_ollama_models(type=None, func=None):
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()

        models_all = resp.json().get("models", [])

        models = []

        for model_entry in models_all:
            if isinstance(model_entry, dict):
                model_name = model_entry.get("model")
            else:
                model_name = model_entry

            if not model_name:
                continue

            capabilities = get_model_capabilities(model_name)

            add = True
            if func and func not in capabilities:
                add = False

            if type and type not in capabilities:
                add = False

            if add:
                models.append(model_name)

        return models

    except Exception as e:
        print(f"Failed to fetch models and capabilities: {e}")
        return []
