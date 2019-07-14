from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView,FileChooserIconView
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput


from functools import partial
import os

class SaveFileDialogue(BoxLayout):
    def __init__(self,
                 button_text,
                 on_ok = lambda *args: None,
                 on_cancel = lambda *args: None,
                 default_path = os.getcwd()
, **kwargs):
        super(SaveFileDialogue, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint = (1, 1)
        fc = self.get_filechooser(default_path)
        self.add_widget(fc)
        self.input = TextInput(text=fc.path)
        self.input.size_hint_y = None
        self.input.size = (50,50)
        self.add_widget(self.input)
        opn_btn = Button(text=button_text, size=(100, 50), size_hint=(None, None))
        cncl_btn = Button(text='Cancel', size=(100, 50), size_hint=(None, None))
        opn_btn.bind(on_release=partial(self.handle_selection, fc))
        cncl_btn.bind(on_release=self.close)
        layout = BoxLayout(orientation='horizontal',size_hint=(None,None))
        layout.add_widget(opn_btn)
        layout.add_widget(cncl_btn)
        self.add_widget(layout)
        self.on_ok = on_ok
        self.on_cancel = on_cancel
        self.valid = False
        self.popup = Popup(title='Choose filename to save to', content=self, auto_dismiss=True)

    def handle_selection(self, filechooser, arg):
        filename = os.path.join(os.path.sep, filechooser.path, self.input.text)
        self.handle_path(filename)
        self.popup.dismiss();


    def handle_path(self,selection):
        if selection:
            self.on_ok(selection)
        else:
            self.popup = Popup(title='File not saved', auto_dismiss=True)

    def close(self,any):
        if self.popup:
            self.popup.dismiss()
            self.on_cancel()

    def get_filechooser(self, default_path):
        def assign(fn):
            self.input.text = fn
        def assign_from_path(path):
            if not path or len(path) ==0:
                self.input.text = ''
            else:
                self.input.text = os.path.basename(path[0])
        return FileChooserIconView(path=default_path,
                                   on_submit=lambda x, y,z: assign_from_path(y),
                                   on_entry_added=lambda x, y, z: assign(''))

    def set_path_callback(self, cb):
        self.path_cb = cb

    def set_fname_callback(self, cb):
        self.fname_cb = cb

    def open(self):
        self.popup.open()


