from pathlib import Path

import pytest

from src.tools.file_tools import EditTool, FindTool, GrepTool, ListTool, ReadTool, WriteTool

pytestmark = pytest.mark.unit


def test_read_write_and_append(tmp_path: Path) -> None:
    writer = WriteTool(tmp_path)
    reader = ReadTool(tmp_path)

    writer.invoke({"path": "nested/a.txt", "content": "one\n"})
    writer.invoke({"path": "nested/a.txt", "content": "two\n", "mode": "append"})

    assert reader.invoke({"path": "nested/a.txt"}).content == "one\ntwo\n"


def test_path_traversal_is_blocked(tmp_path: Path) -> None:
    tool = ReadTool(tmp_path)

    with pytest.raises(PermissionError, match="escapes workspace"):
        tool.invoke({"path": tmp_path.parent / "outside.txt"})


def test_edit_requires_unique_match(tmp_path: Path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("same same", encoding="utf-8")
    tool = EditTool(tmp_path)

    with pytest.raises(ValueError, match="must be unique"):
        tool.invoke({"path": "a.txt", "old_text": "same", "new_text": "new"})


def test_find_grep_and_list_ignore_git(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "hidden.py").write_text("alpha", encoding="utf-8")

    found = FindTool(tmp_path).invoke({"pattern": "*.py"}).content
    matches = GrepTool(tmp_path).invoke({"pattern": "alpha", "glob": "*.py"}).content
    listing = ListTool(tmp_path).invoke({"path": "src"}).content

    assert found == "src/a.py"
    assert matches == "src/a.py:1:def alpha():"
    assert listing == "f a.py"
