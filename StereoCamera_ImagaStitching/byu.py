#-*- coding: utf-8 -*-
#! /usr/bin/env python2



#    Documentation
#
#    project     : open-source robot platform providing personalized advertisements
#    Team        : By U
#    Member      : 
#    Date        : 2019. 08.23 
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
from Imagestitching import Image_Stitching # https://github.com/linrl3/Image-Stitching-OpenCV

# Face API
import requests
from io import BytesIO
from PIL import Image, ImageDraw
import cognitive_face as CF

# 광고 송출
import pygame
#from moviepy.editor import * # 아래로 이

#아규먼트 받는 부분
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-a", "--alltest", dest="alltest",
                  action='store_true', help="test all resolution in playtime")
parser.add_option("-t", "--time", dest="playtime", default = 1, type = "int",
                  help="playtime for streaming [sec] intValue, 0 means forever")
parser.add_option("-i", "--index", dest="index", default = 0, type = "int",
                  help="index of resolusion mode")

(options, args) = parser.parse_args()

#face api key 받아서 사용하는 부분
KEY = 'cb4c2e4ffed845308eb05e7d7f5381df'
CF.Key.set(KEY)

BASE_URL = 'https://byu.cognitiveservices.azure.com/face/v1.0'
CF.BaseUrl.set(BASE_URL)

capture_result = False # 카메라가 정상적으로 동작해서 촬영을 했는지 확인하는 변수

##### 이미지에서 얼굴을 찾아서 bounding box 시작 ####
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


#playtime = 1 #카메라 구동 시간
face_cnt = 0 # 저장할 이미지 번호

def byu_robot_main():
	global face_cnt
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
	test.Set(fmtlist[options.index])
	print 'SET', fmtlist[options.index]
	name = test.GetName()
	test.Start()

	start_time = time.time()
	stop_time = start_time + float(options.playtime)


	##### 카메라로부터 이미지 받기 시작 ####
	costomer_face_img = './costomer_image/faceCapture' + str(face_cnt) + '.jpg' #이미지를 번호 넘버링하면서 저장 가능
	left_img = './costomer_image/left_right_image/left_image' + str(face_cnt) + '.jpg'
	right_img = './costomer_image/left_right_image/right_image' + str(face_cnt) + '.jpg'

	frame_cnt = 0

	# 오캠으로 영상 받기.
	while True:	
		if name == 'oCamS-1CGN-U': # oCamS-1CGN-U 카메라일 경우
		    capture_result = True # 카메라로부터 이미지를 얻었다면 얻었다고 표시         
		    left_, right_ = test.GetFrame(mode=2) # 좌우 카메라 이미지 얻음.
		    
		    left_ = cv2.cvtColor(left_, cv2.COLOR_BAYER_GB2BGR)
		    cv2.imwrite(left_img, left_) # 좌측 이미지 저장
	 
		    right_ = cv2.cvtColor(right_, cv2.COLOR_BAYER_GB2BGR)
		    cv2.imwrite(right_img, right_) #우측 이미지 저장

		else: # oCamS-1CGN-U 카메라가 아닐 경우
		    frame = test.GetFrame()
		    rgb = cv2.cvtColor(frame, cv2.COLOR_YUV2BGR_YUYV)
		    capture_result = True # 카메라로부터 이미지를 얻었다면 얻었다고 표시
		
		char = cv2.waitKey(1)
		if char == 27:
		    break
		if time.time() > stop_time:
		    break
		frame_cnt += 1 

	print 'Result Frame Per Second:', frame_cnt/(time.time()-start_time) #camera 구동 시간

	left = cv2.imread(left_img)
	right = cv2.imread(right_img)

	face_img = Image_Stitching().blending(left, right)

	cv2.imwrite(costomer_face_img, face_img)	

	test.Stop()  
	cv2.destroyAllWindows()
	test.Close()

	##### 카메라로부터 이미지 받기 끝 ####

	##### 이미지에서 얼굴을 찾아서 얼굴에서 특징(나이, 성별)추출 시작 ####
	if capture_result != False: # 카메라가 정상적으로 동작한 경우
	   #print("")

	    img_url = costomer_face_img
	    faces = CF.face.detect(img_url, True, False, 'age,gender')

	    data = {}
	    gender_data = []
	    age_data = []
	    gender_age = []
	    people = 0

	    male = np.zeros(8) #남성 연령대 인원 수 0~9, 10~19, 20~29, 30~39, 40~49, 50~59, 60~69, 70~79, 80~89, 90~99
	    female = np.zeros(8) #여성 연령대 인원 수 0~9, 10~19, 20~29, 30~39, 40~49, 50~59, 60~69, 70~79, 80~89, 90~99

	    for face in faces:
		add = []
		data = face['faceAttributes']
		#gender_data.append(data['gender']) # DB 저장 부분
		#age_data.append(data['age'])
		#data = {'age': age_data, 'gender': gender_data}
		add.append(data['gender'])
		add.append(data['age'])
		gender_age.append(add)
		people += 1

	    people_check = 0 # 촬영한 사진에 얼굴이 있는지 판단하는 변수
			     # 얼굴이 감지 안되면 0, 얼굴 감지 시 1

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

	    ##### 이미지에서 얼굴을 찾아서 얼굴에서 특징(나이, 성별)추출 시작 ####

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
	    #img.show()
	    ##### 이미지에서 얼굴을 찾아서 bounding box 끝 ####

	    
	    ##### 얼굴에서 추출된 정보를 이용하여 광고 추출 및 송출 시작 ####
	    from moviepy.editor import *

	    if people_check == 0:
		print("Not Detected Face!!")
	    else: # 카메라에 정상적으로 얼굴이 찍혔다면 광고 찾아서 실행
		male_max_index = male.argmax()
		female_max_index = female.argmax()
		if male[male_max_index] > female[female_max_index]:
		    print("male: %d~%d"%(male_max_index*10,male_max_index*10+9))
		    if male_max_index == 1:
			print("male video 10~")
			video_file = './adv/male10.mp4'
		    elif male_max_index == 2:
			print("male video 20~")
			video_file = './adv/male20.mp4'
		    elif male_max_index == 3:
			print("male video 30~")
			video_file = './adv/male30.mp4'
		    elif male_max_index == 4:
			print("male video 40~")
			video_file = './adv/male40.mp4'
		    elif male_max_index == 5:
			print("male video 50~")
			video_file = './adv/male50.mp4'
		    elif male_max_index == 6:
			print("male video 60~")
			video_file = './adv/male60.mp4'
		    
		    clip = VideoFileClip(video_file)
		    clip.preview()
	    
		else:
		    print("female: %d~%d"%(female_max_index*10,female_max_index*10+9))
		    if female_max_index == 1:
			print("female video 10~")
			video_file = './adv/female10.mp4'
		    elif female_max_index == 2:
			print("female video 20~")
			video_file = './adv/female20.mp4'
		    elif female_max_index == 3:
			print("female video 30~")
			video_file = './adv/female30.mp4'
		    elif female_max_index == 4:
			print("female video 40~")
			video_file = './adv/female40.mp4'
		    elif female_max_index == 5:
			print("female video 50~") 
			video_file = './adv/female50.mp4'
		    elif female_max_index == 6:
			print("female video 60~")
			video_file = './adv/female60.mp4'
		    
		    clip = VideoFileClip(video_file)
		    clip.preview()
		    img.close()
		    pygame.quit()
		    ##### 얼굴에서 추출된 정보를 이용하여 광고 추출 및 송출 끝 ####
	else: # 카메라가 정상적으로 동작 안한 경우
	    print("error: No Face!! or No Camera!!")
	    print("Please Check camera")    
	
	face_cnt+=1

if __name__ == '__main__':
    try:
        while True:
            byu_robot_main()
    except KeyboardInterrupt:
        print("KeyboardInterrupt!!")
        pygame.quit()
	cv2.destroyAllWindows()





