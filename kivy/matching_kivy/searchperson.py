#-*- coding: utf-8 -*-
# .kv 파일을 이용하여 어플 꾸미기

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window

import requests
from io import BytesIO
from PIL import Image, ImageDraw , ImageFont
import cognitive_face as CF
import textwrap

Window.clearcolor = (0.9, 0.9, 0.9, 1)


KEY = '819a2da808d24811a7b9fa765545a0ad' 
CF.Key.set(KEY)

BASE_URL = 'https://bora.cognitiveservices.azure.com/face/v1.0' 
CF.BaseUrl.set(BASE_URL)

class MyGrid(GridLayout):
    pass

class SearchPersonApp(App):
    group = 'test3_byu'
    img_url = ''
    Accuracy = 0

    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        return MyGrid()
    
    def _on_file_drop(self, window, file_path):
        self.filePath = file_path.decode("utf-8")
        self.img_url = self.filePath

        PERSON_GROUP_ID = self.group
        response = CF.face.detect(self.img_url)

        face_ids = [d['faceId'] for d in response]
        identified_faces = CF.face.identify(face_ids, PERSON_GROUP_ID)

        # compared image
        faces = CF.face.detect(self.img_url,True,False,'age,gender')

        # Download the image from the url
        img = Image.open(self.img_url)

        # For each face returned use the face rectangle and draw a white box.
        draw = ImageDraw.Draw(img)
        
        #Accuracy_index = []

        fnt = ImageFont .  truetype ( 'Pillow/Tests/fonts/FreeMono.ttf' , 15 ) #' ' , (font size)
        
        count = 0
        for f in identified_faces:
            if f['candidates']:
                self.Accuracy = f['candidates'].pop().get('confidence')
                if self.Accuracy >= 0.65:
                    print self.Accuracy
                    break
            count += 1

        #print Accuracy_index
        
        c = 'Accuracy:' + str(self.Accuracy) #변수에 리스트에 있는 매칭 정보를 하나씩 저장 
        draw.rectangle(self.getRectangle(faces[count]), outline='red') #사각형을 그리는함수
        lines = textwrap.wrap(c, width=20) #줄바꿈을 위한 함수 넒이 20포인트 c는 매칭정보 
        y_text = self.getRectangleFont3(faces[count]) #디텍팅된 얼굴크기에서 왼쪽 아래 좌표를 저장하는 변수
        for line in lines: #lines 에 저장된 문자열의 수만큼 반복
            draw.text((self.getRectangleFont2(faces[count]),y_text), line, font=fnt, fill=(100,100,255,255))#텍스트를 그리는 함수
            
            #y_text += 15 #줄바꿈( maching by font size)
            
        img.show()

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

    
if __name__ == "__main__":
    SearchPersonApp().run()