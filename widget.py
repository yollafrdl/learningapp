from kivy.uix.image import Image
from kivy.uix.button import ButtonBehavior


class ImageButton (ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass