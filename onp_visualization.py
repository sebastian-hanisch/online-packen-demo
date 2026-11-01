"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import onp_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.3), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_bins(bins: dict, ref: int, ref_label: str, ffd: int, lower: int, selected: str):
    """Behälter je Regel; Referenz, FFD und Untergrenze als Linien."""
    names = list(C.REGELN)
    colors = [C.COLORS[n] if n == selected else "rgba(150,150,150,0.55)" for n in names]
    fig = go.Figure(go.Bar(x=names, y=[bins[n] for n in names], marker_color=colors, text=[str(bins[n]) for n in names], textposition="outside",
                           hovertemplate="%{x}: %{y} Behälter<extra></extra>"))
    fig.add_hline(y=ref, line=dict(color=C.COLOR_GUARANTEE, dash="dash"), annotation_text=f"{ref_label}: {ref}", annotation_position="top left")
    if ref_label != "FFD":
        fig.add_hline(y=ffd, line=dict(color=C.COLOR_REF, dash="dot"), annotation_text=f"FFD (offline): {ffd}", annotation_position="bottom left")
    fig.add_hline(y=lower, line=dict(color=C.COLOR_REF, dash="dot"), annotation_text=f"Untergrenze: {lower}", annotation_position="bottom right")
    top = max(max(bins.values()), ref) * 1.25
    fig.update_yaxes(title_text="Behälter", range=[0, top])
    return _base(fig, height=340)


def build_fills(fills: list[float], limit: int = 120):
    """Füllgrad der ersten Behälter der hervorgehobenen Regel in Prozent."""
    show = fills[:limit]
    colors = [C.COLOR_FF if f >= 90 else C.COLOR_GUARANTEE if f >= 60 else C.COLOR_NF for f in show]
    fig = go.Figure(go.Bar(x=list(range(1, len(show) + 1)), y=show, marker_color=colors, hovertemplate="Behälter %{x}: %{y:.1f} %<extra></extra>"))
    fig.update_xaxes(title_text="Behälter (in der Reihenfolge ihrer Öffnung)")
    fig.update_yaxes(title_text="Füllgrad (%)", range=[0, 105])
    return _base(fig, height=260)


def _grouped(rows, key, ycol_names, title, height=360, ref_line=None):
    fig = go.Figure()
    for r in ycol_names:
        fig.add_trace(go.Bar(x=[row[key] for row in rows], y=[row[r] for row in rows], name=r, marker_color=C.COLORS[r], hovertemplate="%{x}: %{y:.3f}<extra>" + r + "</extra>"))
    fig.update_layout(barmode="group")
    top = max(row[r] for row in rows for r in ycol_names)
    fig.update_yaxes(title_text=title, range=[0.9, top * 1.08])
    if ref_line is not None:
        fig.add_hline(y=ref_line, line=dict(color=C.COLOR_REF, dash="dot"))
    return _base(fig, height=height)


def build_phases(rows):
    return _grouped(rows, "Präfix", C.REGELN, "Behälter geteilt durch Optimum", ref_line=1.0)


def build_orders(rows):
    return _grouped(rows, "Reihenfolge", C.REGELN, "Behälter geteilt durch Optimum", ref_line=1.0)


def build_typical(rows):
    return _grouped(rows, "Folge", C.REGELN, "Behälter geteilt durch FFD", height=420, ref_line=1.0)


def build_nf(rows):
    fig = go.Figure()
    xs = [str(r["Stücke"]) for r in rows]
    for r in C.REGELN:
        fig.add_trace(go.Scatter(x=xs, y=[row[r] for row in rows], mode="lines+markers", name=r, line=dict(color=C.COLORS[r], width=3 if r == "Next Fit" else 2),
                                 hovertemplate="%{x} Stücke: %{y:.3f}<extra>" + r + "</extra>"))
    fig.add_hline(y=2.0, line=dict(color=C.COLOR_GUARANTEE, dash="dash"), annotation_text="Garantie Next Fit 2", annotation_position="top left")
    fig.update_xaxes(title_text="Zahl der Stücke", type="category")
    fig.update_yaxes(title_text="Behälter geteilt durch Optimum", range=[0.9, 2.2])
    return _base(fig)


def build_growth(rows):
    fig = go.Figure()
    xs = [str(r["n"]) for r in rows]
    for r in ("Next Fit", "First Fit", "Best Fit"):
        fig.add_trace(go.Scatter(x=xs, y=[row[r] for row in rows], mode="lines+markers", name=r, line=dict(color=C.COLORS[r], width=3),
                                 hovertemplate="n = %{x}: %{y:.3f}<extra>" + r + "</extra>"))
    fig.update_xaxes(title_text="Zahl der Stücke n", type="category")
    fig.update_yaxes(title_text="Behälter geteilt durch FFD", range=[1.0, max(r["Next Fit"] for r in rows) * 1.05])
    return _base(fig)
