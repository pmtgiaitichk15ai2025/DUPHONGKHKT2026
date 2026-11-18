# -*- coding: utf-8 -*-
"""Hình Oxyz dựng từ tọa độ trong bài (ca thật web 18/11/2026, Toán 12 Bài 8, flycam M→N)."""
import re
import unittest

import precision_visual_engine as pve

FLIGHT = ("Trong không gian với hệ tọa độ Oxyz, một thiết bị bay flycam xuất phát từ điểm M(2;1;10) "
          "bay thẳng đến điểm N(12;6;30). Hãy tính quãng đường thực tế mà thiết bị bay đã di chuyển từ M đến N.")


def _circle(svg, label_prefix):
    # Tọa độ chấm ngay trước nhãn của điểm
    m = re.search(r'<circle cx="([\d.]+)" cy="([\d.]+)"[^>]*/>\s*<text[^>]*>' + re.escape(label_prefix), svg)
    return float(m.group(1)), float(m.group(2))


class FlightFigure(unittest.TestCase):
    def test_points_not_collapsed_onto_z_axis(self):
        svg = pve.build_oxyz_flight_path_model(FLIGHT)['svg']
        ox = 80.0
        for name in ('M(', 'N('):
            x, _ = _circle(svg, name)
            # Trước bản vá: đúng 0 px (M, N nằm trên trục z). M(2;1;10) thật sự gần trục z nên ngưỡng nhỏ.
            self.assertGreater(abs(x - ox), 2.5, name + " bị vẽ dính trục z")

    def test_exact_labels_and_no_unasked_h(self):
        svg = pve.build_oxyz_flight_path_model(FLIGHT)['svg']
        self.assertIn('M(2;1;10)', svg)
        self.assertIn('N(12;6;30)', svg)
        self.assertNotIn('d_min', svg)
        self.assertNotIn('>H<', svg)

    def test_h_drawn_when_question_asks_shortest_distance(self):
        q = "Trạm O, máy bay đi từ M(1;3;4) đến N(5;7;12). Tìm khoảng cách ngắn nhất từ O đến đường bay."
        self.assertIn('>H<', pve.build_oxyz_flight_path_model(q)['svg'])

    def test_decimal_coordinates_not_truncated(self):
        svg = pve.build_oxyz_flight_path_model("thiết bị bay từ M(1.5;2;3) đến N(4;5.5;6)")['svg']
        self.assertIn('M(1.5;2;3)', svg)
        self.assertIn('N(4;5.5;6)', svg)


LESSON_OPQ = (
    "## Ví dụ\n\nCho $M(1;2;3)$ và $N(4;6;15)$. Tính độ dài $MN$.\n\n"
    "## Vận dụng\n\nMột thiết bị bay điều khiển từ xa xuất phát từ gốc tọa độ $O(0;0;0)$ bay đến điểm "
    "$P(30;40;120)$ (đơn vị mét). Sau đó, thiết bị bay tiếp tục bay từ điểm $P$ đến điểm $Q(50;70;160)$. "
    "Hãy tính tổng quãng đường mà thiết bị bay đã thực hiện.\n"
)


class FlightUsesItsOwnParagraph(unittest.TestCase):
    """Ca thật web 18/11/2026: đề O→P→Q mà hình vẽ M(1;2;3), N(4;6;15) của ví dụ khác."""

    def test_path_from_flight_paragraph(self):
        from services.station1_scope import flight_paragraph, lesson_illustrations
        self.assertIn('oxyz_flight', lesson_illustrations(LESSON_OPQ, 'Toán học', 12))
        para = flight_paragraph(LESSON_OPQ)
        model = pve.build_oxyz_flight_path_model(para)
        self.assertEqual([n for n, _ in model['path']], ['O', 'P', 'Q'])
        svg = model['svg']
        self.assertIn('P(30;40;120)', svg)
        self.assertIn('Q(50;70;160)', svg)
        self.assertNotIn('M(1;2;3)', svg)
        self.assertEqual(svg.count('marker-end="url(#arr_flight)"'), 2)  # hai chặng bay

    def test_print_uses_flight_paragraph(self):
        from services.lesson_export import build_lesson_html
        doc = build_lesson_html("Toán học", 12, "Biểu thức toạ độ", LESSON_OPQ)
        self.assertIn('Q(50;70;160)', doc)
        self.assertNotIn('>M(1;2;3)<', doc)


class PrintExport(unittest.TestCase):
    def test_print_has_oxyz_figure_and_lists_may_break(self):
        from services.lesson_export import build_lesson_html
        lesson = "## Vận dụng\n\n" + FLIGHT + "\n"
        html_doc = build_lesson_html("Toán học", 12, "Biểu thức toạ độ của các phép toán vectơ", lesson)
        self.assertIn('class="oxyz-figure"', html_doc)
        self.assertIn('M(2;1;10)', html_doc)
        self.assertIn('li:has(ul,ol,.katex-display,table){break-inside:auto}', html_doc)


class Interactive3D(unittest.TestCase):
    def test_rotatable_figure_uses_exact_points(self):
        try:
            import plotly  # noqa: F401
        except ImportError:
            self.skipTest('plotly chưa cài')
        from services.oxyz_interactive import lesson_oxyz_figure
        fig = lesson_oxyz_figure('oxyz_flight', pve.build_oxyz_flight_path_model(FLIGHT))
        texts = [t for tr in fig.data for t in (getattr(tr, 'text', None) or ()) if t]
        self.assertIn('M(2;1;10)', texts)
        self.assertIn('N(12;6;30)', texts)
        self.assertNotIn('H', [t[:1] for t in texts if t.startswith('H')])


if __name__ == "__main__":
    unittest.main()
