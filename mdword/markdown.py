import re
from .formatting import InputError

HEADING = re.compile(r"^(#{1,6})\s+(.+)$")
ITEM = re.compile(r"^(?:(-)|\d{1,9}\.)\s+(.+)$")
SEPARATOR = re.compile(r":?-{3,}:?")
INLINE = re.compile(r"(`[^`\n]+`|\*\*[^*\n]+\*\*|\*[^*\n]+\*)")


def spans(text):
    for index, part in enumerate(INLINE.split(text)):
        if not part:
            continue
        if index % 2 == 0:
            yield "plain", part
        elif part.startswith("**"):
            yield "bold", part[2:-2]
        else:
            yield ("code" if part.startswith("`") else "italic"), part[1:-1]


def cells(line):
    return [s.strip() for s in line.strip()[1:-1].split("|")]


def table_line(line):
    s = line.strip()
    return len(s) >= 2 and s.startswith("|") and s.endswith("|")


def parse(text, levels):
    if not isinstance(text, str) or len(text) > 150_000 or not text.strip():
        raise InputError("Введите Markdown объёмом до 150 000 символов.")
    if re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]", text):
        raise InputError("В тексте есть символ, недопустимый для Word.")
    lines = text.lstrip("\ufeff").splitlines()
    if len(lines) > 5000:
        raise InputError("Допускается до 5000 строк.")
    blocks, paragraph = [], []
    i = total_cells = 0
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        heading, item = HEADING.match(s), ITEM.match(s)
        table = table_line(s) and i < len(lines) and table_line(lines[i]) and all(
            SEPARATOR.fullmatch(v) for v in cells(lines[i]))
        if s and not (heading or item or table or s.startswith("```") or s in ("[[toc]]", "[[pagebreak]]")):
            paragraph.append(s)
            continue
        if paragraph:
            blocks.append({"type": "p", "text": " ".join(paragraph)})
            paragraph.clear()
        if heading:
            level = len(heading[1])
            if level > levels:
                raise InputError(f"Строка {i}: добавьте в пресет уровень H{level}.")
            blocks.append({"type": "h", "level": level, "text": heading[2]})
        elif item:
            blocks.append({"type": "ul" if item[1] else "ol", "text": item[2]})
        elif s.startswith("```"):
            start = i
            while i < len(lines) and lines[i].strip() != "```":
                i += 1
            if i == len(lines):
                raise InputError(f"Строка {start}: закройте блок кода тремя обратными кавычками.")
            blocks.append({"type": "code", "text": "\n".join(lines[start:i])})
            i += 1
        elif table:
            rows = [cells(s)]
            width = len(rows[0])
            if width > 16 or len(cells(lines[i])) != width:
                raise InputError(f"Строка {i}: проверьте число столбцов таблицы (до 16).")
            i += 1
            while i < len(lines) and table_line(lines[i]):
                row = cells(lines[i])
                if len(row) != width:
                    raise InputError(f"Строка {i+1}: в таблице должно быть {width} столбцов.")
                rows.append(row)
                i += 1
            total_cells += width * len(rows)
            if total_cells > 3000:
                raise InputError("Допускается до 3000 ячеек в документе.")
            blocks.append({"type": "table", "rows": rows})
        elif s:
            blocks.append({"type": s[2:-2]})
    if paragraph:
        blocks.append({"type": "p", "text": " ".join(paragraph)})
    if sum(b["type"] == "toc" for b in blocks) > 1:
        raise InputError("Оставьте одно оглавление в документе.")
    return blocks
