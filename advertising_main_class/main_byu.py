#-*- coding: utf-8 -*-
#! /usr/bin/env python2



#    Documentation
#
#    project     : Customized advertising transmission mobile robot using MicroSoft Face API
#    Team        : By U(Capstone Design Project)
#    Member      : Young-gi Kim, Geon-Hee Ryu, Eui-song Hwang, Byeong-Ho Lee
#    Date        : 2019. 10. 06
#    Modified    :
#    Description :
#    Reference   :
#         https://potensj.tistory.com/73  - pip, pip3 install 중 permission 관련 오류 해결
#         https://stackoverflow.com/questions/41760385/how-can-i-play-a-mp4-movie-using-moviepy-and-pygame - How play moviepy and pygame
#         http://blog.naver.com/PostView.nhn?blogId=dsz08082&logNo=221373412901&parentCategoryNo=&categoryNo=96&viewDate=&isShowPopularPosts=false&from=postView - pygame install
#         https://github.com/Zulko/moviepy/issues/911  - moviepy install
#         https://yujuwon.tistory.com/entry/python%EC%97%90%EC%84%9C-%EB%8F%99%EC%98%81%EC%83%81-%EC%B2%98%EB%A6%AC%ED%95%98%EA%B8%B0  - How to use moviepy
#         https://github.com/Zulko/moviepy - How to use moviepy, moviepy opensource API
#         https://libsora.so/posts/python-hangul/ - hangul encoding when use python
#         https://azure.microsoft.com/ko-kr/services/cognitive-services/face/ - microsoft Azure 공식 홈페이지.
#         https://docs.microsoft.com/en-us/python/api/azure-cognitiveservices-vision-face/?view=azure-python  - Azure Face API python manual
#         https://blog.naver.com/ljy9378/221463790053 - How to use Face API
#         https://gist.github.com/PandaWhoCodes/6d5f0e3a554d058b1e63851f4e83b800  - Uses local image for Microsoft Azure face API
#         https://stackoverflow.com/questions/40714481/adding-a-local-path-to-microsoft-face-api-by-python - Adding a local path to Microsoft Face API by Python
#         https://stackoverflow.com/questions/50672566/azure-detect-faces-api-how-to-change-the-url-picture-to-a-local-picture - Azure Detect faces API,how to change the URL picture to a local picture?
#         https://social.msdn.microsoft.com/Forums/en-US/e5d72a95-3a44-48bb-b5c9-b261e811d4d9/using-face-api-with-python-and-local-image-files?forum=mlapi - Using face API with Python and local image files
#         https://docs.microsoft.com/ko-kr/azure/cognitive-services/face/tutorials/faceapiinpythontutorial - 빠른 시작: 이미지에서 얼굴을 감지 및 포착하는 Python 스크립트 만들기

# Ocams-1cgn-U & openCV
import liboCams
import cv2
import time
import sys
import numpy as np

# Face API
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import cognitive_face as CF

# Mongo DB
#import pymongo
#from pymongo import MongoClient

from moviepy.editor import *  

#face api key 받아서 사용하는 부분
KEY = '819a2da808d24811a7b9fa765545a0ad' #재홍
CF.Key.set(KEY)

BASE_URL = 'https://bora.cognitiveservices.azure.com/face/v1.0'
CF.BaseUrl.set(BASE_URL)

class Byu:
    def __init__(self, data_max, place, playtime, resolution_index):
        
        self.playtime = playtime
        self.cur_place = place
        self.index = resolution_index

        self.cur_time = time.strftime('%Y%m%d_%H%M%S') # 현재 연/월/일 시간:분:초

        #self.collection = MongoClient("localhost", 27017).test.test
        #self.results_DB

        self.gender_age_data = [] # 데이터 셋 4개씩 담을 리스트
        self.data_count = 0 # 이미지 처리한 횟수(프로세스 동작한 횟수 카운트)
        self.data_max = data_max # 처리할 이미지 갯수 약 4개 당 약 1분
        
        self.start_check = False # 데이터가 없는 경우, 디폴트 광고를 송출
        self.adv_check = False
        self.capture_result = False # 카메라가 정상적으로 동작해서 촬영을 했는지 확인하는 변수

        self.male_max_index = 0
        self.female_max_index = 0
        self.costomer_face_img = " "

        self.video_file = '/home/younggi/byU_main/adv/female30_QR.mp4'

    ##### 이미지에서 얼굴을 찾아서 bounding box 시작 ####
    # Convert width height to a point in a rectangle
    def getRectangle(self,faceDictionary):
        rect = faceDictionary['faceRectangle']
        left = rect['left']
        top = rect['top']
        bottom = left + rect['height']
        right = top + rect['width']
        return ((left, top), (bottom, right))

    def getRectangleFont(self,faceDictionary):
        rect = faceDictionary['faceRectangle']
        left = rect['left']
        top = rect['top']
        right = top + rect['width']
        return (left, right)
    
    def getRectangleFont2(self, faceDictionary):
        rect = faceDictionary['faceRectangle']
        left = rect['left']
        return (left)

    def getRectangleFont3(self, faceDictionary):
        rect = faceDictionary['faceRectangle']
        top = rect['top']
        right = top + rect['width'] 
        return (right)
    
    def faceBounding(self, img_url, faces):
        ####show Face BBox and numbering
        # Download the image from the url
        img = Image.open(img_url)

        # For each face returned use the face rectangle and draw a red box.
        draw = ImageDraw.Draw(img)
        k = 1
        for face in faces: # 캡쳐한 이미지의 얼굴들 빨간색 사각형 밑 번호 표시
            draw.rectangle(self.getRectangle(face), outline='red')
            n = str(k)
            draw.text(self.getRectangleFont(face),n,font=None,fill=(0,0,0,255))
            k += 1

        # Display the image in the users default image browser.
        img.show()
        #img.close()
        ##### 이미지에서 얼굴을 찾아서 bounding box 끝 ####

    """
    def writeDB(self, db_data):
        self.collection.insert_one(db_data) # 고객 데이터 DB 저장
    
    def readDB(self):
        print("show all DB Data")       
        results = self.collection.find()
        return results

    def printDB(self, results):
        for result in results:
            print(result)
    """
    def getImage(self): # 웹캠 버전
        self.cur_time = time.strftime('%Y%m%d_%H%M%S') # 현재 연/월/일 시간:분:초
        self.costomer_face_img = '/home/younggi/byU_main/advertising_main_class/costomer_image/' + self.cur_time + '_' + self.cur_place + '.jpg' #이미지를 시간, 장소로 저장
        cap = cv2.VideoCapture(0) # using USB0

        self.capture_result = False

        if cap.isOpened(): # 사람들 사진촬영하는 부분
            while True:
                ret, frame = cap.read()
                
                if ret:
                    self.capture_result = True
                    cv2.imwrite(self.costomer_face_img, frame)
                    break
                else:
                    self.capture_result = False
                    print('no frame!')
                    break
        else:
            self.capture_result = False
            print('no camera!')

        cap.release()
        cv2.destroyAllWindows()
        
    
    def getImageOcamS(self): # ocam으로 이미지 받기
        self.cur_time = time.strftime('%Y%m%d_%H%M%S') # 현재 연/월/일 시간:분:초
        self.costomer_face_img = '/home/byu/byU_main/advertising_main/costomer_image/' + cur_time + '_' + self.cur_place + '.jpg' #이미지를 시간, 장소로 저장

        # 오캠 구동을 위한 준비 과정
        devpath = liboCams.FindCamera('oCam')
        if devpath is None:
            exit()

        test = liboCams.oCams(devpath, verbose=1)

        fmtlist = test.GetFormatList()
        ctrlist = test.GetControlList()
        test.Close()
        # 오캠 구동을 위한 준비 과정

        # 오캠으로 영상 받기.
        test = liboCams.oCams(devpath, verbose=0)
        test.Set(fmtlist[self.index])
        print 'SET', fmtlist[self.index]
        name = test.GetName()
        test.Start()

        start_time = time.time()
        stop_time = start_time + float(self.playtime)

        ##### 카메라로부터 이미지 받기 시작 ####

        frame_cnt = 0
        self.capture_result = False
          
        # 오캠으로 영상 받기.
        while True:    
            if name == 'oCamS-1CGN-U': # oCamS-1CGN-U 카메라일 경우
                self.capture_result = True # 카메라로부터 이미지를 얻었다면 얻었다고 표시         
                left_ = test.GetFrame(mode=2) # 좌우 카메라 이미지 얻음.
                
                left_ = cv2.cvtColor(left_, cv2.COLOR_BAYER_GB2BGR)
                cv2.imwrite(self.costomer_face_img, left_) # 좌측 이미지 저장

            else: # oCamS-1CGN-U 카메라가 아닐 경우
                print("error Not oCamS-1CGN-U")
            
            char = cv2.waitKey(1)
            if char == 27:
                break
            if time.time() > stop_time:
                break
            frame_cnt += 1

        print 'Result Frame Per Second:', frame_cnt/(time.time()-start_time) #camera 구동 시간

        test.Stop()  
        cv2.destroyAllWindows()
        test.Close()
        ##### 카메라로부터 이미지 받기 끝 ####
    
    def getFeature(self):
        ##### 이미지에서 얼굴을 찾아서 얼굴에서 특징(나이, 성별)추출 시작 ####
        img_url = self.costomer_face_img
        faces = CF.face.detect(img_url, True, False, 'age,gender')
        self.faceBounding(img_url,faces)

        if not faces: # 얼굴 감지되지 않은 경우
            print("Not Detected Face!!")
        else: #얼굴 감지된 경우
            self.start_check = True
            data = {}
            gender_age = []
            people = 0
            customer_data = []
            male = np.zeros(6) #남성 연령대 인원 수  10~19, 20~29, 30~39, 40~49, 50~59, 60~69
            female = np.zeros(6) #여성 연령대 인원 수 10~19, 20~29, 30~39, 40~49, 50~59, 60~69
       
            for face in faces:
                add = []
                data = face['faceAttributes']
        
                add.append(data['gender'])
                add.append(data['age'])
                gender_age.append(add)
                
                customer_data.append(data['gender'])
                customer_data.append(str(data['age']))
                customer_data.append(self.cur_time)
                customer_data.append(self.cur_place)

                DB_data = { 'customer': customer_data }
                people += 1
            
            #self.writeDB(DB_data)

            if self.data_count < self.data_max : ## 지금까지 처리한 데이터(이미지)가 4개 이하이면
                self.gender_age_data.insert(0, gender_age) ## 맨 처음에 그대로 새로운 데이터 삽입(전체 데이터 셋에 추가)
            else: ## 지금까지 처리한 데이터(이미지)가 4개 초과이면(5개부터)
                del self.gender_age_data[self.data_max-1] ## 맨 처음 들어온 데이터(마지막 인덱스) 삭제
                self.gender_age_data.insert(0, gender_age) ## 맨 처음에 새로운 데이터 삽입
            self.data_count +=1

            for gender_age in self.gender_age_data:  # 최근 데이터 4개 불러옴.
                for gender, age in gender_age:  # 남자,여자 각 연령대별 숫자 카운트
                    if gender == 'male' and age >= 10 and age < 20:
                        male[5] += 1
                    elif gender == 'male' and age >= 20 and age < 30:
                        male[4] += 1              
                    elif gender == 'male' and age >= 30 and age < 40:
                        male[3] += 1                       
                    elif gender == 'male' and age >= 40 and age < 50:
                        male[2] += 1                       
                    elif gender == 'male' and age >= 50 and age < 60:
                        male[1] += 1                       
                    elif gender == 'male' and age >= 60 and age < 70:
                        male[0] += 1                       
                    elif gender == 'female' and age >= 10 and age < 20:
                        female[5] += 1                      
                    elif gender == 'female' and age >= 20 and age < 30:
                        female[4] += 1                       
                    elif gender == 'female' and age >= 30 and age < 40:
                        female[3] += 1                       
                    elif gender == 'female' and age >= 40 and age < 50:
                        female[2] += 1                      
                    elif gender == 'female' and age >= 50 and age < 60:
                        female[1] += 1                       
                    elif gender == 'female' and age >= 60 and age < 70:
                        female[0] += 1
                           
            self.male_max_index = male.argmax()
            self.female_max_index = female.argmax()
            self.adv_check = male[self.male_max_index] > female[self.female_max_index]
                
            print("Now Detected People gender,age:")
            print(gender_age)
            print("Now Detected people: %d" %(people))
            print(str(self.data_max) + " image male and female data")
            print("male 10~19: %d"%(male[5]))
            print("male 20~29: %d"%(male[4]))
            print("male 30~39: %d"%(male[3]))
            print("male 40~49: %d"%(male[2]))
            print("male 50~59: %d"%(male[1]))
            print("male 60~69: %d"%(male[0]))
            print("female 10~19: %d"%(female[5]))
            print("female 20~29: %d"%(female[4]))
            print("female 30~39: %d"%(female[3]))
            print("female 40~49: %d"%(female[2]))
            print("female 50~59: %d"%(female[1]))
            print("female 60~69: %d"%(female[0]))

    def display(self):
        if self.start_check == False: # 고객 데이터가 없는 경우 디폴트 임의의 광고 송출
            print("Not costomer data") 
            print("Default advertisement")          
            clip = VideoFileClip(self.video_file)
            clip.preview()
        else:
            if self.adv_check:
                print("male: %d~%d"%(self.male_max_index*10,self.male_max_index*10+9))
                if self.male_max_index == 5:
                    print("male video 10~")
                    self.video_file = '/home/younggi/byU_main/adv/male10_QR.mp4'
                elif self.male_max_index == 4:
                    print("male video 20~")
                    self.video_file = '/home/younggi/byU_main/adv/male20_QR.mp4'
                elif self.male_max_index == 3:
                    print("male video 30~")
                    self.video_file = '/home/younggi/byU_main/adv/male30_QR.mp4'
                elif self.male_max_index == 2:
                    print("male video 40~")
                    self.video_file = '/home/younggi/byU_main/adv/male40_QR.mp4'
                elif self.male_max_index == 1:
                    print("male video 50~")
                    self.video_file = '/home/younggi/byU_main/adv/male50_QR.mp4'
                elif self.male_max_index == 0:
                    print("male video 60~")
                    self.video_file = '/home/younggi/byU_main/adv/male60_QR.mp4'
                    
                clip = VideoFileClip(self.video_file)
                clip.preview()
            else:
                print("female: %d~%d"%(self.female_max_index*10,self.female_max_index*10+9))
                if self.female_max_index == 5:
                    print("female video 10~")
                    self.video_file = '/home/younggi/byU_main/adv/female10_QR.mp4'
                elif self.female_max_index == 4:
                    print("female video 20~")
                    self.video_file = '/home/younggi/byU_main/adv/female20_QR.mp4'
                elif self.female_max_index == 3:
                    print("female video 30~")
                    self.video_file = '/home/younggi/byU_main/adv/female30_QR.mp4'
                elif self.female_max_index == 2:
                    print("female video 40~")
                    self.video_file = '/home/younggi/byU_main/adv/female40_QR.mp4'
                elif self.female_max_index == 1:
                    print("female video 50~")
                    self.video_file = '/home/younggi/byU_main/adv/female50_QR.mp4'
                elif self.female_max_index == 0:
                    print("female video 60~")
                    self.video_file = '/home/younggi/byU_main/adv/female60_QR.mp4'
            
                clip = VideoFileClip(self.video_file)
                clip.preview()
              ##### 얼굴에서 추출된 정보를 이용하여 광고 추출 및 송출 끝 ####
    def advertising(self):
        self.getImage()
        #self.getImageOcams()
        if self.capture_result == True: # 카메라가 정상적으로 동작한 경우         
            self.getFeature()
            self.display()
                    
        else: # 카메라가 정상적으로 동작 안한 경우
            print("error: No Face!! or No Camera!!")
            print("Please Check camera")    

if __name__ == '__main__':
    byu_start = ByU(4, "Deajeon_univ", 1, 5)
    try:
        while True:
            byu_start.advertising()
    except KeyboardInterrupt:
        print("KeyboardInterrupt!!")
        cv2.destroyAllWindows()




