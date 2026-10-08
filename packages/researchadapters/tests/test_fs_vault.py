from researchadapters.fs_vault import FsVault, iter_vault, read_note
from researchcore.ports import VaultReader


def test_iter_vault_is_recursive_and_skips_obsidian(tmp_path):
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / ".obsidian" / "workspace.md").write_text("x", encoding="utf-8")
    (tmp_path / "01 - Area" / "Course").mkdir(parents=True)
    (tmp_path / "01 - Area" / "Course" / "00 - Welcome.md").write_text("# hi", encoding="utf-8")
    (tmp_path / "Root.md").write_text("# root", encoding="utf-8")
    assert iter_vault(tmp_path) == ["01 - Area/Course/00 - Welcome.md", "Root.md"]


def test_read_note_reads_nested_notes(tmp_path):
    (tmp_path / "Area" / "Course").mkdir(parents=True)
    (tmp_path / "Area" / "Course" / "Note.md").write_text("# probe", encoding="utf-8")
    assert read_note(tmp_path, "Area/Course/Note.md") == "# probe"


def test_fs_vault_implements_the_vault_reader_port(tmp_path):
    (tmp_path / "Note.md").write_text("# probe", encoding="utf-8")
    vault: VaultReader = FsVault(tmp_path)
    assert [vault.read(p) for p in vault.list_notes()] == ["# probe"]
