# -*- coding: utf-8 -*-
"""
Created on Sun Nov 17 01:35:48 2019

@author: R. Erdem Uysal
"""

# python object_tracking.py --videoPath video.mp4 --tracker csrt

# Import the necessary libraries
import numpy as np
import cv2
import argparse

from fps import FPS


class Tracker(object):
    
    def __init__(self, videoPath, tracker):
        self.roi = None # Initialize the bounding box coordinates of the object we are going to track
        self.fps = None # Initialize the FPS throughput estimator
        self.video = videoPath
        self.tracker_algorithm = tracker

    def follow(self):

        # Find OpenCV version
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        
        if int(major_ver) == 3 and int(minor_ver) < 3:
                tracker = cv2.Tracker_create(self.tracker_algorithm.upper())
        
        else:
            # Initialize a dictionary that maps strings to their corresponding
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

            # Grab the appropriate object tracker using our dictionary of
            # OpenCV object tracker objects
            tracker = OPENCV_OBJECT_TRACKERS[self.tracker_algorithm]()

        cap = cv2.VideoCapture(self.video)

        if not cap.isOpened():
            print("Error opening video stream or file")
            exit()

        # Loop over frames from the video stream
        while(cap.isOpened()):
            retval, frame = cap.read()
            # Resize the frame (so we can process it faster)
            frame = cv2.resize(frame, (640, 480))
            # Grab the frame dimensions
            (H, W) = frame.shape[:2]
        
            # Check to see if we are currently tracking an object 	
            if self.roi is not None:
                # Grab the new bounding box coordinates of the object
                (success, box) = tracker.update(frame)
        
                # Check to see if the tracking was a success
                if success:
                    (x, y, w, h) = [int(v) for v in box]
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
                # Update the FPS counter
                self.fps.update()
                self.fps.stop()    
            
                # Initialize the set of information we'll be displaying on the frame
                info = [
                        ("Tracking Algorithm", self.tracker_algorithm),
                        ("Success", "Yes" if success else "No"),
                        ("FPS", "{:.2f}".format(self.fps.fps())),
                ]
        
                # Loop over the info tuples and draw them on our frame
                for (i, (k, v)) in enumerate(info):
                    text = "{}: {}".format(k, v)
                    cv2.putText(frame, text, (10, H - ((i * 20) + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 1)
                    
            # Display the resulting frame
            cv2.imshow('Frame', frame)
            
            key = cv2.waitKey(1) & 0xFF    
            
            if key == ord('r'):
                roi = None
                tracker.update(frame)

            # If the 's' key is selected, we are going to "select" a bounding box to track
            if key == ord('s'):
                # Select the bounding box of the object we want to track (make
                # Sure you press ENTER or SPACE after selecting the ROI)
                self.roi = cv2.selectROI('Frame', frame, fromCenter=False,
                                                      showCrosshair=True)
                # Start OpenCV object tracker using the supplied bounding box
                # coordinates, then start the FPS throughput estimator as well
                tracker.init(frame, self.roi)
                self.fps = FPS().start()

            # If the 'q' key was pressed, break from the loop
            elif key == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    # Construct the argument parser and parse the arguments
    # Check the help parameters to understand arguments.
    parser = argparse.ArgumentParser(prog = 'object_tracking.py', description='Object tracking.')
    parser.add_argument('-videoPath', type=str, required=False, help='Path or name of the video file', default = 0)
    parser.add_argument('-tracker', type=str, required = False, help='Name of the built-in OpenCV tracking algorithm.', default = "csrt")
    args = parser.parse_args()

    tracer = Tracker(args.videoPath, args.tracker)
    tracer.follow()