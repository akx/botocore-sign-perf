import json
import argparse
from pathlib import Path


def find_refs(obj, refs):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "ref":
                refs.add(v)
            else:
                find_refs(v, refs)
    elif isinstance(obj, list):
        for item in obj:
            find_refs(item, refs)


def find_unused_parameters(ruleset):
    defined_parameters = set(ruleset.get("parameters", {}).keys())
    referenced_parameters = set()
    find_refs(ruleset.get("rules", []), referenced_parameters)
    # Also find refs in the parameters themselves (for `default` values)
    find_refs(ruleset.get("parameters", {}), referenced_parameters)
    unused_parameters = defined_parameters - referenced_parameters
    return unused_parameters


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="*")
    ap.add_argument("--dir", "-d", type=Path)
    args = ap.parse_args()

    files = list(args.file)
    if args.dir:
        files.extend(args.dir.rglob("**/*rule*.json"))
        files.extend(args.dir.rglob("**/*rule*.json.gz"))

    if not files:
        ap.error("No files specified")

    for file_path in files:
        with open(file_path, "r") as f:
            ruleset = json.load(f)

        unused_parameters = find_unused_parameters(ruleset)

        if unused_parameters:
            print(json.dumps({str(file_path): sorted(unused_parameters)}))


if __name__ == "__main__":
    main()
