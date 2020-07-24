from os import listdir
from PIL import ImageTk,Image
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import time
from PIL import Image, ImageTk
from pathlib import Path
import cv2
import dlib
import numpy as np
import argparse
from contextlib import contextmanager
from wide_resnet import WideResNet
from keras.utils.data_utils import get_file
import pandas as pd
import real_time_video

pretrained_model = "model_weights/weights.28-3.73.hdf5"
modhash = 'fbe63257a054c1c5466cfd7bf14646d6'

df= pd.read_csv("Adds.csv")
From_Age=df["From_Age"]
To_Age=df["To_Age"]
Adds=df["Adds"]
Images=df["Images"]
Gender=df["Gender"]


def get_args():
    parser = argparse.ArgumentParser(description="This script detects faces from web cam input, "
                                                 "and estimates age and gender for the detected faces.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--weight_file", type=str, default=pretrained_model,
                        help="path to weight file (e.g. weights.28-3.73.hdf5)")
    parser.add_argument("--depth", type=int, default=16,
                        help="depth of network")
    parser.add_argument("--width", type=int, default=8,
                        help="width of network")
    parser.add_argument("--margin", type=float, default=0.4,
                        help="margin around detected face for age-gender estimation")
    parser.add_argument("--image_dir", type=str, default=None,
                        help="target image directory; if set, images in image_dir are used instead of webcam")
    args = parser.parse_args()
    return args


def draw_label(image, point, label, font=cv2.FONT_HERSHEY_SIMPLEX,
               font_scale=0.8, thickness=1):
    size = cv2.getTextSize(label, font, font_scale, thickness)[0]
    x, y = point
    cv2.rectangle(image, (x, y - size[1]), (x + size[0], y), (255, 0, 0), cv2.FILLED)
    cv2.putText(image, label, point, font, font_scale, (255, 255, 255), thickness, lineType=cv2.LINE_AA)


@contextmanager
def video_capture(*args, **kwargs):
    global cap
    cap = cv2.VideoCapture(*args, **kwargs)
    yield cap
    

def yield_images():
    # capture video
    with video_capture(0) as cap:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        while True:
            # get video frame
            ret, img = cap.read()

            if not ret:
                raise RuntimeError("Failed to capture image")

            yield img


def yield_images_from_dir(image_dir):
    image_dir = Path(image_dir)

    for image_path in image_dir.glob("*.*"):
        img = cv2.imread(str(image_path), 1)

        if img is not None:
            h, w, _ = img.shape
            r = 640 / max(w, h)
            yield cv2.resize(img, (int(w * r), int(h * r)))


def click():
    args = get_args()
    depth = args.depth
    k = args.width
    weight_file = args.weight_file
    margin = args.margin
    image_dir = args.image_dir

    if not weight_file:
        weight_file = get_file("weights.28-3.73.hdf5", pretrained_model, cache_subdir="pretrained_models",
                               file_hash=modhash, cache_dir=str(Path(__file__).resolve().parent))

    # for face detection
    detector = dlib.get_frontal_face_detector()

    # load model and weights
    img_size = 64
    model = WideResNet(img_size, depth=depth, k=k)()
    model.load_weights(weight_file)

    image_generator = yield_images_from_dir(image_dir) if image_dir else yield_images()

    for img in image_generator:
        input_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_h, img_w, _ = np.shape(input_img)

        # detect faces using dlib detector
        detected = detector(input_img, 1)
        faces = np.empty((len(detected), img_size, img_size, 3))

        if len(detected) > 0:
            for i, d in enumerate(detected):
                x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
                xw1 = max(int(x1 - margin * w), 0)
                yw1 = max(int(y1 - margin * h), 0)
                xw2 = min(int(x2 + margin * w), img_w - 1)
                yw2 = min(int(y2 + margin * h), img_h - 1)
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 2)
                
                faces[i, :, :, :] = cv2.resize(img[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))

            # predict ages and genders of the detected faces
            results = model.predict(faces)
            predicted_genders = results[0]
            ages = np.arange(0, 101).reshape(101, 1)
            predicted_ages = results[1].dot(ages).flatten()
            labelage=int(predicted_ages)
            print(labelage)

            # draw results
            for i, d in enumerate(detected):
                label = "{},{}".format(int(predicted_ages[i]),
                                        "M" if predicted_genders[i][0] < 0.5 else "F")
                draw_label(img, (d.left(), d.top()), label)

                label1=label.split(',')
                label_gender=label1[1]
                count=0
                for age1,age2 in zip(From_Age,To_Age):
                        global add,add_image
                        if age1 < labelage < age2 and label_gender==Gender[count]:
                            #add_id=From_Age.index(age1)
                            add=Adds[count]
                            add_image=Images[count]
                        elif age1 < labelage < age2 and label_gender==Gender[count]:
                            #add_id=From_Age.index(age1)
                            add=Adds[count]
                            add_image=Images[count]
                        else:
                            print("No Adds Found")
                        count=count+1

        cv2.imwrite("res.jpg",img)

        cv2.waitKey(0)
        
        load = Image.open("res.jpg")
        load = load.resize((500, 400), Image.ANTIALIAS)
        render = ImageTk.PhotoImage(load)
        img = Label(image=render)
        img.image = render
        img.place(x=100, y=235)
        cap.release()

def click1():
    real_time_video.emotion()

app = tk.Tk()
app.resizable(0,0)
HEIGHT = 750
WIDTH = 700

C = tk.Canvas(app, height=HEIGHT, width=WIDTH)
background_image= tk.PhotoImage(file='./background.png')
background_label = tk.Label(app, image=background_image, bd=1)
background_label.place(x=0, y=0, relwidth=1, relheight=1)
background_label.pack()
C.pack()

frame = tk.Frame(app,  bg='#42c2f4', bd=5)
frame.place(relx=0.5, rely=0.24, relwidth=1, relheight=1, anchor='n')

submit = tk.Button(frame,font=40, text='Age Gender',height=1,width="13",command=lambda: click())
submit.grid(row=2, column=4,padx=100,pady=20)

submit1 = tk.Button(frame,font=40, text='Emotion',height=1,width="13",command=lambda: click1())
submit1.grid(row=2, column=6,padx=100,pady=20)


lower_frame = tk.Frame(app, bg='#42c2f4', bd=10)
lower_frame.place(relx=0.5, rely=0.46, relwidth=0.75, relheight=0.6, anchor='n')

app.mainloop()
