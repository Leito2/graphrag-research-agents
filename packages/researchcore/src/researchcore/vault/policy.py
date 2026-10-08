"""Which notes get indexed (REQ-16). The resolver still knows excluded notes, so links to them aren't gaps."""
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import PurePosixPath

ALWAYS_EXCLUDED = ".obsidian"


@dataclass(frozen=True)
class IndexPolicy:
    exclude_folders: tuple[str, ...] = ()    # folder names (any depth) or vault-relative folder paths ("A/B")
    private_tag: str = "private"             # also matches nested tags such as "private/health"
    output_dir: str | None = None            # RESEARCH_OUTPUT_DIR, relative to the vault root
    index_output: bool = False

    def is_indexable(self, path: str, tags: Iterable[str] = ()) -> bool:
        folder = PurePosixPath(path).parent
        names, folder_path = set(folder.parts), folder.as_posix()

        def under(prefix: str) -> bool:
            return folder_path == prefix or folder_path.startswith(prefix + "/")

        if ALWAYS_EXCLUDED in names:
            return False
        if any(under(e) if "/" in e else e in names for e in self.exclude_folders):
            return False
        if self.output_dir and not self.index_output and under(self.output_dir.strip("/")):
            return False
        private = self.private_tag.lower()
        return not any(t.lower() == private or t.lower().startswith(private + "/") for t in tags)
