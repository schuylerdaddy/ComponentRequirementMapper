from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView,FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout

from functools import partial
import os

class FileDialogue(BoxLayout):
    def __init__(self,
                 button_text,
                 on_ok = lambda *args: None,
                 on_cancel = lambda *args: None,
                 default_path = os.getcwd()
, **kwargs):
        super(FileDialogue, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, 1)
        fc = self.get_filechooser(default_path)
        self.add_widget(fc)
        opn_btn = Button(text=button_text, size=(100, 50), size_hint=(None, None))
        cncl_btn = Button(text='Cancel', size=(100, 50), size_hint=(None, None))
        opn_btn.bind(on_release=partial(self.handle_selection, fc))
        cncl_btn.bind(on_release=self.close)
        self.add_widget(opn_btn)
        self.add_widget(cncl_btn)
        self.on_ok = on_ok
        self.on_cancel = on_cancel
        self.popup = Popup(title='Choose File', content=self, auto_dismiss=True)

    def handle_selection(self, filechooser, arg):
        self.handle_path(filechooser.path, filechooser.selection)
        self.popup.dismiss();


    def handle_path(self, path, selection):
        if selection and selection[0]:
            self.on_ok(selection[0])

    def close(self,any):
        if self.popup:
            self.popup.dismiss()
            self.on_cancel()

    def get_filechooser(self, default_path):
        return FileChooserIconView(path=default_path)

    def set_path_callback(self, cb):
        self.path_cb = cb

    def set_fname_callback(self, cb):
        self.fname_cb = cb

    def open(self):
        self.popup.open()


