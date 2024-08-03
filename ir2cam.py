import pyrealsense2 as rs #pip install pyrealsense2
import numpy as np
import cv2
import pyvirtualcam #pip install pyvirtualcam
import os, sys, json

def readConfig():
    settingsFile = os.path.join(cwd, "config.json") 
    if os.path.isfile(settingsFile):
        with open(settingsFile) as json_file:
            data = json.load(json_file)
    else:
        data = {
	        "camNumber" : 1,
            "resolution" : [1280, 720],
	        "frameRate" : 30,
            "showFeed" : False
            }
        # Serializing json
        json_object = json.dumps(data, indent=4)
 
        # Writing to config.json
        with open(settingsFile, "w") as outfile:
            outfile.write(json_object)
    return data

# Get the current working
# directory (CWD)
try:
    this_file = __file__
except NameError:
    this_file = sys.argv[0]
this_file = os.path.abspath(this_file)
if getattr(sys, 'frozen', False):
    cwd = os.path.dirname(sys.executable)
else:
    cwd = os.path.dirname(this_file)

print("Current working directory:", cwd)

# Read Config File
config = readConfig()
camNumber = config["camNumber"]
resolution = config["resolution"]
frameRate = config["frameRate"]
showFeed = config["showFeed"]

# We want the points object to be persistent so we can display the 
#last cloud when a frame drops
points = rs.points()
 
# Create a pipeline
pipeline = rs.pipeline()
#Create a config and configure the pipeline to stream
config = rs.config()
width = resolution[0]
height = resolution[1]
config.enable_stream(rs.stream.infrared, camNumber, width, height, rs.format.y8, frameRate)
# Start streaming
profile = pipeline.start(config)
 
# Streaming loop
try:
    with pyvirtualcam.Camera(width=width, height=height, fps=frameRate, fmt=pyvirtualcam.PixelFormat.BGR) as cam:
        print(f'Using virtual camera: {cam.device}')
        while True:
            # Get frameset of color and depth
            frames = pipeline.wait_for_frames()
            ir1_frame = frames.get_infrared_frame(1) # Left IR Camera, it allows 1, 2 or no input
            image = np.asanyarray(ir1_frame.get_data())
            cimage = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
            cam.send(cimage)
            cam.sleep_until_next_frame()
            if showFeed:
                cv2.namedWindow('IR Example', cv2.WINDOW_AUTOSIZE)
                cv2.imshow('IR Example', image)
                key = cv2.waitKey(1)
                # Press esc or 'q' to close the image window
                if key & 0xFF == ord('q') or key == 27:
                    cv2.destroyAllWindows()
                    break
except KeyboardInterrupt:
    pass
finally:
    pipeline.stop()
