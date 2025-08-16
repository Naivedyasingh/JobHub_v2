# generate_tree.py
# Creates a single, visual tree of your JobHub project using Graphviz DOT.
# Output: jobhub_tree.png and jobhub_tree.dot in the project root.

import os
import re
from pathlib import Path

DOT_FILE = "jobhub_tree.dot"
PNG_FILE = "jobhub_tree.png"

# Project folders (adjust if your structure differs)
ROOT = Path(__file__).parent
COMPONENTS = ROOT / "components"
DB = ROOT / "db"
UTILS = ROOT / "utils"
SCREENS = ROOT / "screens"

# Files to include (based on your attachments)
FILES = [
    ROOT / "main.py",
    ROOT / "requirements.txt",
    COMPONENTS / "sidebar.py",
    DB / "models.py",
    DB / "schema.sql",
    UTILS / "auth.py",
    UTILS / "applications.py",
    UTILS / "job_management.py",
    UTILS / "offers.py",
    UTILS / "jobs.py",           # UI utility version
    ROOT / "data_helpers.py",    # DAO/service version (from attachment name)
    SCREENS / "home.py",
    SCREENS / "auth_choice.py",
    SCREENS / "login.py",
    SCREENS / "signup.py",
    SCREENS / "job_dashboard.py",
    SCREENS / "hire_dashboard.py",
    SCREENS / "browse_seekers.py",
    SCREENS / "offer_job.py",
    SCREENS / "post_job.py",
    SCREENS / "my_applications.py",
    SCREENS / "view_applications.py",
    SCREENS / "my_job_postings.py",
    SCREENS / "profile.py",
    SCREENS / "contact.py",
]

def norm(path: Path) -> str:
    try:
        rel = path.relative_to(ROOT).as_posix()
    except Exception:
        rel = path.as_posix()
    return rel

def file_exists(path: Path) -> bool:
    return path.exists() and path.is_file()

def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""

def parse_imports(py_text: str) -> set[str]:
    """
    Parse simple 'from X import Y' and 'import X' to infer local module references.
    We only keep references to our known package roots: components., db., utils., screens.
    """
    refs = set()
    for line in py_text.splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        m1 = re.match(r"from\s+([a-zA-Z0-9_\.]+)\s+import\s+(.+)", line)
        m2 = re.match(r"import\s+([a-zA-Z0-9_\.]+)", line)
        if m1:
            pkg = m1.group(1)
            if pkg.startswith(("components", "db", "utils", "screens")):
                refs.add(pkg)
        elif m2:
            pkg = m2.group(1)
            if pkg.startswith(("components", "db", "utils", "screens")):
                refs.add(pkg)
    return refs

def module_to_paths(mod: str) -> list[str]:
    """
    Convert a module name like 'utils.auth' -> potential paths ['utils/auth.py', 'utils/auth/__init__.py']
    We will match against our FILES list to resolve to existing nodes.
    """
    parts = mod.split(".")
    if len(parts) == 1:
        return [f"{parts[0]}.py", f"{parts[0]}/__init__.py"]
    p = "/".join(parts)
    return [f"{p}.py", f"{p}/__init__.py"]

def build_known_nodes() -> dict[str, Path]:
    """
    Map normalized relative path -> absolute Path for all included FILES that exist.
    """
    mapping = {}
    for p in FILES:
        if file_exists(p):
            mapping[norm(p)] = p
    return mapping

def resolve_ref_to_file(ref: str, known_nodes: dict[str, Path]) -> str | None:
    """
    Try to map a module reference like 'utils.auth' to a concrete file path present in known_nodes.
    """
    candidates = module_to_paths(ref)
    for c in candidates:
        if c in known_nodes:
            return c
        # also try with .py already removed if needed
        if c.endswith(".py") and c[:-3] in known_nodes:
            return c[:-3]
    # Attempt partial matches (e.g., import utils.jobs -> we may have two variants)
    # Prefer exact utils/jobs.py
    for k in known_nodes.keys():
        if k.replace("\\", "/").endswith(candidates[0]):
            return k
    return None

def guess_label(path_rel: str) -> str:
    """
    Create a friendly node label with short info based on filename.
    """
    base = os.path.basename(path_rel)
    if base == "main.py":
        return "main.py (entry)"
    if path_rel.startswith("components/"):
        return f"{path_rel} (component)"
    if path_rel.startswith("db/"):
        return f"{path_rel} (database)"
    if path_rel.startswith("utils/"):
        return f"{path_rel} (utils)"
    if path_rel.startswith("screens/"):
        return f"{path_rel} (screen)"
    if base == "requirements.txt":
        return "requirements.txt"
    if base == "schema.sql":
        return "db/schema.sql"
    return path_rel

def color_for(path_rel: str) -> str:
    """
    Color by layer.
    """
    if path_rel == "main.py":
        return "#ff6b6b"      # red
    if path_rel.startswith("screens/"):
        return "#4ecdc4"      # teal
    if path_rel.startswith("utils/"):
        return "#45b7d1"      # blue
    if path_rel.startswith("db/"):
        return "#96ceb4"      # green
    if path_rel.startswith("components/"):
        return "#feca57"      # yellow
    if path_rel.endswith(".sql") or path_rel.endswith(".txt"):
        return "#e0e0e0"      # gray
    return "#dddddd"

def extract_edges(known_nodes: dict[str, Path]) -> list[tuple[str, str, str]]:
    """
    Build edges (src -> dst, label) from import statements and known relationships.
    """
    edges: list[tuple[str, str, str]] = []

    # Parse imports for each .py file
    for rel, abs_path in known_nodes.items():
        if not rel.endswith(".py"):
            continue
        text = safe_read_text(abs_path)
        refs = parse_imports(text)
        for ref in refs:
            target_rel = resolve_ref_to_file(ref, known_nodes)
            if target_rel:
                edges.append((rel, target_rel, "imports"))

    # Add explicit, high-certainty relationships derived from your codebase:

    # main.py routes to screens and uses db/models + components/sidebar
    if "main.py" in known_nodes:
        for s in list(known_nodes.keys()):
            if s.startswith("screens/") and s.endswith(".py"):
                edges.append(("main.py", s, "routes"))
        if "components/sidebar.py" in known_nodes:
            edges.append(("main.py", "components/sidebar.py", "uses"))
        if "db/models.py" in known_nodes:
            edges.append(("main.py", "db/models.py", "init_db"))
        if "db/schema.sql" in known_nodes:
            edges.append(("db/models.py", "db/schema.sql", "init_schema"))

    # screens -> utils (based on actual usage in provided files)
    def add_if_exists(frm, to, label):
        if frm in known_nodes and to in known_nodes:
            edges.append((frm, to, label))

    add_if_exists("screens/login.py", "utils/auth.py", "uses")
    add_if_exists("screens/signup.py", "utils/validation.py", "uses")
    add_if_exists("screens/signup.py", "utils/auth.py", "uses")
    add_if_exists("screens/profile.py", "utils/auth.py", "uses")
    add_if_exists("screens/profile.py", "utils/validation.py", "uses")
    add_if_exists("screens/job_dashboard.py", "utils/applications.py", "uses")
    add_if_exists("screens/job_dashboard.py", "utils/offers.py", "uses")
    add_if_exists("screens/hire_dashboard.py", "utils/applications.py", "uses")
    add_if_exists("screens/browse_seekers.py", "utils/offers.py", "uses")
    add_if_exists("screens/offer_job.py", "utils/offers.py", "uses")
    add_if_exists("screens/post_job.py", "utils/jobs.py", "uses")
    add_if_exists("screens/my_applications.py", "utils/applications.py", "uses")
    add_if_exists("screens/my_applications.py", "utils/offers.py", "uses")
    add_if_exists("screens/my_job_postings.py", "utils/job_management.py", "uses")
    add_if_exists("components/sidebar.py", "utils/auth.py", "uses")

    # utils -> db/models
    add_if_exists("utils/auth.py", "db/models.py", "uses")
    add_if_exists("utils/applications.py", "db/models.py", "uses")
    add_if_exists("utils/job_management.py", "db/models.py", "uses")
    add_if_exists("utils/offers.py", "db/models.py", "uses")
    add_if_exists("utils/jobs.py", "db/models.py", "uses")
    # DAO/service file also uses DatabaseManager directly
    add_if_exists("data_helpers.py", "db/models.py", "uses")

    # Some screens also touch db/models directly for reads
    add_if_exists("screens/home.py", "db/models.py", "uses")
    add_if_exists("screens/job_dashboard.py", "db/models.py", "uses")
    add_if_exists("screens/hire_dashboard.py", "db/models.py", "uses")
    add_if_exists("screens/browse_seekers.py", "db/models.py", "uses")

    return edges

def write_dot(nodes: dict[str, Path], edges: list[tuple[str, str, str]]):
    with open(DOT_FILE, "w", encoding="utf-8") as f:
        f.write('digraph JobHubTree {\n')
        f.write('  graph [rankdir=LR, splines=true, nodesep=0.4, ranksep=1.0];\n')
        f.write('  node [shape=box, style=filled, fontname="Helvetica", fontsize=10];\n')
        f.write('  edge [fontname="Helvetica", fontsize=9, color="#888888"];\n\n')

        # Subgraphs by layer
        clusters = {
            "entry": [],
            "components": [],
            "screens": [],
            "utils": [],
            "db": [],
            "other": [],
        }
        for rel in nodes.keys():
            if rel == "main.py":
                clusters["entry"].append(rel)
            elif rel.startswith("components/"):
                clusters["components"].append(rel)
            elif rel.startswith("screens/"):
                clusters["screens"].append(rel)
            elif rel.startswith("utils/"):
                clusters["utils"].append(rel)
            elif rel.startswith("db/"):
                clusters["db"].append(rel)
            else:
                clusters["other"].append(rel)

        def emit_cluster(name, label, items):
            if not items:
                return
            f.write(f'  subgraph cluster_{name} ' + '{\n')
            f.write(f'    label="{label}"; color="#cccccc"; style="rounded";\n')
            for rel in items:
                color = color_for(rel)
                label_txt = guess_label(rel)
                f.write(f'    "{rel}" [label="{label_txt}", fillcolor="{color}"];\n')
            f.write('  }\n\n')

        emit_cluster("entry", "Entry Point", clusters["entry"])
        emit_cluster("components", "Components", clusters["components"])
        emit_cluster("screens", "Screens", clusters["screens"])
        emit_cluster("utils", "Utils", clusters["utils"])
        emit_cluster("db", "Database", clusters["db"])
        emit_cluster("other", "Other", clusters["other"])

        # Edges
        for src, dst, label in edges:
            f.write(f'  "{src}" -> "{dst}" [label="{label}"];\n')

        f.write('}\n')

def render_png():
    """
    Try to render PNG using 'dot' if Graphviz is installed.
    If not installed, instruct user to run the command.
    """
    try:
        import subprocess
        subprocess.run(["dot", "-Tpng", DOT_FILE, "-o", PNG_FILE], check=True)
        print(f"Generated {PNG_FILE}")
    except Exception as e:
        print("Could not auto-render PNG. If Graphviz is installed, run:")
        print(f"  dot -Tpng {DOT_FILE} -o {PNG_FILE}")
        print(f"(Error: {e})")

def main():
    # Filter only existing files
    existing = [p for p in FILES if file_exists(p)]
    if not existing:
        print("No target files found. Please run this in your JobHub project root.")
        return

    known_nodes = build_known_nodes()
    edges = extract_edges(known_nodes)
    write_dot(known_nodes, edges)
    render_png()
    print(f"Wrote DOT: {DOT_FILE}")
    if os.path.exists(PNG_FILE):
        print(f"Open: {PNG_FILE}")

if __name__ == "__main__":
    main()
