from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.modalview import ModalView
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from GUI.FileDialogue import FileDialogue
import json



class InfoModal(ModalView):
    def __init__(self,txt, **kwargs):
        super(InfoModal, self).__init__(**kwargs)
        self.size_hint=(None, None)
        self.size=(600, 300)
        self.orientation = 'vertical'
        self.auto_dismiss=False
        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(Label(text=txt,size_hint=(None,None),size=(600, 300)))
        content = Button(text='Ok',size_hint=(None,None),size=(100,30))
        anchor_lc = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor_lc.add_widget(content)
        layout.add_widget(anchor_lc)
        self.add_widget(layout)
        content.bind(on_press=self.dismiss)

class InputModal(ModalView):
    def __init__(self,txt, **kwargs):
        super(InputModal, self).__init__(**kwargs)
        self.size_hint=(None, None)
        self.size=(600, 300)
        self.orientation = 'vertical'
        self.auto_dismiss=False
        layout = BoxLayout(orientation = 'vertical')
        layout.add_widget(Label(text=txt,size_hint=(None,None),size=(600, 100)))
        self.input = TextInput(multiline=False,hint_text="What")
        layout.add_widget(self.input)
        content = Button(text='Ok',size_hint=(None,None),size=(100,30))
        anchor_lc = AnchorLayout(anchor_x='center', anchor_y='bottom')
        anchor_lc.add_widget(content)
        layout.add_widget(anchor_lc)
        self.add_widget(layout)
        content.bind(on_press=self.close)

    def assign_text_callback(self,cb):
        self.cb = cb

    def close(self,any):
        self.text = self.input.text
        self.dismiss()
        if self.cb:
            self.cb(self.text)

class CheckboxModal(ModalView):
    intensity_levels ={}
    def __init__(self,txt,list, **kwargs):
        super(CheckboxModal, self).__init__(**kwargs)
        self.size_hint=(None, None)

        gridSize = len(list) * 75
        self.size=(600, 200 + gridSize)
        self.auto_dismiss = False
        g=GridLayout(cols=4)

        self.checked_values ={}
        print(list)
        g.add_widget(Label(text='Req #'))
        g.add_widget(Label(text='High'))
        g.add_widget(Label(text='Medium'))
        g.add_widget(Label(text='Low'))
        for item in list:
            self.add_check_box_group(g,item)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text=txt, size_hint=(None, None), size=(600, 100)))
        layout.add_widget(g)
        content = Button(text='Ok', size_hint=(None, None), size=(100, 30))
        cancel = Button(text='Cancel', size_hint=(None, None), size=(100, 30))
        layout2 = BoxLayout(orientation='horizontal')
        layout2.add_widget(content)
        layout2.add_widget(cancel)
        anchor_lc = AnchorLayout(anchor_x='center', anchor_y='bottom')
        anchor_lc.add_widget(layout2)
        layout.add_widget(anchor_lc)
        self.add_widget(layout)
        content.bind(on_press=self.close)
        cancel.bind(on_press=self.dismiss)

    def assign_callback(self, cb):
        self.cb = cb

    def close(self, any):
        self.dismiss()
        if self.cb:
            self.cb(self.checked_values)

    def add_check_box_group(self,comp,item):
        chigh = CheckBox()
        chigh.color = [1, 3, 1, 3]
        cmed = CheckBox()
        cmed.color = [1, 3, 1, 3]
        clow = CheckBox()
        clow.color = [1, 3, 1, 3]

        def on_checkbox_high(checkbox, value):
            if value:
                cmed.active = False
                clow.active = False
                CheckboxModal.intensity_levels[item] = 'High'
                self.checked_values[item] = {'value': chigh, 'level': "High"}
            else:
                self.checked_values.pop(item, None)

        def on_checkbox_med(checkbox, value):
            if value:
                chigh.active = False
                clow.active = False
                CheckboxModal.intensity_levels[item] = 'Medium'
                self.checked_values[item] = {'value': cmed, 'level': "Medium"}
            else:
                self.checked_values.pop(item, None)

        def on_checkbox_low(checkbox, value):
            if value:
                cmed.active = False
                chigh.active = False
                CheckboxModal.intensity_levels[item] = 'Low'
                self.checked_values[item] = {'value' : clow, 'level' : "Low"}
            else:
                self.checked_values.pop(item, None)

        chigh.bind(active=on_checkbox_high)
        cmed.bind(active=on_checkbox_med)
        clow.bind(active=on_checkbox_low)

        l = Label(bold=True, font_size=20, text=item)
        comp.add_widget(l)
        comp.add_widget(chigh)
        comp.add_widget(cmed)
        comp.add_widget(clow)



class TextLine(Label):
    def __init__(self,txt, **kwargs):
        super(TextLine, self).__init__(**kwargs)
        lbl = Label(height = 35, color = (0, 0, 1, 1), text=txt, size_hint=(None, None))
        self.add_widget(lbl)
        self.height = 35
        self.color = (0, 0, 1, 1)

class RequirementView(ScrollView):
    requirements = {}
    def __init__(self,**kwargs):
        super(RequirementView, self).__init__(**kwargs)
        self.size_hint = (1, 1)
        self.grid = None
        self.rows = []
        self.set_rows()

    def set_rows(self):
        if self.grid:
            self.remove_widget(self.grid)
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, row_default_height='20dp', row_force_default=True)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        add_button = Button(text="Add New Requirement")
        self.grid.add_widget(add_button)
        add_button.bind(on_press=lambda x: self.add_new_row())
        i=0
        for key in self.rows:
            i+=1
            txt = str(i) + ") " + key
            RequirementView.requirements[str(i)] = key
            self.grid.add_widget(Label(text=txt))
        self.add_widget(self.grid)


    def add_row(self,desc):
        self.rows.append(desc)
        self.set_rows()

    def add_new_row(self):
        self.modal = InputModal('Enter the description:')
        self.modal.assign_text_callback(self.add_row)
        self.modal.open()

class RequirementLinkView(BoxLayout):
    def __init__(self,**kwargs):
        super(RequirementLinkView, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.link_ids = []
        self.clear_widgets()
        self.text = Label(text='None')
        self.add_widget(self.text)
        self.btn = Button(text="Add Linked Requirements")
        self.btn.bind(on_press=lambda x: self.assign_requirement_ids())
        self.add_widget(self.btn)

    def assign_requirement_ids(self):
        c = CheckboxModal('Select Requirements',list(map(lambda x: str(x),range(1,len(RequirementView.requirements)+1))))
        c.assign_callback(self.populate_label)
        c.open()

    def populate_label(self, dict):
        self.link_ids = []
        for id,cbox in dict.items():
            print(cbox)
            if cbox['value'].active:
                self.link_ids.append(id)
        self.text.text = ','.join(self.link_ids)

class ComponentItem(BoxLayout):
    def __init__(self,txt,**kwargs):
        super(ComponentItem, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.text = txt
        self.add_widget(Label(text=txt))
        self.requirement_view = RequirementLinkView()
        self.add_widget(self.requirement_view)

class ComponentView(ScrollView):
    components = []
    def __init__(self,**kwargs):
        super(ComponentView, self).__init__(**kwargs)
        self.size_hint = (1, 1)
        self.grid = None
        self.rows = []
        self.set_rows()

    def set_rows(self):
        if self.grid:
            self.remove_widget(self.grid)
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, row_default_height='40dp', row_force_default=True)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        add_button = Button(text="Add New component")
        self.grid.add_widget(add_button)
        add_button.bind(on_press=lambda x: self.add_new_row())
        for key in self.rows:
            self.add_row(key)
        self.add_widget(self.grid)

    def add_row(self, desc):
        c = ComponentItem(desc)
        ComponentView.components.append(c)
        self.grid.add_widget(c)

    def add_new_row(self):
        self.modal = InputModal('Enter the description:')
        self.modal.assign_text_callback(self.add_row)
        self.modal.open()

class Menu(BoxLayout):
    def __init__(self, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.orientation = 'horizontal'
        exprt_btn = Button(text='Export', size_hint=(None, None), size=(100, 50))
        exprt_btn.bind(on_press=self.generate_popup)
        self.add_widget(exprt_btn)
        self.add_widget(Button(text='Other', size_hint=(None, None), size=(100, 50)))


    def generate_popup(self, any):
        components = []
        for cmp in ComponentView.components:
            links = cmp.requirement_view
            component = {'name':cmp.text,'requirements':
                list(map(lambda id: {
                    'desc': RequirementView.requirements[id],
                    'level': CheckboxModal.intensity_levels[id]
                }, links.link_ids))}
            components.append(component)
            self.output = {'components':components}
            print(self.output)
            FileDialogue(button_text="Save", on_ok=self.save_components_to_file).open()

    def save_components_to_file(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.output, outfile)

class MappingView(BoxLayout):
    def __init__(self,**kwargs):
        super(MappingView, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.add_widget(ComponentView())
        self.add_widget(RequirementView())

class MainLayout(BoxLayout):
    def __init__(self,**kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(MappingView())
        self.add_widget(Menu())


class ComponentRequirementMapper(App):
    def build(self):

        return MainLayout()

if __name__ == '__main__':
    ComponentRequirementMapper().run()