# -*- coding:utf-8 -*-
import PySide6.QtGui
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsTextItem, QGraphicsItem, QGraphicsEllipseItem, QMenu
from PySide6.QtCore import QPointF, QRectF, Qt, QPoint
from PySide6.QtGui import QTransform, QAction
from .AxisObjects import MarkLine, VerticalMarkLine, VShadowMarkLine, HShadowMarkLine, IndicatorLines, MARKTRACK_MODE_LINEAR, MARKTRACK_MODE_LOGSCALE, TICKMARK_BAR_HEIGHT, TICKMARK_BAR_WIDTH
import math

FIT_EXPAND_MARGIN_RATIO = 0.1


class FDViewModel(object):
    def __init__(self):
        super().__init__()
        self.view = None
        self._data = None

    def bindView(self, view):
        self.view = view

    def setData(self, data):
        self._data = data
        if not self.view or not self.view.scene():
            return



class AGraphicsView(QGraphicsView):
    ITEM_TYPE_HULL = "Hull"
    ITEM_TYPE_ELLIPSE = "Ellipse"
    ITEM_TYPE_HULLLABEL = "HullLabel"
    ITEM_TYPE_ELLIPSELABEL = "EllipseLabel"
    ITEM_TYPE_SELECTION_LINE = "SelectionLine"

    def __init__(self, parent):
        super(AGraphicsView, self).__init__(parent)
        # initialize
        self.h_ViewScale = 100.0
        self.v_ViewScale = 100.0
        self.currentzvalue = 1
        self.h_scaleValue = math.log(self.h_ViewScale)
        self.v_scaleValue = math.log(self.v_ViewScale)
        self.axisMode = MARKTRACK_MODE_LOGSCALE
        self.rightDrag = False

        self.viewPosInScene = self.initPos
        self.lastViewPosInScene = self.initPos
        self.lastPos = QPointF(0, 0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._indicator = self._hMarkline = self._vMarkline = self._hsMarkline = self._vsMarkline = None

        self.graphicItems = []
        self.typedGraphicItems = {}

        self.altPressed = False
        self.ctrlPressed = False
        self.shiftPressed = False
        self.setFixedSize(800, 600)

    def setAxisLabel(self, xlabel, ylabel):
        if self._hMarkline:
            self._hMarkline.setAxisLabel(xlabel)
            self._vMarkline.setAxisLabel(ylabel)
            self.update()

    def addItemByType(self, itemtype: str, item: QGraphicsItem):
        """
        add item by type, in order to manage(clear) by type
        :param itemtype: type, a string, like AGraphicsView.ITEM_TYPE_HULL
        :param item: QGraphicsItem
        :return:
        """
        items = self.typedGraphicItems.setdefault(itemtype, [])
        items.append(item)

    def setItemVisibleByType(self, itemtype: str, visible=True):
        if itemtype in self.typedGraphicItems:
            for item in self.typedGraphicItems[itemtype]:
                if visible:
                    item.show()
                else:
                    item.hide()

    def clearItemByType(self, itemtype: str):
        if itemtype in self.typedGraphicItems:
            for item in self.typedGraphicItems[itemtype]:
                self.scene().removeItem(item)
            self.typedGraphicItems.pop(itemtype)

    def clearAllItems(self):
        for vlist in self.typedGraphicItems.values():
            for item in vlist:
                self.scene().removeItem(item)
        self.typedGraphicItems.clear()

    def changeAxisMode(self, mode):
        self.axisMode = mode
        if self._hMarkline:
            self._hMarkline.setAxisMode(mode)
            self._vMarkline.setAxisMode(mode)
            self._hsMarkline.setAxisMode(mode)
            self._vsMarkline.setAxisMode(mode)
            self._indicator.setAxisMode(mode)
            self.refreshMarks()

    def initHelperItems(self):
        self._hMarkline = MarkLine(self)
        self._vMarkline = VerticalMarkLine(self)
        self._hsMarkline = HShadowMarkLine(self)
        self._vsMarkline = VShadowMarkLine(self)
        self._indicator = IndicatorLines(self)

        self.scene().addItem(self._indicator)
        self.scene().addItem(self._hMarkline)
        self.scene().addItem(self._vMarkline)
        self.scene().addItem(self._hsMarkline)
        self.scene().addItem(self._vsMarkline)

    @property
    def initPos(self):
        return QPointF(0, 0)

    def mousePressEvent(self, mouseEvent):
        if mouseEvent.button() == Qt.LeftButton:
            pass
        elif mouseEvent.button() == Qt.MiddleButton:
            pass
        elif mouseEvent.button() == Qt.RightButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.lastPos = mouseEvent.pos()
            self.rightDrag = False

        return super(AGraphicsView, self).mousePressEvent(mouseEvent)

    def getViewRect(self):
        # todo: performance bottleneck
        return self.mapToScene(self.rect()).boundingRect()

    def keyPressEvent(self, event:PySide6.QtGui.QKeyEvent):
        if event.key() == PySide6.QtCore.Qt.Key_Control:
            self.ctrlPressed = True
        elif event.key() == PySide6.QtCore.Qt.Key_Alt:
            self.altPressed = True
        elif event.key() == PySide6.QtCore.Qt.Key_Shift:
            self.shiftPressed = True
    def keyReleaseEvent(self, event:PySide6.QtGui.QKeyEvent):
        if event.key() == PySide6.QtCore.Qt.Key_Control:
            self.ctrlPressed = False
        elif event.key() == PySide6.QtCore.Qt.Key_Alt:
            self.altPressed = False
        elif event.key() == PySide6.QtCore.Qt.Key_Shift:
            self.shiftPressed = False

    def mouseMoveEvent(self, mouseEvent):
        mousePos = QPointF(mouseEvent.pos())
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.rightDrag = True
            diffvec = QPointF(self.lastPos) - mousePos
            diffvec.setY(-diffvec.y() / self.v_ViewScale)
            diffvec.setX(diffvec.x() / self.h_ViewScale)
            self.viewPosInScene = self.lastViewPosInScene + diffvec

            self.resetSceneRect()
        if self._indicator:
            self._indicator.onHoverChanged(self.mapToScene(mousePos.x(), mousePos.y()))
        return super(AGraphicsView, self).mouseMoveEvent(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        mousePos = mouseEvent.pos()
        self.setDragMode(QGraphicsView.NoDrag)
        self.lastViewPosInScene = self.viewPosInScene
        if mouseEvent.button() == Qt.LeftButton and self.ctrlPressed:
            items = self.items(mousePos)
            hititems = []
            for item in items:
                if isinstance(item, QGraphicsEllipseItem) or isinstance(item, QGraphicsTextItem):
                    hititems.append(item)
                    # item.setZValue(self.currentzvalue)
                    # self.currentzvalue += 0.01
                    # break
            menu = QMenu()
            for item in hititems:
                if not hasattr(item, "name"):
                    continue
                action = QAction(item.name, self)
                def ontriggered():
                    item.setZValue(self.currentzvalue)
                    self.currentzvalue += 0.01
                action.triggered.connect(ontriggered)
                menu.addAction(action)
                print("action", item.name)
            menu.exec_(self.mapToGlobal(mousePos))
        return super(AGraphicsView, self).mouseReleaseEvent(mouseEvent)

    def wheelEvent(self, mouseEvent: PySide6.QtGui.QWheelEvent):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            return
        if self.shiftPressed and self.altPressed:
            return
        angleDelta = mouseEvent.angleDelta()
        delta = angleDelta.x() + angleDelta.y()
        if not self.altPressed:
            self.v_scaleValue += delta * 0.002
            self.v_scaleValue = max(- 25, min(10.0, self.v_scaleValue))
        if not self.shiftPressed:
            self.h_scaleValue += delta * 0.002
            self.h_scaleValue = max(- 25, min(10.0, self.h_scaleValue))

        v_oldScale = self.v_ViewScale
        h_oldScale = self.h_ViewScale
        self.h_ViewScale = math.exp(self.h_scaleValue)
        self.v_ViewScale = math.exp(self.v_scaleValue)
        # if self.scene():  # 通知scene
        #     self.scene().onViewScale(self.viewScale)
        v_scale = self.v_ViewScale / v_oldScale
        h_scale = self.h_ViewScale / h_oldScale

        mousePos = self.mapToScene(mouseEvent.position().toPoint())
        vec = QPointF(self.viewPosInScene - mousePos)
        vec.setY(vec.y() / v_scale)
        vec.setX(vec.x() / h_scale)
        self.lastViewPosInScene = self.viewPosInScene = mousePos + vec

        self.onScaleUpdated()

        return super(AGraphicsView, self).wheelEvent(mouseEvent)

    def onScaleUpdated(self):
        self.resetSceneRect()

        self.refreshMarks()

    def setRange(self, xmin, xmax, ymin, ymax):
        # todo: convert data to range
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        if self.axisMode == MARKTRACK_MODE_LOGSCALE:
            xmin = MarkLine.log2lin(xmin)
            xmax = MarkLine.log2lin(xmax)
            ymin = MarkLine.log2lin(ymin)
            ymax = MarkLine.log2lin(ymax)
        xmin -= (xmax - xmin) * TICKMARK_BAR_WIDTH / width
        ymin -= (ymax - ymin) * TICKMARK_BAR_HEIGHT / height
        self.viewPosInScene.setX((xmin + xmax) * 0.5)
        self.viewPosInScene.setY((ymin + ymax) * 0.5)
        self.lastViewPosInScene = self.viewPosInScene
        rect = self.rect()
        self.h_ViewScale = rect.width() / (xmax - xmin)
        self.v_ViewScale = rect.height() / (ymax - ymin)
        self.v_scaleValue = math.log(self.v_ViewScale)
        self.h_scaleValue = math.log(self.h_ViewScale)

        self.onScaleUpdated()

    def fitView(self):
        if not self.typedGraphicItems:
            self.resetView()
            return
        originrect = self.rect()
        rect = QRectF()
        for itemtype in self.typedGraphicItems:
            for item in self.typedGraphicItems[itemtype]:
                if isinstance(item, QGraphicsTextItem):
                    continue
                bb = item.boundingRect()
                rect = rect.united(bb)
        # if rect.width() < rect.height():
        #     rect.setWidth(rect.height())
        # else:
        #     rect.setHeight(rect.width())
        widthoffset = rect.width() * TICKMARK_BAR_WIDTH / originrect.width()
        heightoffset = rect.height() * TICKMARK_BAR_HEIGHT / originrect.height()
        rect.setLeft(rect.left() - widthoffset)
        rect.setWidth(rect.width() + widthoffset)
        rect.setTop(rect.top() - heightoffset)
        rect.setHeight(rect.height() + heightoffset)
        widthmargin = rect.width() * FIT_EXPAND_MARGIN_RATIO
        rect.setWidth(rect.width() + widthmargin)
        rect.setHeight(rect.height() + widthmargin)
        rect.setTop(rect.top() - widthmargin * 0.8)
        rect.setLeft(rect.left() - widthmargin * 0.8)
        self.v_ViewScale = originrect.height() / rect.height()
        self.h_ViewScale = originrect.width() / rect.width()
        self.v_scaleValue = math.log(self.v_ViewScale)
        self.h_scaleValue = math.log(self.h_ViewScale)
        self.viewPosInScene = self.lastViewPosInScene = QPointF((rect.left() + rect.right()) * 0.5,
                                                                (rect.top() + rect.bottom()) * 0.5)
        self.resetSceneRect()

    def resetView(self):
        self.v_ViewScale = 100.0
        self.h_ViewScale = 100.0
        self.currentzvalue = 1
        self.h_scaleValue = math.log(self.h_ViewScale)
        self.v_scaleValue = math.log(self.v_ViewScale)
        self.viewPosInScene = self.initPos
        self.lastViewPosInScene = self.initPos
        self.lastPos = QPointF(0, 0)

        self.resetSceneRect()

    def refreshMarks(self):
        # 刷新显示区域
        if self._hMarkline:
            self._hMarkline.setViewScale(self.v_ViewScale, self.h_ViewScale)
            self._vMarkline.setViewScale(self.v_ViewScale, self.h_ViewScale)
            self._hsMarkline.setViewScale(self.v_ViewScale, self.h_ViewScale)
            self._vsMarkline.setViewScale(self.v_ViewScale, self.h_ViewScale)
            self._indicator.setViewScale(self.v_ViewScale, self.h_ViewScale)

            self._hMarkline.update()
            self._vMarkline.update()
            self._hsMarkline.update()
            self._vsMarkline.update()
            self._indicator.update()

    def setIndicatorVisible(self, visible):
        if self._indicator:
            if visible:
                self._indicator.show()
            else:
                self._indicator.hide()

    def resetSceneRect(self):
        rect = self.rect()
        width = rect.width() / self.h_ViewScale

        height = rect.height() / self.v_ViewScale

        rect = QRectF(self.viewPosInScene.x() - width / 2.0, self.viewPosInScene.y() - height / 2.0, width, height)
        # self.scene().setScale(self.viewScale)
        self.setSceneRect(rect)

        trans = QTransform()
        trans.scale(self.h_ViewScale, -self.v_ViewScale)
        self.setTransform(trans)
        # for item in self.graphicItems:
        #     if isinstance(item, QGraphicsTextItem):
        #         item.setScale(1.0 / self.viewScale)
        self.scene().update()
        self.refreshMarks()
