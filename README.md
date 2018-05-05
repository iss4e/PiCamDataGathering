## Gathering Training Images with the Raspberry Pi
The following scripts were used to gather overhead images of an office for the 
purpose of training a CNN to detect occupancy within that office.
___
The `timed_capture.py` script captures images at a fixed rate and saves them within a directory.  
*Usage*:  
* Supply the script with a folder path as a cmd-line argument to change where images are saved.
* Modify the `captureRate` variable to change the period at which images are taken, in seconds.
* Modify the `endTime` to change when the script automatically quits on that day.
___
The `timed_image_capture.sh` simplifies usage of the python script on the pi. 
This script writes the Pi's captured images to `/home/pi/trainingImages` and pipes the output 
of the python script to `/home/pi/trainingDebug` for debugging purposes.

The recommended way to generate training images is by setting up a cronjob that launches the bash script on a daily basis.
___
*Note*:
One may also launch the bash script manually, but it is important to note that previous images will be overwritten for that day,
unless the `numUploaded` variable is manually increased. For example, if the current folder contains captures up to `cap123.jpg`,
one should increase `numUploaded` to be 124, so that the previous images are not overwritten.

*Note*: it may be necessary to modify the path to the `timed_capture.py` script. 
The bash script currently assumes that the user's script is located in `/home/pi/data_gathering/timed_capture.py`, this may be changed if necessary.


