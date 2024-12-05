# -*- coding:utf-8 -*-
from PySide6.QtCore import QFile, QRectF, QPointF
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QGraphicsScene,
    QFileDialog,
    QTreeView,
    QDialog,
    QMessageBox,
    QFrame,
    QTabWidget,
    QGridLayout,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QToolButton,
    QPushButton

)

class DashChannelPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("DashChannelPanel{border-style: solid; border-width: 1px;}")
        self.start = QToolButton()
        self.start.setText("开始")
        self.start.setStyleSheet("QToolButton{font: bold; color: #f01010}")
        self.start.setCheckable(True)
        self.stable = QToolButton()
        self.stable.setText("恒温")
        self.stable.setStyleSheet("QToolButton{font: bold; color: #106010}")
        self.stable.setCheckable(True)
        tlabel = QLabel("测量温度")
        tlabel.setStyleSheet("QLabel{font: normal 25px; color: #f04040}")
        self.tdata = QLabel()
        vlayout = QVBoxLayout()
        buttonlayout = QHBoxLayout()
        tlayout = QHBoxLayout()
        tlayout.addWidget(tlabel)
        tlayout.addWidget(self.tdata)
        setlayout = QHBoxLayout()
        setlayout.addWidget(QLabel("设定温度"))
        self.tsetdata = QLabel()
        self.powerdata = QLabel()
        setlayout.addWidget(self.tsetdata)
        setlayout.addWidget(QLabel("输出功率"))
        setlayout.addWidget(self.powerdata)

        vlayout.addLayout(tlayout)
        vlayout.addLayout(setlayout)
        vlayout.addLayout(buttonlayout)
        buttonlayout.addWidget(self.start)
        buttonlayout.addWidget(self.stable)
        self.setLayout(vlayout)

        self.setMaximumWidth(200)

        self.start.clicked.connect(self.OnStart)
        self.stable.clicked.connect(self.OnStable)

    def OnStart(self):
        if self.start.isChecked():
            if self.stable.isChecked():
                self.stable.setChecked(False)

    def OnStable(self):
        if self.stable.isChecked():
            if self.start.isChecked():
                self.start.setChecked(False)


class SettingChannelPanel(QFrame):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("SettingChannelPanel{border-style: solid; border-width: 1px;}")
        layout = QGridLayout()
        self.setLayout(layout)

        self.save = QPushButton("保存")
        self.stableT = QLineEdit()
        self.dT = QLineEdit()
        self.targetT = QLineEdit()
        self.P = QLineEdit()
        self.I = QLineEdit()
        self.D = QLineEdit()

        layout.addWidget(QLabel("初始恒温温度"), 1, 1, 1, 1)
        layout.addWidget(self.stableT, 1, 2, 1, 1)
        layout.addWidget(QLabel("变温速率"), 1, 3, 1, 1)
        layout.addWidget(self.dT, 1, 4, 1, 1)
        layout.addWidget(self.save, 1, 5, 1, 4)

        layout.addWidget(QLabel("目标温度"), 2, 1, 1, 1)
        layout.addWidget(self.targetT, 2, 2, 1, 1)
        layout.addWidget(QLabel("P"), 2, 3, 1, 1)
        layout.addWidget(self.P, 2, 4, 1, 1)
        layout.addWidget(QLabel("I"), 2, 5, 1, 1)
        layout.addWidget(self.I, 2, 6, 1, 1)
        layout.addWidget(QLabel("D"), 2, 7, 1, 1)
        layout.addWidget(self.D, 2, 8, 1, 1)
