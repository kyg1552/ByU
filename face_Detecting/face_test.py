#-*- coding: utf-8 -*-
#!/bin/python


"""
    Documentation

    project     : Customized advertising transmission mobile robot using MicroSoft Face API
    Team        : By U(Capstone Design Project)
    Member      : Young-gi Kim, Geon-Hee Ryu, Eui-song Hwang, Byeong-Ho Lee
    Date        : 2019. 06. 02 (Test version 0.4)
    Modified    : 
    Description :
    Reference   :
         https://potensj.tistory.com/73
         https://stackoverflow.com/questions/41760385/how-can-i-play-a-mp4-movie-using-moviepy-and-pygame
         http://blog.naver.com/PostView.nhn?blogId=dsz08082&logNo=221373412901&parentCategoryNo=&categoryNo=96&viewDate=&isShowPopularPosts=false&from=postView
         https://github.com/Zulko/moviepy/issues/911
         https://yujuwon.tistory.com/entry/python%EC%97%90%EC%84%9C-%EB%8F%99%EC%98%81%EC%83%81-%EC%B2%98%EB%A6%AC%ED%95%98%EA%B8%B0
         https://github.com/Zulko/moviepy
         https://libsora.so/posts/python-hangul/
         https://azure.microsoft.com/ko-kr/services/cognitive-services/face/
         https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-vision-face/?view=azure-python
         https://blog.naver.com/ljy9378/221463790053
         https://gist.github.com/PandaWhoCodes/6d5f0e3a554d058b1e63851f4e83b800
         https://stackoverflow.com/questions/40714481/adding-a-local-path-to-microsoft-face-api-by-python
         https://stackoverflow.com/questions/50672566/azure-detect-faces-api-how-to-change-the-url-picture-to-a-local-picture
         https://social.msdn.microsoft.com/Forums/en-US/e5d72a95-3a44-48bb-b5c9-b261e811d4d9/using-face-api-with-python-and-local-image-files?forum=mlapi
         https://docs.microsoft.com/ko-kr/azure/cognitive-services/face/tutorials/faceapiinpythontutorial
"""

import requests
from io import BytesIO
from PIL import Image, ImageDraw
import cognitive_face as CF
import cv2
from moviepy.editor import *
import pygame

KEY = '271462f910094fa780016700488a0b62'
CF.Key.set(KEY)

BASE_URL = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'
CF.BaseUrl.set(BASE_URL)

# You can use this example JPG or replace the URL below with your own URL to a JPEG image.

cap = cv2.VideoCapture(1) # using USB1

capture_result = 0

if cap.isOpened():
    while True:
        ret, frame = cap.read()
        
        if ret:
            cv2.imshow('camera', frame)
            if cv2.waitKey(1) != -1:
                #cv2.waitKey(3000)
                cv2.imwrite('test8.jpg', frame)
                break
        else:
            capture_result = -1
            print('no frame!')
            break
else:
    capture_result = -1
    print('no camera!')

cap.release()
cv2.destroyAllWindows()

if capture_result != -1:
    img_url = './test8.jpg'
    #img_url = '../testimg/test5.jpg'
    faces = CF.face.detect(img_url, True, False, 'age,gender')

    data = {}
    gender_data = []
    age_data = []
    gender_age = []
    people = 0

    male = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #0~9, 10~19, 20~29, 30~39, 40~49, 50~59, 60~69, 70~79, 80~89, 90~99
    female = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] #0~9, 10~19, 20~29, 30~39, 40~49, 50~59, 60~69, 70~79, 80~89, 90~99

    for face in faces:
        add = []
        data = face['faceAttributes']
        #gender_data.append(data['gender'])
        #age_data.append(data['age'])
        #data = {'age': age_data, 'gender': gender_data}
        add.append(data['gender'])
        add.append(data['age'])
        gender_age.append(add)
        people += 1

    people_check = 0

    for gender, age in gender_age: # 남자,여자 각 연령대별 숫자 카운트
        if gender == 'male' and age>=0 and age<10:
            male[0] += 1
            people_check = 1
        elif gender == 'male' and age>=10 and age<20:
            male[1] += 1
            people_check = 1
        elif gender == 'male' and age>=20 and age<30:
            male[2] += 1
            people_check = 1
        elif gender == 'male' and age>=30 and age<40:
            male[3] += 1
            people_check = 1
        elif gender == 'male' and age>=40 and age<50:
            male[4] += 1
            people_check = 1
        elif gender == 'male' and age>=50 and age<60:
            male[5] += 1
            people_check = 1
        elif gender == 'male' and age>=60 and age<70:
            male[6] += 1
            people_check = 1
        elif gender == 'male' and age>=70 and age<80:
            male[7] += 1
            people_check = 1
        elif gender == 'male' and age>=80 and age<90:
            male[8] += 1
            people_check = 1
        elif gender == 'male' and age>=90 and age<100:
            male[9] += 1
            people_check = 1
        elif gender == 'female' and age>=0 and age<10:
            female[0] += 1
            people_check = 1
        elif gender == 'female' and age>=10 and age<20:
            female[1] += 1
            people_check = 1
        elif gender == 'female' and age>=20 and age<30:
            female[2] += 1
            people_check = 1
        elif gender == 'female' and age>=30 and age<40:
            female[3] += 1
            people_check = 1
        elif gender == 'female' and age>=40 and age<50:
            female[4] += 1
            people_check = 1
        elif gender == 'female' and age>=50 and age<60:
            female[5] += 1
            people_check = 1
        elif gender == 'female' and age>=60 and age<70:
            female[6] += 1
            people_check = 1
        elif gender == 'female' and age>=70 and age<80:
            female[7] += 1
            people_check = 1
        elif gender == 'female' and age>=80 and age<90:
            female[8] += 1
            people_check = 1
        elif gender == 'female' and age>=90 and age<100:
            female[9] += 1
            people_check = 1
    

    print("gender age set:")
    print(gender_age)
    print("people: %d" %(people))
    print("male 10~19: %d"%(male[1]))
    print("male 20~29: %d"%(male[2]))
    print("male 30~39: %d"%(male[3]))
    print("male 40~49: %d"%(male[4]))
    print("male 50~59: %d"%(male[5]))
    print("male 60~69: %d"%(male[6]))
    print("female 10~19: %d"%(female[1]))
    print("female 20~29: %d"%(female[2]))
    print("female 30~39: %d"%(female[3]))
    print("female 40~49: %d"%(female[4]))
    print("female 50~59: %d"%(female[5]))
    print("female 60~69: %d"%(female[6]))

    male_max_index = 0
    male_max = male[0]
    female_max_index = 0
    female_max = female[0]
    #gender_max_index = 0

    for i in range(1,10): # 남자, 여자 각각 가장 사람이 많은 연령대 골라냄.
        if people_check == 0:
            male_max_index = -1
            female_max_index = -1
            break
        if male_max <= male[i]:
            male_max_index = i
            male_max = male[i]
        if female_max <= female[i]:
            female_max_index = i
            female_max = female[i]

    # Convert width height to a point in a rectangle
    def getRectangle(faceDictionary):
        rect = faceDictionary['faceRectangle']
        left = rect['left']
        top = rect['top']
        bottom = left + rect['height']
        right = top + rect['width']
        return ((left, top), (bottom, right))

    def getRectangleFont(faceDictionary):
        rect = faceDictionary['faceRectangle']
        left = rect['left']
        top = rect['top']
        bottom = left + rect['height']
        right = top + rect['width']
        return (left, right)

    # Download the image from the url
    img = Image.open(img_url)

    # For each face returned use the face rectangle and draw a red box.
    draw = ImageDraw.Draw(img)
    k = 1
    for face in faces: # 캡쳐한 이미지의 얼굴들 빨간색 사각형 밑 번호 표시
        draw.rectangle(getRectangle(face), outline='red')
        n = str(k)
        draw.text(getRectangleFont(face),n,font=None,fill=(255,255,255,255))
        k += 1

    # Display the image in the users default image browser.
    img.show()

    if male_max_index == -1 or female_max_index == -1:
        print("Not Detected Face!!")
    else: # 카메라에 정상적으로 얼굴이 찍혔다면 광고 찾아서 실
        if male[male_max_index] > female[female_max_index]:
            print("male: %d~%d"%(male_max_index*10,male_max_index*10+9))
            if male_max_index == 1:
                print("male video 10~")
                video_file = 'male10.mp4'
                #video_file = './acua.mp4')
            elif male_max_index == 2:
                print("male video 20~")
                video_file = 'male20.mp4'
                #video_file = './acua.mp4'
            elif male_max_index == 3:
                print("male video 30~")
                video_file = 'male30.mp4'
                #video_file = './acua.mp4'
            elif male_max_index == 4:
                print("male video 40~")
                video_file = 'male40.mp4'
                #video_file = './acua.mp4'
            elif male_max_index == 5:
                print("male video 50~")
                video_file = 'male50.mp4'
                #video_file = './acua.mp4'
            elif male_max_index == 6:
                print("male video 60~")
                video_file = 'male60.mp4'
                #video_file = './acua.mp4'
            
            clip = VideoFileClip(video_file)
            clip.preview()
            #cap = cv2.VideoCapture(video_file)
            #if cap.isOpened():
            #    fps = cap.get(cv2.CAP_PROP_FPS)
            #    delay = int(1000/fps)
            #    while True:
            #        ret, img = cap.read()
            #        if ret:
            #            img = cv2.resize(img, dsize=(1080,1920), interpolation=cv2.INTER_NEAREST)
            #            cv2.imshow(video_file, img)
            #            cv2.waitKey(delay)
            #        else:
            #            break
            #else:
            #    print("can't open video.")
    
        else:
            print("female: %d~%d"%(female_max_index*10,female_max_index*10+9))
            if female_max_index == 1:
                print("female video 10~")
                video_file = 'female10.mp4'
                #video_file = './acua.mp4'
            elif female_max_index == 2:
                print("female video 20~")
                video_file = 'female20.mp4'
                #video_file = './acua.mp4'
            elif female_max_index == 3:
                print("female video 30~")
                video_file = 'female30.mp4'
                #video_file = './acua.mp4'
            elif female_max_index == 4:
                print("female video 40~")
                video_file = 'female40.mp4'
                #video_file = './acua.mp4'
            elif female_max_index == 5:
                print("female video 50~") 
                video_file = 'female50.mp4'
                #video_file = './acua.mp4'
            elif female_max_index == 6:
                print("female video 60~")
                video_file = 'female60.mp4'
                #video_file = './acua.mp4'
            
            clip = VideoFileClip(video_file)
            clip.preview()
            #cap = cv2.VideoCapture(video_file)
            #cap = cv2.resize(cap2, None, fx=1000, fy=600, interpolation=cv2.INTER_NEAREST)
            #if cap.isOpened():
            #    fps = cap.get(cv2.CAP_PROP_FPS)
            #    delay = int(1000/fps)
            #    while True:
            #        ret, img = cap.read()
            #        if ret:
            #            img = cv2.resize(img, dsize=(1080,1920), interpolation=cv2.INTER_NEAREST)
            #            cv2.imshow(video_file, img)
            #            cv2.waitKey(delay)
            #        else:
            #            break
            #else:
            #    print("can't open video.")

else:
    print("error: No Face!! or No Camera!!")
    print("Please Check camera")    

pygame.quit()
###############################################################################################################

"""
import pymongo
import json
import datetime
from pymongo import MongoClient

### Connecting mongoDB with MongoClient
client = MongoClient("localhost", 27017)
#username = 'byu'
#password = '1234'
#client = pymongo.MongoClient('localhost' % (username, password))

### Access database
db = client.test  # attribute style
# db = client['test'] # dictionary style

### Made collection in database
collection = db.test # attribute style
# collection = db['test'] # dictionary style
행
### Document Insert ( insert_one(), insert_many() )

collection.insert_one(data)

#data_id = collection.insert_one(data).inserted_id # the way check id(primary key)
#print(data_id)
print('collection.count(): %d' % collection.count())

"""

"""
Search the Document ( find_one(), fine() )
find_one() method : search the fastest one
find_one( dictionary format { key:value } )
find() method : every Documents, which can be searched
"""

"""
results = collection.find()
for result in results:
    print(result)


"""
"""
mongoDB : Json
Pymongo : Dictionary
So, we gotta convert json to Dictionary


d = json.loads(data)
d['date'] = datetime.datetime.utcnow()

postid = db.logging.insert_one(d).inserted_id
"""

"""
How to remove collection: db.test.remove({})
https://cinema4dr12.tistory.com/735

"""

###############################################################################################################




