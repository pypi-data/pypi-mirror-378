# interface/cli.py
import subprocess
import os
import time
from harsh_ai_assistant.graph import app

VALID_NODES = {"codegen", "debug", "explain"}

# ---------------- COLORS ---------------- #
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def cgreen(text): return f"{Colors.OKGREEN}{text}{Colors.ENDC}"
def cred(text): return f"{Colors.FAIL}{text}{Colors.ENDC}"
def cyellow(text): return f"{Colors.WARNING}{text}{Colors.ENDC}"
def cblue(text): return f"{Colors.OKBLUE}{text}{Colors.ENDC}"

# ---------------- FILESYSTEM HELPERS ---------------- #
def _sanitize_filename(text: str) -> str:
    keep = "-_.() abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(c for c in text if c in keep).strip().replace(" ", "_")[:50]

def save_outputs(query: str, result: dict, filename_override: str = None):
    """Save generated outputs. If filename_override is provided, overwrite that file."""
    if filename_override:
        folder = os.path.dirname(filename_override)
    else:
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        shortq = _sanitize_filename(query) or "query"
        folder = os.path.join("generated", f"{timestamp}-{shortq}")
        os.makedirs(folder, exist_ok=True)

    saved_files = {}

    if "codegen_response" in result and result["codegen_response"]:
        path = os.path.join(folder, "codegen.py") if not filename_override else filename_override
        with open(path, "w", encoding="utf-8") as f:
            f.write(result["codegen_response"])
        saved_files["codegen"] = path

    if "debug_response" in result and result["debug_response"]:
        path = os.path.join(folder, "debug.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(result["debug_response"])
        saved_files["debug"] = path

    if "explain_response" in result and result["explain_response"]:
        path = os.path.join(folder, "explain.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(result["explain_response"])
        saved_files["explain"] = path

    return folder, saved_files

def get_latest_query_folder():
    base = "generated"
    if not os.path.exists(base):
        return None
    folders = [os.path.join(base, f) for f in os.listdir(base) if os.path.isdir(os.path.join(base, f))]
    return max(folders, key=os.path.getmtime) if folders else None

def show_file(filetype: str):
    folder = get_latest_query_folder()
    if not folder:
        print(cred("No generated queries found."))
        return

    filename = os.path.join(folder, f"{filetype}.py" if filetype != "explain" else "explain.md")
    if os.path.exists(filename):
        print(cblue(f"--- {filetype.upper()} ---"))
        with open(filename, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print(cred(f"No {filetype} file found in latest query folder."))

def _run_python_file(path: str, timeout: int = 10) -> str:
    if not path:
        return cred("No filename provided.")
    if not os.path.exists(path):
        return cred(f"File not found: {path}")
    try:
        proc = subprocess.run(["python", path], capture_output=True, text=True, timeout=timeout)
        out = proc.stdout.strip()
        err = proc.stderr.strip()
        if proc.returncode != 0:
            return cred(f"Error (exit {proc.returncode}):\n{err}") if err else cred(f"Process exited with code {proc.returncode}")
        return cgreen(out or "(no output)")
    except subprocess.TimeoutExpired:
        return cred(f"Execution timed out after {timeout}s")
    except Exception as e:
        return cred(f"Execution error: {e}")

# ---------------- CLI ---------------- #
def _print_help():
    print(cblue("""
Commands:
  help                   Show this help
  show <node>            Show node output: codegen | debug | explain
  generate <text>        Generate new code (creates new file)
  run [filename]         Run a saved Python file (if no filename, runs last saved)
  lastfile               Print last saved filename
  raw                    Show the full raw state returned by the workflow
  exit / quit            Quit

Notes:
  - Any plain text (not a command) will be treated as a follow-up edit to the last saved file.
  - Generated files are saved in ./generated/<timestamp>-<query>/.
"""))

def start_cli():
    print(cgreen("🤖 Cursor-AI Assistant (Interactive CLI)"))
    print("Type 'help' for commands. Type 'exit' to quit.\n")

    last_result = {}
    last_saved_filename = ""

    while True:
        try:
            text = input("> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye 👋")
            break

        if not text:
            continue

        parts = text.split()
        cmd = parts[0].lower()

        # help
        if cmd in {"help", "h", "?"}:
            _print_help()
            continue

        # exit
        if cmd in {"exit", "quit"}:
            print(cgreen("Goodbye 👋"))
            break

        # show node
        if cmd == "show" and len(parts) >= 2:
            node = parts[1].lower()
            if node not in VALID_NODES:
                print(cyellow("Unknown node. Valid: codegen, debug, explain"))
                continue
            show_file(node)
            continue

        # explicit generate -> always new file
        if cmd == "generate":
            query = text[len("generate"):].strip()
            if not query:
                print(cyellow("Provide a query after 'generate'."))
                continue
            result = app.invoke({"query": query})
            last_result = result or {}

            folder, saved_files = save_outputs(query, last_result)
            last_saved_filename = saved_files.get("codegen") or last_saved_filename
            print(cgreen(f"✅ Saved outputs to {folder}"))

            output = last_result.get("file_saved") or last_result.get("codegen_response") \
                     or last_result.get("debug_response") or last_result.get("explain_response")
            print(output or cyellow("No response from assistant."))
            continue

        # run filename or last saved
        if cmd == "run":
            filename = " ".join(parts[1:]).strip() if len(parts) >= 2 else last_saved_filename
            if not filename:
                print(cyellow("No filename given and no last saved file available."))
                continue
            print(_run_python_file(filename))
            continue

        # lastfile
        if cmd == "lastfile":
            print(cgreen(last_saved_filename or "No saved file yet."))
            continue

        # raw (debug)
        if cmd == "raw":
            print(last_result or cyellow("No last result."))
            continue

        # default: plain query -> edit last saved file
        query = text
        filename_to_edit = last_saved_filename if last_saved_filename else None

        previous_code = None
        if filename_to_edit and os.path.exists(filename_to_edit):
            with open(filename_to_edit, "r", encoding="utf-8") as f:
                previous_code = f.read()

        result = app.invoke({"query": query, "previous_code": previous_code})
        last_result = result or {}

        folder, saved_files = save_outputs(query, last_result, filename_override=filename_to_edit)
        last_saved_filename = filename_to_edit or last_saved_filename
        print(cgreen(f"✅ Saved outputs to {folder}"))

        output = last_result.get("file_saved") or last_result.get("codegen_response") \
                 or last_result.get("debug_response") or last_result.get("explain_response")
        print(output or cyellow("No response from assistant."))
