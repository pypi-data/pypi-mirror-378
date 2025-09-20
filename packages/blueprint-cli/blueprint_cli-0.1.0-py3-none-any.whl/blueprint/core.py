import os
import fnmatch
import io
from typing import List, Generator

class Blueprint:
    DEFAULT_IGNORES = ["__pycache__", "*.pyc", "*.pyo", "*.exe", "*.dll", "*.so"]

    # ASCII connectors only
    CONN_MID = "+-- "
    CONN_END = "`-- "
    EXT_MID = "|   "
    EXT_END = "    "

    def __init__(self,
                 root: str = ".",
                 include_files: bool = True,
                 max_depth: int | None = None,
                 ignores: List[str] | None = None,
                 show_hidden: bool = False):
        self.root = os.path.abspath(root)
        self.include_files = include_files
        self.max_depth = max_depth
        self.show_hidden = show_hidden

        # Start with default ignores
        self.ignores = self.DEFAULT_IGNORES + (ignores or [])
        # Merge .gitignore if exists
        self._load_gitignore()

        self.total_files = 0
        self.total_folders = 0

    def _load_gitignore(self):
        gitignore_path = os.path.join(self.root, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line.endswith("/"):
                            # Ignore folder itself
                            self.ignores.append(line.rstrip("/"))
                            # Ignore folder contents
                            line = line + "*"
                        self.ignores.append(line)

    def _should_ignore(self, path: str) -> bool:
        name = os.path.basename(path)
        rel_path = os.path.relpath(path, self.root).replace("\\", "/")

        # If show_hidden is True, never ignore hidden files/folders
        if self.show_hidden:
            return any(
                fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern)
                for pattern in self.ignores
                if not pattern.startswith(".")  # ignore patterns for hidden files still apply if they are not hidden
            )

        # If show_hidden is False, ignore hidden files/folders
        if name.startswith("."):
            return True

        return any(fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel_path, pattern)
                for pattern in self.ignores)


    def _walk(self, path: str, prefix: str = "", depth: int = 0) -> Generator[str, None, None]:
        if self.max_depth is not None and depth >= self.max_depth:
            return
        try:
            entries = os.listdir(path)
        except PermissionError:
            return
        entries.sort()
        entries = [e for e in entries if not self._should_ignore(os.path.join(path, e))]

        for idx, entry in enumerate(entries):
            full_path = os.path.join(path, entry)
            is_dir = os.path.isdir(full_path)
            connector = self.CONN_MID if idx < len(entries) - 1 else self.CONN_END
            yield f"{prefix}{connector}{entry}/" if is_dir else f"{prefix}{connector}{entry}"

            if is_dir:
                self.total_folders += 1
                extension = self.EXT_MID if idx < len(entries) - 1 else self.EXT_END
                yield from self._walk(full_path, prefix + extension, depth + 1)
            elif self.include_files:
                self.total_files += 1

    def generate(self, format: str = "tree") -> str:
        buf = io.StringIO()
        buf.write(f"{os.path.basename(self.root)}/\n")
        for line in self._walk(self.root):
            buf.write(line + "\n")
        result = buf.getvalue().rstrip()

        if format == "markdown":
            result = f"```\n{result}\n```"
        return result

    def summary(self) -> str:
        return f"{self.total_folders} folders | {self.total_files} files"
