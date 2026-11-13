import json
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSaveFile, QIODevice, QStandardPaths, QTimer
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout,
                               QLabel, QMainWindow, QMessageBox, QPlainTextEdit, QPushButton, QSplitter,
                               QSizePolicy, QVBoxLayout, QWidget)

from mdword.formatting import DEFAULT, InputError, validate
from mdword.language import display_name, localized_dictionary, localized_sample, parse_message, tr
from mdword.markdown import parse
from mdword.paper import Paper
from mdword.preset_dialog import PresetDialog
from mdword.word import export

ASSETS = Path(__file__).resolve().parent / "assets"
VERSION = (ASSETS / "VERSION").read_text(encoding="ascii").strip()
CONTACT = "mak1nly@yandex.ru"


def atomic_write(path, data):
    file = QSaveFile(str(path))
    if not file.open(QIODevice.OpenModeFlag.WriteOnly) or file.write(data) != len(data) or not file.commit():
        raise OSError(file.errorString())


class Window(QMainWindow):
    def __init__(self, state_path=None):
        super().__init__()
        self.setWindowTitle("MDtoDOCX")
        self.setWindowIcon(QIcon(str(ASSETS / "document.ico")))
        self.resize(1190,760)
        self.path = state_path or Path(QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppConfigLocation)) / "preferences.json"
        self.lang,self.theme,self.items,self.index = "ru","auto",[validate(DEFAULT)],0
        try:
            state = json.loads(self.path.read_text(encoding="utf-8"))
            items = [validate(p) for p in state["items"]]
            if items and state["lang"] in ("ru","en") and state["theme"] in ("auto","light","dark") and 0 <= state["index"] < len(items):
                self.items,self.index,self.lang,self.theme = items,state["index"],state["lang"],state["theme"]
        except (OSError, ValueError, KeyError, TypeError):
            pass
        self.filename = None
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(20,16,20,18)
        layout.setSpacing(12)
        brand = QHBoxLayout()
        logo = QLabel()
        logo.setPixmap(QPixmap(str(ASSETS / "document.png")).scaled(38,44,Qt.KeepAspectRatio,Qt.SmoothTransformation))
        brand.addWidget(logo)
        title = QLabel("MDtoDOCX")
        title.setObjectName("brand")
        brand.addWidget(title)
        brand.addStretch()
        self.settings = QDialog(self)
        self.settings.resize(420, 300)
        self.settings.setWindowModality(Qt.WindowModal)
        self.gear = self.button(brand,self.settings.open)
        self.gear.setText("⚙")
        self.gear.setObjectName("gear")
        self.gear.setFixedSize(40,40)
        layout.addLayout(brand)
        workspace = QWidget()
        layout.addWidget(workspace,1)
        work = QVBoxLayout(workspace)
        work.setContentsMargins(14,16,14,14)
        work.setSpacing(14)
        bar = QHBoxLayout()
        work.addLayout(bar)
        self.preset_label = QLabel()
        bar.addWidget(self.preset_label)
        self.presets = QComboBox()
        self.presets.setMinimumWidth(165)
        self.presets.setMaximumWidth(300)
        bar.addWidget(self.presets)
        self.edit = self.button(bar,lambda:self.edit_preset(False))
        self.add = self.button(bar,lambda:self.edit_preset(True))
        self.add.setText("+")
        self.copy = self.button(bar,self.copy_dictionary)
        bar.addStretch()
        self.save = self.button(bar,self.save_doc)
        self.save.setObjectName("primary")
        split = QSplitter(Qt.Horizontal)
        split.setHandleWidth(16)
        split.setChildrenCollapsible(False)
        work.addWidget(split)
        source_panel,preview_panel = QWidget(), QWidget()
        split.addWidget(source_panel)
        split.addWidget(preview_panel)
        split.setSizes([490,610])
        src,prev = QVBoxLayout(source_panel),QVBoxLayout(preview_panel)
        for box in (src,prev):
            box.setContentsMargins(0,0,0,0)
            box.setSpacing(8)
        sh,ph = QHBoxLayout(), QHBoxLayout()
        src.addLayout(sh)
        prev.addLayout(ph)
        self.filename_label = QLabel("Markdown")
        self.filename_label.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.filename_label.setTextFormat(Qt.PlainText)
        sh.addWidget(self.filename_label, 1)
        self.open = self.button(sh,self.open_md)
        self.preview_label = QLabel()
        ph.addWidget(self.preview_label)
        ph.addStretch()
        self.mode = QComboBox()
        ph.addWidget(self.mode)
        for header in (sh, ph):
            header.setSpacing(8)
            header.setAlignment(Qt.AlignVCenter)
        for control in (self.open, self.mode):
            control.setMinimumHeight(32)
        self.source = QPlainTextEdit()
        self.source.setFont(QFont("Consolas",11))
        src.addWidget(self.source)
        self.paper = Paper()
        prev.addWidget(self.paper)
        settings_layout = QVBoxLayout(self.settings)
        settings_layout.setContentsMargins(22,20,22,14)
        settings_layout.addStretch()
        fields = QWidget()
        form = QFormLayout(fields)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)
        settings_layout.addWidget(fields,0,Qt.AlignCenter)
        settings_layout.addStretch()
        self.theme_label,self.language_label = QLabel(),QLabel()
        self.themes,self.languages = QComboBox(),QComboBox()
        self.languages.addItems(["Русский","English"])
        self.languages.setCurrentIndex(int(self.lang=="en"))
        form.addRow(self.theme_label,self.themes)
        form.addRow(self.language_label,self.languages)
        self.version_label = QLabel()
        self.contact_label = QLabel()
        self.contact_label.setOpenExternalLinks(True)
        self.contact_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        for label in (self.version_label,self.contact_label):
            label.setObjectName("settingsFooter")
            label.setAlignment(Qt.AlignCenter)
            settings_layout.addWidget(label)
        self.translate()
        self.restyle()
        self.refresh()
        self.presets.currentIndexChanged.connect(self.choose)
        self.mode.currentIndexChanged.connect(self.refresh)
        self.source.textChanged.connect(self.source_changed)
        self.languages.currentIndexChanged.connect(self.change_language)
        self.themes.currentIndexChanged.connect(self.change_theme)
        QApplication.styleHints().colorSchemeChanged.connect(self.restyle)
        self.copy_timer=QTimer(self,singleShot=True,interval=1500)
        self.copy_timer.timeout.connect(lambda:self.copy.setText(self.t("copy")))

    @staticmethod
    def button(layout,slot):
        b = QPushButton()
        layout.addWidget(b)
        b.clicked.connect(slot)
        return b

    def t(self,key):
        return tr(self.lang,key)

    def translate(self):
        self.settings.setWindowTitle(self.t("settings"))
        self.gear.setAccessibleName(self.t("settings"))
        self.gear.setToolTip(self.t("settings"))
        self.version_label.setText(f"{self.t('version')} {VERSION}")
        self.contact_label.setText(f'{self.t("bug_contact")} <a href="mailto:{CONTACT}">{CONTACT}</a>')
        for w,key in [(self.preset_label,"preset"),(self.edit,"edit"),(self.copy,"copy"),(self.save,"export"),
                      (self.open,"open"),(self.preview_label,"preview"),(self.theme_label,"theme"),(self.language_label,"language")]:
            w.setText(self.t(key))
        self.add.setToolTip(self.t("add"))
        self.add.setAccessibleName(self.t("add"))
        self.source.setPlaceholderText(self.t("placeholder"))
        self.fill(self.presets,[display_name(p,self.lang) for p in self.items],self.index)
        self.fill(self.mode,[self.t("sample"),self.t("mine")],max(0,self.mode.currentIndex()))
        self.fill(self.themes,[self.t(k) for k in ("auto","light","dark")],("auto","light","dark").index(self.theme))

    @staticmethod
    def fill(combo,values,index):
        combo.blockSignals(True)
        combo.clear()
        combo.addItems(values)
        combo.setCurrentIndex(index)
        combo.blockSignals(False)

    def persist(self):
        try:
            self.path.parent.mkdir(parents=True,exist_ok=True)
            atomic_write(self.path,json.dumps(dict(items=self.items,index=self.index,lang=self.lang,theme=self.theme),ensure_ascii=False).encode())
        except OSError:
            self.error(self.t("state"))

    def change_language(self,i):
        self.lang = ("ru","en")[i]
        self.translate()
        self.refresh()
        self.persist()

    def change_theme(self,i):
        self.theme=("auto","light","dark")[i]
        self.restyle()
        self.persist()

    def restyle(self,*_):
        dark = self.theme=="dark" or (self.theme=="auto" and QApplication.styleHints().colorScheme()==Qt.ColorScheme.Dark)
        bg,panel,text,line,accent = ("#171a23","#242834","#e9ebf5","#43495b","#b6aaff") if dark else ("#f5f6fa","#ffffff","#24263c","#d7dbe5","#5446c7")
        QApplication.instance().setStyleSheet(f"""
          QWidget {{background:{bg};color:{text};font-family:'Segoe UI';font-size:10pt;}}
          QLabel#brand {{font-size:18pt;font-weight:700;}}
          QPushButton#gear {{font-family:'Segoe UI Symbol';font-size:18pt;padding:0;}}
          QLabel#settingsFooter {{font-size:9pt;}}
          QTabWidget::pane {{border:1px solid {line};border-radius:6px;}}
          QTabBar::tab {{padding:7px 16px;color:{text};}}
          QTabBar::tab:selected {{color:{accent};border-bottom:2px solid {accent};}}
          QPushButton,QComboBox,QLineEdit,QSpinBox,QDoubleSpinBox {{background:{panel};border:1px solid {line};border-radius:5px;padding:5px 8px;}}
          QPushButton:hover,QComboBox:hover {{border-color:{accent};}}
          QPushButton#primary {{background:#5446c7;color:white;border-color:#5446c7;}}
          QPlainTextEdit,QTextEdit {{background:{panel};border:1px solid {line};border-radius:5px;padding:7px;}}
          QPlainTextEdit {{font-family:Consolas;font-size:11pt;}}
          QTextEdit#paper {{background:white;color:#171717;selection-color:white;selection-background:#5446c7;}}
          QAbstractItemView {{background:{panel};color:{text};selection-background-color:#5446c7;selection-color:white;}}
          QSplitter::handle {{background:{bg};}}
        """)

    def choose(self,i):
        self.index=i
        self.mode.setCurrentIndex(0)
        self.refresh()
        self.persist()

    def source_changed(self):
        self.mode.setCurrentIndex(1)
        self.refresh()

    def refresh(self):
        p=self.items[self.index]
        text=localized_sample(p,self.lang) if self.mode.currentIndex()==0 else self.source.toPlainText()
        self.paper.show_document(text,p,self.lang)

    def edit_preset(self,new):
        dialog=PresetDialog(self,self.items[self.index],new)
        if dialog.exec():
            if new:
                self.index=len(self.items)
                self.items.append(dialog.result_preset)
            else:
                self.items[self.index]=dialog.result_preset
            self.translate()
            self.choose(self.index)
        dialog.deleteLater()

    def copy_dictionary(self):
        QApplication.clipboard().setText(localized_dictionary(self.items[self.index],self.lang))
        self.copy.setText(self.t("copied"))
        self.copy_timer.start()

    def error(self,message):
        QMessageBox.warning(self,self.t("error"),message)

    def open_md(self):
        path,_=QFileDialog.getOpenFileName(self,self.t("open"),"","Markdown (*.md *.markdown);;Text (*.txt)")
        if not path:
            return
        try:
            with open(path,"rb") as f:
                data=f.read(600001)
            if len(data)>600000:
                raise InputError(self.t("limit"))
            text=data.decode("utf-8-sig")
            if len(text)>150000:
                raise InputError(self.t("limit"))
            self.source.setPlainText(text)
            self.filename=Path(path)
            self.filename_label.setText(self.filename.name)
            self.filename_label.setToolTip(self.filename.name)
        except InputError as e:
            self.error(str(e))
        except (OSError,UnicodeError):
            self.error(self.t("input"))

    def save_doc(self):
        p=self.items[self.index]
        try:
            blocks=parse(self.source.toPlainText(),len(p["headings"]))
        except InputError as e:
            self.error(parse_message(e,self.lang))
            return
        name=self.filename.with_suffix(".docx") if self.filename else Path("Document.docx" if self.lang=="en" else "Документ.docx")
        path,_=QFileDialog.getSaveFileName(self,self.t("export"),str(name),"Word (*.docx)")
        if path:
            try:
                atomic_write(path,export(blocks,p,self.lang))
            except OSError:
                self.error(self.t("disk"))


if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setApplicationName("MDtoDOCX")
    app.setApplicationVersion(VERSION)
    w=Window()
    w.show()
    sys.exit(app.exec())

