from .formatting import DEFAULT
from .preview import dictionary, sample

UI = {
    "copy_selection": ("Копировать выделенное", "Copy selection"),
    "copy_preview": ("Копировать весь текст", "Copy all text"),
    "select_all": ("Выделить всё", "Select all"),
    "page": ("Формат страницы", "Paper size"), "orientation": ("Ориентация", "Orientation"),
    "portrait": ("Книжная", "Portrait"), "landscape": ("Альбомная", "Landscape"),
    "before": ("Перед, пт", "Before, pt"), "after": ("После, пт", "After, pt"),
    "table_grid": ("Границы таблицы", "Table borders"), "table_bold": ("Полужирная шапка", "Bold table header"),
    "page_tab": ("Страница", "Page"), "tables": ("Таблицы", "Tables"),
    "editor": ("Редактор", "Editor"), "settings": ("Настройки", "Settings"),
    "theme": ("Тема", "Theme"), "language": ("Язык", "Language"),
    "auto": ("Авто (система)", "System"), "light": ("Светлая", "Light"), "dark": ("Тёмная", "Dark"),
    "preset": ("Пресет", "Preset"), "edit": ("Изменить", "Edit"),
    "add": ("Новый пресет", "New preset"), "copy": ("Скопировать словарь", "Copy dictionary"),
    "copied": ("Скопировано", "Copied"), "open": ("Открыть .md", "Open .md"),
    "export": ("Сохранить DOCX", "Save DOCX"), "preview": ("Предпросмотр", "Preview"),
    "sample": ("Образец пресета", "Preset sample"), "mine": ("Мой документ", "My document"),
    "placeholder": ("Введите Markdown…", "Enter Markdown…"), "name": ("Название", "Name"),
    "font": ("Шрифт", "Font"), "size": ("Размер, пт", "Size, pt"),
    "align": ("Выравнивание", "Alignment"), "indent": ("Первая строка, см", "First line, cm"),
    "spacing": ("Интервал", "Line spacing"), "margins": ("Поля, см", "Margins, cm"),
    "left": ("Слева", "Left"), "center": ("По центру", "Center"), "right": ("Справа", "Right"),
    "justify": ("По ширине", "Justified"), "top": ("Сверху", "Top"), "bottom": ("Снизу", "Bottom"),
    "levels": ("Уровни заголовков", "Heading levels"), "bold": ("Полужирный", "Bold"),
    "save": ("Сохранить", "Save"), "cancel": ("Отмена", "Cancel"), "error": ("Ошибка", "Error"),
    "duplicate": ("Пресет с таким названием уже есть.", "A preset with this name already exists."),
    "invalid": ("Проверьте параметры пресета.", "Check the preset settings."),
    "input": ("Не удалось прочитать Markdown в UTF-8.", "Could not read UTF-8 Markdown."),
    "limit": ("До 150 000 символов.", "Limit: 150,000 characters."),
    "disk": ("Не удалось сохранить файл.", "Could not save the file."),
    "empty": ("Введите Markdown.", "Enter some Markdown."),
    "saved": ("Сохранено", "Saved"), "lab": ("Лабораторная работа", "Lab report"),
    "toc": ("Оглавление", "Table of contents"), "state": ("Не удалось сохранить настройки.", "Could not save settings."),
}


def tr(lang, key):
    return UI[key][lang == "en"]


def display_name(p, lang):
    return tr(lang, "lab") if p["name"] == DEFAULT["name"] else p["name"]


EN_RULES = """Return only the UTF-8 Markdown file contents, without an enclosing code fence.
The header defines Word formatting. Omit the header from the document.

Markup dictionary
# Heading — level one. Use ##, ### and so on up to the level count in the header.
Plain text — a paragraph. Separate paragraphs with a blank line.
**text** — bold. *text* — italic. `text` — monospace.
- text — bullet item. 1. text — numbered item.
| A | B | — table row. Follow the header with | --- | --- |.
[[pagebreak]] — page break on its own line.
[[toc]] — table of contents on its own line. Its title is added automatically.
Three backticks on separate lines open and close a code block.
Use only these elements, single-level lists and rectangular tables."""


def localized_dictionary(p, lang):
    orientation = tr(lang,"landscape" if p["landscape"] else "portrait")
    flag = ("Да", "Нет") if lang == "ru" else ("Yes", "No")
    extra = [f"{p['page']}, {orientation}", f"{tr(lang,'before')}: {p['before']:g}; {tr(lang,'after')}: {p['after']:g}"]
    for key in ("table_bold","table_grid"):
        extra.append(f"{tr(lang,key)}: {flag[not p[key]]}")
    for i,h in enumerate(p["headings"],1):
        extra.append(f"H{i} — {tr(lang,'before')}: {h['before']:g}, {tr(lang,'after')}: {h['after']:g}")
    if lang == "ru":
        return dictionary(p).replace("A4, книжная ориентация.", "\n".join(extra), 1)
    lines = [display_name(p, lang), *extra,
             f"Body: {p['font']}, {p['size']:g} pt, {tr(lang,p['align']).lower()}.",
             f"First-line indent: {p['indent']:g} cm. Line spacing: {p['spacing']:g}.",
             "Margins (cm): " + ", ".join(f"{k} {v:g}" for k,v in p["margins"].items())]
    for i, h in enumerate(p["headings"], 1):
        weight = "bold" if h["bold"] else "regular"
        lines.append(f"H{i}: {h['size']:g} pt, {weight}, {tr(lang,h['align']).lower()}.")
    return "\n".join(lines) + "\n\n" + EN_RULES


def localized_sample(p, lang):
    if lang == "ru":
        return sample(p)
    text = (f"# Formatting preview\n\nThis is a sample of the {display_name(p, lang)} preset. "
            f"The body uses {p['font']} at {p['size']:g} pt. "
            "This paragraph shows the first-line indent, page margins and line spacing.")
    for i in range(2, len(p["headings"]) + 1):
        text += "\n\n" + "#"*i + f" Level {i} heading\n\nThis is how a section looks in the selected preset."
    return text + f"\n\n| Setting | Value |\n| --- | --- |\n| First-line indent | {p['indent']:g} cm |\n| Line spacing | {p['spacing']:g} |"


def parse_message(error, lang):
    if lang == "ru":
        return str(error)
    text = str(error)
    if "150 000" in text:
        return "Enter Markdown, up to 150,000 characters."
    if "5000" in text:
        return "Use up to 5,000 lines."
    if "3000" in text:
        return "Use up to 3,000 table cells."
    if "оглавление" in text:
        return "Use only one table of contents."
    if "символ" in text:
        return "The text contains a character that Word cannot store."
    if text.startswith("Строка "):
        line, _, details = text.partition(":")
        message = ("Add the required heading level to the preset." if "уровень" in details
                   else "Close the code fence." if "кода" in details
                   else "Check the table column count (up to 16).")
        return "Line " + line.split()[-1] + ": " + message
    return "Invalid Markdown."
