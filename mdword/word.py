from io import BytesIO

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

from .markdown import spans
from .formatting import page_size, validate
from docx.enum.section import WD_ORIENT

ALIGN = dict(left=WD_ALIGN_PARAGRAPH.LEFT, center=WD_ALIGN_PARAGRAPH.CENTER,
             right=WD_ALIGN_PARAGRAPH.RIGHT, justify=WD_ALIGN_PARAGRAPH.JUSTIFY)


def inline(paragraph, text, bold=False):
    for kind, content in spans(text):
        run = paragraph.add_run(content)
        if bold or kind == "bold":
            run.bold = True
        if kind == "italic":
            run.italic = True
        if kind == "code":
            run.font.name = "Courier New"


def export(blocks, preset, language="ru"):
    preset = validate(preset)
    doc = Document()
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE if preset["landscape"] else WD_ORIENT.PORTRAIT
    section.page_width, section.page_height = map(Cm, page_size(preset))
    for side, value in preset["margins"].items():
        setattr(section, side + "_margin", Cm(value))
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = preset["font"], Pt(preset["size"])
    fmt = normal.paragraph_format
    fmt.first_line_indent, fmt.line_spacing = Cm(preset["indent"]), preset["spacing"]
    fmt.space_before, fmt.space_after, fmt.alignment = Pt(preset["before"]), Pt(preset["after"]), ALIGN[preset["align"]]
    for i, opt in enumerate(preset["headings"], 1):
        style = doc.styles[f"Heading {i}"]
        style.font.name, style.font.size = preset["font"], Pt(opt["size"])
        fonts = style.element.rPr.rFonts
        for attr in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            fonts.attrib.pop(qn("w:" + attr), None)
        style.font.bold, style.font.italic = opt["bold"], False
        style.font.color.rgb = RGBColor(0, 0, 0)
        f = style.paragraph_format
        f.first_line_indent, f.alignment = Cm(0), ALIGN[opt["align"]]
        f.space_before, f.space_after = Pt(opt["before"]), Pt(opt["after"])
    heading_lines = ["".join(v for _, v in spans(b["text"])) for b in blocks if b["type"] == "h"]
    previous = None
    for block in blocks:
        kind = block["type"]
        if kind == "table":
            rows = block["rows"]
            table = doc.add_table(rows=0, cols=len(rows[0]), style="Table Grid" if preset["table_grid"] else "Normal Table")
            for index, values in enumerate(rows):
                row = table.add_row()
                if index == 0:
                    row._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
                for cell, value in zip(row.cells, values):
                    p = cell.paragraphs[0]
                    p.paragraph_format.first_line_indent = Cm(0)
                    p.alignment = ALIGN["left"]
                    inline(p, value, index == 0 and preset["table_bold"])
        elif kind == "pagebreak":
            doc.add_page_break()
        elif kind == "toc":
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.add_run("Table of contents" if language == "en" else "Оглавление").bold = True
            p = doc.add_paragraph()
            field = OxmlElement("w:fldSimple")
            field.set(qn("w:instr"), f'TOC \\o "1-{len(preset["headings"])}" \\h')
            field.set(qn("w:dirty"), "true")
            fallback = "Add headings for the table of contents." if language == "en" else "Добавьте заголовки для оглавления."
            run = p.add_run("\n".join(heading_lines) or fallback)
            field.append(run._r)
            p._p.append(field)
            setting = OxmlElement("w:updateFields")
            setting.set(qn("w:val"), "true")
            doc.settings.element.append(setting)
        elif kind in ("ol", "ul"):
            p = doc.add_paragraph()
            if previous != kind:
                numbering = doc.part.numbering_part.element
                legacy = doc.styles["List Number" if kind == "ol" else "List Bullet"]
                base = numbering.num_having_numId(legacy.element.pPr.numPr.numId.val)
                num = numbering.add_num(base.abstractNumId.val)
                num.add_lvlOverride(0).add_startOverride(1)
            prop = p._p.get_or_add_pPr().get_or_add_numPr()
            prop.get_or_add_ilvl().val = 0
            prop.get_or_add_numId().val = num.numId
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            inline(p, block["text"])
        elif kind == "code":
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.alignment = ALIGN["left"]
            p.add_run(block["text"]).font.name = "Courier New"
        else:
            p = doc.add_heading(level=block["level"]) if kind == "h" else doc.add_paragraph()
            inline(p, block["text"])
        previous = kind
    output = BytesIO()
    doc.save(output)
    return output.getvalue()
