from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.properties import ListProperty, ObjectProperty

from loadFile import PickerLayout
from trainModel import TrainModel

class MyLayout(BoxLayout):
    myPickerLayout = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        orientation = 'vertical'
        self.mainLayout = GridLayout(rows = 3, size_hint = (1,1))
        self.title = Label(text = "Let's Learn your Images!",
                           size_hint = (1, 0.2),
                           pos_hint = {'center_x':0.5, 'center_y': 0.5})
        self.mainLayout.add_widget(self.title)
        self.myPickerLayout = PickerLayout()
        # self.image = self.myPickerLayout.images
        
        self.mainLayout.add_widget(self.myPickerLayout)
        self.trainLayout = TrainModel()
        self.mainLayout.add_widget(self.trainLayout)
        self.add_widget(self.mainLayout)

        self.myPickerLayout.bind(images = self.trainLayout.getImage)
        self.myPickerLayout.bind(labels = self.trainLayout.getLabel)



class LearningApp(App):
    def build(self):
        return MyLayout()

LearningApp().run()
