from html import escape

from .markdown import spans
from .formatting import DICTIONARY, page_size

ALIGN = {"left": "Слева", "center": "По центру", "right": "Справа", "justify": "По ширине"}


def fmt(value):
    return f"{value:g}".replace(".", ",")


def dictionary(p):
    m = p["margins"]
    lines = [p["name"], "A4, книжная ориентация.",
             f"Текст: {p['font']}, {fmt(p['size'])} пт, {ALIGN[p['align']].lower()}.",
             f"Первая строка: {fmt(p['indent'])} см. Интервал: {fmt(p['spacing'])}.",
             "Поля (см): " + ", ".join(f"{k} {fmt(m[v])}" for k, v in
                                      [("слева", "left"), ("справа", "right"), ("сверху", "top"), ("снизу", "bottom")])]
    for i, h in enumerate(p["headings"], 1):
        weight = "полужирный" if h["bold"] else "обычный"
        lines.append(f"H{i}: {fmt(h['size'])} пт, {weight}, {ALIGN[h['align']].lower()}.")
    return "\n".join(lines) + "\n\n" + DICTIONARY


def sample(p):
    text = (f"# Предпросмотр оформления\n\nЭто образец пресета «{p['name']}». "
            f"Основной текст набран шрифтом {p['font']}, {fmt(p['size'])} пт. "
            "В этом абзаце видны отступ первой строки и расстояние между строками.")
    for i in range(2, len(p["headings"]) + 1):
        text += "\n\n" + "#" * i + f" Заголовок уровня {i}\n\nТак выглядит текст раздела в выбранном оформлении."
    return (text + "\n\n| Параметр | Значение |\n| --- | --- |\n"
            f"| Первая строка | {fmt(p['indent'])} см |\n| Интервал | {fmt(p['spacing'])} |")


def inline(text):
    tags = {"bold": "b", "italic": "i", "code": "tt"}
    return "".join(f"<{tags[k]}>{escape(v)}</{tags[k]}>" if k in tags else escape(v) for k, v in spans(text))


def preview(blocks, p, width, toc_title="Оглавление"):
    # Qt rich text uses logical pixels. Scale a 210 mm sheet to its viewport.
    cm = width / page_size(p)[0]
    px = cm * 2.54 / 72
    margins = p["margins"]
    base = f"margin:0;line-height:{round(p['spacing']*100)}%;"
    para = f"{base}text-indent:{p['indent']*cm:.1f}px;margin-top:{p['before']*px}px;margin-bottom:{p['after']*px}px;"
    result = []
    previous, ordinal = None, 0
    for b in blocks:
        k = b["type"]
        if k == "h":
            h = p["headings"][b["level"] - 1]
            weight = "bold" if h["bold"] else "normal"
            style = f"{base}margin-top:{h['before']*px}px;margin-bottom:{h['after']*px}px;font-size:{h['size']*px}px;font-weight:{weight}"
            result.append(f'<p align="{h["align"]}" style="{style}">{inline(b["text"])}</p>')
        elif k == "table":
            result.append(f'<table border="{int(p["table_grid"])}" cellspacing="0" cellpadding="3" width="100%">')
            for i, row in enumerate(b["rows"]):
                tag = "th" if i == 0 and p["table_bold"] else "td"
                result.append("<tr>" + "".join(f"<{tag}>{inline(cell)}</{tag}>" for cell in row) + "</tr>")
            result.append("</table>")
        elif k == "code":
            result.append("<pre>" + escape(b["text"]) + "</pre>")
        elif k == "toc":
            result.append(f"<p><b>{escape(toc_title)}</b></p>" + "<br>".join(inline(h["text"]) for h in blocks if h["type"] == "h"))
        elif k == "pagebreak":
            result.append("<hr>")
        elif k in ("ul", "ol"):
            ordinal = ordinal + 1 if previous == "ol" else 1
            marker = "•" if k == "ul" else f"{ordinal}."
            result.append(f'<p style="{base}margin-left:{cm*.5}px">{marker} {inline(b["text"])}</p>')
        else:
            result.append(f'<p align="{p["align"]}" style="{para}">{inline(b["text"])}</p>')
        previous = k
    # The font is set through QFont, never interpolated into a style attribute.
    pad = [round(margins[k]*cm) for k in ("top","right","bottom","left")]
    return ("<html><body><table width='100%' cellspacing='0' cellpadding='0'><tr>"
            f"<td style='padding:{pad[0]}px {pad[1]}px {pad[2]}px {pad[3]}px'>"
            + "".join(result) + "</td></tr></table></body></html>")

