# -*- coding: utf-8 -*-
"""Hình Oxyz 3D xoay được (Plotly) cho Trạm 1, cùng phong cách Lab "Tọa độ Điểm & Vectơ" sẵn có.

Owner 18/11/2026: hình tĩnh dựng từ tọa độ bị suy biến (M, N rơi lên trục z); cần tương tác xoay
như các bộ phục dựng 3D đã làm. Hình tĩnh SVG vẫn giữ cho bản in.
Chỉ dùng đúng tọa độ trong đề (model['points'] do precision_visual_engine bóc tách), không gọi AI.
"""


def _num(v):
    v = float(v)
    return str(int(v)) if v.is_integer() else f'{v:g}'


def _label(name, p):
    return f'{name}({_num(p[0])};{_num(p[1])};{_num(p[2])})'


def oxyz_figure(points, segments=(), arrow=None, title=''):
    """points: {tên: (x,y,z)}; segments: [(tên1, tên2)]; arrow: (gốc, ngọn) vẽ có mũi tên."""
    import plotly.graph_objects as go

    fig = go.Figure()
    coords = [c for p in points.values() for c in p] + [0.0]
    span = max(abs(c) for c in coords) or 1.0
    # Mỗi trục dài theo tọa độ lớn nhất trên chính trục đó (không kéo cả ba trục theo trục dài nhất).
    ext = [max([abs(p[i]) for p in points.values()] + [span * 0.25]) * 1.3 for i in range(3)]
    # Ba trục qua gốc O
    for axis, vec, color in (('x', (ext[0], 0, 0), '#f87171'), ('y', (0, ext[1], 0), '#4ade80'), ('z', (0, 0, ext[2]), '#60a5fa')):
        fig.add_trace(go.Scatter3d(x=[0, vec[0]], y=[0, vec[1]], z=[0, vec[2]], mode='lines+text',
                                   line=dict(color=color, width=4), text=['', axis], textposition='top center',
                                   textfont=dict(size=16, color=color), hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0], mode='markers+text', marker=dict(size=5, color='#ffffff'),
                               text=['O'], textposition='bottom left', hoverinfo='skip', showlegend=False))
    # Đường gióng: điểm → chân trên (Oxy) → hai trục (như Lab tọa độ điểm)
    for name, (x, y, z) in points.items():
        if name == 'O':
            continue
        if abs(z) > 1e-9:
            fig.add_trace(go.Scatter3d(x=[x, x], y=[y, y], z=[0, z], mode='lines',
                                       line=dict(color='#f59e0b', width=2, dash='dash'), hoverinfo='skip', showlegend=False))
        fig.add_trace(go.Scatter3d(x=[x, x, 0], y=[0, y, y], z=[0, 0, 0], mode='lines',
                                   line=dict(color='#94a3b8', width=1.5, dash='dot'), hoverinfo='skip', showlegend=False))
        if abs(z) > 1e-9 and (abs(x) > 1e-9 or abs(y) > 1e-9):
            fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[0], mode='markers', marker=dict(size=3, color='#a855f7'),
                                       hovertext=[f"Hình chiếu của {name} trên (Oxy): ({_num(x)};{_num(y)};0)"],
                                       hoverinfo='text', showlegend=False))
    for a, b in segments:
        pa, pb = points[a], points[b]
        fig.add_trace(go.Scatter3d(x=[pa[0], pb[0]], y=[pa[1], pb[1]], z=[pa[2], pb[2]], mode='lines',
                                   line=dict(color='#38bdf8', width=7), hoverinfo='skip', showlegend=False))
    if arrow:
        pa, pb = points[arrow[0]], points[arrow[1]]
        fig.add_trace(go.Cone(x=[pb[0]], y=[pb[1]], z=[pb[2]], u=[pb[0] - pa[0]], v=[pb[1] - pa[1]], w=[pb[2] - pa[2]],
                              sizemode='absolute', sizeref=span * 0.08, anchor='tip', showscale=False,
                              colorscale=[[0, '#38bdf8'], [1, '#38bdf8']], hoverinfo='skip'))
    names = [n for n in points if n != 'O']
    fig.add_trace(go.Scatter3d(x=[points[n][0] for n in names], y=[points[n][1] for n in names],
                               z=[points[n][2] for n in names], mode='markers+text',
                               marker=dict(size=7, color='#38bdf8'), text=[_label(n, points[n]) for n in names],
                               textposition=['middle right' if i == 0 else 'top center' for i in range(len(names))],
                               textfont=dict(size=13, color='#e2e8f0'),
                               hoverinfo='text', showlegend=False))
    axis_style = dict(backgroundcolor='#0f172a', gridcolor='#1e293b', zerolinecolor='#475569')
    fig.update_layout(
        title=title, template='plotly_dark', height=480, margin=dict(l=0, r=0, t=40 if title else 10, b=0),
        scene=dict(xaxis=dict(title='Ox', **axis_style), yaxis=dict(title='Oy', **axis_style),
                   # Khung lập phương như Lab tọa độ sẵn có: trục dài/ngắn khác nhau vẫn đọc rõ; số trên trục giữ đúng tọa độ.
                   zaxis=dict(title='Oz', **axis_style), aspectmode='cube',
                   camera=dict(eye=dict(x=1.55, y=1.45, z=0.95))),
    )
    return fig


def lesson_oxyz_figure(key, model):
    """Từ model của precision_visual_engine (oxyz_flight / oxyz_tetra) → hình xoay được, hoặc None."""
    pts = (model or {}).get('points') or {}
    if key == 'oxyz_flight' and {'M', 'N'} <= set(pts):
        show = {'M': pts['M'], 'N': pts['N']}
        if '>H<' in str(model.get('svg') or '') or '"H"' in str(model.get('svg') or ''):
            show['H'] = pts['H']
        return oxyz_figure(show, segments=[('M', 'N')], arrow=('M', 'N'))
    if key == 'oxyz_tetra' and {'A', 'B', 'C'} <= set(pts):
        show = {'O': (0.0, 0.0, 0.0), 'A': pts['A'], 'B': pts['B'], 'C': pts['C']}
        return oxyz_figure(show, segments=[('A', 'B'), ('B', 'C'), ('C', 'A'), ('O', 'A'), ('O', 'B'), ('O', 'C')])
    return None
