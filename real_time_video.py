from keras.preprocessing.image import img_to_array
import imutils
import cv2
from keras.models import load_model
import numpy as np
import time
#import serial 
# parameters for loading data and images
detection_model_path = 'haarcascade_files/haarcascade_frontalface_default.xml'
emotion_model_path = 'models/_mini_XCEPTION.102-0.66.hdf5'
prev_time = time.time()
# hyper-parameters for bounding boxes shape
# loading models
face_detection = cv2.CascadeClassifier(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)
EMOTIONS = ["angry" ,"disgust","scared", "happy", "sad", "surprised",
 "neutral"] 



def emotion():
    # starting video streaming
    cv2.namedWindow('your_face')
    camera = cv2.VideoCapture(0)  


    while True:
        time.sleep(0)
        frame = camera.read()[1]
        #reading the frame
        label=""

        frame = imutils.resize(frame,500, 500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        
        canvas = np.zeros((250, 300, 3), dtype="uint8")
        frameClone = frame.copy()
        if len(faces) > 0:
            faces = sorted(faces, reverse=True,
            key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
                        # Extract the ROI of the face from the grayscale image, resize it to a fixed 28x28 pixels, and then prepare
                # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (64, 64))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)

            
            preds = emotion_classifier.predict(roi)[0]
            emotion_probability = np.max(preds)
            label = EMOTIONS[preds.argmax()]
        else: continue

    
        for (i, (emotion, prob)) in enumerate(zip(EMOTIONS, preds)):
                    # construct the label text
                    if(prob>0.38):
                        text = "{}: {:.2f}%".format(emotion, prob * 100)
                    
                    # draw the label + probability bar on the canvas
                # emoji_face = feelings_faces[np.argmax(preds)]
                    
                        w = int(prob * 300)
                        cv2.rectangle(canvas, (7, (i * 35) + 5),
                        (w, (i * 35) + 35), (0, 0, 255), -1)
                        cv2.putText(canvas, text, (10, (i * 35) + 23),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45,
                        (255, 255, 255), 2)
                        cv2.putText(frameClone, label, (fX, fY - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                        cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH),
                                    (0, 0, 255), 2)
                        nowTime = time.time()
                        if label=="happy":
                                print('left')
                                #ser.write("L".encode())
                            
                    
                        elif label=="sad":
                            print('Up')
                            #ser.write("F".encode())
                            
                        
                        elif label=="angry":
                            print('Down')
                            #ser.write("B".encode())
                            

                        elif label=="scared":
                                print('right')
                                #ser.write("R".encode())
                        
                        elif label=="neutral"  or label=="disgust":
                            print('stop')
                            #ser.write("1".encode())
                        

        cv2.imshow('your_face', frameClone)
        cv2.imshow("Probabilities", canvas)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    #ser.close()
    camera.release()
    cv2.destroyAllWindows()

