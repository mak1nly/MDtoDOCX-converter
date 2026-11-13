import math


class InputError(ValueError):
    pass


DEFAULT = {
    "name": "Лабораторная работа", "font": "Times New Roman", "size": 14,
    "indent": 1.25, "spacing": 1.5, "align": "justify",
    "margins": dict.fromkeys(("left", "right", "top", "bottom"), 2.54),
    "headings": [{"size": 14, "bold": True, "align": "left"} for _ in range(3)],
}

DICTIONARY = """Верни только содержимое Markdown-файла в UTF-8, без внешнего блока кода.
Шапка описывает оформление в Word. Не включай её в текст документа.

Словарь разметки
# Заголовок — первый уровень. Используй ##, ### и далее до числа уровней из шапки.
Обычный текст — абзац. Разделяй абзацы пустой строкой.
**текст** — полужирный. *текст* — курсив. `текст` — моноширинный.
- текст — пункт маркированного списка. 1. текст — пункт нумерованного списка.
| A | B | — строка таблицы. После шапки добавь строку | --- | --- |.
[[pagebreak]] — разрыв страницы на отдельной строке.
[[toc]] — оглавление на отдельной строке. Заголовок «Оглавление» добавляется автоматически.
Три обратные кавычки на отдельных строках открывают и закрывают блок кода.
Используй только перечисленные элементы, списки одного уровня и прямоугольные таблицы."""

PAGES = {"A4": (21, 29.7), "A5": (14.8, 21), "Letter": (21.59, 27.94)}
DEFAULT.update(page="A4", landscape=False, before=0, after=0, table_bold=True, table_grid=True)
for heading in DEFAULT["headings"]:
    heading.update(before=12, after=6)


def page_size(p):
    dimensions = PAGES[p.get("page", "A4")]
    return dimensions[::-1] if p.get("landscape") else dimensions


def label(value, limit):
    if not isinstance(value, str) or not 0 < len(value.strip()) <= limit or not value.isprintable():
        raise InputError("Проверьте название пресета и шрифт.")
    return value.strip()


def number(value, low, high):
    if type(value) not in (int, float) or not low <= value <= high or not math.isfinite(value):
        raise InputError(f"Число должно быть в диапазоне {low}–{high}.")
    return value


def alignment(value):
    if value not in ("left", "center", "right", "justify"):
        raise InputError("Неизвестное выравнивание.")
    return value


def validate(p):
    try:
        h = p["headings"]
        if not isinstance(h, list) or not 1 <= len(h) <= 6:
            raise InputError("Выберите от 1 до 6 уровней заголовков.")
        if any(type(row["bold"]) is not bool for row in h):
            raise InputError("Проверьте начертание заголовка.")
        if p.get("page", "A4") not in PAGES or any(type(p.get(k, DEFAULT[k])) is not bool for k in ("landscape","table_bold","table_grid")):
            raise InputError("Проверьте настройки страницы и таблицы.")
        return {
            **{k:p.get(k, DEFAULT[k]) for k in ("page","landscape","table_bold","table_grid")},
            **{k:number(p.get(k, 0), 0, 72) for k in ("before","after")},
            "name": label(p["name"], 64), "font": label(p["font"], 80),
            "size": number(p["size"], 8, 48), "indent": number(p["indent"], 0, 4),
            "spacing": number(p["spacing"], 1, 3), "align": alignment(p["align"]),
            "margins": {k: number(p["margins"][k], 0.5, 5) for k in DEFAULT["margins"]},
            "headings": [{"size": number(row["size"], 8, 60), "bold": row["bold"],
                          "before": number(row.get("before",12),0,72), "after": number(row.get("after",6),0,72),
                          "align": alignment(row["align"])} for row in h],
        }
    except (TypeError, KeyError, IndexError):
        raise InputError("Пресет содержит неполные параметры.") from None
