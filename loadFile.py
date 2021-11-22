from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar 
from kivy.clock import Clock
from numpy import asarray
from PIL import Image
from mtcnn.mtcnn import MTCNN

import os
import cv2
import sqlite3
import threading
import time

from widget import ImageButton


class PickerLayout(FloatLayout):
    db = ObjectProperty({'dbName': 'data.db', 'tableName': 'data'})
    images = ListProperty([])
    labels = ListProperty([])
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # orientation = 'horizontal'
        size_hint = (1,0.4)
        self.detector = MTCNN()
        self.target_size = (224,224)
        self.progress_value = 0
        self.thread_flag = False
        self.inputBox = BoxLayout(orientation = 'horizontal', 
                                  spacing = 5,
                                  size_hint = (None, None), 
                                  width = 495, 
                                  height = 30, 
                                  pos_hint = {'center_x':0.5, 'center_y': 0.5})
        # Link or path
        self.linkBox = BoxLayout(orientation = 'horizontal',
                                 size_hint = (None, None), 
                                 width = 230, 
                                 height = 30, 
                                 pos_hint = {'center_x':0.5, 'center_y': 0.5})
        self.linkText = TextInput(text = '',
                                  hint_text = 'Image / Folder Path',
                                  disabled = True,
                                  background_color = [186, 187, 221, 0.8],
                                  size_hint = (None, None),
                                  width = 200,
                                  height = 30)
        self.linkButton = ImageButton(source = 'images/folder2.png', 
                                      size = (30,30), 
                                      pos_hint = {'center_x':0.5, 'center_y':0.5}) 
        self.popup = Popup(title='Test popup',
                           content=Label(text='Hello world'),
                           size_hint=(None, None), 
                           size=(400, 400))
        # Label
        self.labelText = TextInput(hint_text = 'Type your image label',
                                   text = '',
                                   background_color = [186, 187, 221, 0.8],
                                   size_hint = (None, None),
                                   width = 200,
                                   height = 30)
        # Input button
        self.inputButton = Button(text = 'Add',
                                #   background_color = [190, 103, 175, 0.8],
                                  size = (50,30))

        # Progress bar
        self.progressBar = ProgressBar()
        self.progressPop = Popup(title = 'Please wait while we preprocess your images',
                                 content = self.progressBar,
                                 size_hint=(0.8, 0.2),
                                 auto_dismiss = False)
        

        self.linkBox.add_widget(self.linkText)
        self.linkBox.add_widget(self.linkButton) 
        self.inputBox.add_widget(self.linkBox)
        self.inputBox.add_widget(self.labelText)
        self.inputBox.add_widget(self.inputButton)
        self.add_widget(self.inputBox)

        self.linkButton.bind(on_release = self.show_load)
        self.inputButton.bind(on_release = self.progressUp)

            
    def show_load(self, instance):
        filechooser = ObjectProperty()
        self.loadBox = BoxLayout(orientation = 'vertical')
        self.popup = Popup(title="Load file", content = self.loadBox,
                            size_hint=(0.6, 0.6))
        self.fileChooser = FileChooserIconView(dirselect = True,
                                               filters = ['*.png', '*.jpg', '*.jpeg'])
        self.buttonBox = BoxLayout(orientation = 'horizontal',
                                   size_hint = (1, None),
                                   height = 30)
        self.buttonLoad = Button(text = 'Load File')
        self.buttonCancel = Button(text = 'Cancel')
        self.buttonBox.add_widget(self.buttonLoad)
        self.buttonBox.add_widget(self.buttonCancel)
        self.loadBox.add_widget(self.fileChooser)
        self.loadBox.add_widget(self.buttonBox)
        self.popup.open()
        self.fileChooser.bind(selection = self.load_folder)
        self.buttonLoad.bind(on_press = self.load)
        self.buttonCancel.bind(on_press = self.cancel)


    def cancel(self, instance):
        self.linkText.text = ''
        self.popup.dismiss()
    
    def load(self, instance):
        self.popup.dismiss()

    def load_folder(self, obj, val):
        # print(val)
        self.linkText.text = str(self.fileChooser.selection[0])
    
    def progressUp(self, instance):
        self.progressPop.open()
        self.thread_flag = True
        self.ev = threading.Event()
        self.thread = threading.Thread(target = self.add_images)
        self.thread.start()
    
    def dismiss(self, *args):
        self.ev.clear()
        self.thread_flag = False
        self.progressPop.dismiss()
    
    def clock(self, *args):
        #Stops the clock when the progress bar value reaches its maximum
        if self.progress_value >= 100:
            Clock.unschedule(self.clock)
        self.progressBar.value = self.progress_value

        
    def add_images(self):
        print("Adding Images")
        self.progress_value = 0
        Clock.schedule_interval(self.clock, 1 / 60)
        label = str(self.labelText.text)
        if self.thread_flag:
            try:
                path = str(self.linkText.text)
                print(path)
                if os.path.isdir(path):
                    images = os.listdir(path)
                    self.value = round(100 / (len(images) * 4))
                    for image in images:
                        image_path = os.path.join(path, image)
                        image = cv2.imread(image_path)
                        # print(image.shape)
                        self.progress_value += self.value
                        image = self.preprocessImages(image, self.target_size)
                        self.images.append(image)
                        self.labels.append(label)
                        self.progress_value += self.value
                        print("image added")
                    self.dismiss()
                    # print(len(self.images))
                    # print(len(self.labels))
                
                elif os.path.isfile(path):
                    self.value = 25
                    image = cv2.imread(path)
                    self.progress_value += self.value
                    image = self.preprocessImages(image, self.target_size)
                    # print(image.shape)
                    self.images.append(image)
                    self.labels.append(label)
                    self.progress_value += self.value
                    self.dismiss()
                    print("image added")

            except:
                print('Failed to add images')
        self.labelText.text = ''
        self.linkText.text = ''
        
    def resizeImage(self, img, target_size= (224,224), fill_color=(0, 0, 0)):
        factor1 = target_size[0] / img.size[0]
        factor2 = target_size[1] / img.size[1]
        factor = min(factor1, factor2)
        
        new_size = (int(img.size[0] * factor), int(img.size[1] * factor))
        img = img.resize(new_size)
        
        new_im = Image.new('RGB', target_size, fill_color)
        new_im.paste(img, (int((target_size[0] - img.size[0]) / 2), int((target_size[1] - img.size[1]) / 2)))
        self.progress_value += self.value
        return new_im

    def preprocessImages(self, img, size = (224, 224)):
        result = self.detector.detect_faces(img)
        # print(result[0]['box'])
        x1, y1, width, height = result[0]['box']
        x2, y2 = x1 + width, y1 + height
        face = img[y1:y2, x1:x2]
        image = Image.fromarray(face)
        image = self.resizeImage(image, (224,224), fill_color=(0, 0, 0))
        face_array = asarray(image)
        self.progress_value += self.value
        return face_array
    
    # harusnya di file trainModel
    # def load_files(self, instance):
    #     # print(len(self.images))
    #         =
