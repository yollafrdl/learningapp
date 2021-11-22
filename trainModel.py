from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.properties import ListProperty, ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar 
from kivy.clock import Clock
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras import Model
from tensorflow.keras.utils import to_categorical
from numpy import asarray
from sklearn import preprocessing
import os
import cv2
import numpy as np
import threading

from loadFile import PickerLayout

class TrainModel(FloatLayout):
    images = ListProperty([])
    labels = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # orientation = 'horizontal'
        size_hint = (1,0.4)
        self.progress_value = 0
        self.thread_flag = False
        # self.image = image
        
        self.trainBox = BoxLayout(orientation = 'horizontal',
                                  size_hint = (None, None),
                                  width = 100,
                                  height = 40,
                                  pos_hint = {'center_x':0.5, 'center_y': 0.5})
        self.trainButton = Button(text = "Train Data",
                                  size = (100,40))
        self.trainBox.add_widget(self.trainButton)
        self.add_widget(self.trainBox)

        self.progressBar = ProgressBar()
        self.progressPop = Popup(title = 'Please wait while we train your images',
                                 content = self.progressBar,
                                 size_hint=(0.8, 0.2),
                                 auto_dismiss = False)

        self.trainButton.bind(on_press = self.progressUp)
        self.data = PickerLayout()
    
    
    def getImage(self, myPickerLayout, images):
        self.images = images

    def getLabel(self, myPickerLayout, labels):
        self.labels = labels

        
    def progressUp(self, instance):
        self.progressPop.open()
        self.thread_flag = True
        self.ev = threading.Event()
        self.thread = threading.Thread(target = self.train)
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

    def train(self):
        Clock.schedule_interval(self.clock, 1 / 60)
        image_input = []
        label_input = []
        for i in self.images:
            image_input.append(i)
        image_input = np.array(image_input)
        
        for i in self.labels:
            label_input.append(i)
        preprocess_label = preprocessing.LabelEncoder()
        label = preprocess_label.fit_transform(label_input)
        label = to_categorical(label)
        print(label.shape)
        num_label = len(label[0])
        model = VGG16(weights='imagenet', 
                                  input_shape=(224, 224, 3),
                                  include_top=False)
        for layer in model.layers:
	        layer.trainable = False

        flat = Flatten()(model.layers[-1].output)
        flat2 = Dense(1024, activation='relu')(flat)
        output = Dense(num_label, activation='softmax')(flat2)
        # define new model
        model = Model(inputs=model.inputs, outputs=output)
        model.compile(optimizer='adam',
                      loss='binary_crossentropy',
                      metrics=['accuracy'])

        epochs = 3
        value = round(100 / epochs)
        for e in range(epochs):
            model.fit(image_input, label, epochs = 1, batch_size = 2)
            self.progress_value += value
        self.dismiss()
        # model.save("new model.h5")
        # print("model saved!")


        # y = model.predict(image_input)
        # print(y)
        # x = y.argmax(axis=-1)
        # print(x)
        # z = preprocess_label.inverse_transform(x)
        # print(z)

     

    