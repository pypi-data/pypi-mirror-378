import asyncio
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable, List, Optional, Union

import cursor

from ..spinner import get_spinner


class EscapeCode(Enum):
    RESET = "0"


@dataclass
class Color:
    red: int
    green: int
    blue: int


class ColoringType(Enum):
    FOREGROUND = "38"
    BACKGROUND = "48"


def e(
    element: Union[EscapeCode, Color],
    coloring_type: ColoringType = ColoringType.FOREGROUND,
) -> Optional[str]:
    if isinstance(element, EscapeCode):
        return f"\033[{element.value}m"
    elif isinstance(element, Color):
        return f"\033[{coloring_type.value};2;{element.red};{element.green};{element.blue}m"
    return None


def colored(
    string: str,
    fg: Optional[Color] = None,
    bg: Optional[Color] = None,
    next_fg: Optional[Color] = None,
    next_bg: Optional[Color] = None,
) -> str:
    fg_string = "" if fg is None else e(fg, coloring_type=ColoringType.FOREGROUND)
    bg_string = "" if bg is None else e(bg, coloring_type=ColoringType.BACKGROUND)
    next_fg_string = (
        "" if next_fg is None else e(next_fg, coloring_type=ColoringType.FOREGROUND)
    )
    next_bg_string = (
        "" if next_bg is None else e(next_bg, coloring_type=ColoringType.BACKGROUND)
    )

    c_string = f"{bg_string}{fg_string}{string}{e(EscapeCode.RESET)}"
    if next_bg is not None:
        c_string += next_bg_string
    if next_fg is not None:
        c_string += next_fg_string
    return c_string


def shade(color: Color, shade_factor: float) -> Color:
    factor = max(0.0, min(shade_factor, 1.0))  # clamp to [0, 1]
    return Color(
        red=int(color.red * factor),
        green=int(color.green * factor),
        blue=int(color.blue * factor),
    )


COLOR_WHITE = Color(red=255, green=255, blue=255)
COLOR_CYAN = Color(red=1, green=87, blue=155)
COLOR_GRAY = Color(red=100, green=100, blue=100)
COLOR_RED_LIGHT = Color(red=239, green=83, blue=80)
COLOR_GREEN = Color(red=104, green=159, blue=56)

COLOR_SPINNER = COLOR_CYAN
COLOR_BORDER = COLOR_GRAY
COLOR_MESSAGE = shade(COLOR_GRAY, 0.2)
COLOR_MESSAGE_TEXT = COLOR_GRAY
COLOR_MUS = COLOR_RED_LIGHT

FINISHED_STRING = colored("✅ Finished", fg=COLOR_GREEN)

LENGTH_EMOJI = 2


def render_progress_box(label: str, emoji: str, progress_frame: str):
    c_divider = colored("│", fg=COLOR_BORDER)
    label_length = LENGTH_EMOJI + 1 + len(label)
    upper_box = (
        colored("┌─" + "─" * label_length + "─┬─────────────┐", fg=COLOR_BORDER) + "\n"
    )
    progress = (
        c_divider
        + f" {emoji}"
        + f" {label} "
        + c_divider
        + f" {colored(progress_frame, fg=COLOR_SPINNER)} "
        + c_divider
        + "\n"
    )
    lower_box = colored("└─" + "─" * label_length + "─┴─────────────┘", fg=COLOR_BORDER)
    return upper_box + progress + lower_box


def render_code_line(
    line_number: int,
    content: str,
    filename: Optional[str] = None,
    width: Optional[int] = None,
) -> str:
    string_line_number = colored(
        f" {str(line_number).rjust(4)} ",
        fg=shade(COLOR_WHITE, 0.4),
        bg=shade(COLOR_GRAY, 0.2),
    )
    content_width = width - 6 if width is not None else len(content) + 2
    content_padded = content.ljust(content_width)
    string_content = colored(
        f" {content_padded} ", fg=shade(COLOR_WHITE, 0.6), bg=shade(COLOR_GRAY, 0.3)
    )
    if filename is None:
        line_heading = "\n"
    else:
        line_heading = (
            " " * (width - len(filename))
            + colored("◢", fg=shade(COLOR_GRAY, 0.3))
            + colored(
                f" {filename} ", fg=shade(COLOR_WHITE, 0.4), bg=shade(COLOR_GRAY, 0.3)
            )
            + "\n"
        )
    line_padding = (
        " "
        + colored(" " * 6, bg=shade(COLOR_GRAY, 0.2))
        + colored(" " * (content_width + 2), bg=shade(COLOR_GRAY, 0.3))
        + "\n"
    )
    line_content = " " + string_line_number + string_content + "\n"
    return line_heading + line_padding + line_content + line_padding


def message_partitions(
    message: str, width: int, word_highlight_fn: Optional[Callable[[str], str]] = None
) -> List[str]:
    words = message.split()
    lines = []
    current_line = []
    for i, word in enumerate(words):
        current_line_length = sum([len(w) for w in current_line]) + max(
            len(current_line) - 1, 0
        )
        if current_line_length + len(word) + 1 <= width:
            current_line.append(word)
        else:
            line_string = " ".join(current_line).ljust(width)
            if word_highlight_fn is not None:
                for w in current_line:
                    line_string = line_string.replace(w, word_highlight_fn(w))
            lines.append(line_string)
            current_line = [word]
    # FLUSH OUT REMAINING LINE
    line_string = " ".join(current_line).ljust(width)
    if word_highlight_fn is not None:
        for w in current_line:
            line_string = line_string.replace(w, word_highlight_fn(w))
    lines.append(line_string)
    return lines


def render_llm_message(
    message: str, width: int, word_highlight_fn: Optional[Callable[[str], str]] = None
) -> str:
    line_1_avatar = " " + colored("      ", bg=shade(COLOR_GRAY, 0.2))
    line_2_avatar = " " + colored("  🤖  ", bg=shade(COLOR_GRAY, 0.2))
    line_3_avatar = " " + colored("      ", bg=shade(COLOR_GRAY, 0.2))
    width_avatar = 1 + 6
    width_text_box = width - 6
    line_1_message = colored(" ◥", fg=COLOR_MESSAGE) + colored(
        " " * width_text_box, bg=COLOR_MESSAGE
    )
    line_n_message = colored(" " * width_text_box, bg=COLOR_MESSAGE)

    output = ""
    output += line_1_avatar + line_1_message + "\n"
    for i, line in enumerate(
        message_partitions(
            message, width=width_text_box - 4, word_highlight_fn=word_highlight_fn
        )
    ):
        if i == 0:
            front = line_2_avatar
        elif i == 1:
            front = line_3_avatar
        else:
            front = " " * width_avatar
        output += (
            front
            + "  "
            + colored("  " + line + "  ", fg=COLOR_GRAY, bg=shade(COLOR_GRAY, 0.2))
            + "\n"
        )
    output += " " * width_avatar + "  " + line_n_message + "\n"
    return output


def highlight_detail(word: str, fg: Color, bg: Color) -> str:
    return colored(f" {word} ", fg=fg, bg=bg)


def render_details(
    detail_strings: Iterable[str], width: int, fg: Color, bg: Color
) -> str:
    lines = message_partitions(
        " ".join(detail_strings),
        width=width,
        word_highlight_fn=lambda x: highlight_detail(x, fg, bg),
    )
    lines_indented = [f"  {line}" for line in lines]
    return "\n".join(lines_indented)


async def progress_box(label: str, emoji: str):
    spinner_generator = get_spinner()
    cursor_up = "\x1b[2A"
    with cursor.HiddenCursor():
        sys.stdout.write("\n\n")
        while True:
            spinner_frame = next(spinner_generator)
            sys.stdout.write(
                f"\r{cursor_up}{render_progress_box(label, emoji, spinner_frame)}"
            )
            sys.stdout.flush()
            try:
                await asyncio.sleep(0.07)
            except asyncio.CancelledError:
                break
    sys.stdout.write(
        f"\r{cursor_up}{render_progress_box(label, emoji, FINISHED_STRING)}"
    )
    sys.stdout.write("\n")
