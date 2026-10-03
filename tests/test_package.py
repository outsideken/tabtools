"""Tests for tabtools package metadata."""

from __future__ import annotations


class TestPackage:
    def test_version_has_one_source(self):
        # tabtools/_version.py is the only place the version is typed;
        # pyproject.toml reads it from there (outsideken/tabtools#2).
        import re
        from pathlib import Path

        import tabtools

        pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")
        project = re.search(r"^\[project\]\n(.*?)(?=^\[)", pyproject, re.M | re.S).group(1)
        assert not re.search(r"^version\s*=", project, re.M), "[project] must not type a version"
        assert re.search(r'^dynamic\s*=\s*\["version"\]', project, re.M)
        assert 'attr = "tabtools._version.__version__"' in pyproject
        assert re.fullmatch(r"\d+\.\d+\.\d+([ab]|rc)?\d*", tabtools.__version__)

    def test_messages_loaded_prints(self, capsys):
        from tabtools._messages import loaded

        loaded("tabtools", "1.2.3")  # sample value, not the package version
        out = capsys.readouterr().out
        assert "ℹ️ [tabtools] v1.2.3 loaded." in out