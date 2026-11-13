from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QGridLayout,
                               QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSpinBox,
                               QTabWidget, QVBoxLayout, QWidget)
from PySide6.QtCore import QTimer
from .language import display_name, localized_sample, tr
from .paper import Paper
from .formatting import InputError, validate


class PresetDialog(QDialog):
    def __init__(self, parent, p, new):
        super().__init__(parent)
        self.lang = parent.lang
        t = lambda key: tr(self.lang, key)
        self.setWindowTitle(t("add" if new else "edit"))
        self.resize(1090, 590)
        layout = QVBoxLayout(self)
        columns = QHBoxLayout()
        columns.setSpacing(16)
        layout.addLayout(columns,1)
        tabs = QTabWidget()
        columns.addWidget(tabs,5)
        self.paper = Paper()
        columns.addWidget(self.paper,6)
        body = QWidget()
        form = QFormLayout(body)
        tabs.addTab(body, t("preset"))
        self.name = QLineEdit(t("add") if new else display_name(p, self.lang))
        self.name.setMaxLength(64)
        self.original = p
        self.font = QLineEdit(p["font"])
        self.font.setMaxLength(80)
        self.size = self.number(p["size"], 8, 48)
        self.indent = self.number(p["indent"], 0, 4)
        self.spacing = self.number(p["spacing"], 1, 3)
        self.align = self.alignment(p["align"])
        for key in ("name","font","size","align","indent","spacing"):
            form.addRow(t(key), getattr(self,key))
        self.before = self.number(p["before"],0,72)
        self.after = self.number(p["after"],0,72)
        form.addRow(t("before"), self.before)
        form.addRow(t("after"), self.after)
        margin = QWidget()
        mf = QFormLayout(margin)
        self.page = QComboBox()
        self.page.addItems(["A4","A5","Letter"])
        self.page.setCurrentText(p["page"])
        self.orientation = QComboBox()
        self.orientation.addItems([t("portrait"),t("landscape")])
        self.orientation.setCurrentIndex(int(p["landscape"]))
        mf.addRow(t("page"),self.page)
        mf.addRow(t("orientation"),self.orientation)
        self.margins = {}
        for k,v in p["margins"].items():
            self.margins[k] = self.number(v, .5, 5)
            mf.addRow(t("margins")+" · "+t(k),self.margins[k])
        tabs.addTab(margin,t("page_tab"))
        headings = QWidget()
        grid = QGridLayout(headings)
        self.levels = QSpinBox()
        self.levels.setRange(1,6)
        self.levels.setValue(len(p["headings"]))
        grid.addWidget(QLabel(t("levels")),0,0,1,2)
        grid.addWidget(self.levels,0,2)
        grid.addWidget(QLabel(t("size")),1,1)
        grid.addWidget(QLabel(t("align")),1,2)
        grid.addWidget(QLabel(t("before")),1,4)
        grid.addWidget(QLabel(t("after")),1,5)
        self.rows = []
        for i in range(6):
            h = p["headings"][min(i,len(p["headings"])-1)]
            row = [QLabel(f"H{i+1}"), self.number(h["size"],8,60), self.alignment(h["align"]), QCheckBox(t("bold"))]
            row[-1].setChecked(h["bold"])
            row.extend([self.number(h["before"],0,72),self.number(h["after"],0,72)])
            for j,w in enumerate(row):
                grid.addWidget(w,i+2,j)
            self.rows.append(row)
        self.levels.valueChanged.connect(self.update_rows)
        self.update_rows()
        grid.setRowStretch(8,1)
        tabs.addTab(headings,t("levels"))
        tables = QWidget()
        tf = QFormLayout(tables)
        self.table_grid, self.table_bold = QCheckBox(t("table_grid")), QCheckBox(t("table_bold"))
        for key in ("table_grid","table_bold"):
            w=getattr(self,key)
            w.setChecked(p[key])
            tf.addRow(w)
        tabs.addTab(tables,t("tables"))
        actions = QHBoxLayout()
        actions.addStretch()
        for key, action in [("cancel",self.reject),("save",self.submit)]:
            button = QPushButton(t(key))
            button.clicked.connect(action)
            actions.addWidget(button)
        layout.addLayout(actions)
        self.is_new = new
        self.preview_timer = QTimer(self,singleShot=True,interval=45)
        self.preview_timer.timeout.connect(self.live_preview)
        for widget_type,signal in [(QLineEdit,"textChanged"),(QComboBox,"currentIndexChanged"),
                                   (QCheckBox,"toggled"),(QSpinBox,"valueChanged"),(QDoubleSpinBox,"valueChanged")]:
            for w in self.findChildren(widget_type):
                getattr(w,signal).connect(lambda *_: self.preview_timer.start())
        self.live_preview()

    def update_rows(self):
        for i,row in enumerate(self.rows):
            for w in row:
                w.setVisible(i < self.levels.value())

    def alignment(self,value):
        combo = QComboBox()
        for key in ("left","right","center","justify"):
            combo.addItem(tr(self.lang,key),key)
        combo.setCurrentIndex(combo.findData(value))
        return combo

    @staticmethod
    def number(value, low, high):
        spin = QDoubleSpinBox()
        spin.setRange(low, high)
        spin.setDecimals(2)
        spin.setValue(value)
        return spin

    def values(self):
        name = self.name.text().strip()
        if not self.is_new and name == display_name(self.original, self.lang):
            name = self.original["name"]
        return validate(dict(name=name, font=self.font.text(), size=self.size.value(),
                page=self.page.currentText(),landscape=bool(self.orientation.currentIndex()),
                table_bold=self.table_bold.isChecked(),table_grid=self.table_grid.isChecked(),
                before=self.before.value(),after=self.after.value(),
                indent=self.indent.value(), spacing=self.spacing.value(), align=self.align.currentData(),
                margins={k:w.value() for k,w in self.margins.items()},
                headings=[dict(size=s.value(),align=a.currentData(),bold=b.isChecked(),before=bs.value(),after=af.value())
                          for _,s,a,b,bs,af in self.rows[:self.levels.value()]]))

    def live_preview(self):
        try:
            p = self.values()
        except InputError:
            return
        self.paper.show_document(localized_sample(p,self.lang),p,self.lang)

    def submit(self):
        try:
            self.result_preset = self.values()
            parent = self.parent()
            if any(display_name(p,self.lang) == display_name(self.result_preset,self.lang)
                   for i,p in enumerate(parent.items) if self.is_new or i != parent.index):
                raise ValueError(tr(self.lang,"duplicate"))
        except (InputError,ValueError) as e:
            message = tr(self.lang,"invalid") if isinstance(e,InputError) else str(e)
            QMessageBox.warning(self,tr(self.lang,"error"),message)
            return
        self.accept()

