import sys
import scipy.io as sio
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
import time
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
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


class Thread(QThread):
    changePixmap = pyqtSignal(QPixmap)

    def __init__(self, parent, frame):
        super(Thread, self).__init__(parent)
        self.cur_frame = frame
        self.parent = parent

    def run(self):
        print("worker started")
        while True:
            if self.parent.isPaused == False and self.parent.isStarted == True:
                print("frame reader started")
                self.parent.ret, self.parent.cur_frame = self.parent.cap.read()
                if self.parent.cur_frame is None:
                    break

                self.parent.cur_frame = imutils.resize(
                    self.parent.cur_frame, width=500)
                (H, W) = self.cur_frame.shape[:2]
                print(self.parent.cur_frame)
                # check to see if we are currently tracking an object
                if self.parent.initBB is not None:
                    # grab the new bounding box coordinates of the object
                    (success, box) = self.parent.tracker.update(
                        self.parent.cur_frame)

                    # check to see if the tracking was a success
                    if success:
                        (x, y, w, h) = [int(v) for v in box]
                        cv2.rectangle(self.parent.cur_frame, (x, y), (x + w, y + h),
                                      (0, 255, 0), 2)

                        # update the FPS counter
                        self.parent.fps.update()
                        self.parent.fps.stop()

                        # initialize the set of information we'll be displaying on
                        # the frame
                        info = [
                            ("Tracker", self.parent.tracker_type),
                            ("Success", "Yes" if success else "No"),
                            ("FPS", "{:.2f}".format(self.parent.fps.fps())),
                            ("Cords", "("+str(x)+","+str(y)+")")
                        ]

                    for (i, (k, v)) in enumerate(info):
                        text = "{}: {}".format(k, v)
                        cv2.putText(self.parent.cur_frame, text, (10, H - ((i * 20) + 20)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                    # th = Thread(self, self.cur_frame)
                    # th.changePixmap.connect(lambda p: self.setImage(p))
                    # th.start()
                    # show the output frame
                    img = QtGui.QImage(
                        self.parent.cur_frame, self.parent.cur_frame.shape[1], self.parent.cur_frame.shape[0], QtGui.QImage.Format_RGB888)
                    pix = QtGui.QPixmap.fromImage(img)
                    self.changePixmap.emit(pix)
                    self.parent.frame_array.append(self.parent.cur_frame)
                    self.parent.frame_pos = self.parent.frame_pos + 1
                    key = cv2.waitKey(1) & 0xFF
                    # if the 's' key is selected, we are going to "select" a bounding
                    # box to track
                    if key == ord("s"):
                        # select the bounding box of the object we want to track (make
                        # sure you press ENTER or SPACE after selecting the ROI)
                        self.parent.initBB = cv2.selectROI("Frame", self.parent.cur_frame, fromCenter=False,
                                                           showCrosshair=True)

                        # start OpenCV object tracker using the supplied bounding box
                        # coordinates, then start the FPS throughput estimator as well
                        self.parent.tracker.init(
                            self.parent.frame, self.parent.initBB)
                        self.parent.fps = FPS().start()

                    # if the `q` key was pressed, break from the loop
                    elif key == ord("q"):
                        break
                else:
                    break


class VideoCapture(QtWidgets.QWidget):
    def __init__(self, filename, parent):
        super(QtWidgets.QWidget, self).__init__()
        self.cap = cv2.VideoCapture(str(filename))
        self.video_frame = QtWidgets.QLabel()
        parent.layout.addWidget(self.video_frame)
        self.ret, self.cur_frame = self.cap.read()
        print("cur frame init")
        self.frame_array = []
        self.frame_array.append(self.cur_frame)
        self.frame_pos = 0
        self.frame_displayed = None
        self.fps = None
        self.isPaused = True
        self.isStarted = False
        self.initBB = None
        self.tracker_type = "csrt"
        self.tracker = OPENCV_OBJECT_TRACKERS["csrt"]()
        self.displayFrame()

    def nextFrameSlot(self):
        print("next frame")
        self.ret, self.cur_frame = self.cap.read()
        self.frame_array.append(self.cur_frame)
        self.frame_pos = self.frame_pos + 1
        print(self.frame_pos)
        self.displayFrame()

    def prevFrameSlot(self):
        print("prev frame")
        if len(self.cur_frame) < 1:
            return
        if len(self.frame_array) < 1 or self.frame_pos == 0:
            return
        prev_frame_pos = self.frame_pos - 1
        self.cur_frame = self.frame_array[prev_frame_pos]
        self.frame_pos = prev_frame_pos
        print(self.frame_pos)
        self.displayFrame()

    def displayFrame(self):
        print("displaying frame")
        if len(self.cur_frame) < 1:
            return
        else:
            print(self.cur_frame)
            self.cur_frame = imutils.resize(
                self.cur_frame, width=500)
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
                    fps.update()
                    fps.stop()

                    # initialize the set of information we'll be displaying on
                    # the frame
                    info = [
                        ("Tracker", self.tracker_type),
                        ("Success", "Yes" if success else "No"),
                        ("FPS", "{:.2f}".format(self.fps.fps())),
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
            self.setImage(pix)

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.video_frame.setPixmap(image)

    def start(self):
        print("Started")
        self.isPaused = False
        self.isStarted = True
        th = Thread(self, self.cur_frame)
        th.changePixmap.connect(lambda p: self.setImage(p))
        th.start()

    def pause(self):
        # self.timer.stop()
        print("paused..!!")

    def deleteLater(self):
        self.cap.release()
        super(QtGui.QWidget, self).deleteLater()


class VideoDisplayWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(VideoDisplayWidget, self).__init__(parent)

        self.layout = QtWidgets.QFormLayout(self)

        self.startButton = QtWidgets.QPushButton('Start', parent)
        self.startButton.clicked.connect(parent.startCapture)

        self.pauseButton = QtWidgets.QPushButton('Pause', parent)

        self.nextButton = QtWidgets.QPushButton('Next Frame', parent)

        self.prevButton = QtWidgets.QPushButton('Prev Frame', parent)

        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.pauseButton)
        self.layout.addWidget(self.nextButton)
        self.layout.addWidget(self.prevButton)

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
