import numpy as np
import cv2
import os
import time
import h5py
import dlib
from imutils import face_utils
from keras.models import load_model
import sys
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Dropout
from keras.layers import Dense, Activation, Flatten
import time
from PIL import Image
from Model import model


def getImagesAndLabels():
    path = 'dataset'
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:

        # if there is an error saving any jpegs
        try:
            PIL_img = Image.open(imagePath).convert('L')  # convert it to grayscale
        except:
            continue
        img_numpy = np.array(PIL_img, 'uint8')

        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faceSamples.append(img_numpy)
        ids.append(id)
    return faceSamples, ids


_, ids = getImagesAndLabels()
model = model((32, 32, 1), len(set(ids)))
model.load_weights('trained_model.h5')
model.summary()

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
font = cv2.FONT_HERSHEY_SIMPLEX


def start():
    cap = cv2.VideoCapture(0)
    print('here')
    ret = True

    clip = []
    while ret:
        # read frame by frame
        ret, frame = cap.read()
        nframe = frame
        faces = faceCascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30))

        try:
            (x, y, w, h) = faces[0]
        except:
            continue
        frame = frame[y:y + h, x:x + w]
        frame = cv2.resize(frame, (32, 32))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('result small', frame)
        c = cv2.waitKey(1)
        if c & 0xFF == ord('q'):
            break

        # gray = gray[np.newaxis,:,:,np.newaxis]
        gray = gray.reshape(-1, 32, 32, 1).astype('float32') / 255.
        print(gray.shape)
        prediction = model.predict(gray)
        print("prediction:" + str(prediction))
        labels = ['Victor', 'Lucas']
        prediction = prediction.tolist()

        listv = prediction[0]
        n = listv.index(max(listv))
        print("Highest Probability: " + labels[n] + "==>" + str(prediction[0][n]))
        #        print( "Highest Probability: " + "User " + str(n) + "==>" + str(prediction[0][n]) )
        print("\n")
        for (x, y, w, h) in faces:
            try:
                cv2.rectangle(nframe, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(nframe, str(labels[n]), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
                cv2.putText(nframe, str(confidence), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
            except:
                la = 2
        prediction = np.argmax(model.predict(gray), 1)
        print(prediction)
        cv2.imshow('result', nframe)
        c = cv2.waitKey(1)
        if c & 0xFF == ord('q'):
            break
        #time.sleep(.800)
    cap.release()
    cv2.destroyAllWindows()


start()
