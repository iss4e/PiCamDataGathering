from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import datetime
import imutils
import pudb
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if len(sys.argv) != 2:
    print("Improper cmd-line args, must pass in path to save to!")
    sys.exit(0)

homeDir = sys.argv[1]

if not os.path.isdir(homeDir):
    print("Not a directory path!")
    sys.exit(0)

# camera init
logger.info("Initializing Camera...")
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=(640, 480))

# necessary to warm-up
time.sleep(0.1)
logger.info("Done initializing")

avg = None
motionCounter = 0

lastUploaded = None
numUploaded = 0

prevMotionTime = datetime.datetime.now()
now = datetime.datetime.now()
today6pm = now.replace(hour=18, minute=0, second=0,microsecond=0)

dayString = now.strftime("%b-%d")
uploadPath = os.path.join(homeDir, dayString)

logger.info("Creating directory for today")

# safely create today's directory
try:
    os.makedirs(uploadPath)
except OSError:
    if not os.path.isdir(uploadPath):
        raise

logger.info("Entering camera capturing loop...")

for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = f.array
    timestamp = datetime.datetime.now()

    if timestamp > today6pm:
        logger.info("timestamp exceeds 6pm mark, exiting program!")
        # stop gathering 
        sys.exit(0)

    roomOccupied = False

    frame = imutils.resize(frame, width = 500)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    if avg is None:
        avg = gray.copy().astype("float")
        rawCapture.truncate(0)
        continue

    cv2.accumulateWeighted(gray, avg, 0.5)
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frameDelta,5, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]


    for c in cnts:
        # if the contour is too small, ignore it
        if cv2.contourArea(c) < 5000:
                continue

        # compute the bounding box for the contour, draw it on the frame,
        # and update the text
        roomOccupied = True

    
    if roomOccupied:
        if (timestamp - prevMotionTime).seconds >= 3: 
            motionCounter += 1

            if motionCounter >= 8:

                prevMotionTime = timestamp
                motionCounter = 0

                if lastUploaded is None or (timestamp - lastUploaded).seconds >= 120: 
                    filePath = os.path.join(uploadPath, "cap_{}.jpg".format(numUploaded))
                    logger.info("Uploading image: {}".format(filePath))

                    cv2.imwrite(filePath, f.array)
                    lastUploaded = timestamp
                    numUploaded += 1
    else:
        motionCounter = 0

    rawCapture.truncate(0)
