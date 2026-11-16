# -*- coding: utf-8 -*-
"""Strip leaked plot/BBT machine specs from exam stems; coerce f/bbt for renderers."""
from __future__ import annotations

import json
import re
from copy import deepcopy

PLOT_TYPES = {
    "func_3",
    "cubic",
    "func_1_1",
    "func_2_1",
    "parabola",
    "parabola_fprime",
    "func_2",
    "func_exp",
    "func_log",
    "linear_region",
    "area",
    "revolve_ox",
}

_REQUIRED = {
    "func_3": {"a", "b", "c", "d"},
    "cubic": {"a", "b", "c", "d"},
    "func_1_1": {"a", "b", "c", "d"},
    "func_2_1": {"a", "b", "c", "d", "e"},
    "parabola": {"a", "b", "c"},
    "parabola_fprime": {"a", "b", "c"},
    "func_2": {"a", "b", "c"},
}

_INLINE_KEY_RE = re.compile(
    r'(?P<prefix>(?:^|[\s,;:\(\[\{]))(?P<key>f|geom_3d|composite_visual|thermal_pv_visual|food_web_visual)\s*=\s*(?P<brace>\{)',
    re.I,
)
_BARE_TYPE_RE = re.compile(
    r'\{\s*"type"\s*:\s*"(?P<type>func_[^"]+|cubic|parabola(?:_fprime)?|linear_region|area|revolve_ox)"',
    re.I,
)


def _slice_balanced_object(text: str, open_idx: int) -> str | None:
    if open_idx < 0 or open_idx >= len(text) or text[open_idx] != "{":
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(open_idx, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[open_idx : i + 1]
    return None


def coerce_plot_spec(value):
    """Return a dict plot spec when value is a usable f object or JSON string."""
    if isinstance(value, dict):
        kind = str(value.get("type") or "").strip()
        if not kind:
            return None
        needed = _REQUIRED.get(kind)
        if needed and not needed <= set(value.keys()):
            return None
        return value
    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            return None
        if raw.lower().startswith("f="):
            raw = raw[2:].strip()
        if not raw.startswith("{"):
            return None
        try:
            parsed = json.loads(raw)
        except Exception:
            return None
        return coerce_plot_spec(parsed)
    return None


def _looks_like_plot_spec(obj) -> bool:
    return isinstance(obj, dict) and str(obj.get("type") or "") in PLOT_TYPES


def strip_inline_plot_specs(text: str):
    """Remove leaked f={...} / bare plot JSON from stem text; return (clean, specs)."""
    if text is None:
        return "", []
    s = str(text)
    found = []

    def _consume(match_start: int, brace_idx: int, key: str | None):
        blob = _slice_balanced_object(s, brace_idx)
        if not blob:
            return None
        try:
            obj = json.loads(blob)
        except Exception:
            return None
        if not _looks_like_plot_spec(obj):
            return None
        found.append({"key": (key or "f").lower(), "spec": obj})
        # Drop a trailing comma/space left by inline dumps.
        end = brace_idx + len(blob)
        while end < len(s) and s[end] in " \t,;":
            end += 1
        start = match_start
        # Keep a single space if we deleted mid-sentence glue.
        left = s[:start].rstrip()
        right = s[end:].lstrip()
        glue = " " if left and right and not left.endswith(("\n", "(", "[", "{")) else ""
        return left + glue + right

    # Pass 1: explicit f={...} (and sibling visual keys)
    guard = 0
    while guard < 20:
        guard += 1
        m = _INLINE_KEY_RE.search(s)
        if not m:
            break
        brace_idx = m.start("brace")
        # Include only the key= part in the deletion, keep preceding punctuation char.
        key_start = m.start("key")
        nxt = _consume(key_start, brace_idx, m.group("key"))
        if nxt is None:
            # Skip this brace to avoid infinite loop on malformed JSON.
            s = s[: brace_idx] + " " + s[brace_idx + 1 :]
            continue
        s = nxt

    # Pass 2: bare {"type":"func_3",...} dumps left in the stem
    guard = 0
    while guard < 20:
        guard += 1
        m = _BARE_TYPE_RE.search(s)
        if not m:
            break
        brace_idx = m.start()
        nxt = _consume(brace_idx, brace_idx, "f")
        if nxt is None:
            s = s[: brace_idx] + " " + s[brace_idx + 1 :]
            continue
        s = nxt

    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s).strip(" ,;\t")
    return s, found


def sanitize_question_visuals(question: dict, *, inplace: bool = False) -> dict:
    """Clean stem leaks and coerce f/bbt so graphs/BBT can render."""
    if not isinstance(question, dict):
        return question
    q = question if inplace else deepcopy(question)

    cleaned, specs = strip_inline_plot_specs(q.get("q", ""))
    if cleaned != str(q.get("q", "") or ""):
        q["q"] = cleaned

    coerced = coerce_plot_spec(q.get("f"))
    if coerced is not None:
        q["f"] = coerced
    elif "f" in q and not isinstance(q.get("f"), dict):
        q.pop("f", None)

    for item in specs:
        key = item["key"]
        spec = item["spec"]
        if key == "f":
            if coerce_plot_spec(q.get("f")) is None:
                q["f"] = spec
        elif key in q and not isinstance(q.get(key), dict):
            q[key] = spec
        elif key not in q:
            q[key] = spec

    # bbt must be a multi-line | table string for web renderers — drop JSON dumps.
    bbt = q.get("bbt")
    if isinstance(bbt, dict):
        q.pop("bbt", None)
    elif isinstance(bbt, str):
        raw = bbt.strip()
        if raw.startswith("{") and '"type"' in raw:
            q.pop("bbt", None)
        elif raw.lower() in {"null", "none", "{}"}:
            q.pop("bbt", None)

    for stmt in q.get("stmts") or []:
        if isinstance(stmt, dict) and "t" in stmt:
            stmt["t"], _ = strip_inline_plot_specs(stmt.get("t", ""))

    for opt_i, opt in enumerate(q.get("opt") or []):
        cleaned_opt, _ = strip_inline_plot_specs(opt)
        q["opt"][opt_i] = cleaned_opt

    return q


def sanitize_exam_visuals(exam: dict) -> dict:
    """Walk exam parts and sanitize every question object."""
    if not isinstance(exam, dict):
        return exam
    out = deepcopy(exam)
    for part in ("p1", "p2", "p3"):
        rows = out.get(part)
        if not isinstance(rows, list):
            continue
        out[part] = [
            sanitize_question_visuals(q, inplace=False) if isinstance(q, dict) else q
            for q in rows
        ]
    reading = out.get("part_doc_hieu")
    if isinstance(reading, dict) and isinstance(reading.get("questions"), list):
        reading["questions"] = [
            sanitize_question_visuals(q, inplace=False) if isinstance(q, dict) else q
            for q in reading["questions"]
        ]
    viet = out.get("part_viet")
    if isinstance(viet, list):
        out["part_viet"] = [
            sanitize_question_visuals(q, inplace=False) if isinstance(q, dict) else q
            for q in viet
        ]
    return out
