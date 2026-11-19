# -*- coding: utf-8 -*-
"""Bộ đọc khoa học bản Python phải đọc GIỐNG HỆT bản JS đã có (owner 19/11/2026)."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

from services.scientific_speech import SpeechError, prepare_text, speech_text

ROOT = Path(__file__).resolve().parents[1]
CASES = [
    ("Hàm số $y=x^3-3x+1$.", "vi", "Toán học"),
    (r"Ta có $\frac{1}{\sqrt{2}}$.", "vi", "Toán học"),
    (r"Tích phân $\int_0^1 x^2\,dx$ và $\lim_{x\to 0}\frac{\sin x}{x}=1$.", "vi", "Toán học"),
    (r"Véc tơ $\vec{AB}=\overrightarrow{CD}$, $\sqrt[3]{8}=2$, $x\in\mathbb{R}$, $\Delta \geq 0$.", "vi", "Toán học"),
    ("Vật có khối lượng 2 kg, đi 3 km trong 5 s.", "vi", "Vật lý"),
    ("Tham số $y=2m+1$.", "vi", "Toán học"),
    (r"Ion $\ce{Na+}$, $\ce{Ca^2+}$, $\ce{Fe^{3+}}$ và $\ce{H2 + O2 -> H2O}$; $\ce{N2 + 3H2 <=> 2NH3}$.", "vi", "Hóa học"),
    ("Phân tử DNA và ATP; TXĐ của hàm số, BBT, hệ Oxyz.", "vi", "Sinh học"),
    ("TXĐ và TCĐ, TCN của đồ thị trong Oxy.", "vi", "Toán học"),
    ("Bảng:\n| x | y |\n|---|---|\n| 1 | 2 |", "vi", "Toán học"),
    (r"The derivative $f'(x)=2x$ and $\frac{a}{b}$.", "en", "Tiếng Anh"),
    ("## Tiêu đề\n- ý một\n- ý **hai** [link](http://a.b)\n```py\nx=1\n```", "vi", "Tin học"),
]


@unittest.skipUnless(shutil.which("node"), "cần Node để so với bản JS")
class Parity(unittest.TestCase):
    def test_python_matches_js_exactly(self):
        script = ("const r=require(process.argv[1]);const cases=JSON.parse(require('fs').readFileSync(0,'utf8'));"
                  "console.log(JSON.stringify(cases.map(([t,l,s])=>{try{return r.prepareText(t,l,s)}catch(e){return 'ERR'}})));")
        out = subprocess.run(["node", "-e", script, str(ROOT / "assets" / "scientific_speech_reader.js")],
                             input=json.dumps(CASES), capture_output=True, text=True, encoding="utf-8", check=True)
        js = json.loads(out.stdout)
        for (text, lang, subject), expected in zip(CASES, js):
            try:
                got = prepare_text(text, lang, subject)
            except SpeechError:
                got = "ERR"
            self.assertEqual(got, expected, text)


class Behaviour(unittest.TestCase):
    def test_strict_errors_like_js_but_lesson_reading_never_aborts(self):
        with self.assertRaises(SpeechError):
            prepare_text(r"Công thức $\unknowncmd{x}$", "vi", "Toán học")
        got = speech_text(r"Biết $\unknowncmd{x}$ và $\frac{1}{2}$ kg.", "Vật lý")
        self.assertIn("công thức, xem trên màn hình", got)
        self.assertIn("phân số, tử số 1, mẫu số 2", got)


class StationWiring(unittest.TestCase):
    """Owner 19/11/2026: thanh đọc cho gia sư Trạm 1/2/3; mọi giọng máy chủ qua bộ đọc khoa học."""

    def test_all_tutor_replies_have_reader_and_scientific_text(self):
        src = (ROOT / "app.py").read_text(encoding="utf-8")
        for key in ('f"t1_chat_{t1_msg_index}"', 'f"t2_msg_{idx_m}"', 'f"t3_msg_{index}"', '"tram1_lesson"'):
            self.assertIn(key, src)
        body = src.split("def create_pedagogical_tts_component", 1)[1].split("\ndef ", 1)[0]
        self.assertIn("clean_speech = _sci_speech(clean_speech, subject_name)", body)
        self.assertLess(body.index("_sci_speech(clean_speech"), body.index("generate_pedagogical_tts_audio_bytes(clean_speech"))


if __name__ == "__main__":
    unittest.main()
