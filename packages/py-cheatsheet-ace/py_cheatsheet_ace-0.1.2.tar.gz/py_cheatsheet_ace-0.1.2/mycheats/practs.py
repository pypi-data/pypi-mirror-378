import importlib.resources as pkg_resources

# The path to your practicals folder inside the package
PRACTICALS_PATH = "mycheats.practicals"

def show(name: str):
    """Prints the code of a given practical file."""
    try:
        filename = f"{name}.py"
        code = pkg_resources.read_text(PRACTICALS_PATH, filename)
        print(f"--- Code for: {name} ---\n")
        print(code)
    except FileNotFoundError:
        print(f"❌ Error: Cheatsheet '{name}' not found.")
        print("Use list_all() to see available cheatsheets.")

def list_all():
    """Lists all available practical files."""
    print("📚 Available cheatsheets:")
    try:
        files = pkg_resources.contents(PRACTICALS_PATH)
        # Filter out __init__.py and other non-cheatsheet files
        cheatsheets = [f.replace(".py", "") for f in files if f.endswith(".py") and not f.startswith("__")]
        if not cheatsheets:
            print(" - No cheatsheets found.")
            return
        for name in sorted(cheatsheets):
            print(f" - {name}")
    except ModuleNotFoundError:
        print("Error reading cheatsheets directory.")