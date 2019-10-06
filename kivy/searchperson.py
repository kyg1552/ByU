#-*- coding: utf-8 -*-

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

import requests
from io import BytesIO
from PIL import Image, ImageDraw , ImageFont
import cognitive_face as CF
import textwrap
import argparse

KEY = '819a2da808d24811a7b9fa765545a0ad' 
CF.Key.set(KEY)

BASE_URL = 'https://bora.cognitiveservices.azure.com/face/v1.0' 
CF.BaseUrl.set(BASE_URL)

class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.cols = 1

        self.inside = GridLayout()
        self.inside.cols = 2

        self.inside.add_widget(Label(text="Group Name: "))
        self.group = TextInput(multiline=False)
        self.inside.add_widget(self.group)

        self.inside.add_widget(Label(text="Image: "))
        self.image = TextInput(multiline=False)
        self.inside.add_widget(self.image)

        self.add_widget(self.inside)

        self.submit = Button(text="Submit", font_size=40)
        self.submit.bind(on_press=self.pressed)
        self.add_widget(self.submit)

    def getRectangle(self, faceDictionary):
        rect = faceDictionary['faceRectangle']
        left = rect['left']
        top = rect['top']
        bottom = left + rect['height'] 
        right = top + rect['width']
        return ((left, top), (bottom, right))

    def getRectangleFont(self, faceDictionary):
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

    def pressed(self, instance):
        group = self.group.text
        image = "./"+ self.image.text

        PERSON_GROUP_ID = group
        response = CF.face.detect(image)

        face_ids = [d['faceId'] for d in response]
        identified_faces = CF.face.identify(face_ids, PERSON_GROUP_ID)

        # compared image
        img_url = image
        faces = CF.face.detect(img_url,True,False,'age,gender')

        # Download the image from the url
        img = Image.open(img_url)

        # For each face returned use the face rectangle and draw a white box.
        draw = ImageDraw.Draw(img)

        Face_match = []
        Face_candidates = []

        fnt = ImageFont .  truetype ( 'Pillow/Tests/fonts/FreeMono.ttf' , 15 ) #' ' , (font size)
        
        for f in identified_faces: 
            Face_match.append(f['faceId']) #얼굴식별 id를 리스트에 저장
            Face_candidates.append(f['candidates']) #얼굴 매칭 정보를 리스트에 저장

        print Face_match 
        print Face_candidates

        count = 0

        for face in faces: #얼굴 수 만큼 루프
            # m = 'FaceID:' + str( Face_match[count])
            c = 'Candidates:' + str( Face_candidates[count]) #변수에 리스트에 있는 매칭 정보를 하나씩 저장 
            draw.rectangle(self.getRectangle(face), outline='red') #사각형을 그리는함수
            lines = textwrap.wrap(c, width=20) #줄바꿈을 위한 함수 넒이 20포인트 c는 매칭정보 
            y_text = self.getRectangleFont3(face) #디텍팅된 얼굴크기에서 왼쪽 아래 좌표를 저장하는 변수
            for line in lines: #lines 에 저장된 문자열의 수만큼 반복
                draw.text((self.getRectangleFont2(face),y_text), line, font=fnt, fill=(0,0,0,255))#텍스트를 그리는 함수
                #
                y_text += 15 #줄바꿈( maching by font size)
        #       draw.rectangle((getRectangleFont2(face),y_text),fill='white' ,outline=None)
        #       draw.text(getRectangleFont(face),m,font=fnt,fill=(255,255,255,255))
            count = count + 1

                # Display the image in the users default image browser.
        img.show()

        print("group: ", group, "image: ", image)

        self.group.text = ""
        self.image.text = ""

class SearchPersonApp(App):
    def build(self):
        return MyGrid()


if __name__ == "__main__":
    SearchPersonApp().run()