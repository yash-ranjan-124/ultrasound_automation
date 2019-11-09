import sys
import scipy.io as sio
from imutils.video import VideoStream
from imutils.video import FPS
import imutils
import time
from PyQt5 import QtGui, QtCore, QtWidgets
import cv2


class Tracker():
    def __init__(self, tracker_type, frame):
        OPENCV_OBJECT_TRACKERS = {
            "csrt": cv2.TrackerCSRT_create,
            "kcf": cv2.TrackerKCF_create,
            "boosting": cv2.TrackerBoosting_create,
            "mil": cv2.TrackerMIL_create,
            "tld": cv2.TrackerTLD_create,
            "medianflow": cv2.TrackerMedianFlow_create,
            "mosse": cv2.TrackerMOSSE_create
        }
        self.frame = frame
        self.tracker_type = tracker_type
        self.tracker = OPENCV_OBJECT_TRACKERS[tracker_type]()
        self.initBB = None

    def track(self):
        frame = imutils.resize(self.frame, width=500)
        (H, W) = frame.shape[:2]

        if self.initBB is not None:
            # grab the new bounding box coordinates of the object
            (success, box) = self.tracker.update(frame)

            # check to see if the tracking was a success
            if success:
                (x, y, w, h) = [int(v) for v in box]
                cv2.rectangle(frame, (x, y), (x + w, y + h),
                              (0, 255, 0), 2)

            # update the FPS counter
            self.fps.update()
            self.fps.stop()

            # initialize the set of information we'll be displaying on
            # the frame
            info = [
                ("Tracker",  self.tracker_type),
                ("Success", "Yes" if success else "No"),
                ("FPS", "{:.2f}".format(self.fps.fps())),
            ]
            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            return frame

        key = cv2.waitKey(1) & 0xFF
        # if the 's' key is selected, we are going to "select" a bounding
        # box to track
        if key == ord("s"):
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
            initBB = cv2.selectROI("Frame", frame, fromCenter=False,
                                   showCrosshair=True)

            # start OpenCV object tracker using the supplied bounding box
            # coordinates, then start the FPS throughput estimator as well
            self.tracker.init(frame, self.initBB)
            self.fps = FPS().start()


class VideoCapture(QtWidgets.QWidget):
    def __init__(self, filename, parent):
        super(QtWidgets.QWidget, self).__init__()
        self.cap = cv2.VideoCapture(str(filename))
        self.video_frame = QtWidgets.QLabel()
        parent.layout.addWidget(self.video_frame)
        self.cur_frame = None
        self.fps = None

    def nextFrameSlot(self):
        print("next frame")
        ret, frame = self.cap.read()
        frame = frame
        Tracker("csrt", frame).track()

        self.cur_frame = frame

        img = QtGui.QImage(
            self.cur_frame, self.cur_frame.shape[1], self.cur_frame.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)

    def prevFrameSlot(self):
        print("prev frame")
        if self.cur_frame == None:
            return
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


class VideoDisplayWidget(QtWidgets.QWidget):
    def __init__(self, parent):
        super(VideoDisplayWidget, self).__init__(parent)

        self.layout = QtWidgets.QFormLayout(self)

        self.startButton = QtWidgets.QPushButton('Start', parent)
        self.startButton.clicked.connect(parent.startCapture)

        self.pauseButton = QtWidgets.QPushButton('Pause', parent)

        self.nextButton = QtWidgets.QPushButton('Next Frame', parent)

        self.prevButton = QtWidgets.QPushButton('Prev Frame', parent)

        self.getCords_btn = QtWidgets.QPushButton('Get Cordinates', parent)

        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.pauseButton)
        self.layout.addWidget(self.nextButton)
        self.layout.addWidget(self.prevButton)
        self.layout.addWidget(self.getCords_btn)

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
        if not self.capture and self.isVideoFileLoaded:
            self.capture = VideoCapture(
                self.videoFileName, self.videoDisplayWidget)
            self.videoDisplayWidget.pauseButton.clicked.connect(
                lambda: self.capture.pause())
            self.videoDisplayWidget.nextButton.clicked.connect(
                lambda: self.capture.nextFrameSlot())
            self.videoDisplayWidget.prevButton.clicked.connect(
                lambda: self.capture.prevFrameSlot())
        self.capture.start()

    def endCapture(self):
        self.capture.deleteLater()
        self.capture = None

    def loadVideoFile(self):
        try:
            self.videoFileName = QtWidgets.QFileDialog.getOpenFileName(self, 'Open file',
                                                                       '/Users/yashasvi.ranjan/ultra', "Video files (*.mp4 *.mpgev)")[0]
            self.isVideoFileLoaded = True
        except:
            print("Please select a .h264 file")

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
