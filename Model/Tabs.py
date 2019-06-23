import json as JSON
import numpy as np
import matplotlib.pyplot as plt
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg

class statistic_item:
    def __init__(self, name, func):
        self.name = name
        self.func = func


test_dict = {
    'components':[
        {
            'name': 'Controller',
            'requirements':[
                {
                     'desc': 'Must be responsive',
                     'level':'high'
                 },
                {
                    'desc': 'I can zoom in',
                    'level':'low'
                },
                {
                    'desc': 'I can cancel',
                    'level':'medium'
                },
            ]
        },
        {
            'name': 'Business Intelligence',
            'requirements': [
                {
                    'desc': 'Data should survive crash',
                    'level':'high'
                },
                {
                    'desc': 'I want to be able to make predictions',
                    'level':'high'
                },
                {
                    'desc': 'I want to keep costs low',
                    'level':'medium'
                },
            ]
        },
        {
            'name': 'Data Access',
            'requirements': [
                {
                    'desc': 'Data should survive crash',
                    'level':'high'
                },
                {
                    'desc': 'I should be able to view logged changes',
                    'level':'low'
                },
            ]
        },
        {
            'name': 'GUI',
            'requirements': [
                {
                    'desc': 'Must be responsive',
                    'level':'medium'
                },
                {
                    'desc': 'I can zoom in',
                    'level':'low'
                },
                {
                    'desc': 'I can cancel',
                    'level': 'high'
                },
                {
                    'desc': 'I should be able to view logged changes',
                    'level':'low'
                },
                {
                    'desc': 'I want mobile and desktop apps',
                    'level':'high'
                },
                {
                    'desc': 'I want the login page to be beautiful',
                    'level':'medium'
                },
            ]
        }
    ]
}

test_json = JSON.dumps(test_dict)

def count_dictionary_insert(dict,val):
    if val in dict:
        dict[val] = dict[val] +1
    else:
        dict[val] = 0

def set_dictionary_insert(dict,val1,val2):
    if val1 not in dict:
        dict[val1] = set([])
    dict[val1].add(val2)

def requirements_apply(json,fn):
    com_req = JSON.loads(json)
    for com in com_req['components']:
        for req in com['requirements']:
           fn(req,com)

def unique_requirements(json):
    s = set()
    requirements_apply(json,lambda r,c:s.add(r['desc']))
    return s

def group_by_levels(values):
    unique_reqs = []
    high_reqs =[]
    med_reqs =[]
    low_reqs = []
    for txt, lvl in values:
        if txt not in unique_reqs:
            unique_reqs.append(txt)
        if lvl == 'high':
            high_reqs.append(txt)
        elif lvl == 'low':
            low_reqs.append(txt)
        else:
            med_reqs.append(txt)
    return high_reqs,med_reqs,low_reqs,unique_reqs


def scatter_plot(json):
    if not json:
        json = test_json
    com_map = {}
    req_map  ={}
    requirements_apply(json, lambda r, c: set_dictionary_insert(req_map,r['desc'],(c['name'],r['level'])))
    requirements_apply(json, lambda r, c: set_dictionary_insert(com_map,c['name'],(r['desc'],r['level'])))

    yplots = []
    xplot_desc_map = {}
    num = 1
    unique_reqs = {}
    high_reqs =([],[])
    med_reqs =([],[])
    low_reqs = ([],[])
    for key, val_set in com_map.items():
        for txt, lvl in val_set:
            if txt not in unique_reqs:
                unique_reqs[txt]=(str(num))
                num = num + 1
            if lvl.lower() == 'high':
                high_reqs[0].append(key)
                high_reqs[1].append(txt)
            elif lvl.lower() == 'low':
                low_reqs[0].append(key)
                low_reqs[1].append(txt)
            else:
                med_reqs[0].append(key)
                med_reqs[1].append(txt)

    colors = ['red', 'orange','green']

    plt.clf()
    plt.title('Scatterplot')
    for (comp,req),clr in zip([high_reqs,med_reqs,low_reqs],colors):
        plt.scatter(comp,req,color=clr)

    # Plot bars and create text labels for the table
    cell_text = []
    for key,val in xplot_desc_map.items():
        cell_text.append([val,key])

    return FigureCanvasKivyAgg(plt.gcf()),cell_text


# def component_correlation(json):
#
# def requirement_correlation(json):
#
# def component_proportion(json):
#
# def requirement_proportion(json):
#
# def component_affinity(json):
#
# def requirement_affinity(json):

statisticViews = {
    'Scatter Plot':scatter_plot,
    'Component Correlation':scatter_plot,
    'Requirement Correlation':scatter_plot,
    'Component Proportion': scatter_plot,
    'Requirement Proportion': scatter_plot,
    'Component Affinity': scatter_plot,
    'Requirement Affinity': scatter_plot
}