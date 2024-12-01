# -*- coding:utf-8 -*-
# @ModuleName: AxisObjects

from PySide6.QtWidgets import QGraphicsObject, QGraphicsItem, QGraphicsTextItem
from PySide6.QtGui import QBrush, QPen, QColor, QFont, QPolygonF
from PySide6.QtCore import QLineF, QPointF, QRectF, Qt
import math

MARKTRACK_MODE_LINEAR = 0
MARKTRACK_MODE_LOGSCALE = 1

MARKTRACK_HEIGHT = 40  # 刻度条的高度

# 画布的宽度:
SCENE_WIDTH = 600
SCENE_HEIGHT = 400
# 时间刻度条的背景色:
MARKTRACK_BG_COLOR = QColor(255, 255, 255, 255)
# 时间刻度线的颜色:
TICKS_COLOR = QColor(134, 134, 134, 255)
# 刻度文字的颜色:
TICKS_TEXT_COLOR = QColor(0, 0, 0, 255)
# 刻度文字的字体:
TICKS_TEXT_FONT = QFont("Arial", 10)
LABEL_TEXT_FONT = QFont("Arial", 12)
INDICATOR_TEXT_COLOR = QColor(50, 200, 50, 255)

# 刻度线距离scene绘图面板最上方的距离
TICKMARK_BAR_HEIGHT = 50.0
TICKMARK_BAR_WIDTH = TICKMARK_BAR_HEIGHT * 1.5
TICKMARK_HEIGHT = 8

MAJORTICK_HEIGHT = 19.0
MINORTICK_HEIGHT = 10.0

MINOR_TICK_COUNT = 10

# units of linearscale corresponding to logscale
LOGSCALE_UNITS = 1000.0
LINEARSCALE_UNITS = 1000.0
LINEAR_TO_LOG = LINEARSCALE_UNITS / LOGSCALE_UNITS

# 轨道的边框颜色:
TRACK_BORDER_COLOR = QColor("#202020")


class MarkLine(QGraphicsObject):
    """docstring for MarkLine: 刻度线."""
    TEXTANGLE = 0
    MAJORTICK_COLOR = QColor(112, 112, 112, 255)
    MINORTICK_COLOR = QColor(112, 112, 112, 255)

    def __init__(self, view):
        super(MarkLine, self).__init__()
        self.view = view
        self.v_view_scale = 100.0
        self.h_view_scale = 100.0  # 画布缩放倍率
        self.textitem = None
        self._axisMode = MARKTRACK_MODE_LOGSCALE
        self._markTextItem = []
        self._markLines = []
        self._markLinesBold = []
        self._viewRect = None
        self.label = "Axis"
        self.labelitem = QGraphicsTextItem(self)
        self.labelitem.setFont(LABEL_TEXT_FONT)
        self.labelitem.setDefaultTextColor(TICKS_TEXT_COLOR)
        self.labelitem.setZValue(0)
        self.labelitem.setRotation(self.TEXTANGLE)
        self.labelitem.setFlag(QGraphicsItem.ItemIgnoresTransformations)

        # 设置刻度线的颜色:
        self.pen = QPen(QColor(0, 0, 0, 0))
        self.pen.setWidth(0)  # linewidth not zooming
        self.brush = QBrush(MARKTRACK_BG_COLOR, Qt.SolidPattern)

        self.setZValue(200)
        self.setFlags(QGraphicsItem.ItemSendsScenePositionChanges)

    def setAxisLabel(self, label):
        self.label = label

    @property
    def axisMin(self):
        rect = self.view.getViewRect()
        return rect.left() + TICKMARK_BAR_WIDTH / self.h_view_scale

    @property
    def axisMax(self):
        rect = self.view.getViewRect()
        return rect.right()

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        if a < self.axisMin:
            return
        return QLineF(a, rect.top() + (TICKMARK_BAR_HEIGHT - MAJORTICK_HEIGHT) / self.v_view_scale, a,
                      rect.top() + TICKMARK_BAR_HEIGHT / self.v_view_scale)

    def transFormLogMinorCoord(self, a, basea=None, base=None):
        if self._axisMode == MARKTRACK_MODE_LOGSCALE and basea is not None:
            a = math.log10(a + 1) * base + basea
        return a

    def makeMinorLine(self, a, basea=None, base=None):
        rect = self.view.getViewRect()

        a = self.transFormLogMinorCoord(a, basea, base)

        if a < self.axisMin:
            return
        return QLineF(a, rect.top() + (TICKMARK_BAR_HEIGHT - MINORTICK_HEIGHT) / self.v_view_scale, a,
                      rect.top() + TICKMARK_BAR_HEIGHT / self.v_view_scale)

    def makeTextPos(self, a):
        rect = self.view.getViewRect()
        y = rect.top() + (TICKMARK_BAR_HEIGHT *0.7) / self.v_view_scale
        x = a - 20 / self.h_view_scale
        if a < self.axisMin:
            return
        return QPointF(x, y)

    def _generateLogText(self, i, a):
        # add tick texts
        pos = self.makeTextPos(self.log2lin(a))
        if pos:
            if i >= len(self._markTextItem):
                item = QGraphicsTextItem(self)
                item.setFont(TICKS_TEXT_FONT)
                item.setDefaultTextColor(TICKS_TEXT_COLOR)
                item.setZValue(0)
                item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
                self._markTextItem.append(item)
            else:
                item = self._markTextItem[i]
            item.setPos(pos)
            item.setPlainText(self.getMarkText(self.log2lin(a)))
            item.show()

    def calcLogLevel(self, level, maxlog, minlog):
        # maxlog, minlog = self.lin2log(self.axisMax), self.lin2log(self.axisMin)
        base = 10 ** level
        lowborder = base * math.floor(minlog / base)
        if lowborder + 9 * base < minlog:
            return "Stop"
        if lowborder + base > maxlog:
            return "Over"
        for i in range(9):
            if minlog < lowborder + (i + 1) * base < maxlog:
                return lowborder + (i + 1) * base
        return "Continue"

    def drawMajorLogLine(self, startlevel, minlog, maxlog, i, lines):
        base = 10 ** startlevel
        a = math.floor(minlog / base) * base
        if a == 0:
            a = base
        while a < maxlog:
            # calc major ticks
            if minlog < a:
                majorline = self.makeMajorLine(self.log2lin(a))
                if majorline:
                    lines.append(majorline)
                # if main:
                self._generateLogText(i, a)
                i += 1
            a += base
        return i

    def logUpdateMark(self):
        originmaxlog, originminlog = maxlog, minlog = self.lin2log(self.axisMax), self.lin2log(self.axisMin)
        minrange = (originmaxlog - originminlog) * 0.01
        for item in self._markTextItem:
            item.hide()
        lines = []
        maxlogbase = math.log10(maxlog)
        minlogbase = math.log10(minlog)
        maxbase = math.ceil(maxlogbase)
        minbase = math.floor(minlogbase)

        i = 0

        startlevel = math.floor(math.log10(maxlog - minlog))
        ret = self.calcLogLevel(startlevel, maxlog, minlog)
        times = 0
        while ret != "Stop":
            if not isinstance(ret, str):
                i = self.drawMajorLogLine(startlevel, minlog, maxlog, i, lines)
                maxlog = ret
                times += 1
                if times >= 3:
                    break
            startlevel -= 1
            if maxlog - minlog < minrange:
                break
            ret = self.calcLogLevel(startlevel, maxlog, minlog)

        self._markLinesBold = lines

    def linearUpdateMark(self):
        arange = self.axisMax - self.axisMin
        divs = int(arange / 10 ** math.floor(math.log10(arange)))
        # divs: how many major ticks in view
        if divs < 2:
            divs *= 10
            base = 10 ** (math.floor(math.log10(arange)) - 1)
        else:
            base = 10 ** (math.floor(math.log10(arange)))
        # base: 0.1 1 10 100, etc
        lines = []
        minor_lines = []
        i = 0
        # hide all textitem first
        for item in self._markTextItem:
            item.hide()
        a = math.floor(self.axisMin / base) * base
        while a < self.axisMax:
            i += 1
            # calc major ticks
            majorline = self.makeMajorLine(a)
            if majorline:
                lines.append(majorline)
            # calc minor ticks
            if self._axisMode == MARKTRACK_MODE_LINEAR or base > 1:
                for j in range(1, MINOR_TICK_COUNT):
                    mina = a + j * base / MINOR_TICK_COUNT
                    minorline = self.makeMinorLine(mina)
                    if minorline:
                        minor_lines.append(minorline)
            else:
                for j in range(1, MINOR_TICK_COUNT - 1):
                    minorline =self.makeMinorLine(j, a, base)
                    if minorline:
                        minor_lines.append(minorline)
            # add tick texts
            pos = self.makeTextPos(a)
            if pos:
                if i >= len(self._markTextItem):
                    item = QGraphicsTextItem(self)
                    item.setFont(TICKS_TEXT_FONT)
                    item.setDefaultTextColor(TICKS_TEXT_COLOR)
                    item.setZValue(0)
                    item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
                    self._markTextItem.append(item)
                else:
                    item = self._markTextItem[i]
                item.setPos(pos)
                item.setPlainText(self.getMarkText(a))
                item.show()

            a += base

        self._markLinesBold = lines
        self._markLines = minor_lines

    def updateMark(self, force=False):
        # 获取可视区域
        rect = self.view.getViewRect()
        if not force and self._viewRect == rect:
            return
        self._viewRect = rect
        try:
            arange = self.axisMax - self.axisMin
            if self._axisMode == MARKTRACK_MODE_LOGSCALE and arange < LINEAR_TO_LOG * 2:
                self.logUpdateMark()
            else:
                self.linearUpdateMark()

        except OverflowError:
            pass

    @staticmethod
    def lin2log(v):
        return 10 ** (v / LINEAR_TO_LOG)

    @staticmethod
    def log2lin(v):
        return math.log10(v) * LINEAR_TO_LOG

    def getVisualCoord(self, logiccoord):
        if self._axisMode == MARKTRACK_MODE_LINEAR:
            return logiccoord
        else:
            return self.lin2log(logiccoord)

    def getMarkText(self, a):
        return "%g" % self.getVisualCoord(a)

    def setAxisMode(self, mode):
        self._axisMode = mode
        self.updateMark(force=True)
        self.update()

    def paintBackground(self, painter):
        # 背景色
        # self.
        rect = self.boundingRect()
        painter.pen().setWidth(0)
        painter.fillRect(rect, self.brush)

    def paintMinorTick(self, painter):
        # 细刻度线
        pen = QPen(self.MINORTICK_COLOR)
        pen.setWidth(0)
        painter.setPen(pen)
        painter.drawLines(self._markLines)

    def paintMajorTick(self, painter):
        # 粗刻度线
        boldPen = QPen(self.MAJORTICK_COLOR)
        boldPen.setWidth(0)
        painter.setPen(boldPen)
        painter.drawLines(self._markLinesBold)

    def paintBorderLine(self, painter):
        boldPen = QPen(self.MAJORTICK_COLOR)
        boldPen.setWidth(0)
        painter.setPen(boldPen)
        rect = self.boundingRect()
        # 水平线
        painter.drawLine(self.getBorderLine(rect))

    def paint(self, painter, option, widget):
        """绘制刻度线."""
        self.updateMark()

        self.paintBackground(painter)

        self.paintMinorTick(painter)

        self.paintMajorTick(painter)

        self.paintBorderLine(painter)

        self.paintAxisLabel(painter)

    def paintAxisLabel(self, painter):
        rect = self.view.getViewRect()
        x = rect.center().x()
        y = rect.top() + (TICKMARK_BAR_HEIGHT *0.4) / self.v_view_scale
        self.labelitem.setPos(x, y)
        self.labelitem.setPlainText(self.label)
        self.labelitem.show()

    def getBorderLine(self, rect):
        y = float(rect.top()) + TICKMARK_BAR_HEIGHT / self.v_view_scale
        return QLineF(self.axisMin, y, rect.right(), y)

    def boundingRect(self):
        """交互范围."""
        rect = self.view.getViewRect()
        height = TICKMARK_BAR_HEIGHT / self.v_view_scale
        newRect = QRectF(rect.left(), rect.top(), rect.width(), height)
        return newRect

    def getViewScale(self):
        if self.scene() is None:
            return 1.0
        return self.view.getScale()

    def setViewScale(self, v_scale, h_scale):
        self.v_view_scale = v_scale
        self.h_view_scale = h_scale
        self.updateMark()
        self.update()


class VerticalMarkLine(MarkLine):
    TEXTANGLE = -90

    def boundingRect(self):
        """交互范围."""
        rect = self.view.getViewRect()
        width = TICKMARK_BAR_WIDTH / self.h_view_scale
        newRect = QRectF(rect.left(), rect.top(), width, rect.height())
        return newRect

    def getBorderLine(self, rect):
        x = float(rect.left()) + TICKMARK_BAR_WIDTH / self.h_view_scale
        return QLineF(x, self.axisMin, x, rect.bottom())

    def paintAxisLabel(self, painter):
        rect = self.view.getViewRect()
        y = rect.center().y()
        x = rect.left() + (TICKMARK_BAR_WIDTH *0.05) / self.h_view_scale
        self.labelitem.setPos(x, y)
        self.labelitem.setPlainText(self.label)
        self.labelitem.show()

    @property
    def axisMin(self):
        rect = self.view.getViewRect()
        return rect.top() + TICKMARK_BAR_HEIGHT / self.v_view_scale

    @property
    def axisMax(self):
        rect = self.view.getViewRect()
        return rect.bottom()

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        if a < self.axisMin:
            return
        return QLineF(rect.left() + (TICKMARK_BAR_WIDTH - MAJORTICK_HEIGHT) / self.h_view_scale, a,
                      rect.left() + TICKMARK_BAR_WIDTH / self.h_view_scale, a)

    def makeMinorLine(self, a, basea=None, base=None):
        rect = self.view.getViewRect()

        a = self.transFormLogMinorCoord(a, basea, base)
        if a < self.axisMin:
            return
        return QLineF(rect.left() + (TICKMARK_BAR_WIDTH - MINORTICK_HEIGHT) / self.h_view_scale, a,
                      rect.left() + TICKMARK_BAR_WIDTH / self.h_view_scale, a)

    def makeTextPos(self, a):
        rect = self.view.getViewRect()
        x = rect.left() + (TICKMARK_BAR_WIDTH *0.3)/ self.h_view_scale
        y = a + 10 / self.v_view_scale
        if a < self.axisMin:
            return
        return QPointF(x, y)


class IndicatorLines(QGraphicsObject):

    def __init__(self, view):
        super(IndicatorLines, self).__init__()
        self.v_view_scale = 100.0
        self.h_view_scale = 100.0
        self.view = view
        self._viewRect = None
        self._axisMode = MARKTRACK_MODE_LOGSCALE
        self.hoverPos = QPointF(-9999, -9999)
        self.vline = QLineF()
        self.hline = QLineF()
        self.textitem = item = QGraphicsTextItem(self)
        item.setFont(QFont("Arial", 12, 2))
        item.setDefaultTextColor(INDICATOR_TEXT_COLOR)
        item.setZValue(400)
        item.setFlag(QGraphicsItem.ItemIgnoresTransformations)
        item.hide()
        # 设置刻度线的颜色:
        self.pen = QPen(QColor(255, 0, 0, 200), 0, Qt.DashLine)
        self.pen.setWidth(0)  # linewidth not zooming

        self.setZValue(400)
        self.setFlags(QGraphicsItem.ItemSendsScenePositionChanges)

    def setViewScale(self, v_scale, h_scale):
        self.v_view_scale = v_scale
        self.h_view_scale = h_scale
        self.onHoverChanged(self.hoverPos)

    def boundingRect(self):
        """交互范围."""
        rect = self.view.getViewRect()
        return rect

    def setAxisMode(self, mode):
        self._axisMode = mode
        self.onHoverChanged(self.hoverPos)
        self.update()

    def onHoverChanged(self, pos):
        rect = self.view.getViewRect()
        self.hoverPos = pos
        self.vline = QLineF(pos.x(), rect.top(), pos.x(), rect.bottom())
        self.hline = QLineF(rect.left(), pos.y(), rect.right(), pos.y())
        self.textitem.setPos(pos + QPointF(0, - 25 / self.v_view_scale))
        if self._axisMode == MARKTRACK_MODE_LOGSCALE:

            self.textitem.setPlainText("%g, %g" % (10 ** (pos.x()), 10 ** (pos.y())))
        else:
            self.textitem.setPlainText("%g, %g" % (pos.x(), pos.y()))
        self.textitem.show()
        self.update()

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawLine(self.vline)
        painter.drawLine(self.hline)



class HShadowMarkLine(MarkLine):
    MAJORTICK_COLOR = QColor(112, 112, 112, 128)

    def __init__(self, view):
        super(HShadowMarkLine, self).__init__(view)
        self.setZValue(-200)

    def boundingRect(self):
        rect = self.view.getViewRect()
        return rect

    def paint(self, painter, option, widget):
        """绘制刻度线."""
        self.updateMark()

        self.paintMajorTick(painter)

        self.paintBorderLine(painter)

    def paintBorderLine(self, painter):
        boldPen = QPen(QColor(0, 0, 0, 255))
        boldPen.setWidth(0)
        painter.setPen(boldPen)
        rect = self.boundingRect()
        # 水平线
        painter.drawLine(self.getBorderLine(rect))

    def getBorderLine(self, rect):
        y = rect.bottom()
        return QLineF(rect.left(), y, rect.right(), y)

    def paintMajorTick(self, painter):
        # 粗刻度线
        boldPen = QPen(self.MAJORTICK_COLOR, 0, Qt.DotLine)
        # boldPen.setWidth(0)
        painter.setPen(boldPen)
        painter.drawLines(self._markLinesBold)

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        return QLineF(a, rect.top(), a, rect.bottom())


class VShadowMarkLine(HShadowMarkLine):
    @property
    def axisMin(self):
        rect = self.view.getViewRect()
        return rect.top()

    @property
    def axisMax(self):
        rect = self.view.getViewRect()
        return rect.bottom()

    def makeMajorLine(self, a):
        rect = self.view.getViewRect()
        return QLineF(rect.left(), a, rect.right(), a)

    def getBorderLine(self, rect):
        x = float(rect.right() - 3.0 / self.h_view_scale)
        return QLineF(x, rect.top(), x, rect.bottom())