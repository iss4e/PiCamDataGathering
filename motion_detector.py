from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import datetime
import imutils
import pudb

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 16
rawCapture = PiRGBArray(camera, size=(640, 480))

# necessary to warm-up
time.sleep(0.1)

avg = None
motionCounter = 0
lastUploaded = datetime.datetime.now()

for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    frame = f.array
    timestamp = datetime.datetime.now()
    roomOccupied = False 
    text = "Unoccupied"

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
        print("occupied!")
        if (timestamp - lastUploaded).seconds >= 3:
            motionCounter += 1

            if motionCounter >= 8:
                cv2.imshow("Frame", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break

                lastUploaded = timestamp
                motionCounter = 0

    else:
        motionCounter = 0
    rawCapture.truncate(0)
