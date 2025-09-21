# core/graph.py
import os
import re
from datetime import datetime
from .core.models import get_llm
from .core.state import AssistantState
from langgraph.graph import StateGraph

# ---------------- LLM INIT ---------------- #
llm = get_llm()

# ---------------- HELPERS ---------------- #
def _extract_text(result) -> str:
    """Safely extract text from LLM output."""
    if result is None:
        return ""
    if hasattr(result, "content"):
        return str(result.content)
    if isinstance(result, str):
        return result
    try:
        return str(result)
    except Exception:
        return ""

def _slugify(text: str, maxlen: int = 40) -> str:
    """Clean string for filenames."""
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    return text[:maxlen].strip("-") or "snippet"

# ---------------- NODES ---------------- #
def codegen_node(state: AssistantState) -> dict:
    result = llm.invoke(state.get("codegen_query", ""))
    return {"codegen_response": _extract_text(result)}

def debug_node(state: AssistantState) -> dict:
    result = llm.invoke(state.get("debug_query", ""))
    return {"debug_response": _extract_text(result)}

def explain_node(state: AssistantState) -> dict:
    result = llm.invoke(state.get("explain_query", ""))
    return {"explain_response": _extract_text(result)}

def save_python_file(state: AssistantState) -> dict:
    """Save codegen output to generated/*.py."""
    content = state.get("codegen_response", "")
    if not content.strip():
        return {"file_saved": "No codegen output to save.", "saved_filename": ""}

    # Extract Python fenced block
    code = None
    if "```python" in content:
        try:
            code = content.split("```python", 1)[1].split("```", 1)[0].strip()
        except Exception:
            code = None

    # Fallback: try to find a Python-like snippet
    if not code:
        lines = content.splitlines()
        candidate = []
        for line in lines:
            if line.strip().startswith(("def ", "import ", "from ", "class ", "if ", "print(", "__name__")) or (line and line.startswith(" ")):
                candidate.append(line)
            elif candidate:
                break
        code = "\n".join(candidate).strip() if candidate else None

    if not code:
        return {"file_saved": "No Python code block found in response.", "saved_filename": ""}

    # Prepare folder
    folder = "generated"
    os.makedirs(folder, exist_ok=True)
    slug = _slugify(state.get("query", "snippet"))
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{slug}_{timestamp}.py"
    fullpath = os.path.join(folder, filename)

    try:
        with open(fullpath, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        return {"file_saved": f"Saved to {fullpath}", "saved_filename": fullpath}
    except Exception as e:
        return {"file_saved": f"Failed to save file: {e}", "saved_filename": ""}

# ---------------- WORKFLOW ---------------- #
workflow = StateGraph(AssistantState)

# Router node
workflow.add_node("router", lambda state: {"query": state.get("query", "")})

# Core nodes
workflow.add_node("codegen", codegen_node)
workflow.add_node("debug", debug_node)
workflow.add_node("explain", explain_node)
workflow.add_node("save_file", save_python_file)

# Annotated edges to avoid multi-value error
workflow.add_edge("router", "codegen", state_key="codegen_query")
workflow.add_edge("router", "debug", state_key="debug_query")
workflow.add_edge("router", "explain", state_key="explain_query")

# Save codegen output automatically
workflow.add_edge("codegen", "save_file", state_key="file_saved")

workflow.set_entry_point("router")
app = workflow.compile()
