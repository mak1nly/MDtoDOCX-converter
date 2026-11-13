import os
import tempfile
import unittest
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM","offscreen")
from PySide6.QtTest import QTest
from PySide6.QtCore import QPoint, Qt
from PySide6.QtWidgets import QApplication
from docx import Document

from app import Window
from mdword.formatting import DEFAULT
from mdword.preset_dialog import PresetDialog


class Desktop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_copy_preview(self):
        with tempfile.TemporaryDirectory() as tmp:
            w = Window(Path(tmp) / "prefs.json")
            dialog = PresetDialog(w, DEFAULT, False)
            try:
                w.source.setPlainText("# Результат\n\nТекст **отчёта**")
                for paper, word in [(w.paper, "отчёта"), (dialog.paper, "пресета")]:
                    paper.render()
                    QTest.keyClick(paper, Qt.Key_C, Qt.ControlModifier)
                    self.assertEqual(self.app.clipboard().text(), paper.toPlainText().strip())
                    self.assertTrue(paper.find(word))
                    QTest.keyClick(paper, Qt.Key_C, Qt.ControlModifier)
                    self.assertEqual(self.app.clipboard().text(), word)
            finally:
                dialog.close()
                w.close()

    def test_editor_panel_spacing(self):
        with tempfile.TemporaryDirectory() as tmp:
            window = Window(Path(tmp) / "prefs.json")
            try:
                window.show()
                window.filename_label.setText("Лабораторная работа " * 10 + ".md")
                for language in (0, 1):
                    window.languages.setCurrentIndex(language)
                    for width in (850, 1190):
                        window.resize(width, 660)
                        self.app.processEvents()
                        for left, right in [(window.open, window.preview_label), (window.source, window.paper)]:
                            edge = left.mapTo(window, QPoint(left.width(), 0)).x()
                            start = right.mapTo(window, QPoint()).x()
                            self.assertGreaterEqual(start - edge, 12)
            finally:
                window.close()

    def test_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            w = Window(path/"prefs.json")
            w.show()
            QTest.qWait(150)
            self.assertIn("Предпросмотр", w.paper.toPlainText())
            w.languages.setCurrentIndex(1)
            w.themes.setCurrentIndex(2)
            w.copy_dictionary()
            self.assertEqual(w.copy.text(),"Copied")
            dictionary = self.app.clipboard().text()
            self.assertIn("Lab report",dictionary)
            self.assertIn("[[toc]]",dictionary)
            self.assertFalse(any("А" <= c <= "я" for c in dictionary))
            dialog = PresetDialog(w,DEFAULT,True)
            dialog.show()
            dialog.name.setText("Custom")
            dialog.page.setCurrentText("Letter")
            dialog.orientation.setCurrentIndex(1)
            dialog.size.setValue(22)
            dialog.after.setValue(18)
            dialog.rows[0][4].setValue(32)
            dialog.table_grid.setChecked(False)
            QTest.qWait(350)
            self.assertIn("22 pt",dialog.paper.toPlainText())
            self.assertEqual(dialog.paper.content[1]["after"],18)
            self.assertTrue(dialog.paper.content[1]["landscape"])
            self.assertEqual(w.items[0]["size"],14)
            dialog.submit()
            w.items.append(dialog.result_preset)
            w.translate()
            w.presets.setCurrentIndex(1)
            f = path/"report.md"
            f.write_text("[[toc]]\n\n# Result\n\n| A | B |\n| --- | --- |\n| 1 | 2 |",encoding="utf8")
            with patch("app.QFileDialog.getOpenFileName",return_value=(str(f),"")):
                w.open_md()
            out=path/"report.docx"
            with patch("app.QFileDialog.getSaveFileName",return_value=(str(out),"")):
                w.save_doc()
            doc=Document(BytesIO(out.read_bytes()))
            self.assertEqual(doc.paragraphs[0].text,"Table of contents")
            self.assertEqual(doc.styles["Normal"].font.size.pt,22)
            self.assertEqual(doc.styles["Normal"].paragraph_format.space_after.pt,18)
            self.assertEqual(doc.styles["Heading 1"].paragraph_format.space_before.pt,32)
            self.assertAlmostEqual(doc.sections[0].page_width.cm,27.94,2)
            self.assertEqual(doc.tables[0].style.name,"Normal Table")
            reopened=Window(path/"prefs.json")
            self.assertEqual((reopened.lang,reopened.theme,reopened.index),("en","dark",1))
            self.assertEqual(len(reopened.items),2)
            w.languages.setCurrentIndex(0)
            w.copy_dictionary()
            self.assertEqual(w.copy.text(),"Скопировано")
            self.assertIn("# Result",w.source.toPlainText())
            for widget in [dialog,w,reopened]:
                widget.close()

