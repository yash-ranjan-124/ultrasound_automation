from imutils.video import VideoStream
from imutils.video import FPS
import logging
import argparse
import imutils
import time
import cv2


ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", type=str,
                help="path to input video file")
ap.add_argument("-t", "--tracker", type=str, default="kcf",
                help="OpenCV object tracker type")
ap.add_argument("-s", "--slow", type=str, default=0,
                help="OpenCV object tracker type")
args = vars(ap.parse_args())

# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

# if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
# function to create our object tracker
if int(major) == 3 and int(minor) < 3:
    tracker = cv2.Tracker_create(args["tracker"].upper())

# otherwise, for OpenCV 3.3 OR NEWER, we need to explicity call the
# approrpiate object tracker constructor:
else:
    # initialize a dictionary that maps strings to their corresponding
    # OpenCV object tracker implementations
    OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
    }

    # grab the appropriate object tracker using our dictionary of
    # OpenCV object tracker objects
    tracker = OPENCV_OBJECT_TRACKERS[args["tracker"]]()

# initialize the bounding box coordinates of the object we are going
# to track

tracker_list = ["csrt", "kcf", "boosting", "mil", "tld", "medianflow", "mosse"]


def getTrackerPos(tracker):
    for i in range(0, len(tracker_list)):
        if OPENCV_OBJECT_TRACKERS[args["tracker"]]:
            return i


tracker_pos = getTrackerPos(args["tracker"])
tracker_name = args["tracker"]
initBB = None

# if a video path was not supplied, grab the reference to the web cam
if not args.get("video", False):
    print("[INFO] starting video stream...")
    vs = VideoStream(src=0).start()
    time.sleep(1.0)

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# initialize the FPS throughput estimator
fps = None

# loop over frames from the video stream
isRecording = True
sleepTime = int(args["slow"])


logging.basicConfig(filename="log.txt", filemode='a',level=logging.INFO)



def logFramesData(data={}):
    if data is None:
        return
    else:
        logging.info({
            "frame":data['frameNo'] ,  
            "userFlag":data["user"]  , 
            "tracker": data["tracker"] , 
            "initBB":str(data["initBB"])
        })


def displayFrame(flag="next", user=False):
    ret = None
    frame = None
    if flag == "next":
        ret, frame = vs.read()

    if flag == "prev":
        next_frame = vs.get(cv2.CAP_PROP_POS_FRAMES)
        current_frame = next_frame - 1
        previous_frame = current_frame - 1
        vs.set(cv2.CAP_PROP_POS_FRAMES, previous_frame)
        ret, frame = vs.read()

    if flag == "cur":
        next_frame = vs.get(cv2.CAP_PROP_POS_FRAMES)
        current_frame = next_frame - 1
        vs.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = vs.read()

    if not ret:
        return None
    # check to see if we have reached the end of the stream
    if frame is None:
        return None

    # resize the frame (so we can process it faster) and grab the
    # frame dimensions
    frame = imutils.resize(frame, width=500)
    (H, W) = frame.shape[:2]

    # check to see if we are currently tracking an object
    if initBB is not None:
        # grab the new bounding box coordinates of the object
        (success, box) = tracker.update(frame)

        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)

            # update the FPS counter
            fps.update()
            fps.stop()

            # initialize the set of information we'll be displaying on
            # the frame
            info = [
                ("Tracker", tracker_name),
                ("Success", "Yes" if success else "No"),
                ("FPS", "{:.2f}".format(fps.fps())),
                ("Cords", "("+str(x)+","+str(y)+")")
            ]

            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            logFramesData({
                "initBB":initBB,
                "tracker": tracker_name,
                "frameNo": vs.get(cv2.CAP_PROP_POS_FRAMES) - 1,
                "user": 1 if user else 0
            })

    # show the output frame
    cv2.imshow("frame", frame)
    return frame


while True:
    # grab the current frame, then handle if we are using a
    # VideoStream or VideoCapture object
    frame = displayFrame()
    if frame is None:
        break

    key = cv2.waitKey(1) & 0xFF

    # if the 's' key is selected, we are going to "select" a bounding
    # box to track
    if key == ord("s"):
            # select the bounding box of the object we want to track (make
            # sure you press ENTER or SPACE after selecting the ROI)
        initBB = cv2.selectROI("frame", frame, fromCenter=False,
                               showCrosshair=True)

        # start OpenCV object tracker using the supplied bounding box
        # coordinates, then start the FPS throughput estimator as well
        tracker.init(frame, initBB)
        fps = FPS().start()
        frame = displayFrame("cur", True)

    elif key == ord("x"):
        while True:
            key2 = cv2.waitKey(1) or 0xff
            if frame is None:
                exit()
            cv2.imshow('frame', frame)
            if key2 == ord('x'):
                break
            elif key2 == ord("n"):
                frame = displayFrame()

            elif key2 == ord("p"):
                frame = displayFrame("prev")

            elif key2 == ord("s"):
                        # select the bounding box of the object we want to track (make
                    # sure you press ENTER or SPACE after selecting the ROI)
                initBB = cv2.selectROI("frame", frame, fromCenter=False,
                                       showCrosshair=True)

                # start OpenCV object tracker using the supplied bounding box
                # coordinates, then start the FPS throughput estimator as well
                tracker.init(frame, initBB)
                fps = FPS().start()

                frame = displayFrame("cur", True)     

            elif key2 == ord("r"):
                        # select the bounding box of the object we want to track (make
                    # sure you press ENTER or SPACE after selecting the ROI)
                initBB = cv2.selectROI("frame", frame, fromCenter=False,
                                       showCrosshair=True)
                tracker = OPENCV_OBJECT_TRACKERS[tracker_name]()
                # start OpenCV object tracker using the supplied bounding box
                # coordinates, then start the FPS throughput estimator as well
                tracker.init(frame, initBB)
                fps = FPS().start()

                frame = displayFrame("cur", True) 

            elif key2 == ord("q"):
                exit()

            elif key2 == ord("t"):
                i = tracker_pos
                if i < len(tracker_list) - 1:
                    temp_pos = i + 1
                    tracker = OPENCV_OBJECT_TRACKERS[tracker_list[temp_pos]]()
                    tracker_pos = temp_pos
                    tracker_name = tracker_list[tracker_pos]
                    initBB = cv2.selectROI("frame", frame, fromCenter=False,
                                           showCrosshair=True)
                    tracker.init(frame, initBB)
                    fps = FPS().start()
                    frame = displayFrame("cur", True)

            elif key2 == ord("y"):
                i = tracker_pos
                if i > 0:
                    temp_pos = i - 1
                    tracker = OPENCV_OBJECT_TRACKERS[tracker_list[temp_pos]]()
                    tracker_pos = temp_pos
                    tracker_name = tracker_list[tracker_pos]
                    initBB = cv2.selectROI("frame", frame, fromCenter=False,
                                           showCrosshair=True)
                    tracker.init(frame, initBB)
                    fps = FPS().start()
                    frame = displayFrame("cur", True)

        # if the `q` key was pressed, break from the loop
    elif key == ord("q"):
        break

    elif key == ord("d"):
        sleepTime = sleepTime - 1 if sleepTime > 0 else sleepTime

    elif key == ord("i"):
        sleepTime = sleepTime + 1

    elif key == ord("t"):
        i = tracker_pos
        if i < len(tracker_list) - 1:
            temp_pos = i + 1
            tracker = OPENCV_OBJECT_TRACKERS[tracker_list[temp_pos]]()
            tracker_pos = temp_pos
            tracker_name = tracker_list[tracker_pos]
            initBB = cv2.selectROI("frame", frame, fromCenter=False,
                                   showCrosshair=True)
            tracker.init(frame, initBB)
            fps = FPS().start()
            frame = displayFrame("cur", True)

    elif key == ord("y"):
        i = tracker_pos
        if i > 0:
            temp_pos = i - 1
            tracker = OPENCV_OBJECT_TRACKERS[tracker_list[temp_pos]]()
            tracker_pos = temp_pos
            tracker_name = tracker_list[tracker_pos]
            initBB = cv2.selectROI("frame", frame, fromCenter=False,
                                   showCrosshair=True)
            tracker.init(frame, initBB)
            fps = FPS().start()
            frame = displayFrame("cur", True)

    time.sleep(sleepTime)

# if we are using a webcam, release the pointer
if not args.get("video", False):
    vs.stop()

# otherwise, release the file pointer
else:
    vs.release()

# close all windows
cv2.destroyAllWindows()
