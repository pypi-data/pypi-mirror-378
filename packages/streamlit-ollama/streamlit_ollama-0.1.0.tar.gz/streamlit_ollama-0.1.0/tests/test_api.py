from streamlit_ollama.api import get_ollama_models, get_model_capabilities

def test_get_model_capabilities():
    capabilities = get_model_capabilities("llama3")
    assert isinstance(capabilities, list)

def test_get_ollama_models():
    models = get_ollama_models()
    assert isinstance(models, list)
