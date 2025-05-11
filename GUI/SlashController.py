
from consts import SLASH_INTERVAL_S
class SlashObject(object):
    def __init__(self):
        super().__init__()
        self.p0 = [0, 0]
        self.p1 = [0, 0]
        self.visible = False

    def create(self, startTime, currentValue, targetDT, targetT):
        if targetDT == 0:
            return
        self.p0[0] = startTime
        self.p0[1] = currentValue
        self.p1[1] = targetT
        flytime = (targetT - currentValue) / targetDT
        self.p1[0] = startTime + flytime
        self.visible = True

    def move(self, direction):
        if direction == "left":
            self.p0[0] -= SLASH_INTERVAL_S
            self.p1[0] -= SLASH_INTERVAL_S
        else:
            self.p0[0] += SLASH_INTERVAL_S
            self.p1[0] += SLASH_INTERVAL_S


    def setVisible(self, visible):
        self.visible = visible


class SlashController(object):
    def __init__(self):
        super().__init__()
        self.slashs = [SlashObject() for i in range(4)]
    def getSlashObjects(self):
        return self.slashs

    def move(self, direction, index):
        self.slashs[index].move(direction)

    def createSlash(self, index, startTime, currentValue, targetDT, targetT):
        self.slashs[index].create(startTime, currentValue, targetDT, targetT)

    def setVisible(self, visible, index):
        self.slashs[index].setVisible(visible)

    def hideAll(self):
        for i in range(4):
            self.slashs[i].setVisible(False)
