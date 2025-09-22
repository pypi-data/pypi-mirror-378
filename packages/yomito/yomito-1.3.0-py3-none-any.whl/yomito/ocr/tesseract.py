"""Tesseract integration."""

import csv
import ctypes
import functools
import logging
import os
import re
import subprocess
import sys
from ctypes import wintypes
from os import linesep, PathLike
from pathlib import Path
from typing import Union

logger = logging.getLogger(__name__)


@functools.cache
def get_short_path(long_path: str) -> str:
    if sys.platform != "win32":
        raise NotImplementedError("Windows only")

    _GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
    _GetShortPathName.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _GetShortPathName.restype = wintypes.DWORD

    needed = _GetShortPathName(long_path, None, 0)
    if needed == 0:
        raise ctypes.WinError()

    buf = ctypes.create_unicode_buffer(needed)
    result = _GetShortPathName(long_path, buf, needed)
    if result == 0:
        raise ctypes.WinError()

    return buf.value


def _run_command(cmd_args: list[str]) -> str:
    try:
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", None)
        kwargs = {"creationflags": creationflags} if creationflags else {}
        proc = subprocess.run(cmd_args, capture_output=True, text=True, check=True, **kwargs)
        return proc.stdout
    except FileNotFoundError as e:
        raise FileNotFoundError("Tesseract not found") from e


def get_languages(
    tesseract_cmd: Union[PathLike, str], tessdata_path: Union[PathLike, str, None]
) -> list[str]:
    cmd_args = [str(tesseract_cmd), "--list-langs"]
    if tessdata_path:
        if sys.platform == "win32":
            tessdata_path = get_short_path(str(tessdata_path))
        cmd_args.extend(["--tessdata-dir", str(tessdata_path)])

    output = _run_command(cmd_args)

    if languages := re.findall(r"^([a-zA-Z_]+)\r{0,1}$", output, flags=re.M):
        return languages

    raise ValueError("Could not load Tesseract languages")


def _run_tesseract(tesseract_bin_path: Union[PathLike, str], image_path: str, args: list[str]) -> list[list[str]]:
    input_image_path = image_path
    
    if sys.platform == "win32":
        input_image_path = get_short_path(input_image_path)

    cmd_args = [str(tesseract_bin_path), input_image_path, input_image_path, "-c", "tessedit_create_tsv=1", *args]

    _run_command(cmd_args)

    with Path(f"{input_image_path}.tsv").open(encoding="utf-8") as fh:
        lines = list(csv.reader(fh, delimiter="\t", quotechar=None))
    
    try:
        os.unlink(f"{input_image_path}.tsv")
    except OSError:
        pass

    return lines


def _tsv_to_list_of_dict(tsv_lines: list[list[str]]) -> list[dict]:
    fields = tsv_lines.pop(0)
    words: list[dict] = [{} for _ in range(len(tsv_lines))]
    
    for idx, line in enumerate(tsv_lines):
        for field, value in zip(fields, line, strict=False):
            if field == "text":
                words[idx][field] = value
            elif field == "conf":
                words[idx][field] = float(value)
            else:
                words[idx][field] = int(value)

    words = [w for w in words if "text" in w]
    return [w for w in words if w["text"].strip()]


def perform_ocr(tesseract_bin_path: Union[PathLike, str], image_path: str, args: list[str]) -> list[dict]:
    lines = _run_tesseract(tesseract_bin_path, image_path, args)
    result = _tsv_to_list_of_dict(lines)
    
    try:
        os.unlink(image_path)
    except OSError:
        pass
    
    return result