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
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QLabel,
    QToolButton

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

