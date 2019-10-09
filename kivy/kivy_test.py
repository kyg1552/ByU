#-*- coding: utf-8 -*-

from kivy.app import App
from kivy.core.window import Window

import requests
from io import BytesIO
from PIL import Image, ImageDraw , ImageFont
import cognitive_face as CF
import textwrap


class WindowFileDropExampleApp(App):
    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        return

    def _on_file_drop(self, window, file_path):
        img_url = file_path
        img = Image.open(img_url)
        img.show()
        print(file_path)
        return

if __name__ == '__main__':
    WindowFileDropExampleApp().run()

