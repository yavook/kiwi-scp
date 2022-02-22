import re
from enum import Enum, auto
from typing import List

import attr
import wcwidth


class WAlignment(Enum):
    LEFT = auto()
    RIGHT = auto()
    CENTER = auto()


@attr.s
class WString:
    s: str = attr.ib()

    # from https://stackoverflow.com/a/38662876
    ANSI_ESCAPES = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")

    def __str__(self) -> str:
        return self.s

    def __len__(self) -> int:
        return wcwidth.wcswidth(WString.ANSI_ESCAPES.sub("", self.s))

    def pad(self, alignment: WAlignment = WAlignment.CENTER, wlen: int = 0, char: str = " ") -> "WString":
        char = char[0]

        if alignment is WAlignment.LEFT:
            return WString(f"{self}{char * wlen}")
        elif alignment is WAlignment.RIGHT:
            return WString(f"{char * wlen}{self}")
        else:
            pad_l, pad_r = wlen // 2, wlen - (wlen // 2)
            return WString(f"{char * pad_l}{self}{char * pad_r}")


@attr.s
class WParagraph:
    lines: List[WString] = attr.ib()

    def __str__(self) -> str:
        return "\n".join(
            str(line)
            for line in self.lines
        )

    @classmethod
    def from_strings(cls, *source: str) -> "WParagraph":
        return cls([
            WString(line)
            for line in source
        ])

    def align(self, alignment: WAlignment = WAlignment.CENTER, padding: int = 0, char: str = " ") -> "WParagraph":
        total_length = max(
            len(line)
            for line in self.lines
        ) + padding
        pad_lengths = (
            total_length - len(line)
            for line in self.lines
        )

        return WParagraph([
            line.pad(alignment, wlen, char)
            for line, wlen in zip(self.lines, pad_lengths)
        ])

    def surround(self, char: str, padding: int = 1) -> "WParagraph":
        char = char[0]
        padding = " " * padding

        l_border, r_border = char + padding, padding + char

        lines = [
            WString(f"{l_border}{line}{r_border}")
            for line in self.lines
        ]
        extra_line = char * len(lines[0])

        return WParagraph([
            extra_line,
            *lines,
            extra_line,
        ])

    def emphasize(self, count: int = 3, padding: int = 1) -> "WParagraph":
        padding = " " * padding
        l_border, r_border = (">" * count) + padding, padding + ("<" * count)

        return WParagraph([
            WString(f"{l_border}{line}{r_border}")
            for line in self.lines
        ])
