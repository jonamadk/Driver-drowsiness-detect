from scipy.spatial import distance
from imutils import face_utils
import numpy as np
import pygame 
# import time
import dlib
import cv2
import imutils
from cv2.cv2 import putText, rectangle


EYE_ASPECT_RATIO_THRESHOLD = 0.21
MOUTH_ASPECT_RATIO_THRESHOLD = 0.6

EYE_ASPECT_RATIO_CONSEC_FRAMES = 25
MOUTH_ASPECT_RATIO_CONSEC_FRAMES = 20




