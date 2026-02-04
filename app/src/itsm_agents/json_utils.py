import json
import re

def extract_json(text: str) -> str:
    if not text:
        return ""
    text = text.strip()

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()

    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1 and end > start:
        return text[start:end+1].strip()

    return text

def repair_json(s: str) -> str:
    if not s:
        return s

    # remove trailing commas before closing braces/brackets
    s = re.sub(r",\s*([\]}])", r"\1", s)
    # remove trailing comma at end
    s = re.sub(r",\s*$", "", s)

    # balance brackets (for truncated output)
    open_sq, close_sq = s.count("["), s.count("]")
    open_cu, close_cu = s.count("{"), s.count("}")

    if close_sq < open_sq:
        s += "]" * (open_sq - close_sq)
    if close_cu < open_cu:
        s += "}" * (open_cu - close_cu)

    return s.strip()

def load_json_strict(text: str) -> dict:
    extracted = extract_json(text)
    try:
        return json.loads(extracted)
    except json.JSONDecodeError:
        fixed = repair_json(extracted)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            # Return empty dict if still invalid
            return {}
