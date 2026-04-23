import os
import re

FILES = [
    "lib/PubTypes.lua",
    "lib/Types.lua",
    "lib/WidgetTypes.lua",
    "lib/config.lua",
    "lib/Internal.lua",
    "lib/API.lua",
    "lib/widgets/Root.lua",
    "lib/widgets/Window.lua",
    "lib/widgets/Menu.lua",
    "lib/widgets/Format.lua",
    "lib/widgets/Text.lua",
    "lib/widgets/Button.lua",
    "lib/widgets/Checkbox.lua",
    "lib/widgets/RadioButton.lua",
    "lib/widgets/Input.lua",
    "lib/widgets/Combo.lua",
    "lib/widgets/Tree.lua",
    "lib/widgets/Table.lua",
    "lib/widgets/Tab.lua",
    "lib/widgets/Plot.lua",
    "lib/widgets/Image.lua",
    "lib/widgets/init.lua",
    "lib/demoWindow.lua",
    "lib/init.lua",
]

def path_to_varname(path):
    return "_iris_" + path.replace("lib/", "").replace(".lua", "").replace("/", "_")

def normalize(path):
    parts = []
    for seg in path.split("/"):
        if seg == "..":
            if parts: parts.pop()
        elif seg and seg != ".":
            parts.append(seg)
    return "/".join(parts)

def resolve_require(inner, current_file):
    inner = inner.strip()
    if not inner.startswith("script"):
        return None

    current_file = current_file.replace("\\", "/")
    resolved_dir = "/".join(current_file.split("/")[:-1])
    parts = inner.split(".")

    i = 1
    name_parts = []
    while i < len(parts):
        if parts[i] == "Parent":
            parent = "/".join(resolved_dir.split("/")[:-1])
            resolved_dir = parent if parent else "lib"
        else:
            name_parts = parts[i:]
            break
        i += 1

    if not name_parts:
        return None

    name = "/".join(name_parts)
    for candidate in [f"{resolved_dir}/{name}.lua", f"{resolved_dir}/{name}/init.lua"]:
        if normalize(candidate) in FILES:
            return path_to_varname(normalize(candidate))

    return None

def strip_comments(src):
    src = re.sub(r'--\[\[.*?\]\]', '', src, flags=re.DOTALL)
    src = re.sub(r'--[^\n]*', '', src)
    src = re.sub(r'\n\s*\n', '\n', src)
    return src.strip()

def bundle():
    out = [
        "assert(game:GetService('RunService'):IsClient(), 'Iris must run on the client')",
        "",
    ]
    unresolved = []
    missing = []

    for filepath in FILES:
        if not os.path.exists(filepath):
            missing.append(filepath)
            continue

        varname = path_to_varname(filepath)

        with open(filepath, "r", encoding="utf-8") as f:
            src = f.read()

        # src = strip_comments(src)

        def replacer(match):
            resolved = resolve_require(match.group(1), filepath)
            if resolved:
                return resolved
            if match.group(1).strip().startswith("script"):
                unresolved.append(f"  {filepath}: require({match.group(1).strip()})")
            return match.group(0)

        src = re.sub(r'require\(([^)]+)\)', replacer, src)

        out.append(f"local {varname} = (function()")
        out.append(f"    local script = {{ Name = \"{os.path.basename(filepath)}\" }}")
        for line in src.splitlines():
            out.append("    " + line)
        out.append("end)()")
        out.append("")

    out.append("return _iris_init")

    with open("iris_bundle.lua", "w", encoding="utf-8") as f:
        f.write("\n".join(out))

    print("── Done")
    if missing:
        print(f"── Missing files ({len(missing)}):")
        for f in missing: print(f"     {f}")
    if unresolved:
        print(f"── Unresolved requires ({len(unresolved)}):")
        for r in unresolved: print(r)
    else:
        print("── All requires resolved cleanly")
    print(f"── Output: iris_bundle.lua ({os.path.getsize('iris_bundle.lua') // 1024}kb)")
    print("── URL after push:")
    print("     https://raw.githubusercontent.com/Hawkking-cloud/LoadstringIris/main/iris_bundle.lua")

if __name__ == "__main__":
    bundle()
