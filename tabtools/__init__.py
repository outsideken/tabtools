"""
tabtools
========
Tabular profiling and anomaly scoring for the JEMA toolkit.

Import directly::

    from tabtools.profile import quick_profile, category_candidates
    from tabtools.anomaly import anomaly_score, flag_outliers, anomaly_summary

Compose with ``viztools.palettes.ANOMALY_PALETTE`` for diverging anomaly
maps and charts.  Depends on ``wherewhen>=0.2.0`` for notification style.

On first import prints ``ℹ️ [tabtools] v<version> loaded.``
"""

from tabtools._version import __version__

from tabtools.anomaly import anomaly_score, anomaly_summary, flag_outliers
from tabtools.profile import category_candidates, quick_profile

__all__ = [
    # profile
    "quick_profile",
    "category_candidates",
    # anomaly
    "anomaly_score",
    "flag_outliers",
    "anomaly_summary",
    "list_functions",
]


def list_functions(query: str = "") -> None:
    """Print a catalogue of public tabtools functions grouped by module."""
    import inspect
    from tabtools import anomaly, profile

    sections = [
        ("profile", profile),
        ("anomaly", anomaly),
    ]
    q = query.strip().lower()

    for section_name, module in sections:
        names = getattr(module, "__all__", [])
        funcs = [
            (name, getattr(module, name))
            for name in names
            if inspect.isfunction(getattr(module, name, None))
        ]
        if q:
            funcs = [
                (n, o) for n, o in funcs
                if q in n.lower() or q in (inspect.getdoc(o) or "").split("\n")[0].lower()
            ]
        if not funcs:
            continue
        print(f"\n{'─' * 60}")
        print(f"  {section_name}")
        print(f"{'─' * 60}")
        for name, obj in funcs:
            doc = inspect.getdoc(obj) or ""
            summary = doc.split("\n")[0]
            print(f"  {name:<35} {summary}")


from tabtools._messages import loaded as _loaded

_loaded("tabtools", __version__)