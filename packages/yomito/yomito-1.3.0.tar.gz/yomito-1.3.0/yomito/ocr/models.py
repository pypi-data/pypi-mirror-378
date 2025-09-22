"""Data models for Kaneki OCR library."""

import enum
import os
from dataclasses import dataclass, field
from os import PathLike
from typing import Union


@enum.unique
class PSM(enum.IntEnum):
    """Tesseract page segmentation modes."""
    
    OSD_ONLY = 0
    AUTO_OSD = 1
    AUTO_ONLY = 2
    AUTO = 3
    SINGLE_COLUMN = 4
    SINGLE_BLOCK_VERT_TEXT = 5
    SINGLE_BLOCK = 6
    SINGLE_LINE = 7
    SINGLE_WORD = 8
    CIRCLE_WORD = 9
    SINGLE_CHAR = 10
    SPARSE_TEXT = 11
    SPARSE_TEXT_OSD = 12
    RAW_LINE = 13
    COUNT = 14


@enum.unique
class OEM(enum.IntEnum):
    """Tesseract OCR engine modes."""
    
    TESSERACT_ONLY = 0
    LSTM_ONLY = 1
    TESSERACT_LSTM_COMBINED = 2
    DEFAULT = 3


@dataclass
class TessArgs:
    """Tesseract arguments."""
    
    tessdata_path: Union[PathLike, str, None]
    lang: str
    oem: OEM
    psm: PSM

    def as_list(self) -> list[str]:
        arg_list = [
            "-l", self.lang,
            "--oem", str(self.oem.value),
            "--psm", str(self.psm.value),
        ]
        if self.tessdata_path:
            arg_list.extend(["--tessdata-dir", str(self.tessdata_path)])
        if self.is_language_without_spaces():
            arg_list.extend(["-c", "preserve_interword_spaces=1"])
        return arg_list

    def is_language_without_spaces(self) -> bool:
        languages_without_spaces = {
            "chi_sim", "chi_sim_vert", "chi_tra", "chi_tra_vert",
            "jpn", "jpn_vert", "kor"
        }
        selected_languages = set(self.lang.split("+"))
        return selected_languages.issubset(languages_without_spaces)


@dataclass
class OcrResult:
    """OCR result with metadata."""
    
    tess_args: TessArgs
    words: list[dict]
    parsed: str = ""

    @property
    def mean_conf(self) -> float:
        if conf_values := [float(w.get("conf", 0)) for w in self.words]:
            return sum(conf_values) / len(conf_values)
        return 0

    @property
    def text(self) -> str:
        return self.parsed or self.add_linebreaks()

    def add_linebreaks(
        self,
        block_sep: str = os.linesep * 2,
        par_sep: str = os.linesep,
        line_sep: str = os.linesep,
        word_sep: str = " ",
    ) -> str:
        last_block_num = None
        last_par_num = None
        last_line_num = None
        text = ""

        for word in self.words:
            block_num = word.get("block_num", None)
            par_num = word.get("par_num", None)
            line_num = word.get("line_num", None)

            if block_num != last_block_num:
                text += block_sep + word["text"]
            elif par_num != last_par_num:
                text += par_sep + word["text"]
            elif line_num != last_line_num:
                text += line_sep + word["text"]
            else:
                text += word_sep + word["text"]

            last_block_num = block_num
            last_par_num = par_num
            last_line_num = line_num

        return text.strip()

    @property
    def num_chars(self) -> int:
        return sum(len(w["text"]) for w in self.words)

    @property
    def num_words(self) -> int:
        return len(self.words)