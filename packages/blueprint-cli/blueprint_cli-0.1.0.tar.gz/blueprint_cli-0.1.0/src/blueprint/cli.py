import argparse
import os
import sys
from .core import Blueprint
from . import __version__  # Import version dynamically

CONFIG_FILE = ".blueprintrc"

BLUEPRINT_RC_TEMPLATE = f"""# Blueprint configuration file

# Blueprint version: {__version__}

# Maximum depth to traverse the directory tree (0 = unlimited)
depth=2

# Include hidden files and folders (true/false)
show_hidden=false

# Include files in the tree (true/false)
include_files=true

# Comma-separated list of patterns to ignore
ignore=*.pyc,*.pyo,__pycache__,node_modules

# Output format: "tree" or "markdown"
format=tree
"""

def load_config(root: str) -> dict:
    cfg_path = os.path.join(root, CONFIG_FILE)
    config = {}
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and "=" in line:
                    key, val = line.split("=", 1)
                    config[key.strip()] = val.strip()
    return config


class BlueprintCLI:
    def __init__(self):
        self.args = self.parse_args()
        # If no args provided, show version and exit
        if len(sys.argv) == 1:
            print(f"Blueprint CLI version {__version__}")
            sys.exit(0)

    def parse_args(self):
        parser = argparse.ArgumentParser(
            prog="blueprint",
            description=f"Blueprint {__version__} — Project structure generator"
        )
        parser.add_argument("path", nargs="?", default=".", help="Project root path")
        parser.add_argument("-o", "--output", help="Save output to a file")
        parser.add_argument("--no-files", action="store_true", help="Show directories only")
        parser.add_argument("-d", "--depth", type=int, help="Max depth of tree")
        parser.add_argument("--show-hidden", action="store_true", help="Include hidden files/folders")
        parser.add_argument("-i", "--ignore", help="Comma-separated ignore patterns")
        parser.add_argument("--no-summary", action="store_true", help="Hide folder/file summary")
        parser.add_argument("-f", "--format", choices=["tree", "markdown"], default=None, help="Output format")
        parser.add_argument("--init-config", action="store_true", help="Generate a default .blueprintrc in the project root")
        parser.add_argument("--version", action="store_true", help="Show Blueprint CLI version")
        return parser.parse_args()

    def run(self):
        args = self.args

        if args.version:
            print(f"Blueprint CLI version {__version__}")
            return

        # Handle --init-config
        if args.init_config:
            cfg_path = os.path.join(args.path, CONFIG_FILE)
            if os.path.exists(cfg_path):
                print(f"{CONFIG_FILE} already exists at {args.path}")
            else:
                with open(cfg_path, "w", encoding="utf-8") as f:
                    f.write(BLUEPRINT_RC_TEMPLATE)
                print(f"Created default {CONFIG_FILE} at {args.path}")
            return

        if not os.path.exists(args.path):
            print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
            sys.exit(1)

        config = load_config(args.path)

        max_depth = args.depth if args.depth is not None else int(config.get("depth", 0)) or None
        show_hidden = args.show_hidden or config.get("show_hidden", "false").lower() == "true"
        include_files = not args.no_files and config.get("include_files", "true").lower() == "true"
        ignores = config.get("ignore", "").split(",") if config.get("ignore") else []
        if args.ignore:
            ignores += args.ignore.split(",")

        output_format = args.format or config.get("format", "tree")

        bp = Blueprint(
            root=args.path,
            include_files=include_files,
            max_depth=max_depth,
            ignores=ignores,
            show_hidden=show_hidden
        )

        output = bp.generate(format=output_format)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Saved to {args.output}")
        else:
            try:
                print(output)
            except UnicodeEncodeError:
                print(output.encode("utf-8", errors="replace").decode("utf-8"))

            if not args.no_summary:
                print("\n" + bp.summary())


def main():
    cli = BlueprintCLI()
    cli.run()


if __name__ == "__main__":
    main()
