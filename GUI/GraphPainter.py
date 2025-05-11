# -*- coding:utf-8 -*-
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsLineItem
from PySide2.QtGui import QPen, QColor
from PySide2.QtCore import Qt
from .GraphicView.AGraphicsView import AGraphicsView

class MyLine(QGraphicsLineItem):

    def boundingRect(self):
        rect = super().boundingRect()
        if rect.width() == 0:
            rect.setWidth(0.1)
        if rect.height() == 0:
            rect.setHeight(0.1)
        return rect

class DashLine(MyLine):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(x1, y1, x2, y2)
        self.pen = QPen(QColor(30, 30, 30, 200), 0, Qt.DashLine)
        self.pen.setWidth(0)  # linewidth not zooming

        self.setPen(self.pen)

class GraphPainter(object):
    def __init__(self, view: AGraphicsView):
        super().__init__()
        self.view = view
        self.scene = view.scene()
        self.linepen = QPen()
        self.linepen.setWidth(0)
        self.workers = None
        self.slashCtrl = None
        self.pointData = []

    def Reset(self):
        self.pointData.clear()

    def SaveData(self, path):
        with open(path, "wt") as fp:
            fp.write("Disp(mm),Force(N),Temp(C)\n")
            for data in self.pointData:
                fp.write(f"{data[0]},{data[1]},{data[2]}\n")

    def Invalidate(self):
        if not self.workers:
            return
        self.view.clearAllItems()
        slashs = []
        if self.slashCtrl:
            slashs = self.slashCtrl.getSlashObjects()
        for i, worker in enumerate(self.workers):
            tdata = worker.T_data
            if len(tdata) == 0:
                continue
            t0 = tdata[0][0]
            tx = 0
            ty = tdata[0][1]
            if slashs:
                slash = slashs[i]
                if not slash.visible:
                    continue
                item = DashLine(slash.p0[0] - t0, slash.p0[1], slash.p1[0] - t0, slash.p1[1])
                self.scene.addItem(item)
                self.view.addItemByType("slash", item)
            for d in tdata[1:]:
                item = MyLine(tx, ty, d[0] - t0, d[1])
                tx = d[0] - t0
                ty = d[1]
                item.setPen(self.linepen)
                self.scene.addItem(item)
                self.view.addItemByType("line", item)
        self.view.fitView()

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
