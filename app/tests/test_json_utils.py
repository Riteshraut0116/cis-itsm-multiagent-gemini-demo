from app.src.itsm_agents.json_utils import load_json_strict

def test_load_json_strict_handles_fences():
    text = "```json\n{\"a\":1}\n```"
    assert load_json_strict(text) == {"a": 1}

def test_load_json_strict_repairs_trailing_commas():
    text = "{\"a\":1,}"
    assert load_json_strict(text) == {"a": 1}