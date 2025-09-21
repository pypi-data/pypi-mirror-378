# core/graph.py
import os
from datetime import datetime
import re
from harish_ai_assistant.core.models import get_llm
from harish_ai_assistant.core.state import AssistantState
from langgraph.graph import StateGraph

# Initialize LLM (model name optional)
llm = get_llm()

# Helper to safely extract text from the LLM result
def _extract_text(result) -> str:
    if result is None:
        return ""
    # common attr used earlier
    if hasattr(result, "content"):
        return str(result.content)
    # sometimes result could be a dict/list/str
    if isinstance(result, (str,)):
        return result
    try:
        return str(result)
    except Exception:
        return ""

# Clean up a short slug for filenames (keep only safe chars)
def _slugify(text: str, maxlen: int = 40) -> str:
    text = text.strip().lower()
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9\-]", "", text)
    return text[:maxlen].strip("-") or "snippet"

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
    """Extract Python code from codegen_response and save to generated/*.py with timestamp."""
    content = state.get("codegen_response", "") or ""
    if not content.strip():
        return {"file_saved": "No codegen output to save.", "saved_filename": ""}

    # Try to extract python fenced block
    code = None
    if "```python" in content:
        try:
            code = content.split("```python", 1)[1].split("```", 1)[0].strip()
        except Exception:
            code = None

    # fallback: try to find first block that looks like Python (def / import / if __name__)
    if not code:
        lines = content.splitlines()
        # gather contiguous lines that start with common python leads OR have indentation
        candidate = []
        for line in lines:
            if line.strip().startswith(("def ", "import ", "from ", "class ", "if ", "print(", "__name__")) or (line and line.startswith(" ")):
                candidate.append(line)
            elif candidate:
                # break when candidate ended
                break
        code = "\n".join(candidate).strip() if candidate else None

    if not code:
        # As a last resort, save the whole content but mark not clearly python
        return {"file_saved": "No Python code block found in response.", "saved_filename": ""}

    # Prepare folder
    folder = "generated"
    os.makedirs(folder, exist_ok=True)

    # safe filename
    slug = _slugify(state.get("query", "snippet"))
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"{slug}_{timestamp}.py"
    fullpath = os.path.join(folder, filename)

    # Do not overwrite; filename includes timestamp so it won't
    try:
        with open(fullpath, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        return {"file_saved": f"Saved to {fullpath}", "saved_filename": fullpath}
    except Exception as e:
        return {"file_saved": f"Failed to save file: {e}", "saved_filename": ""}

# Build workflow
workflow = StateGraph(AssistantState)

# router passes query through
workflow.add_node("router", lambda state: {"query": state["query"]})

workflow.add_node("codegen", codegen_node)
workflow.add_node("debug", debug_node)
workflow.add_node("explain", explain_node)
workflow.add_node("save_file", save_python_file)

# edges: router -> codegen -> save_file (we still save automatically after gen)
workflow.add_edge("router", "codegen")
workflow.add_edge("router", "debug")
workflow.add_edge("router", "explain")
workflow.add_edge("codegen", "save_file")

workflow.set_entry_point("router")
app = workflow.compile()
