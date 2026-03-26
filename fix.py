import os

with open("app.py", "r") as f:
    lines = f.readlines()

def build_app():
    out = []
    in_optimizer = False
    for i, line in enumerate(lines):
        if line.startswith("def render_optimizer():"):
            in_optimizer = True
            out.append(line)
            continue
            
        if line.startswith("# --- ROUTING LOGIC ---"):
            in_optimizer = False

        if in_optimizer:
            if line.strip() == "":
                out.append(line)
            else:
                out.append("    " + line)
        else:
            out.append(line)
            
    with open("app.py", "w") as f:
        f.writelines(out)

build_app()
