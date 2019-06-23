from kivy.uix.anchorlayout import AnchorLayout
from kivy.lang import Builder
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
import Model.Tabs as tb
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Rectangle
from GUI.FileDialogue import FileDialogue
from functools import partial
import os


red = [1,0,0,1]
green = [0,1,0,1]
blue =  [0,0,1,1]
purple = [1,0,1,1]

class TabPanels(BoxLayout):
    def __init__(self,json_retriever=None,**kwargs):
        super(TabPanels, self).__init__(**kwargs)
        self.orientation ='vertical'
        self.json_retriever = json_retriever

    def set_tabs(self,tab_data):
        for tab,fn in tab_data.items():
            btn = Button(text=tab, size=(100, 100), size_hint=(1, 1.0/len(tab_data) ))
            btn.bind(on_press = partial(self.run_func_and_refresh_tab, fn ))
            self.add_widget(btn)

    def set_parent(self,parent):
        self.parent = parent
    def run_func_and_refresh_tab(self,fn,caller):
        new_panel,new_table = fn(self.json_retriever())
        self.parent.refresh_graph_panel(new_panel,new_table)

class MenuBar(AnchorLayout):
    def __init__(self, **kwargs):
        super(MenuBar, self).__init__(**kwargs)
        self.size_hint =(None,None)
        anchor_rb = AnchorLayout(anchor_x='right', anchor_y='center',size_hint=(None,None))
        crt_btn = Button(text='Create', size=(100, 50), size_hint=(None, None))
        opn_btn = Button(text='Open', size=(100, 50), size_hint=(None, None))
        opn_btn.bind(on_press=self.generate_popup)
        anchor_rb.add_widget(opn_btn)
        self.add_widget(anchor_rb)
        self.size_hint_y = None
        self.fname_cb = lambda *args: None
        self.data = None

    def generate_popup(self,any):
        FileDialogue(button_text="Load",on_ok= self.read_filepath).open()

    def read_filepath(self,fp):
        if fp:
            self.filepath = fp
            self.data = open(fp, 'r').read()

    def get_loaded_data(self):
        return self.data


class TextLine(AnchorLayout):
    def __init__(self,txt, **kwargs):
        super(TextLine, self).__init__(**kwargs)

        #self.anchor_x='left'
        #self.anchor_y='center'
        self.size_hint = (1, None)
        lbl = Label(height = 35, color = (0, 0, 1, 1), text=txt, size_hint=(None, None))
        #lbl.anchor_x = 'left'
        self.add_widget(lbl)
        self.height = 35

class ReqTable(ScrollView):
    def __init__(self, **kwargs):
        super(ReqTable, self).__init__(**kwargs)
        self.size_hint = (1,None)
        self.grid = None

    def set_table(self, rows):
        if self.grid:
            self.remove_widget(self.grid)
        self.grid = GridLayout(cols=2, size_hint=(1,None),row_default_height=50)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.size_hint = (1, .3)

        for key,value in rows:
            #self.grid.add_widget(TextLine('{}: {}'.format(key,value)))
            self.grid.add_widget(Label(text=str('{}:  '.format(key)),height=35,size_hint_x=None,width=50))
            l = Label(text=value, halign='left', size_hint=(None,1))
            l.bind(texture_size=l.setter('size'))
            self.grid.add_widget(l)

        self.add_widget(self.grid)


class DataView(BoxLayout):
    def __init__(self, graph, table,**kwargs):
        super(DataView, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint =(1, 1)
        self.add_widget(graph)
        self.add_widget(table)

class MainView(BoxLayout):
    def __init__(self,json_retriever = None, **kwargs):
        super(MainView, self).__init__(**kwargs)
        graph_panel = Button()
        tpn = TabPanels(size_hint=(.3, 1),json_retriever=json_retriever)
        tpn.set_tabs(tb.statisticViews)
        self.add_widget(tpn)
        tpn.set_parent(self)
        table= ReqTable()
        self.dataView = DataView(self.generate_graph_panel(graph_panel),table)
        self.add_widget(self.dataView)

    def refresh_graph_panel(self,new_panel,table_data=None):
        self.remove_widget(self.dataView)
        table = ReqTable()
        table.set_table(table_data)
        self.dataView = DataView(self.generate_graph_panel(new_panel), table)
        self.add_widget(self.dataView)

    def generate_graph_panel(self,component):
        comp = BoxLayout(size_hint = (1, 0.7))
        comp.add_widget(component)
        self.dataView = comp
        return self.dataView


class Dashboard(BoxLayout):
    def __init__(self,**kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self.orientation = 'vertical'
        mb = MenuBar()
        self.add_widget(mb)
        self.add_widget(MainView(json_retriever=mb.get_loaded_data))

class RequirementComponentApp(App):
    def build(self):
        return Dashboard()

if __name__ == '__main__':
    RequirementComponentApp().run()