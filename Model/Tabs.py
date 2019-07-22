import json as JSON
from operator import itemgetter

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


#def component_correlation(json):

#def requirement_correlation(json):

def component_proportion(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']

    all_reqs = unique_requirements(json)
    unique_req_count = len(all_reqs)
    coms = sorted([(com['name'],len(com['requirements'])) for com in com_req],key=itemgetter(1), reverse=True)

    labels = list(map(itemgetter(0),coms))
    values = list(map(lambda x: x[1] / unique_req_count, coms))

    table_data = [("'#'","'Requirement Coverage'")]
    for idx, val in enumerate(labels, start=1):
        v = values[idx-1]
        txt = '{}: {:.2%}'.format(val,v)
        table_data.append((str(idx),txt))
        labels[idx - 1] = str(idx)

    #explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Component Proportion(not weighted)')
    return FigureCanvasKivyAgg(plt.gcf()),table_data

def requirement_proportion(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']

    req_com = {}
    coms = set()

    for com in com_req:
        coms.add(com['name'])
        for req in com['requirements']:
            if req['desc'] not in req_com:
                req_com[req['desc']] = []
            req_com[req['desc']].append(com['name'])

    com_count = len(coms)

    reqs = sorted([(req, len(coms)) for req,coms in req_com.items() ], key=itemgetter(1), reverse=True)

    labels = []
    values = list(map(lambda x: x[1] / com_count, reqs))

    table_data = [("'#'","'Component Coverage'")]
    for idx, val in enumerate(reqs, start=1):
        v = values[idx - 1]
        txt = '{}: {:.2%}'.format(val[0], v)
        table_data.append((str(idx), txt))
        labels.append(str(idx))
    # explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Requirement Proportion(not weighted)')
    return FigureCanvasKivyAgg(plt.gcf()), table_data

def get_requirement_score(reqs):
        t = 0
        for req in reqs:
            if req['level'] == 'low':
                t += 1
            if req['level'] == 'medium':
                t += 2
            if req['level'] == 'high':
                t += 3
        return t/3

def component_influence(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']

    all_reqs = unique_requirements(json)
    unique_req_count = len(all_reqs)

    coms = sorted([(com['name'],get_requirement_score(com['requirements'])) for com in com_req],key=itemgetter(1), reverse=True)

    labels = list(map(itemgetter(0),coms))
    values = list(map(lambda x: x[1] / unique_req_count, coms))

    table_data = [("'#'","'Requirement Coverage'")]
    for idx, val in enumerate(coms, start=1):
        v = values[idx-1]
        txt = '{}: {:.2%}'.format(val[0],v)
        table_data.append((str(idx),txt))
        labels[idx - 1] = str(idx)

    #explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    val_mod = list(map(lambda x:x*150.0,values))
    ax1.pie(val_mod, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Component Influence (weighted)')
    return FigureCanvasKivyAgg(plt.gcf()),table_data

def requirement_influence(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']

    req_com = {}
    coms = set()

    for com in com_req:
        coms.add(com['name'])
        for req in com['requirements']:
            if req['desc'] not in req_com:
                req_com[req['desc']] = []
            req_com[req['desc']].append({'name':com['name'],'level':req['level']})

    com_count = len(coms)

    reqs = sorted([(req, get_requirement_score(coms)) for req,coms in req_com.items() ], key=itemgetter(1), reverse=True)

    labels = []
    values = list(map(lambda x: x[1] / com_count, reqs))

    table_data = [("'#'","'Component Coverage'")]
    for idx, val in enumerate(reqs, start=1):
        v = values[idx - 1]
        txt = '{}: {:.2%}'.format(val[0], v)
        table_data.append((str(idx), txt))
        labels.append(str(idx))
    # explode = (0, 0.1, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

    fig1, ax1 = plt.subplots()
    ax1.pie(values, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title('Requirement Influence(Weighted)')
    return FigureCanvasKivyAgg(plt.gcf()), table_data

# def component_affinity(json):
#
# def requirement_affinity(json):

statisticViews = {
    'Scatter Plot':scatter_plot,
    'Component Correlation':scatter_plot,
    'Requirement Correlation':scatter_plot,
    'Component Proportion': component_proportion,
    'Requirement Proportion': requirement_proportion,
    'Component Influence': component_influence,
    'Requirement Influence': requirement_influence,
    'Component Affinity': scatter_plot,
    'Requirement Affinity': scatter_plot
}