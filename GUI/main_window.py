# -*- coding:utf-8 -*-
import os
import json
from PySide6.QtCore import QFile, QRectF, QPointF, QTimer
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
    QPushButton

)
from PySide6.QtGui import QBrush, QPen, QColor, QFont, QIcon, QPainter
import main_controller
from .panels import DashChannelPanel, SettingChannelPanel
from .GraphicView.AGraphicsView import AGraphicsView
from .GraphPainter import GraphPainter
from consts import QT_UPDATE_INTERVAL_MS, CONFIG_FILE_NAME
from functools import partial

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dash_panels = []
        self.settings = []
        self.config = {}
        self.LoadConfig()
        self._setupUI()
        self._InitController()

    def _InitController(self):
        main_controller.Init_workers(4)
        self.workers = main_controller.g_workers
        self.updatetimer = QTimer()
        self.updatetimer.setInterval(QT_UPDATE_INTERVAL_MS)
        self.updatetimer.timeout.connect(self.onTimer)
        self.updatetimer.start()
        self.painter.workers = self.workers

    def SaveConfig(self):
        with open(CONFIG_FILE_NAME, "w") as fp:
            json.dump(self.config, fp, indent=2)

    def LoadConfig(self):
        if not os.path.exists(CONFIG_FILE_NAME):
            self.SaveConfig()
        else:
            with open(CONFIG_FILE_NAME) as fp:
                self.config = json.load(fp)

    def onTimer(self):
        self.painter.Invalidate()
        for i in range(4):
            self.dash_panels[i].SetMeasureData(self.workers[i])

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
            if str(i) in self.config:
                panel.SetTData(self.config[str(i)])
            panel.start.clicked.connect(partial(self.onStart, i))
            panel.stable.clicked.connect(partial(self.onStable, i))

        self.clearBtn = QPushButton("清屏")
        self.clearBtn.clicked.connect(self.onClear)
        lvlayout.addWidget(self.clearBtn)

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
        slayout = QVBoxLayout()
        frame2.setLayout(slayout)
        for i in range(4):
            settingpanel = SettingChannelPanel()
            self.settings.append(settingpanel)
            slayout.addWidget(settingpanel)
            if str(i) in self.config:
                settingpanel.SetData(self.config[str(i)])
            settingpanel.save.clicked.connect(partial(self.onSave, i))

    def onClear(self):
        pass

    def onStart(self, index):
        worker = self.workers[index]
        if self.dash_panels[index].start.isChecked():
            self.workers[index].start_decend()
        else:
            worker.stop()

    def onStable(self, index):
        worker = self.workers[index]
        if self.dash_panels[index].stable.isChecked():
            self.workers[index].start_stable()
        else:
            worker.stop()

    def onSave(self, index):
        data = self.settings[index].GetData()
        self.dash_panels[index].SetData(data)
        self.config.setdefault(str(index), {}).update(data)
        self.SaveConfig()
        self.setWorkerParams(self.workers[index], data)

    def setWorkerParams(self, worker, data):
        try:
            worker.set_pid_params(float(data["p"]), float(data["i"]), float(data["d"]))
            worker.target_T = float(data["targetT"])
            worker.target_dT = float(data["dT"])
            worker.initial_T = float(data["stableT"])
        except:
            print("Param error:", data)

    def closeEvent(self, event):
        main_controller.Stop_workers()
        return super().closeEvent(event)
