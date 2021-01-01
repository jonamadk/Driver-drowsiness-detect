from flask import Flask, render_template, Response
import cv2
from constant import *
from flask import Flask, Response, request
from flask_restful import Api , Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow , fields
from patch_request import patch_sleep_stat , patch_yawn_stat
app = Flask(__name__)

api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db = SQLAlchemy(app)
ma = Marshmallow(app)


def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A+B) / (2*C)
    return ear

def mouth_aspect_ratio(mouth):
    D = distance.euclidean(mouth[2], mouth[10])
    E = distance.euclidean(mouth[4],mouth[8])
    F = distance.euclidean(mouth[0],mouth[6])
    mar = (D+E) / (2*F)
    return mar

def mid_point(p1,p2):
    return int((p1.x +p2.x)/2), int((p1.y +p2.y)/2)


def get_frame():
    video_capture =cv2.VideoCapture(0)

    pygame.mixer.init()
    pygame.mixer.music.load('audio/alarm.wav')
    
    COUNTER = 0
    COUNTER_MOUTH = 0
    yawns = 0
    yawn_status = False

    
   
        
    face_cascade=cv2.CascadeClassifier("haarcascade_frontalface_alt2.xml")
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor('shape_predictor_68_face_landmarks.dat')
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS['left_eye']
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS['right_eye']
    (mStart,mEnd)  = face_utils.FACIAL_LANDMARKS_IDXS['mouth']
        
    while(True):
        
        ret, frame = video_capture.read()
        # concat frame one by one and show result
        frame = imutils.resize(frame, width=600)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector(gray, 0)
        face_rectangle = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in face_rectangle:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            for face in faces:
                    
                    
                shape = predictor(gray, face)
                shape = face_utils.shape_to_np(shape)

                landmarks = predictor(gray,face)
                left_left_point = (landmarks.part(36).x , landmarks.part(36).y)
                left_right_point = (landmarks.part(39).x , landmarks.part(39).y)
                left_center_top = mid_point(landmarks.part(37), landmarks.part(38))
                left_center_bottom = mid_point(landmarks.part(40), landmarks.part(41))
                
                right_left_point = (landmarks.part(42).x , landmarks.part(42).y)
                right_right_point = (landmarks.part(45).x , landmarks.part(45).y)
                right_center_top = mid_point(landmarks.part(43), landmarks.part(44))
                right_center_bottom = mid_point(landmarks.part(46), landmarks.part(47))
                
                
                left_hor_line = cv2.line(frame,left_left_point,left_right_point,(0,255,0),1)
                left_ver_line = cv2.line(frame,left_center_top,left_center_bottom,(0,255,0),2)
                
                
                right_hor_line = cv2.line(frame,right_left_point,right_right_point,(0,255,0),1)
                right_ver_line = cv2.line(frame, right_center_top,right_center_bottom,(0,255,0),2)
                
                for n in range(0,68):
                    x = landmarks.part(n).x 
                    y = landmarks.part(n).y 
                    cv2.circle(frame,(x,y),2,(255,255,0),-2)

                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                mmouth = shape[mStart:mEnd]

                #Calculate aspect ratio of both eyes
                leftEyeAspectRatio = eye_aspect_ratio(leftEye)
                rightEyeAspectRatio = eye_aspect_ratio(rightEye)
                mouthAspectRatio = mouth_aspect_ratio(mmouth)
                eyeAspectRatio = (leftEyeAspectRatio + rightEyeAspectRatio) / 2
                        
                previous_yawn_status = yawn_status

        
                    
                if(eyeAspectRatio < EYE_ASPECT_RATIO_THRESHOLD):  
                    COUNTER += 1
                    if COUNTER >= EYE_ASPECT_RATIO_CONSEC_FRAMES:
                        pygame.mixer.music.play(-1)
                        patch_sleep_stat(True)
                        cv2.putText(frame," SLEEPING",(50,250),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
                        
                        cv2.putText(frame," SLEEPING",(50,250),cv2.FONT_HERSHEY_COMPLEX,1,(0,0,255),2)
                           
                    else:
                        
                        patch_sleep_stat(False)
                                             
                else:
                    pygame.mixer.music.stop()
                    patch_sleep_stat(False)
                    COUNTER = 0

                    
                    
                if(mouthAspectRatio > MOUTH_ASPECT_RATIO_THRESHOLD):
                    COUNTER_MOUTH += 1
              
                    if (COUNTER_MOUTH>MOUTH_ASPECT_RATIO_CONSEC_FRAMES):
                        yawn_status = True
                        COUNTER_MOUTH = 0  
                else:
                    yawn_status = False

                if previous_yawn_status == True and yawn_status == False:
                    yawns +=1
                    
                    if yawns >= 4:
                        
                        patch_yawn_stat(True)
                        yawns =0
                        pygame.mixer.music.play()
                    else:
                        patch_yawn_stat(False)
                        pygame.mixer.music.stop()
                       

        if not ret:
            break
        else:
            sucess, buffer =cv2.imencode('.jpg',frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') 

    video_capture.release() 

               

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


class Data(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    sleep_stat = db.Column(db.Boolean, unique=False , default = False)
    yawn_stat = db.Column(db.Boolean, unique = False, default = False)

class DataSchema(ma.Schema):
    class Meta:
        fields = ('id', 'sleep_stat','yawn_stat')

data_schema = DataSchema()
datas_schema = DataSchema (many = True)

class DatasResource(Resource):
    def get (self):
        return datas_schema.dump(Data.query.all())

    def post (self):
        data = request.json
        post = Data(sleep_stat= data['sleep_stat'], yawn_stat = data['yawn_stat'])
        db.session.add(post)
        db.session.commit()
        return data_schema.dump(post)
    
class DataResource(Resource):
    def get(self, pk):
        return data_schema.dump(Data.query.get_or_404(pk))
    
    def patch(self, pk):
        data = request.json
        post = Data.query.get_or_404(pk)

        if 'sleep_stat' in data:
            post.sleep_stat = data['sleep_stat']
        
        if 'yawn_stat' in data:
            post.yawn_stat = data['yawn_stat']

        db.session.commit()

        return data_schema.dump(post)

api.add_resource(DataResource,'/post/<int:pk>')
api.add_resource(DatasResource, '/posts')


if __name__ == '__main__':
    app.run()