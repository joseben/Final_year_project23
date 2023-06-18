import cv2
import numpy as np
import face_recognition

import requests

# ESP32 URL
URL = "http://192.168.1.29"
AWB = True

t=[True]

#******************************************
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file',
         'https://www.googleapis.com/auth/drive']

# Reading Credentails from ServiceAccount Keys file
credentials = ServiceAccountCredentials.from_json_keyfile_name('pythonupdate-390114-82b0be741c4e.json', scope)

# intitialize the authorization object            
gc = gspread.authorize(credentials)

sheet = gc.open('medical data book').sheet1
count= int( sheet.acell('H1').value )+1

#******************************************


# Face recognition and opencv setup
cap = cv2.VideoCapture(URL + ":81/stream")
face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml') # insert the full path to haarcascade file if you encounter any problem

vid = cv2.VideoCapture(0)

def set_resolution(url: str, index: int=1, verbose: bool=False):
    try:
        if verbose:
            resolutions = "10: UXGA(1600x1200)\n9: SXGA(1280x1024)\n8: XGA(1024x768)\n7: SVGA(800x600)\n6: VGA(640x480)\n5: CIF(400x296)\n4: QVGA(320x240)\n3: HQVGA(240x176)\n0: QQVGA(160x120)"
            print("available resolutions\n{}".format(resolutions))

        if index in [10, 9, 8, 7, 6, 5, 4, 3, 0]:
            requests.get(url + "/control?var=framesize&val={}".format(index))
        else:
            print("Wrong index")
    except:
        print("SET_RESOLUTION: something went wrong")

def set_quality(url: str, value: int=1, verbose: bool=False):
    try:
        if value >= 10 and value <=63:
            requests.get(url + "/control?var=quality&val={}".format(value))
    except:
        print("SET_QUALITY: something went wrong")

def set_awb(url: str, awb: int=1):
    try:
        awb = not awb
        requests.get(url + "/control?var=awb&val={}".format(1 if awb else 0))
    except:
        print("SET_QUALITY: something went wrong")
    return awb

if __name__ == '__main__':
    set_resolution(URL, index=8)

    while True:
        if cap.isOpened():
            ret, frame = cap.read()

            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)

                faces = face_classifier.detectMultiScale(gray)
                for (x, y, w, h) in faces:
                    center = (x + w//2, y + h//2)
                    frame = cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 0), 4)

            cv2.imshow("frame", frame)
            cv2.imwrite('Image_Capture.jpg',frame)
            
            face1 = face_recognition.load_image_file('image_folder/usain bolt.jpg')
            face1 = cv2.cvtColor(face1,cv2.COLOR_BGR2RGB)
            #------to find the face location
            face_1 = face_recognition.face_locations(face1)[0]
            #--Converting image into encodings
            train_encode1 = face_recognition.face_encodings(face1)[0]

            #Train 2nd face
            face2 = face_recognition.load_image_file('image_folder/Anoop_sir.jpg')
            face2 = cv2.cvtColor(face2,cv2.COLOR_BGR2RGB)
            #------to find the face location
            face_2 = face_recognition.face_locations(face2)[0]
            #--Converting image into encodings
            train_encode2 = face_recognition.face_encodings(face2)[0]

            #Train 3rd face
            face3 = face_recognition.load_image_file('image_folder/Bejoy_sir.jpg')
            face3 = cv2.cvtColor(face3,cv2.COLOR_BGR2RGB)
            #------to find the face location
            face_3 = face_recognition.face_locations(face3)[0]
            #--Converting image into encodings
            train_encode3 = face_recognition.face_encodings(face3)[0]

            #----- lets testface an image
            testface = face_recognition.load_image_file('Image_Capture.jpg')
            testface = cv2.cvtColor(testface, cv2.COLOR_BGR2RGB)
            testface_encode = face_recognition.face_encodings(testface)[0]

            #cv2.imshow('face1', face1)
            r1=(face_recognition.compare_faces([train_encode1],testface_encode))
            r2=(face_recognition.compare_faces([train_encode2],testface_encode))
            r3=(face_recognition.compare_faces([train_encode3],testface_encode))

            if r1==t:
                print("Usian Blot")
                sheet.update_cell(count, 1, 'Usian Bolt')
                break
            elif r2==t:
                print("Anoop Sir")
                sheet.update_cell(count, 1, 'Anoop Sir')
                break
            elif r3==t:
                print("Bejoy sir")
                sheet.update_cell(count, 1, 'Bejoy Sir')
                break
            else:
                print("Not found")

            key = cv2.waitKey(1)

            if key == ord('r'):
                idx = int(input("Select resolution index: "))
                set_resolution(URL, index=idx, verbose=True)

            elif key == ord('q'):
                val = int(input("Set quality (10 - 63): "))
                set_quality(URL, value=val)

            elif key == ord('a'):
                AWB = set_awb(URL, AWB)

            elif key == 27:
                break
            
    sheet.update('H1', count)
    cv2.destroyAllWindows()
    cap.release()
