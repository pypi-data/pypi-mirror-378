# In file: mycheats/practs.py
import importlib.resources as pkg_resources

PRACTICALS_PATH = "mycheats.practicals"

def show(name: str):
    try:
        filename = f"{name}.py"
        code = pkg_resources.read_text(PRACTICALS_PATH, filename)
        print(f"--- Code for: {name} ---\n")
        print(code)
    except FileNotFoundError:
        print(f"❌ Error: Cheatsheet '{name}' not found.")
        print("Use list_all() to see available cheatsheets.")

def list_all():
    print("📚 Available cheatsheets:")
    try:
        files = pkg_resources.contents(PRACTICALS_PATH)
        cheatsheets = [f.replace(".py", "") for f in files if f.endswith(".py") and f != "__init__.py"]
        if not cheatsheets:
            print(" - No cheatsheets found.")
            return
        for name in sorted(cheatsheets):
            print(f" - {name}")
    except ModuleNotFoundError:
        print("Error reading cheatsheets directory.")