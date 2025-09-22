import re
from .mapping import (
    ANSI_RESET,
    contains_foreground_color,
    contains_background_color,
    contains_style,
    get_foreground_color,
    get_background_color,
    get_style,
)
from pyglow.utilities.utils import get_closest_match

def parse_color(tag: str):
    tag = tag.lower()

    m = re.match(r"^rgb\((-?\d+),(-?\d+),(-?\d+)\)$", tag)
    if m:
        r, g, b = map(int, m.groups())
        if not all(0 <= x <= 255 for x in (r, g, b)):
            raise ValueError(f"RGB values out of range in tag `{tag}`")
        return f"\u001b[38;2;{r};{g};{b}m"

    m = re.match(r"^hex\(#([A-Fa-f0-9]{6})\)$", tag)
    if m:
        hex_code = m.group(1)
        r, g, b = int(hex_code[:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
        return f"\u001b[38;2;{r};{g};{b}m"

    m = re.match(r"^fg\((#([A-Fa-f0-9]{6})|rgb\((-?\d+),(-?\d+),(-?\d+)\))\)$", tag)
    if m:
        if m.group(2):
            hex_code = m.group(2)
            r, g, b = int(hex_code[:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
        else:
            r, g, b = map(int, m.groups()[2:])
            if not all(0 <= x <= 255 for x in (r, g, b)):
                raise ValueError(f"RGB values out of range in tag `{tag}`")
        return f"\u001b[38;2;{r};{g};{b}m"

    m = re.match(r"^bg\((#([A-Fa-f0-9]{6})|rgb\((-?\d+),(-?\d+),(-?\d+)\))\)$", tag)
    if m:
        if m.group(2):
            hex_code = m.group(2)
            r, g, b = int(hex_code[:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16)
        else:
            r, g, b = map(int, m.groups()[2:])
            if not all(0 <= x <= 255 for x in (r, g, b)):
                raise ValueError(f"RGB values out of range in tag `{tag}`")
        return f"\u001b[48;2;{r};{g};{b}m"

    return None

def extract_tag(s: str, start: int):
    end = s.find("]", start)
    if end == -1:
        raise ValueError("Unclosed tag")
    return s[start + 1:end].strip(), end + 1

def stack_to_ansi(stack):
    return "".join(s["ansi"] for s in stack if s["type"] == "style")

class Parser:
    @staticmethod
    def parse(input_str: str):
        output = []
        stack = []
        i = 0
        length = len(input_str)

        while i < length:
            if input_str.startswith("[/", i):
                tag_content, i = extract_tag(input_str, i)
                tag_lower = tag_content.lower()
                if tag_lower == "link":
                    for idx in range(len(stack)-1, -1, -1):
                        if stack[idx]["type"] == "link":
                            stack.pop(idx)
                            output.append("\033]8;;\033\\")
                            break
                else:
                    for idx in range(len(stack)-1, -1, -1):
                        if stack[idx]["type"] == "style":
                            stack.pop(idx)
                            break
                output.append(ANSI_RESET + stack_to_ansi(stack))
                continue

            elif input_str[i] == "[":
                tag_string, i = extract_tag(input_str, i)
                tag_lower = tag_string.lower()
                if tag_lower.startswith("link="):
                    url = tag_string[5:]
                    stack.append({"type": "link", "url": url})
                    output.append(f"\033]8;;{url}\033\\")
                    continue

                tags = tag_string.split()
                ansi_list = []
                for tag in tags:
                    tag_lower = tag.lower()
                    color_ansi = parse_color(tag_lower)
                    if color_ansi:
                        ansi_list.append(color_ansi)
                    elif contains_foreground_color(tag_lower):
                        ansi_list.append(get_foreground_color(tag_lower))
                    elif contains_background_color(tag_lower):
                        ansi_list.append(get_background_color(tag_lower))
                    elif contains_style(tag_lower):
                        ansi_list.append(get_style(tag_lower))
                    else:
                        suggestion = get_closest_match(tag_lower)
                        if suggestion:
                            raise KeyError(f"Tag `{tag}` not found. Did you mean '{suggestion}'?")
                        else:
                            raise KeyError(f"Tag `{tag}` not found.")
                if ansi_list:
                    ansi_str = "".join(ansi_list)
                    output.append(ansi_str)
                    stack.append({"type": "style", "ansi": ansi_str})
                continue

            else:
                output.append(input_str[i])
                i += 1

        while stack:
            tag = stack.pop()
            if tag["type"] == "link":
                output.append("\033]8;;\033\\")
            output.append(ANSI_RESET)

        return "".join(output)
