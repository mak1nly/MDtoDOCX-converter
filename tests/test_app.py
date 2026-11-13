import copy
import unittest
from io import BytesIO
from zipfile import ZipFile

from docx import Document
from docx.oxml.ns import qn

from mdword.formatting import DEFAULT, InputError, validate
from mdword.markdown import parse
from mdword.word import export


class Documents(unittest.TestCase):
    def test_roundtrip(self):
        source = "# Глава\n\n[[toc]]\n\nТекст **жирный** *курсив* <img>\n\n| A | B |\n| --- | --- |\n| 1 | 2 |\n\n[[pagebreak]]\n1. Один\n2. Два\n\nТекст\n\n1. Сначала\n- Пункт\n```\nx=1\n```"
        stream = BytesIO(export(parse(source, 3), validate(DEFAULT)))
        self.assertIsNone(ZipFile(stream).testzip())
        doc = Document(stream)
        self.assertEqual(doc.styles["Normal"].font.name, "Times New Roman")
        self.assertEqual(doc.styles["Normal"].font.size.pt, 14)
        self.assertAlmostEqual(doc.styles["Normal"].paragraph_format.first_line_indent.cm, 1.25, 2)
        self.assertAlmostEqual(doc.sections[0].left_margin.cm, 2.54, 2)
        self.assertEqual(doc.tables[0].cell(1, 1).text, "2")
        self.assertEqual(doc.paragraphs[0].style.name, "Heading 1")
        self.assertTrue(doc.element.xpath("//w:fldSimple"))
        self.assertTrue(doc.element.xpath("//w:br[@w:type='page']"))
        self.assertTrue(doc.element.xpath("//w:r[w:b or w:rPr/w:b]"))
        self.assertIn("<img>", doc.element.xml.replace("&lt;", "<").replace("&gt;", ">"))
        ids = [x.get(qn("w:val")) for x in doc.element.xpath("//w:numPr/w:numId")]
        self.assertEqual(ids[0], ids[1])
        self.assertNotEqual(ids[1], ids[2])

    def test_custom_styles(self):
        p = copy.deepcopy(DEFAULT)
        p.update(font="Arial", indent=0, size=12)
        p["headings"][0].update(size=22, bold=False, align="center")
        doc = Document(BytesIO(export(parse("# Тест", 3), validate(p))))
        h = doc.styles["Heading 1"]
        self.assertEqual(h.font.size.pt, 22)
        self.assertFalse(h.font.bold)
        self.assertEqual(h.font.name, "Arial")

    def test_invalid_input(self):
        for text in ("", "hi\x00", "#### H", "x"*150001, "```\nopen", "|a|b|\n|---|---|\n|1|", "[[toc]]\n[[toc]]"):
            with self.subTest(text=text[:20]), self.assertRaises(InputError):
                parse(text, 3)
        for bad in (None, {}, dict(DEFAULT, size=float("nan")), dict(DEFAULT, headings=[])):
            with self.assertRaises(InputError):
                validate(bad)
