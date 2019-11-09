import cv2
import numpy as np
from PyQt5 import QtGui, QtCore, QtWidgets


class Capture():
    def __init__(self, filename, parent):
        self.capturing = False
        self.c = cv2.VideoCapture(str(filename))
        self.video_frame = QtWidgets.QLabel()
        self.video_frame.move(200, 100)
        parent.video_layout.addWidget(self.video_frame)
        self.timer = QtCore.QTimer()

    def startCapture(self):
        print("pressed start")
        self.capturing = True
        cap = self.c
        self.start()
        # while(self.capturing):
        #     ret, frame = cap.read()
        #     cv2.imshow("Capture", frame)
        #     cv2.waitKey(5)
        # cap.release()
        # cv2.destroyAllWindows()

    def nextFrameSlot(self):
        print("next frame")
        ret, frame = self.c.read()
        print(frame.shape)
        # frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # CV_BGR2RGB
        img = QtGui.QImage(
            frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def prevFrameSlot(self):
        print("prev frame")
        ret, frame = self.c.read()
        frame = frame - 1
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # CV_BGR2RGB
        img = QtGui.QImage(
            frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def start(self):
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(10000.0/30)

    def endCapture(self):
        print("pressed End")
        self.capturing = False

        # cv2.destroyAllWindows()

    def pauseCapture(self):
        print("pressed paused")
        cap = self.c
        self.capturing = False
        self.timer.stop()

    def quitCapture(self):
        print("pressed Quit")
        if self.c:
            cap = self.c
            self.capturing = False
            cap.release()
        cv2.destroyAllWindows()
        QtCore.QCoreApplication.quit()


class VideoDisplayWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.video_layout = QtWidgets.QVBoxLayout(self)
        # self.video_layout.addWidget(self.video_frame)
        # self.video_frame_title = QtWidgets.QPushButton('Video Player', parent)
        # self.video_frame_title2 = QtWidgets.QPushButton(
        #     'Video Player2', parent)

        self.toolbar_layout = QtWidgets.QHBoxLayout(self)
        self.loadFileButton = QtWidgets.QPushButton('Load Files')
        self.loadFileButton.clicked.connect(
            lambda: self.onFileLoadHandler(parent))

        self.startButton = QtWidgets.QPushButton('Start', parent)

        self.pauseButton = QtWidgets.QPushButton('Pause', parent)

        self.end_button = QtWidgets.QPushButton('End', parent)

        self.quit_button = QtWidgets.QPushButton('Quit', parent)

        self.next_frame_button = QtWidgets.QPushButton('Next Frame', parent)

        self.prev_frame_button = QtWidgets.QPushButton('Prev Frame', parent)

        self.draw_selector_button = QtWidgets.QPushButton(
            'Draw Selector', parent)

        self.get_sel_cords_btn = QtWidgets.QPushButton(
            'Get Selector Cordinates', parent)

        self.toolbar_layout.addWidget(self.loadFileButton)
        self.toolbar_layout.addWidget(self.startButton)
        self.toolbar_layout.addWidget(self.pauseButton)
        self.toolbar_layout.addWidget(self.end_button)
        self.toolbar_layout.addWidget(self.quit_button)
        self.toolbar_layout.addWidget(self.next_frame_button)
        self.toolbar_layout.addWidget(self.prev_frame_button)
        self.toolbar_layout.addWidget(self.draw_selector_button)
        self.toolbar_layout.addWidget(self.get_sel_cords_btn)
        self.main_layout.addChildLayout(self.toolbar_layout)
        self.main_layout.addChildLayout(self.video_layout)
        self.main_layout.stretch(1)

    def onFileLoadHandler(self, parent):
        print(parent)
        self.videoFileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                                   '/Users/yashasvi.ranjan/ultra', "Video files (*.mp4 *.mpgev)")
        self.isVideoFileLoaded = True
        print(self.videoFileName)
        parent.capture = Capture(self.videoFileName[0], self)
        print(parent.capture)
        self.addButtonHandlers(parent)

    def addButtonHandlers(self, parent):
        self.startButton.clicked.connect(lambda: parent.capture.startCapture())
        self.pauseButton.clicked.connect(lambda: parent.capture.pauseCapture())
        self.end_button.clicked.connect(lambda: parent.capture.endCapture())
        self.quit_button.clicked.connect(lambda: parent.capture.quitCapture())
        self.next_frame_button.clicked.connect(
            lambda: parent.capture.nextFrameSlot())
        self.prev_frame_button.clicked.connect(
            lambda: parent.capture.prevFrameSlot())
        # self.draw_selector_button.clicked.connect(
        #     lambda: self.capture.draw_selector)
        # self.get_sel_cords_btn.clicked.connect(
        #     lambda: parent.capture.get_selector_cords)


class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Control Panel')
        self.capture = None
        self.videoDisplayWidget = VideoDisplayWidget(self)
        # self.setCentralWidget(self.videoDisplayWidget)
        self.setGeometry(400, 400, 950, 550)
        self.show()


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec_())
