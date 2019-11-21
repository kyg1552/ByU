#-*- coding: utf-8 -*-
#! /usr/bin/env python2

#    Documentation
#
#    project     : Customized advertising transmission mobile robot using MicroSoft Face API
#    Team        : By U(Capstone Design Project)
#    Member      : Young-gi Kim, Geon-Hee Ryu, Eui-song Hwang, Byeong-Ho Lee
#    Last Modify : 2019. 11. 15
#        
# Ocams-1cgn-U & openCV
import liboCams
import cv2
import time
import sys
import numpy as np

# Face API
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import cognitive_face as CF
import textwrap

# Mongo DB
import pymongo
from pymongo import MongoClient

from moviepy.editor import *  

#face api key 받아서 사용하는 부분
KEY = 'bdac449abb36444cb6bc5a53867a0fd0' #12월 7일까지
CF.Key.set(KEY)

BASE_URL = 'https://byu2.cognitiveservices.azure.com/face/v1.0'
CF.BaseUrl.set(BASE_URL)

class Byu:
    def __init__(self, group, image_queue, place, playtime, resolution_index):
        
        self.playtime = playtime
        self.cur_place = place
        self.index = resolution_index

        self.group = group # 찾고자 하는 인물을 등록한 그룹
        self.Accuracy = 0 # 찾고자하는 인물 정확도

        self.cur_time = time.strftime('%Y%m%d_%H%M%S') # 현재 연/월/일 시간:분:초

        self.collection = MongoClient("localhost", 27017).test.test

        self.gender_age_data = [] # 데이터 셋 4개씩 담을 리스트
        self.data_count = 0 # 이미지 처리한 횟수(프로세스 동작한 횟수 카운트)
        self.image_queue = image_queue # 처리할 이미지 큐
        
        self.start_check = False # 데이터가 없는 경우, 디폴트 광고를 송출
        self.adv_check = False
        self.capture_result = False # 카메라가 정상적으로 동작해서 촬영을 했는지 확인하는 변수

        self.male_max_index = 0
        self.female_max_index = 0
        self.costomer_face_img = " " # 카메라로부터 찍은 원본 이미지
        self.processing_img = " " # 히스토그램 평활화를 한 이미지 -> 너무 밝거나 너무 어두운 이미지는 얼굴 인식이 안되서 평활화 처리를 함.

        self.video_file = '/home/byu/byU_main/adv/male50_QR.mp4' # default 광고

        self.data = {}
        self.gender_age = []
        self.people = 0
        self.customer_data = []
        self.male = np.zeros(6) #남성 연령대 인원 수  10~19, 20~29, 30~39, 40~49, 50~59, 60~69
        self.female = np.zeros(6) #여성 연령대 인원 수 10~19, 20~29, 30~39, 40~49, 50~59, 60~69

    def img_histequalize(self, original_img, precessing_img):
        img = cv2.imread(original_img)
        
        img_yuv = cv2.cvtColor(img, cv2.COLOR_BGR2YUV)

        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])

        img_output = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

        cv2.imwrite(precessing_img, img_output) # 좌측 이미지 저장

    def writeDB(self, db_data):
        self.collection.insert_one(db_data) # 고객 데이터 DB 저장
    
    def readDB(self):
        print("show all DB Data")       
        results = self.collection.find()
        return results

    def printDB(self, results):
        for result in results:
            print(result)

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
            draw.text(self.getRectangleFont(face),n,font=None,fill=(100,0,100,100))
            k += 1

        # Display the image in the users default image browser.
        img.show()

    def getImageOcamS(self, mode = 'day'): # ocam으로 이미지 받기
        self.cur_time = time.strftime('%Y%m%d_%H%M%S') # 현재 연/월/일 시간:분:초
        self.costomer_face_img = '/home/byu/byU_main/advertising_main/costomer_image/' + self.cur_time + '_' + self.cur_place + '.jpg' #이미지를 시간, 장소로 저장
        self.processing_img = '/home/byu/byU_main/advertising_main/processing_image/' + self.cur_time + '_' + self.cur_place + '_p.jpg' #히스토그램 평활화한 이미지 저장 파일명
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
                if mode == 'night':
                    self.img_histequalize(self.costomer_face_img, self.processing_img) # 히스토그램 평활화한 이미지 저장
            else: # oCamS-1CGN-U 카메라가 아닐 경우
                print("Error Not oCamS-1CGN-U")
            
            char = cv2.waitKey(1)
            if char == 27:
                break
            if time.time() > stop_time:
                break
            frame_cnt += 1

        print 'Result Frame Per Second:', frame_cnt/(time.time()-start_time) #camera 구동 시간
        print('------------------------------------------------------')
        print('')

        test.Stop()  
        cv2.destroyAllWindows()
        test.Close()
        ##### 카메라로부터 이미지 받기 끝 ####
    
    def findperson(self, group, img_url):
        PERSON_GROUP_ID = group
        response = CF.face.detect(img_url)

        face_ids = [d['faceId'] for d in response]
        if not face_ids:
            print "Can't Find People! Not Detect Face."
        else:
            identified_faces = CF.face.identify(face_ids, PERSON_GROUP_ID)
            print identified_faces

            # compared image
            faces = CF.face.detect(img_url,True,False,'age,gender')

            # Download the image from the url
            img = Image.open(img_url)

            # For each face returned use the face rectangle and draw a white box.
            draw = ImageDraw.Draw(img)
            
            fnt = ImageFont .  truetype ( 'Pillow/Tests/fonts/FreeMono.ttf' , 15 ) #' ' , (font size)
            
            count = -1
            for f in identified_faces:
                count += 1
                if f['candidates']:
                    self.Accuracy = f['candidates'].pop().get('confidence')
                    if self.Accuracy >= 0.65:
                        print('------------------------------------------------------')
                        print('')
                        print "****등록된 인물 있음*****"
                        print("일치율: %f"%self.Accuracy)
                        print ''
                        
                        #화면에 찾는 인물 바운딩박스와 일치율 표시
                        c = "Accuracy:" + str(self.Accuracy) #변수에 리스트에 있는 매칭 정보를 하나씩 저장 
                        draw.rectangle(self.getRectangle(faces[count]), outline='red') #사각형을 그리는함수
                        lines = textwrap.wrap(c, width=20) #줄바꿈을 위한 함수 넒이 20포인트 c는 매칭정보 
                        y_text = self.getRectangleFont3(faces[count]) #디텍팅된 얼굴크기에서 왼쪽 아래 좌표를 저장하는 변수
                        for line in lines: #lines 에 저장된 문자열의 수만큼 반복
                            draw.text((self.getRectangleFont2(faces[count]),y_text), line, font=fnt, fill=(100,100,255,255))#텍스트를 그리는 함수
                    
                        img.show()
                        
                        break
    
    def getFeature(self, img_url):
        ##### 이미지에서 얼굴을 찾아서 얼굴에서 특징(나이, 성별)추출 시작 ####
        faces = CF.face.detect(img_url, True, False, 'age,gender')

        if not faces: # 얼굴 감지되지 않은 경우
            print("Can't Detected Face!! No get costomer Feature")
        else: #얼굴 감지된 경우
            self.start_check = True

            #self.faceBounding(img_url,faces)
            
            self.data = {}
            
            self.people = 0
            self.customer_data = []
            self.male = np.zeros(6) #남성 연령대 인원 수  10~19, 20~29, 30~39, 40~49, 50~59, 60~69
            self.female = np.zeros(6) #여성 연령대 인원 수 10~19, 20~29, 30~39, 40~49, 50~59, 60~69
       
            for face in faces:
                add = []
                self.data = face['faceAttributes']
        
                add.append(self.data['gender'])
                add.append(self.data['age'])
                self.gender_age.append(add)
                
                self.customer_data.append(self.data['gender'])
                self.customer_data.append(str(self.data['age']))
                self.customer_data.append(self.cur_time)
                self.customer_data.append(self.cur_place)

                DB_data = { 'customer': self.customer_data }
                self.people += 1
            
            self.writeDB(DB_data) # DB에 고객 데이터 저장

            if self.data_count < self.image_queue : ## 지금까지 처리한 데이터(이미지)가 4개 이하이면
                self.gender_age_data.insert(0, self.gender_age) ## 맨 처음에 그대로 새로운 데이터 삽입(전체 데이터 셋에 추가)
            else: ## 지금까지 처리한 데이터(이미지)가 4개 초과이면(5개부터)
                del self.gender_age_data[self.image_queue-1] ## 맨 처음 들어온 데이터(마지막 인덱스) 삭제
                self.gender_age_data.insert(0, self.gender_age) ## 맨 처음에 새로운 데이터 삽입
            self.data_count +=1

            for self.gender_age in self.gender_age_data:  # 최근 데이터 4개 불러옴.
                for gender, age in self.gender_age:  # 남자,여자 각 연령대별 숫자 카운트
                    if gender == 'male' and age >= 10 and age < 20:
                        self.male[5] += 1
                    elif gender == 'male' and age >= 20 and age < 30:
                        self.male[4] += 1              
                    elif gender == 'male' and age >= 30 and age < 40:
                        self.male[3] += 1                       
                    elif gender == 'male' and age >= 40 and age < 50:
                        self.male[2] += 1                       
                    elif gender == 'male' and age >= 50 and age < 60:
                        self.male[1] += 1                       
                    elif gender == 'male' and age >= 60 and age < 70:
                        self.male[0] += 1                       
                    elif gender == 'female' and age >= 10 and age < 20:
                        self.female[5] += 1                      
                    elif gender == 'female' and age >= 20 and age < 30:
                        self.female[4] += 1                       
                    elif gender == 'female' and age >= 30 and age < 40:
                        self.female[3] += 1                       
                    elif gender == 'female' and age >= 40 and age < 50:
                        self.female[2] += 1                      
                    elif gender == 'female' and age >= 50 and age < 60:
                        self.female[1] += 1                       
                    elif gender == 'female' and age >= 60 and age < 70:
                        self.female[0] += 1
                           
            self.male_max_index = self.male.argmax()
            self.female_max_index = self.female.argmax()
            self.adv_check = self.male[self.male_max_index] > self.female[self.female_max_index]
            
            print('------------------------------------------------------')
            print("최근 인식된 총 얼굴 수: %d" %(self.people))
            print("최근 인식된 사람들의 성별,나이 정보")
            print(self.gender_age)
            del self.gender_age[:]

            print('')
            print("현재 누적 데이터 처리 고객 수")
            print("10대 남성: %d"%(self.male[5]))
            print("20대 남성: %d"%(self.male[4]))
            print("30대 남성: %d"%(self.male[3]))
            print("40대 남성: %d"%(self.male[2]))
            print("50대 남성: %d"%(self.male[1]))
            print("60대 남성: %d"%(self.male[0]))
            
            print('')
            print("10대 여성: %d"%(self.female[5]))
            print("20대 여성: %d"%(self.female[4]))
            print("30대 여성: %d"%(self.female[3]))
            print("40대 여성: %d"%(self.female[2]))
            print("50대 여성: %d"%(self.female[1]))
            print("60대 여성: %d"%(self.female[0]))
            print('')
            print('------------------------------------------------------')

    def display(self):
        if self.start_check == False: # 고객 데이터가 없는 경우 디폴트 임의의 광고 송출
            print("Not costomer data") 
            print("Default advertisement")          
            clip = VideoFileClip(self.video_file)
            clip.preview()
        else:
            if self.adv_check:
                if self.male_max_index == 5:
                    print("10대 남성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/male10_QR.mp4'
                elif self.male_max_index == 4:
                    print("20대 남성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/male20_QR.mp4'
                elif self.male_max_index == 3:
                    print("30대 남성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/male30_QR.mp4'
                elif self.male_max_index == 2:
                    print("40대 남성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/male40_QR.mp4'
                elif self.male_max_index == 1:
                    print("50대 남성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/male50_QR.mp4'
                elif self.male_max_index == 0:
                    print("60대 남성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/male60_QR.mp4'
                    
                clip = VideoFileClip(self.video_file)
                clip.preview()
            else:
                if self.female_max_index == 5:
                    print("10대 여성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/female10_QR.mp4'
                elif self.female_max_index == 4:
                    print("20대 여성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/female20_QR.mp4'
                elif self.female_max_index == 3:
                    print("30대 여성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/female30_QR.mp4'
                elif self.female_max_index == 2:
                    print("40대 여성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/female40_QR.mp4'
                elif self.female_max_index == 1:
                    print("50대 여성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/female50_QR.mp4'
                elif self.female_max_index == 0:
                    print("60대 여성 광고 송출")
                    self.video_file = '/home/byu/byU_main/adv/female60_QR.mp4'
            
                clip = VideoFileClip(self.video_file)
                clip.preview()
              
    def advertising(self,mode):
        if mode == 'day':
            self.getImageOcamS()
            self.findperson(self.group, self.costomer_face_img) # 찾고자 하는 사람 찾기

            if self.capture_result == True: # 카메라가 정상적으로 동작한 경우         
                self.getFeature(self.costomer_face_img)
                self.display()
                        
            else: # 카메라가 정상적으로 동작 안한 경우
                print("error: No Face!! or No Camera!!")
                print("Please Check camera")

        elif mode == 'night':
            self.getImageOcamS(mode = 'night')
            self.findperson(self.group, self.processing_img) # 찾고자 하는 사람 찾기
            
            #self.capture_result = True
            #self.processing_img = './image1.JPG'

            if self.capture_result == True: # 카메라가 정상적으로 동작한 경우         
                self.getFeature(self.processing_img)
                self.display()
                        
            else: # 카메라가 정상적으로 동작 안한 경우
                print("error: No Face!! or No Camera!!")
                print("Please Check camera")    

if __name__ == '__main__':
    byu_start = Byu(image_queue = 4,group = 'register3',place = "서울상공회의소",playtime = 1, resolution_index = 5) # find_group, image_queue, place, camera_playtime, resolution_index
    #byu_start.advertising(mode = 'night') #주간 혹은 밝은 곳에서 광고 디스플레이
    #byu_start.printDB(byu_start.readDB())
    #byu_start.advertising(mode = 'day')
    
    try:
        while True:
            #byu_start.advertising(mode = 'day') #주간 혹은 밝은 곳에서 광고 디스플레이
            byu_start.advertising(mode = 'night') #야간 혹은 주변이 어두운 곳에서 광고 디스플레이
            #byu_start.printDB(byu_start.readDB()) # DB에 저장된 데이터 출력
    except KeyboardInterrupt:
        print("KeyboardInterrupt!!")
        cv2.destroyAllWindows()
    



