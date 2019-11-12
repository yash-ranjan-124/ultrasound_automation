import sys
import scipy.io as sio
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
import time
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QRubberBand, QLabel, QWidget
from PyQt5.QtCore import QRect, QPoint, QSize
import cv2


OPENCV_OBJECT_TRACKERS = {
    "csrt": cv2.TrackerCSRT_create,
    "kcf": cv2.TrackerKCF_create,
    "boosting": cv2.TrackerBoosting_create,
    "mil": cv2.TrackerMIL_create,
    "tld": cv2.TrackerTLD_create,
    "medianflow": cv2.TrackerMedianFlow_create,
    "mosse": cv2.TrackerMOSSE_create
}


class VideoCapture(QtWidgets.QWidget):
    def __init__(self, filename, parent):
        super(QtWidgets.QWidget, self).__init__()
        self.cap = cv2.VideoCapture(str(filename))
        self.video_frame = QtWidgets.QLabel()
        parent.layout.addWidget(self.video_frame)
        self.ret, self.cur_frame = self.cap.read()
        self.fps = None
        self.initBB = None
        self.tracker_type = "csrt"
        self.tracker = OPENCV_OBJECT_TRACKERS[self.tracker_type]()
        self.displayFrame()
        self.timer = None

    def nextFrameSlot(self):
        print("next frame")
        ret, frame = self.cap.read()

        self.cur_frame = frame
        self.displayFrame()

    def prevFrameSlot(self):
        print("prev frame")
        if len(self.cur_frame) < 1:
            return
        pos_frame = self.cap.get(cv2.CAP_PROP_POS_FRAMES)
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, pos_frame-1)
        self.ret, self.cur_frame = self.cap.read()
        self.displayFrame()

    def displayFrame(self):
        self.cur_frame = imutils.resize(self.cur_frame, width=500)
        (H, W) = self.cur_frame.shape[:2]
        # check to see if we are currently tracking an object
        if self.initBB is not None:
                # grab the new bounding box coordinates of the object
            (success, box) = self.tracker.update(self.cur_frame)

            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(self.cur_frame, (x, y), (x + w, y + h),
                              (0, 255, 0), 2)

                # update the FPS counter
                self.fps.update()
                self.fps.stop()

                # initialize the set of information we'll be displaying on
                # the frame
                info = [
                    ("Tracker", self.tracker_type),
                    ("Success", "Yes" if success else "No"),
                    ("FPS", "{:.2f}".format(self.fps.fps())),
                    ("Cords", "("+str(x)+","+str(y)+")")
                ]
        else:
            info = [
                ("Tracker", self.tracker_type),
                ("Success",  "No"),
                ("FPS", 0),
                ("Cords", "N/A")
            ]

        for (i, (k, v)) in enumerate(info):
            text = "{}: {}".format(k, v)
            cv2.putText(self.cur_frame, text, (10, H - ((i * 20) + 20)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

        img = QtGui.QImage(
            self.cur_frame, self.cur_frame.shape[1], self.cur_frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(10000.0/30)

    def pause(self):
        self.timer.stop()

    def deleteLater(self):
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()

    def selectCords(self):
        if self.timer and len(self.cur_frame) > 0:
            self.pause()
            self.rubberband = QRubberBand(QRubberBand.Rectangle, self)
            self.video_frame.mousePressEvent = self.mousePressEvent
            self.video_frame.mouseMoveEvent = self.mouseMoveEvent
            self.video_frame.mouseReleaseEvent = self.mouseReleaseEvent
            self.video_frame.setMouseTracking(True)
            print("init bb")
            print(self.initBB)

        # # start OpenCV object tracker using the supplied bounding box
        #     # coordinates, then start the FPS throughput estimator as well
        #     self.tracker.init(self.cur_frame, self.initBB)
        #     self.fps = FPS().start()
    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(
            QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, event.pos()).normalized())
        QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            selected = []
            rect = self.rubberband.geometry()
            for child in self.findChildren(QtGui.QPushButton):
                if rect.intersects(child.geometry()):
                    selected.append(child)
            print('Selection Contains:\n '),
            if selected:
                print('  '.join(
                    'Button: %s\n' % child.text() for child in selected))
            else:
                print(' Nothing\n')
        QWidget.mouseReleaseEvent(self, event)
        # self.tracker.init(self.cur_frame, self.initBB)
        self.fps = FPS().start()
        self.start()


class VideoDisplayWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(VideoDisplayWidget, self).__init__(parent)

        self.layout = QtWidgets.QFormLayout(self)

        self.startButton = QtWidgets.QPushButton('Start', parent)
        self.startButton.clicked.connect(parent.startCapture)

        self.pauseButton = QtWidgets.QPushButton('Pause', parent)

        self.nextButton = QtWidgets.QPushButton('Next Frame', parent)

        self.prevButton = QtWidgets.QPushButton('Prev Frame', parent)

        self.selectCordsButton = QtWidgets.QPushButton('Select Cords', parent)

        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.pauseButton)
        self.layout.addWidget(self.nextButton)
        self.layout.addWidget(self.prevButton)
        self.layout.addWidget(self.selectCordsButton)

        self.setLayout(self.layout)


class ControlWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(50, 50, 800, 600)
        self.setWindowTitle("PyTrack")

        self.capture = None

        self.matPosFileName = None
        self.videoFileName = None
        self.positionData = None
        self.updatedPositionData = {'red_x': [], 'red_y': [
        ], 'green_x': [], 'green_y': [], 'distance': []}
        self.updatedMatPosFileName = None

        self.isVideoFileLoaded = False
        self.isPositionFileLoaded = False

        self.quitAction = QtWidgets.QAction("&Exit", self)
        self.quitAction.setShortcut("Ctrl+Q")
        self.quitAction.setStatusTip('Close The App')
        self.quitAction.triggered.connect(self.closeApplication)

        self.openVideoFile = QtWidgets.QAction("&Open Video File", self)
        self.openVideoFile.setShortcut("Ctrl+Shift+V")
        self.openVideoFile.setStatusTip('Open .h264 File')
        self.openVideoFile.triggered.connect(self.loadVideoFile)

        self.mainMenu = self.menuBar()
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(self.openVideoFile)
        self.fileMenu.addAction(self.quitAction)

        self.videoDisplayWidget = VideoDisplayWidget(self)
        self.setCentralWidget(self.videoDisplayWidget)

    def startCapture(self):
        if self.capture and self.isVideoFileLoaded:
            self.capture.start()

    def endCapture(self):
        self.capture.deleteLater()
        self.capture = None

    def loadVideoFile(self):
        try:
            self.videoFileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                                       '/Users/yashasvi.ranjan/ultra', "Video files (*.mp4 *.mpgev)")[0]
            self.isVideoFileLoaded = True
            if not self.capture and self.isVideoFileLoaded:
                self.capture = VideoCapture(
                    self.videoFileName, self.videoDisplayWidget)
                self.videoDisplayWidget.pauseButton.clicked.connect(
                    lambda: self.capture.pause())
                self.videoDisplayWidget.nextButton.clicked.connect(
                    lambda: self.capture.nextFrameSlot())
                self.videoDisplayWidget.prevButton.clicked.connect(
                    lambda: self.capture.prevFrameSlot())
                self.videoDisplayWidget.selectCordsButton.clicked.connect(
                    lambda: self.capture.selectCords())

        except:
            print("Please select a video file")

    def closeApplication(self):
        choice = QtWidgets.QMessageBox.question(
            self, 'Message', 'Do you really want to exit?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if choice == QtWidgets.QMessageBox.Yes:
            print("Closing....")
            sys.exit()
        else:
            pass


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = ControlWindow()
    window.show()
    sys.exit(app.exec_())
