# -*- coding: utf-8 -*-
"""Giữ đề giả do AppTest sinh ra ngoài data/exam_cache thật.

AppTest bấm Sinh đề với AI giả lập sẽ lưu đề vào cache. Nếu ghi vào kho thật,
các test chạy sau (ví dụ GD KT&PL 12 phải rỗng) sẽ đọc phải đề giả đó.
"""
import os
import shutil
import tempfile

_ENV = "GSAI_EXAM_CACHE_DIR"
_state = []


def setUpModule():
    temp_dir = tempfile.mkdtemp(prefix="gsai_exam_cache_test_")
    _state.append((os.environ.get(_ENV), temp_dir))
    os.environ[_ENV] = temp_dir


def tearDownModule():
    if not _state:
        return
    previous, temp_dir = _state.pop()
    if previous is None:
        os.environ.pop(_ENV, None)
    else:
        os.environ[_ENV] = previous
    shutil.rmtree(temp_dir, ignore_errors=True)
