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

from GUI.FileDialogue import OpenFileDialogue
from GUI.SaveFileDialogue import SaveFileDialogue

import json

class ComponentRequirementTextFileReader:
    def decorate_line(self,line):
        words = line.strip().split(' ')
        return ' '.join([word.lower().capitalize() for word in words])

    def read_requirements(self,fd):
        req = None
        comps = []
        for line in fd.readlines():
            line = line.strip()
            if not line:
                yield (req,comps)
                comps = []
                req = []
            if not req:
                req = line.strip().capitalize()
            else:
                terms = line.split(':')
                level = terms[1].strip().capitalize()
                comps.append((self.decorate_line(terms[0]), level))
        yield (req,comps)

    def read_mappings(self,filepath):
        reqs = []
        coms = []
        com_data = []
        idx = 1
        with open(filepath,'r') as fd:
            for req in self.read_requirements(fd):
                if req and req[0] and req[1]:
                    reqs.append(req[0])
                    for link in req[1]:
                        comp = link[0]
                        level = link[1]
                        if comp in coms:
                            c_idx = coms.index(comp)
                            com_data[c_idx][1][idx] =level
                        else:
                            coms.append(comp)
                            com_data.append((comp,{idx:level}))
                    idx +=1
        return com_data, reqs

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

class EditLabel(Button):
    def __init__(self, txt=None, **kwargs):
        super(EditLabel, self).__init__(**kwargs)
        self.text = self.format_text(txt) if txt else ''
        self.on_press = self.update

    def update(self):
        modal = InputModal(txt=self.text)
        modal.assign_text_callback(self.change_text)
        modal.open()

    def change_text(self,str):
        self.text = self.format_text(str)

    def format_text(self, txt):
        return txt

class LineNumberedEditLabel(EditLabel):
    def __init__(self, number, txt=None,  **kwargs):
        self.number = number
        super(LineNumberedEditLabel, self).__init__(txt=txt,**kwargs)

    def format_text(self,txt):
        RequirementView.requirements[self.number] = txt
        return '{}) {}'.format(self.number,txt)

class CheckboxModal(ModalView):
    intensity_levels ={}
    def __init__(self,txt,list,existing=None, **kwargs):
        super(CheckboxModal, self).__init__(**kwargs)
        self.size_hint=(None, None)

        gridSize = len(list) * 75
        self.size=(600, 200 + gridSize)
        self.auto_dismiss = False
        g=GridLayout(cols=4)

        self.checked_values ={}
        g.add_widget(Label(text='Req #'))
        g.add_widget(Label(text='High'))
        g.add_widget(Label(text='Medium'))
        g.add_widget(Label(text='Low'))
        for item in list:
            if existing and item in existing:
                self.add_check_box_group(g, item, existing[item])
            else:
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
            links = {}
            for id,data in self.checked_values.items():
                if data['value'].active:
                    links[id] = data['level']
            self.cb(links)

    def add_check_box_group(self,comp,item,existing_level=None):
        chigh = CheckBox()
        chigh.color = [1, 3, 1, 3]
        cmed = CheckBox()
        cmed.color = [1, 3, 1, 3]
        clow = CheckBox()
        clow.color = [1, 3, 1, 3]

        if existing_level:
            if existing_level.lower() == 'high':
                chigh.active = True
                self.checked_values[item] = {'value': chigh, 'level': "High"}
            if existing_level.lower() == 'medium':
                cmed.active = True
                self.checked_values[item] = {'value': cmed, 'level': "Medium"}
            if existing_level.lower() == 'low':
                clow.active = True
                self.checked_values[item] = {'value': clow, 'level': "Low"}

        def on_checkbox_high(checkbox, value):
            if value:
                cmed.active = False
                clow.active = False
                CheckboxModal.intensity_levels[item] = 'High'
                self.checked_values[item] = {'value': chigh, 'level': "High"}
            else:
                CheckboxModal.intensity_levels[item] = None
                self.checked_values.pop(item, None)

        def on_checkbox_med(checkbox, value):
            if value:
                chigh.active = False
                clow.active = False
                CheckboxModal.intensity_levels[item] = 'Medium'
                self.checked_values[item] = {'value': cmed, 'level': "Medium"}
            else:
                CheckboxModal.intensity_levels[item] = None
                self.checked_values.pop(item, None)

        def on_checkbox_low(checkbox, value):
            if value:
                cmed.active = False
                chigh.active = False
                CheckboxModal.intensity_levels[item] = 'Low'
                self.checked_values[item] = {'value' : clow, 'level' : "Low"}
            else:
                CheckboxModal.intensity_levels[item] = None
                self.checked_values.pop(item, None)

        chigh.bind(active=on_checkbox_high)
        cmed.bind(active=on_checkbox_med)
        clow.bind(active=on_checkbox_low)

        l = Label(bold=True, font_size=20, text=str(item))
        comp.add_widget(l)
        comp.add_widget(chigh)
        comp.add_widget(cmed)
        comp.add_widget(clow)

class RequirementView(ScrollView):
    requirements = {}
    def __init__(self,requirements=None,**kwargs):
        super(RequirementView, self).__init__(**kwargs)
        self.size_hint = (1, 1)
        self.grid = None
        if requirements:
            self.rows = requirements
        else:
            self.rows = []
        self.set_rows()

    def set_rows(self):
        if self.grid:
            self.remove_widget(self.grid)
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, row_default_height='20dp', row_force_default=True)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        add_button = Button(text="Add New Requirement",background_color=[0,0,1,1])
        self.grid.add_widget(add_button)
        add_button.bind(on_press=lambda x: self.add_new_row())
        i=0
        for key in self.rows:
            i+=1
            RequirementView.requirements[i] = key
            self.grid.add_widget(LineNumberedEditLabel(number=i,txt=key))
        self.add_widget(self.grid)


    def add_row(self,desc):
        self.rows.append(desc)
        self.set_rows()

    def add_new_row(self):
        self.modal = InputModal('Enter the description:')
        self.modal.assign_text_callback(self.add_row)
        self.modal.open()

class RequirementLinkView(BoxLayout):
    def __init__(self,requirement_links=None,**kwargs):
        super(RequirementLinkView, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.link_ids = []
        self.clear_widgets()
        self.text_label = Label(text = 'None')
        self.tag=None
        if requirement_links:
            self.populate_label(requirement_links)
        self.add_widget(self.text_label)
        self.btn = Button(text="Add Linked Requirements")
        self.btn.bind(on_press=lambda x: self.assign_requirement_ids())
        self.add_widget(self.btn)

    def assign_requirement_ids(self):
        all_labels = range(1,len(RequirementView.requirements)+1)
        c = CheckboxModal('Select Requirements',all_labels,self.tag)
        c.assign_callback(self.populate_label)
        c.open()

    def populate_label(self, link_items):
        self.link_ids = []
        for id in link_items:
            self.link_ids.append(str(id))
        self.text_label.text = ','.join([str(id) for id in self.link_ids])
        self.tag = link_items


class ComponentItem(BoxLayout):
    def __init__(self,txt,requirement_links=None,**kwargs):
        super(ComponentItem, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.text = txt
        self.label = EditLabel(txt=txt)
        self.add_widget(self.label)
        self.requirement_view = RequirementLinkView(requirement_links=requirement_links)
        self.add_widget(self.requirement_view)

    def get_text(self):
        return self.label.text

class ComponentView(ScrollView):
    components = []
    def __init__(self,component_data=None,**kwargs):
        super(ComponentView, self).__init__()
        self.size_hint = (1, 1)
        self.grid = None
        self.rows = []
        self.set_rows()
        if component_data:
            for comp, req_links in component_data:
                self.add_row(comp,reqs=req_links)

    def set_rows(self):
        if self.grid:
            self.remove_widget(self.grid)
        self.grid = GridLayout(cols=1, spacing=10, size_hint_y=None, row_default_height='40dp', row_force_default=True)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        add_button = Button(text="Add New component",background_color=[0,0,1,1])
        self.grid.add_widget(add_button)
        add_button.bind(on_press=lambda x: self.add_new_row())
        for key in self.rows:
            self.add_row(key)
        self.add_widget(self.grid)

    def add_row(self, desc, reqs = None):
        c = ComponentItem(desc,requirement_links=reqs)
        ComponentView.components.append(c)
        self.grid.add_widget(c)

    def add_new_row(self):
        self.modal = InputModal('Enter the description:')
        self.modal.assign_text_callback(self.add_row)
        self.modal.open()

class Menu(BoxLayout):
    def __init__(self, reload_func, **kwargs):
        super(Menu, self).__init__(**kwargs)
        self.size_hint = (1, None)
        self.orientation = 'horizontal'
        self.reload_func = reload_func
        exprt_btn = Button(text='Export JSON', size_hint=(None, None), size=(400, 70),background_color=[0,1,0,1])
        exprt_btn.bind(on_press=self.generate_save_popup)
        imprt_btn = Button(text='Import JSON', size_hint=(None, None), size=(400, 70),background_color=[0,1,0,1])
        imprt_btn.bind(on_press=self.generate_open_popup)
        self.add_widget(exprt_btn)
        self.add_widget(imprt_btn)

    def generate_save_popup(self, any):
        components = []
        for cmp in ComponentView.components:
            if cmp.requirement_view.tag:
                links = [{
                    'desc': RequirementView.requirements[id],
                    'level': level
                } for id, level in cmp.requirement_view.tag.items()]
                component = {'name':cmp.get_text(),'requirements': links}
                components.append(component)
        self.output = {'components':components}
        SaveFileDialogue(button_text="Save", on_ok=self.save_components_to_file).open()

    def generate_open_popup(self, any):
        OpenFileDialogue(button_text="Load", on_ok=self.read_filepath_and_load).open()

    def save_components_to_file(self, path):
        with open(path, 'w') as outfile:
            json.dump(self.output, outfile,indent=2)

    def read_filepath_and_load(self,fp):
        if fp and fp.endswith('.json'):
            txt = open(fp,'r').read()
            data = json.loads(txt)
            comp_data= []
            reqs = []
            CheckboxModal.intensity_levels = {}
            for comp in data['components']:
                print('\ncomp: {}\n'.format(comp))
                name = comp['name']
                comp_req_ids={}
                for req in comp['requirements']:
                    desc = req['desc']
                    level = req['level']
                    if desc not in reqs:
                        reqs.append(desc)
                        idx = len(reqs)
                    else:
                        idx = reqs.index(desc) + 1

                    comp_req_ids[idx]= level
                comp_data.append((name,comp_req_ids))
            self.reload_func(comp_data,reqs)
        elif fp:
            comp_data,reqs = ComponentRequirementTextFileReader().read_mappings(fp)
            self.reload_func(comp_data, reqs)

class MappingView(BoxLayout):
    def __init__(self,component_data=None,requirements=None,**kwargs):
        super(MappingView, self).__init__(**kwargs)
        self.orientation = 'horizontal'
        self.add_widget(ComponentView(component_data=component_data))
        self.add_widget(RequirementView(requirements=requirements))

class MainLayout(BoxLayout):
    def __init__(self,**kwargs):
        super(MainLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.mapping_view = MappingView()
        self.add_widget(self.mapping_view)
        self.add_widget(Menu(reload_func=self.reload_view))

    def reload_view(self, comp_data, reqs):
        self.remove_widget(self.mapping_view)
        self.mapping_view = MappingView(component_data=comp_data,requirements=reqs)
        self.add_widget(self.mapping_view)


class ComponentRequirementMapper(App):
    def build(self):

        return MainLayout()

if __name__ == '__main__':
    ComponentRequirementMapper().run()