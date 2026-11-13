from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QKeySequence
from PySide6.QtWidgets import QApplication, QMenu, QTextEdit

from .formatting import InputError, page_size
from .language import parse_message, tr
from .markdown import parse
from .preview import preview


class Paper(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.setObjectName("paper")
        self.content = None
        self.timer = QTimer(self, singleShot=True, interval=55)
        self.timer.timeout.connect(self.render)

    def copy_text(self):
        if self.textCursor().hasSelection():
            self.copy()
        elif not self.document().isEmpty():
            QApplication.clipboard().setText(self.toPlainText().strip())

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.StandardKey.Copy):
            self.copy_text()
            event.accept()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event):
        lang = self.content[2] if self.content else "ru"
        menu = QMenu(self)
        key = "copy_selection" if self.textCursor().hasSelection() else "copy_preview"
        copy_action = menu.addAction(tr(lang, key), self.copy_text)
        copy_action.setEnabled(not self.document().isEmpty())
        menu.addAction(tr(lang, "select_all"), self.selectAll)
        menu.exec(event.globalPos())
        menu.deleteLater()

    def show_document(self, text, preset, lang):
        self.content = (text, preset, lang)
        self.timer.start()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.timer.start()

    def render(self):
        if not self.content:
            return
        text,p,lang = self.content
        try:
            blocks = parse(text,len(p["headings"])) if text.strip() else []
        except InputError as e:
            self.setPlainText(parse_message(e,lang))
            return
        width = max(80, self.viewport().width()-12)
        font = QFont(p["font"])
        font.setPixelSize(max(1,round(p["size"]*width/page_size(p)[0]*2.54/72)))
        scroll = self.verticalScrollBar().value()
        self.document().setDefaultFont(font)
        self.setHtml(preview(blocks,p,width,tr(lang,"toc")))
        self.verticalScrollBar().setValue(scroll)
