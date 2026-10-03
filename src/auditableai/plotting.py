"""Shared figure styling. Statistical estimates must be computed explicitly.

Use MPLBACKEND=Agg for headless server rendering. This module intentionally
does not select a backend or compute confidence intervals.
"""


def apply_thesis_style(*, font_scale: float = 1.0) -> None:
    """Apply the dissertation's initial seaborn/matplotlib visual defaults."""
    import seaborn as sns

    sns.set_theme(
        context="paper",
        style="ticks",
        palette="colorblind",
        font="DejaVu Sans",
        font_scale=font_scale,
        rc={
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titleweight": "normal",
            "figure.facecolor": "white",
            "savefig.facecolor": "white",
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        },
    )
