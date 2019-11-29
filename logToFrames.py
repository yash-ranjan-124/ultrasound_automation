from imutils.video import VideoStream
from imutils.video import FPS
import logging
import argparse
import imutils
import time
import cv2
import sys
import os
import json
from ast import literal_eval as make_tuple


ap = argparse.ArgumentParser()
ap.add_argument("-l", "--logFile", type=str,help="path to input log file")

ap.add_argument("-v", "--video", type=str, help="path to input video file")                

ap.add_argument("-s", "--slow", type=str, default=0,help="OpenCV object tracker type")

args = vars(ap.parse_args())

# extract the OpenCV version info
(major, minor) = cv2.__version__.split(".")[:2]

# if we are using OpenCV 3.2 OR BEFORE, we can use a special factory
# function to create our object tracker
OPENCV_OBJECT_TRACKERS = ""
tracker = None
OPENCV_OBJECT_TRACKERS = {
        "csrt": cv2.TrackerCSRT_create,
        "kcf": cv2.TrackerKCF_create,
        "boosting": cv2.TrackerBoosting_create,
        "mil": cv2.TrackerMIL_create,
        "tld": cv2.TrackerTLD_create,
        "medianflow": cv2.TrackerMedianFlow_create,
        "mosse": cv2.TrackerMOSSE_create
}

filename = args['logFile']    
videofile = args['video']
loopSleepTime = args['slow']  if args['slow'] else 0


if not os.path.isfile(filename) or not os.path.isfile(videofile):
    print("log file  or video file Not found")
    exit()

vs = cv2.VideoCapture(args["video"])


initBB = None
algo = None

def displayFrame(flag="next", user=0):
    frame = None
    ret = None
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

    if initBB is not None:
        # grab the new bounding box coordinates of the object
        (success, box) = tracker.update(frame)

        # check to see if the tracking was a success
        if success:
            (x, y, w, h) = [int(v) for v in box]
            cv2.rectangle(frame, (x, y), (x + w, y + h),
                          (0, 255, 0), 2)

            # update the FPS counter
           

            # initialize the set of information we'll be displaying on
            # the frame
            info = [
                ("Tracker", algo),
                ("Success", "Yes" if success else "No"),
                ("Cords", str(initBB))
            ]

            # loop over the info tuples and draw them on our frame
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("frame", frame)
    return frame


fp = open(filename)
frameLogDict = {}

for cnt, line in enumerate(fp):
    line = line[10:]
    line = line.replace("\'","\"")
    op = json.loads(line)
    key = str(op["frame"])
    frameLogDict[key] = op
    frameLogDict[key]["initBB"] = make_tuple(op["initBB"])

print(frameLogDict)   

while True:
    frame = displayFrame("next",0)
    if frame is None:
        break
    next_frame = vs.get(cv2.CAP_PROP_POS_FRAMES)
    current_frame = next_frame - 1
    cur_frame = str(current_frame)
    print(cur_frame)
    if cur_frame in frameLogDict:
        algo = frameLogDict[cur_frame]["tracker"]
        tracker = OPENCV_OBJECT_TRACKERS[algo]()
        initBB = frameLogDict[cur_frame]["initBB"]
        tracker.init(frame, initBB)
        frame = displayFrame("cur", frameLogDict[cur_frame]["userFlag"])
    else:
        pass
        #tracker.d(frame, initBB)
        #frame = displayFrame("cur", frameLogDict[cur_frame]["userFlag"])     

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break    


# close all windows
cv2.destroyAllWindows()        
      
       
    




