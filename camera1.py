
from packages import *
from services import call_api, call_api_mouth



class VideoCamera(object):
    def __init__(self):
        self.video_capture = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video_capture.release()
    
    def eye_aspect_ratio(self,eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])

        ear = (A+B) / (2*C)
        return ear

    def mouth_aspect_ratio(self,mouth):
        D = distance.euclidean(mouth[2], mouth[10])
        E = distance.euclidean(mouth[4],mouth[8])
        F = distance.euclidean(mouth[0],mouth[6])
    
        
        mar = (D+E) / (2*F)
        
        return mar
    
    def get_frame(self):
        pygame.mixer.init()
        pygame.mixer.music.load('audio/alarm.wav')
        
    
        COUNTER = 0
        COUNTER_MOUTH = 0
        yawns = 0
        yawn_status = False
        
        ear_status = False
        face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']
        (mStart,mEnd)  = face_utils.FACIAL_LANDMARKS_IDXS['mouth']
        
        while(True):
        
            ret, frame = self.video_capture.read()
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector(gray, 0)
            face_rectangle = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in face_rectangle:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                for face in faces:
                    
                    
                    shape = predictor(gray, face)
                    shape = face_utils.shape_to_np(shape)
                    leftEye = shape[lStart:lEnd]
                    rightEye = shape[rStart:rEnd]
                    mmouth = shape[mStart:mEnd]

                    #Calculate aspect ratio of both eyes
                    leftEyeAspectRatio = self.eye_aspect_ratio(leftEye)
                    rightEyeAspectRatio = self.eye_aspect_ratio(rightEye)
                    mouthAspectRatio = self.mouth_aspect_ratio(mmouth)
                    eyeAspectRatio = (leftEyeAspectRatio + rightEyeAspectRatio) / 2
                   
                    
                    previous_yawn_status = yawn_status
                    previous_ear_status = ear_status
                    if(eyeAspectRatio < EYE_ASPECT_RATIO_THRESHOLD):
                        
                        COUNTER += 1
                        if COUNTER >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                            pygame.mixer.music.play(-1)
                            call_api(True)
                            print("sleeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeping")
                            
                        else:
                            call_api(False)
                            print("no sleep")             
                    else:
                        pygame.mixer.music.stop()
                        COUNTER = 0
                    
                    if(mouthAspectRatio > MOUTH_ASPECT_RATIO_THRESHOLD):
                        COUNTER_MOUTH += 1
                        print("mouth open frame", COUNTER_MOUTH)
                        if (COUNTER_MOUTH>MOUTH_ASPECT_RATIO_CONSEC_FRAMES):
                            yawn_status = True
                            COUNTER_MOUTH = 0  
                    else:
                        yawn_status = False
                       

                    if previous_yawn_status == True and yawn_status == False:
                        yawns +=1
                    
                        if yawns >= 5:
                            call_api_mouth(yawns)
                            yawns =0
                            pygame.mixer.music.play() 
                        else:
                            call_api_mouth(1)
                            
                            
                       

obj = VideoCamera()
obj.get_frame()
