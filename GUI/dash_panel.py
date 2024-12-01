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
        self.stable = QToolButton()
        self.stable.setText("恒温")
        self.tlabel = QLabel("测量温度：")
        vlayout = QVBoxLayout()
        buttonlayout = QHBoxLayout()
        vlayout.addWidget(self.tlabel)
        vlayout.addLayout(buttonlayout)
        buttonlayout.addWidget(self.start)
        buttonlayout.addWidget(self.stable)
        self.setLayout(vlayout)

        self.setMaximumWidth(200)

