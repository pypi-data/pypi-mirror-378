# core/graph.py
import os
from datetime import datetime
import re
from .core.models import get_llm
from .core.state import AssistantState
from langgraph.graph import StateGraph

# Initialize LLM
llm = get_llm()

# Helper to safely extract text from LLM result
def _extract_text(result) -> str:
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

# Clean up slug for filenames
def _slugify(text: str, maxlen: int = 40) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    return text[:maxlen].strip("-") or "snippet"

# Node functions
def codegen_node(state: AssistantState) -> dict:
    """Generate code for the query."""
    result = llm.invoke(state["query"])
    content = _extract_text(result)
    return {"codegen_response": content}

def debug_node(state: AssistantState) -> dict:
    """Debug or analyze code for the query."""
    result = llm.invoke(state["query"])
    content = _extract_text(result)
    return {"debug_response": content}

def explain_node(state: AssistantState) -> dict:
    """Explain code or logic for the query."""
    result = llm.invoke(state["query"])
    content = _extract_text(result)
    return {"explain_response": content}

def save_python_file(state: AssistantState) -> dict:
    """Save Python code from codegen_response to generated/*.py"""
    content = state.get("codegen_response", "") or ""
    if not content.strip():
        return {"file_saved": "No codegen output to save.", "saved_filename": ""}

    # Extract Python fenced block
    code = None
    if "```python" in content:
        try:
            code = content.split("```python", 1)[1].split("```", 1)[0].strip()
        except Exception:
            code = None

    # Fallback: extract first Python-like block
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

# Build workflow
workflow = StateGraph(AssistantState)

# Router node
workflow.add_node("router", lambda state: {"query": state["query"]})

# Main nodes
workflow.add_node("codegen", codegen_node)
workflow.add_node("debug", debug_node)
workflow.add_node("explain", explain_node)
workflow.add_node("save_file", save_python_file)

# Connect nodes
workflow.add_edge("router", "codegen")
workflow.add_edge("router", "debug")
workflow.add_edge("router", "explain")
workflow.add_edge("codegen", "save_file")

# Set entry point and compile workflow
workflow.set_entry_point("router")
app = workflow.compile()
