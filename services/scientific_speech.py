# -*- coding: utf-8 -*-
"""Bộ đọc chuẩn khoa học — bản Python của assets/scientific_speech_reader.js (VERSION 20261102.2).

Owner 19/11/2026: giọng nữ/nam/Thầy Trí tạo MP3 trên máy chủ phải đọc công thức đúng như bộ đọc khoa học
đã có trong trình duyệt (phân số, căn, tích phân, véc tơ, \\ce, đơn vị, thuật ngữ môn). Hai bản được giữ
giống nhau bằng test so trực tiếp với bản JS (tests/test_scientific_speech_parity.py, cần Node).

prepare_text() giữ đúng hành vi JS (báo lỗi khi gặp ký hiệu chưa hỗ trợ). speech_text() dùng cho cả bài:
công thức nào chưa hỗ trợ thì đọc "công thức, xem trên màn hình" thay vì bỏ cả bài.
"""
import re
import unicodedata

VERSION = "20261102.2"

SUBJECT_TERMS = {
    "Toán học": {"TXĐ": "tập xác định", "TCĐ": "tiệm cận đứng", "TCN": "tiệm cận ngang", "TCX": "tiệm cận xiên",
                 "BBT": "bảng biến thiên", "Oxyz": "hệ tọa độ ô ích y dét", "Oxy": "hệ tọa độ ô ích y"},
    "Vật lý": {"AC": "dòng điện xoay chiều", "DC": "dòng điện một chiều"},
    "Hóa học": {"pH": "pê hát"},
    "Sinh học": {"ADN": "a đê en", "ARN": "a rờ en", "DNA": "đi en ây", "RNA": "a rờ en ây", "ATP": "a tê pê"},
    "Tin học": {"CPU": "xi pi iu", "RAM": "ram", "HTML": "hát tê em lờ", "SQL": "ét kiu eo"},
    "Địa lý": {"GDP": "gi đi pi", "GIS": "gi ai ét"},
}
COMMANDS = {
    "alpha": ("an pha", "alpha"), "beta": ("bê ta", "beta"), "gamma": ("gam ma", "gamma"),
    "delta": ("đen ta", "delta"), "Delta": ("đen ta", "delta"), "omega": ("ô mê ga", "omega"),
    "Omega": ("ôm", "ohm"), "pi": ("pi", "pi"), "theta": ("thê ta", "theta"),
    "infty": ("vô cực", "infinity"), "leq": ("nhỏ hơn hoặc bằng", "less than or equal to"),
    "le": ("nhỏ hơn hoặc bằng", "less than or equal to"), "geq": ("lớn hơn hoặc bằng", "greater than or equal to"),
    "ge": ("lớn hơn hoặc bằng", "greater than or equal to"), "neq": ("khác", "not equal to"),
    "notin": ("không thuộc", "not an element of"), "in": ("thuộc", "an element of"),
    "approx": ("xấp xỉ", "approximately"), "times": ("nhân", "times"), "cdot": ("nhân", "times"),
    "pm": ("cộng trừ", "plus or minus"), "to": ("tiến tới", "approaches"),
    "rightarrow": ("mũi tên sang phải", "right arrow"), "Rightarrow": ("suy ra", "implies"),
    "Leftrightarrow": ("tương đương", "if and only if"), "forall": ("với mọi", "for all"),
    "exists": ("tồn tại", "there exists"), "subset": ("là tập con của", "is a subset of"),
    "subseteq": ("là tập con hoặc bằng", "is a subset of or equal to"),
    "sin": ("sin", "sine"), "cos": ("cô sin", "cosine"), "tan": ("tang", "tangent"),
    "cot": ("cô tang", "cotangent"), "ln": ("lô ga tự nhiên", "natural logarithm"), "log": ("lô ga", "logarithm"),
    "int": ("tích phân", "integral"), "sum": ("tổng", "sum"), "lim": ("giới hạn", "limit"),
    "partial": ("đạo hàm riêng", "partial"), "nabla": ("na bla", "nabla"),
    "nearrow": ("mũi tên lên phải", "upward right arrow"), "searrow": ("mũi tên xuống phải", "downward right arrow"),
}
UNITS = {"kg": "ki lô gam", "cm": "xen ti mét", "mm": "mi li mét", "km": "ki lô mét", "m": "mét", "s": "giây",
         "mol": "mol", "Hz": "héc", "kHz": "ki lô héc", "MHz": "mê ga héc", "Pa": "pát xcan", "kPa": "ki lô pát xcan",
         "J": "jun", "W": "oát", "V": "vôn", "A": "am pe", "N": "niu tơn", "Ω": "ôm", "°C": "độ xê"}
_FORMULA_RE = re.compile(r"\$\$([\s\S]*?)\$\$|\\\[([\s\S]*?)\\\]|\\\(([^\n]*?)\\\)|\$([^$\n]+)\$")


class SpeechError(ValueError):
    pass


def subject_name(value):
    return {"Toán": "Toán học", "Vật lí": "Vật lý", "Hoá học": "Hóa học", "Địa lí": "Địa lý"}.get(value, value)


def replace_terms(text, subject):
    terms = dict(SUBJECT_TERMS.get(subject_name(subject), {}))
    if subject == "Khoa học tự nhiên":
        for s in ("Vật lý", "Hóa học", "Sinh học"):
            terms.update(SUBJECT_TERMS[s])
    for term, spoken in terms.items():
        text = re.sub(r"(?<![^\W_])" + re.escape(term) + r"(?![^\W_])", spoken, text)
    return text


def formula_speech(source, lang="vi"):
    en = lang == "en"
    st = {"i": 0, "depth": 0}

    def say(vi, english):
        return english if en else vi

    def group():
        while st["i"] < len(source) and source[st["i"]].isspace():
            st["i"] += 1
        if st["i"] >= len(source) or source[st["i"]] != "{":
            if st["i"] >= len(source):
                raise SpeechError("Công thức thiếu đối số.")
            ch = source[st["i"]]
            st["i"] += 1
            return ch
        st["i"] += 1
        return parse(True)

    def chemical_group():
        while st["i"] < len(source) and source[st["i"]] == " ":
            st["i"] += 1
        if st["i"] >= len(source) or source[st["i"]] != "{":
            raise SpeechError("Công thức hóa học thiếu ngoặc.")
        st["i"] += 1
        start, count = st["i"], 1
        while st["i"] < len(source) and count:
            c = source[st["i"]]
            st["i"] += 1
            count += (c == "{") - (c == "}")
        if count:
            raise SpeechError("Công thức hóa học chưa đóng.")
        value = source[start:st["i"] - 1]
        if not re.fullmatch(r"[A-Za-z0-9\s(){}.+\-=<>^_]+", value):
            raise SpeechError("Ký hiệu hóa học này chưa có cách đọc đã hỗ trợ.")
        charges = []
        value = re.sub(r"\^\{(\d*[+-])\}", r"^\1", value)

        def charge_token(base, n, sign):
            charges.append(say(" mang điện tích ", " with charge ") + (n + " " if n else "") +
                           (say("dương", "positive") if sign == "+" else say("âm", "negative")))
            return base + " gsaiioncharge" + str(len(charges) - 1) + "end "
        value = re.sub(r"([A-Za-z0-9)])\^(\d*)([+-])(?=\s|$)", lambda m: charge_token(m[1], m[2], m[3]), value)
        value = re.sub(r"([A-Za-z0-9)])([+-])(?=\s|$)", lambda m: charge_token(m[1], "", m[2]), value)
        value = re.sub(r"<=>|<->", say(" phản ứng thuận nghịch ", " reversible reaction "), value)
        value = re.sub(r"->|=>", say(" tạo thành ", " yields "), value)
        value = re.sub(r"([A-Z][a-z]?)(\d*)", lambda m: say(" ký hiệu ", " symbol ") + " ".join(m[1]) +
                       (say(" chỉ số ", " subscript ") + m[2] if m[2] else "") + " ", value)
        value = value.replace("+", say(" cộng ", " plus "))
        value = re.sub(r"[{}]", "", value)
        value = value.replace("^", say(" điện tích ", " charge ")).replace("_", say(" chỉ số ", " subscript "))
        value = re.sub(r"gsaiioncharge(\d+)end", lambda m: charges[int(m[1])], value)
        return say(" công thức hóa học: ", " chemical notation: ") + value

    def parse(grouped):
        st["depth"] += 1
        if st["depth"] > 16:
            raise SpeechError("Công thức quá sâu để đọc an toàn.")
        out = ""
        while st["i"] < len(source):
            c = source[st["i"]]
            st["i"] += 1
            if c == "}":
                if not grouped:
                    raise SpeechError("Công thức thừa dấu ngoặc.")
                st["depth"] -= 1
                return out
            if c == "{":
                out += " " + parse(True) + " "
                continue
            if c == "\\":
                m = re.match(r"[A-Za-z]+", source[st["i"]:])
                if not m:
                    st["i"] += 1
                    out += " "
                    continue
                cmd = m[0]
                st["i"] += len(cmd)
                if cmd in ("left", "right", "displaystyle", "limits"):
                    continue
                if cmd == "ce":
                    out += chemical_group()
                elif cmd in ("frac", "dfrac", "tfrac"):
                    numerator, denominator = group(), group()
                    out += (say(" phân số, tử số ", " fraction, numerator ") + numerator +
                            say(", mẫu số ", ", denominator ") + denominator + say(", hết phân số. ", ", end fraction. "))
                elif cmd == "sqrt":
                    order = say("hai", "two")
                    if st["i"] < len(source) and source[st["i"]] == "[":
                        end = source.find("]", st["i"])
                        if end < 0:
                            raise SpeechError("Căn thức chưa đóng.")
                        order = source[st["i"] + 1:end]
                        st["i"] = end + 1
                    out += say(" căn bậc ", " root of order ") + order + say(" của ", " of ") + group() + say(", hết căn. ", ", end root. ")
                elif cmd in ("vec", "overrightarrow"):
                    out += say(" véc tơ ", " vector ") + re.sub(r"([A-Z])(?=[A-Z])", r"\1 ", group()) + " "
                elif cmd in ("int", "sum", "lim"):
                    lower = upper = ""
                    for _ in range(2):
                        while st["i"] < len(source) and source[st["i"]] == " ":
                            st["i"] += 1
                        if st["i"] < len(source) and source[st["i"]] == "_":
                            st["i"] += 1
                            lower = group()
                        elif st["i"] < len(source) and source[st["i"]] == "^":
                            st["i"] += 1
                            upper = group()
                        else:
                            break
                    out += " " + COMMANDS[cmd][1 if en else 0] + " "
                    if lower:
                        out += (say("khi ", "as ") if cmd == "lim" else say("từ ", "from ")) + lower + " "
                    if upper:
                        out += say("đến ", "to ") + upper + " "
                elif cmd in ("text", "mathrm", "operatorname", "mathbf", "mathbb", "mathcal"):
                    value = group().strip()
                    out += say(" tập số thực ", " real numbers ") if cmd == "mathbb" and value == "R" else " " + value + " "
                elif cmd in COMMANDS:
                    out += " " + COMMANDS[cmd][1 if en else 0] + " "
                else:
                    raise SpeechError("Chưa có cách đọc công thức cho \\" + cmd + ". Hãy đối chiếu công thức trên màn hình.")
            elif c == "^":
                out += say(" mũ ", " to the power ") + group() + " "
            elif c == "_":
                out += say(" chỉ số dưới ", " subscript ") + group() + " "
            elif c == "=":
                out += say(" bằng ", " equals ")
            elif c == "+":
                out += say(" cộng ", " plus ")
            elif c in "-−":
                out += say(" trừ ", " minus ")
            elif c == "<":
                out += say(" nhỏ hơn ", " less than ")
            elif c == ">":
                out += say(" lớn hơn ", " greater than ")
            elif c == "/":
                out += say(" chia cho ", " divided by ")
            elif c == "'":
                out += say(" phẩy ", " prime ")
            else:
                out += c
        st["depth"] -= 1
        if grouped:
            raise SpeechError("Công thức thiếu dấu ngoặc đóng.")
        return out
    return re.sub(r"\s+", " ", parse(False)).strip()


def _code_note(lang):
    return " Code block; refer to the displayed code. " if lang == "en" else " Khối mã; đối chiếu mã trên màn hình. "


def prepare_text(text, lang="vi", subject="", lenient=False):
    formulas = []
    text = unicodedata.normalize("NFC", str(text))
    text = re.sub(r"```[\s\S]*?```", _code_note(lang), text)

    def keep(m):
        src = m[1] or m[2] or m[3] or m[4] or ""
        try:
            formulas.append(formula_speech(src, lang))
        except SpeechError:
            if not lenient:
                raise
            formulas.append(" a formula; see the screen " if lang == "en" else " công thức, xem trên màn hình ")
        return " GSAISPEECHFORMULA" + str(len(formulas) - 1) + "END "
    text = _FORMULA_RE.sub(keep, text)
    text = re.sub(r"```[\s\S]*?```", _code_note(lang), text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]*>", " ", text)
    text = re.sub(r"(?m)^\s*#{1,6}\s+", "", text)
    text = re.sub(r"(?m)^\s*[-*•]\s+", "", text)
    if "$" in text:
        if not lenient:
            raise SpeechError("Dấu phân cách công thức chưa đầy đủ; hãy chọn trọn công thức.")
        text = text.replace("$", " ")
    if re.search(r"\\[A-Za-z]+", text):
        if not lenient:
            raise SpeechError("Đoạn chọn còn mã công thức chưa hỗ trợ. Hãy chọn trọn công thức hoặc đối chiếu bản hiển thị.")
        text = re.sub(r"\\[A-Za-z]+", " ", text)
    text = re.sub(r"(?m)^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$", "", text)
    text = re.sub(r"\s*\|\s*", "; ", text)
    text = re.sub(r"[*`~]", "", text)
    text = re.sub(r"\n\s*\n", ".\n", text)
    text = re.sub(r"([.!?;:])\1+", r"\1", text)
    if lang == "vi":
        text = replace_terms(text, subject)
        if subject_name(subject) in ("Toán học", "Vật lý", "Hóa học", "Khoa học tự nhiên", "Công nghệ"):
            text = re.sub(r"(\d+(?:[.,]\d+)?)\s*(MHz|kHz|kPa|kg|cm|mm|km|mol|Hz|Pa|°C|Ω|m|s|J|W|V|A|N)(?![^\W_])",
                          lambda m: m[1] + " " + UNITS[m[2]], text)
    text = re.sub(r"GSAISPEECHFORMULA(\d+)END", lambda m: formulas[int(m[1])], text)
    return re.sub(r"[ \t]+", " ", text).strip()


def speech_text(text, subject="", lang=None):
    """Văn bản đọc cho cả bài/câu trả lời (máy chủ tạo MP3): đúng bộ đọc khoa học, không bỏ cả bài vì một công thức."""
    lang = lang or ("en" if subject_name(subject) == "Tiếng Anh" else "vi")
    return prepare_text(text, lang, subject, lenient=True)
