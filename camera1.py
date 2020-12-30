from packages import *

from services import call_api , call_api_mouth

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


    def mid_point(self,p1,p2):
        return int((p1.x +p2.x)/2), int((p1.y +p2.y)/2)

    
    def get_frame(self):
        pygame.mixer.init()
        pygame.mixer.music.load('audio/alarm.wav')
        
    
        COUNTER = 0
        COUNTER_MOUTH = 0
        yawns = 0
        yawn_status = False
        

        face_cascade = cv2.CascadeClassifier("haarcascades/haarcascade_frontalface_default.xml")



        #Load face detector and predictor, uses dlib shape predictor file
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')

        #Extract indexes of facial landmarks for the left and right eye
        (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
        (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']

        (mStart,mEnd)  = face_utils.FACIAL_LANDMARKS_IDXS['mouth']


        #Give some time for camera to initialize(not required)

        while(True):
            #Read each frame and flip it, and convert to grayscale
            ret, frame = self.video_capture.read()
            frame = imutils.resize(frame, width=450)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            #Detect facial points through detector function
            faces = detector(gray, 0)

            #Detect faces through haarcascade_frontalface_default.xml
            face_rectangle = face_cascade.detectMultiScale(gray, 1.3, 5)

            #Draw rectangle around each face detected
            for (x,y,w,h) in face_rectangle:
                cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
                
            #Detect facial points
            for face in faces:
                
                shape = predictor(gray, face)
                shape = face_utils.shape_to_np(shape)
                
                landmarks = predictor(gray,face)
                left_left_point = (landmarks.part(36).x , landmarks.part(36).y)
                left_right_point = (landmarks.part(39).x , landmarks.part(39).y)
                left_center_top = self.mid_point(landmarks.part(37), landmarks.part(38))
                left_center_bottom = self.mid_point(landmarks.part(40), landmarks.part(41))
                
                right_left_point = (landmarks.part(42).x , landmarks.part(42).y)
                right_right_point = (landmarks.part(45).x , landmarks.part(45).y)
                right_center_top = self.mid_point(landmarks.part(43), landmarks.part(44))
                right_center_bottom = self.mid_point(landmarks.part(46), landmarks.part(47))
                
                
                left_hor_line = cv2.line(frame,left_left_point,left_right_point,(0,255,0),1)
                left_ver_line = cv2.line(frame,left_center_top,left_center_bottom,(0,255,0),2)
                
                
                right_hor_line = cv2.line(frame,right_left_point,right_right_point,(0,255,0),1)
                right_ver_line = cv2.line(frame, right_center_top,right_center_bottom,(0,255,0),2)
                
                for n in range(0,68):
                    x = landmarks.part(n).x 
                    y = landmarks.part(n).y 
                    cv2.circle(frame,(x,y),2,(255,255,0),-2)

            

                #Get array of coordinates of leftEye and rightEye
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                mmouth = shape[mStart:mEnd]

                #Calculate aspect ratio of both eyes
                leftEyeAspectRatio = self.eye_aspect_ratio(leftEye)
                rightEyeAspectRatio = self.eye_aspect_ratio(rightEye)
                mouthAspectRatio = self.mouth_aspect_ratio(mmouth)
                print("mouthspectRatio",mouthAspectRatio)
            

                eyeAspectRatio = (leftEyeAspectRatio + rightEyeAspectRatio) / 2
                print("Eyeaspect ratio", eyeAspectRatio)
                

                #Use hull to remove convex contour discrepencies and draw eye shape around eyes
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                mouthHull = cv2.convexHull(mmouth)
                
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [mouthHull], -1, (0, 255, 0), 1)
                
                
                previous_yawn_status = yawn_status
            
                
                #Detect if eye aspect ratio is less than threshold
                if(eyeAspectRatio < EYE_ASPECT_RATIO_THRESHOLD):
                    
                    COUNTER += 1
                    # print("EYE ASPECT COUNTER FRAME",COUNTER)
                    # print("less than theshold")
                    #If no. of frames is greater than threshold frames,
                    if COUNTER >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        call_api(True)
                        # print("SLEEPING_SLEEPING_SLEEPING_SLEEPING")
                        # print("EAR",eyeAspectRatio)
                        # print(call_api)
                        pygame.mixer.music.play(-1)

                        cv2.putText(frame," SLEEPING",(50,450),
                                cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
                        
                        
                        cv2.putText(frame," SLEEPING",(50,450),
                                cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
                                
                        
                    else:
                        call_api(False)
                    
                        
                else:
                    pygame.mixer.music.stop()
                    call_api(False)
                    COUNTER = 0
                        
                        
                        
                        
                if(mouthAspectRatio > MOUTH_ASPECT_RATIO_THRESHOLD):
                    COUNTER_MOUTH += 1
                    # print("mouth open frame", COUNTER_MOUTH)
                    
                    if (COUNTER_MOUTH>=MOUTH_ASPECT_RATIO_CONSEC_FRAMES):
                        yawn_status = True
                        COUNTER_MOUTH = 0
                        print("MAR",mouthAspectRatio)
                        cv2.putText(frame,"Yawning",(50,450),
                                cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
                        output_text = "Yawn Count:" + str(yawns+1)
                    
                        cv2.putText(frame,output_text,(50,50),
                                cv2.FONT_HERSHEY_COMPLEX,1,(0,255,127),2)
                        
                else:
                    yawn_status = False
                    # print("MAR<THRESHOLD")
                    call_api_mouth(False)
                    
                
                    
                if previous_yawn_status == True and yawn_status == False:
                    yawns +=1
                
                    if yawns >= 4:
                        yawns =0
                        call_api_mouth(True)
                        pygame.mixer.music.play()
                        
                        
                        cv2.putText(frame," YAWNINIG Freq", (50,50),
                                    cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
                        
                        
                        
                        cv2.putText(frame, output_text + ">THRESHHOLD VALUE", (50,50),
                                cv2.FONT_HERSHEY_COMPLEX, 1,(0,255,127),2)   
                        
                    
                        
                    else:
                        print("yawn count is less")

                        call_api_mouth(False)
                    
            
                    
            cv2.imshow('Video', frame)
            if(cv2.waitKey(1) & 0xFF == ord('q')):
                break
                        


        #Finally when video capture is over, release the video capture and destroyAllWindows
obj = VideoCamera()
obj.get_frame()

        
        

        
        
                
                
                
                
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
         
