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

class RegisterApp(App):
    GroupName = 'test12_byu'
    ImageName = 'gunryu'
    GroupInfo = 'student'
    img_url = ''

    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        return MyGrid()

    def _on_file_drop(self, window, file_path):
        self.filePath = file_path.decode("utf-8")
        self.img_url = self.filePath
        print 'ok image'

        PERSON_GROUP_ID = self.GroupName
        CF.person_group.create(PERSON_GROUP_ID, self.GroupName)

        name = self.ImageName # name -> image_name
        user_data = self.GroupInfo # user_data -> group_info

        response = CF.person.create(PERSON_GROUP_ID, name, user_data)

        person_id = response['personId']

        CF.person.add_face(self.img_url, PERSON_GROUP_ID, person_id, user_data=None, target_face=None)

        print CF.person.lists(PERSON_GROUP_ID)

        CF.person_group.train(PERSON_GROUP_ID)

        response = CF.person_group.get_status(PERSON_GROUP_ID)
        status = response['status']

        print "Register Ok!"
 
if __name__ == "__main__":
    RegisterApp().run()