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
    QLabel

)
from PySide6.QtGui import QBrush, QPen, QColor, QFont, QIcon, QPainter
import main_controller
from .dash_panel import DashChannelPanel
from .GraphicView.AGraphicsView import AGraphicsView
from .GraphPainter import GraphPainter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dash_panels = []
        self._setupUI()


    def _setupUI(self):
        self.setWindowTitle("PID Heater")
        # self.resize(1920, 1080)
        mainWidget = QTabWidget()
        self.setCentralWidget(mainWidget)

        frame1 = QFrame()
        frame2 = QFrame()
        mainWidget.addTab(frame1, "DashBoard")
        mainWidget.addTab(frame2, "Settings")

        # dashboard
        hlayout = QHBoxLayout()
        lvlayout = QVBoxLayout()
        frame1.setLayout(hlayout)
        hlayout.addLayout(lvlayout, 1)
        for i in range(4):
            panel = DashChannelPanel()
            lvlayout.addWidget(panel)
            self.dash_panels.append(panel)

        self.view = AGraphicsView(self)
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        self.painter = GraphPainter(self.view)

        self.view.resetView()
        self.view.initHelperItems()
        self.view.changeAxisMode(0)
        self.view._hMarkline.setAxisLabel("时间 (s)")
        self.view._vMarkline.setAxisLabel("温度 (°C)")
        hlayout.addWidget(self.view, 4)
        # settings

