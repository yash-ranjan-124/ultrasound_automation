import sys
import cv2
import time
from PyQt5 import QtGui, QtCore
# , QCoreApplication, QObject, QRunnable, QThreadPool
from PyQt5.QtCore import QThread, Qt, pyqtSignal, QRect
# , QPushButton, QAction, QMessageBox
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QLabel
from PyQt5.QtGui import QImage, QPixmap, QPainter, QBrush, QColor


vid_path = './race.mp4'


class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(vid_path)
        # ii=0
        while True:
            ret, frame = cap.read()
            #print (ii)
            #ii +=1
            # cv2.waitKey(50)
            time.sleep(0.05)
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QtGui.QImage(
                    rgbImage.data, w, h, bytesPerLine, QtGui.QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class App(QWidget):
    def __init__(self):
        super().__init__()
        [...]
        self.setWindowTitle('OFVAT')
        self.setGeometry(50, 50, 1800, 1200)
        # create a label
        self.label = QLabel(self)
        self.label.move(280, 120)
        self.label.resize(640, 480)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        self.initUI()

    # @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def initUI(self):
        th = Thread(self)
        th.changePixmap.connect(self.setImage)
        th.start()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))
        qp.setBrush(br)
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        self.begin = event.pos()
        self.end = event.pos()
        self.update()


if __name__ == "__main__":  #
    app = QApplication(sys.argv)
    Gui = App()
    Gui.show()
    sys.exit(app.exec_())
