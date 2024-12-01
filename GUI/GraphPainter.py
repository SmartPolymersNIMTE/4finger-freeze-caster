# -*- coding:utf-8 -*-
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsLineItem
from PySide6.QtGui import QPen, QColor
from .GraphicView.AGraphicsView import AGraphicsView

class MyLine(QGraphicsLineItem):

    def boundingRect(self):
        rect = super().boundingRect()
        if rect.width() == 0:
            rect.setWidth(0.1)
        if rect.height() == 0:
            rect.setHeight(0.1)
        return rect

class GraphPainter(object):
    def __init__(self, view: AGraphicsView):
        super().__init__()
        self.view = view
        self.scene = view.scene()
        self.linepen = QPen()
        self.linepen.setWidth(0)
        self.pointData = []

    def Reset(self):
        self.pointData.clear()

    def SaveData(self, path):
        with open(path, "wt") as fp:
            fp.write("Disp(mm),Force(N),Temp(C)\n")
            for data in self.pointData:
                fp.write(f"{data[0]},{data[1]},{data[2]}\n")

    def AddData(self, x, y, z):
        self.pointData.append((x, y, z))
        if len(self.pointData) == 1:
            # item = self.scene.addLine(x, y, x, y, self.linepen)
            pass
        else:
            item = MyLine(self.pointData[-2][0], self.pointData[-2][1], x, y)
            item.setPen(self.linepen)
            self.scene.addItem(item)
            self.view.addItemByType("line", item)
            self.view.fitView()