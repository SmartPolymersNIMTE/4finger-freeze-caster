from typing import List

from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QDialog


class setAxesPopUp(QDialog):
    def __init__(self, column_candidates: List[str]):
        super().__init__()
        file = QFile("Axes.ui")
        file.open(QFile.ReadOnly)
        file.close()
        loader = QUiLoader()
        self.ui = loader.load(file)
        self.propList = self.columnCandidateFilter(column_candidates)
        self.ui.x_n.addItems(self.propList)
        self.ui.x_d.addItems(self.propList)
        self.ui.y_n.addItems(self.propList)
        self.ui.y_d.addItems(self.propList)
        self.newX = None
        self.newY = None
        self.ui.buttonBox.accepted.connect(self.passingInfo)
        self.ui.buttonBox.rejected.connect(self.close)

    def exec_(self):
        return self.ui.exec_()

    def passingInfo(self):
        #here read users input and bring back the info of x and y axes
        #n stands for numerator, d stands for denominator
        x_n = self.ui.x_n.currentText()
        y_n = self.ui.y_n.currentText()
        x_d = self.ui.x_d.currentText()
        y_d = self.ui.y_d.currentText()
        # Default handle empty exp_box to be 1.
        # TODO(kaiyang): newX and newY should be Latex str.
        self.newX = [x_n, int(self.ui.x_nExp.text()) if self.ui.x_nExp.text() else 1,
                     x_d, int(self.ui.x_nExp.text()) if self.ui.x_nExp.text() else 1]
        self.newY = [y_n, int(self.ui.x_nExp.text()) if self.ui.x_nExp.text() else 1,
                     y_d, int(self.ui.x_nExp.text()) if self.ui.x_nExp.text() else 1]

    def returnNewXY(self):
        # Return None if the user provides no information.
        if self.newX:
            return [self.newX, self.newY]
        else:
            return None

    @staticmethod
    def columnCandidateFilter(candidates: List[str]):
        updatedcandidates = []
        for candidate in candidates:
            simcandidate = candidate.split("_")[0]
            if simcandidate not in updatedcandidates:
                if simcandidate.lower() != "color":
                    updatedcandidates.append(simcandidate)
        return updatedcandidates
