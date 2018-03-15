from picamera import PiCamera
import time
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
camera.resolution = (3280, 2464)

# necessary to warm-up
time.sleep(0.1)
logger.info("Done initializing")

lastUploaded = None
numUploaded = 197 

now = datetime.datetime.now()
today6pm = now.replace(hour=22, minute=0, second=0,microsecond=0)

dayString = now.strftime("%b-%d-%a")
uploadPath = os.path.join(homeDir, dayString)

captureRate = 2*60 # capture period (in sec)

logger.info("Capture every {} seconds".format(captureRate))
logger.info("Creating directory for today")

# safely create today's directory
try:
    os.makedirs(uploadPath)
except OSError:
    if not os.path.isdir(uploadPath):
        raise

logger.info("Entering camera capturing loop...")

while(True):
    timestamp = datetime.datetime.now()

    if timestamp > today6pm:
        logger.info("timestamp exceeds 6pm mark, exiting program!")
        # stop gathering 
        sys.exit(0)

    if lastUploaded is None or (timestamp - lastUploaded).seconds >= captureRate: 

        filePath = os.path.join(uploadPath, "cap_{:03d}.jpg".format(numUploaded))
        logger.info("Uploading image: {} @ {}".format(filePath, timestamp.strftime("%H:%M")))
        camera.capture(filePath)
        lastUploaded = timestamp
        numUploaded += 1

