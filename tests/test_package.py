"""Tests for tabtools package metadata."""

from __future__ import annotations


class TestPackage:
    def test_version_string(self):
        import tabtools

        assert tabtools.__version__ == "0.1.1"

    def test_messages_loaded_prints(self, capsys):
        from tabtools._messages import loaded

        loaded("tabtools", "0.1.1")
        out = capsys.readouterr().out
        assert "ℹ️ [tabtools] v0.1.1 loaded." in out