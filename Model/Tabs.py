import json as JSON
from operator import itemgetter

import itertools
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
            if req['level'].lower() == 'low':
                t += 1
            if req['level'].lower() == 'medium':
                t += 2
            if req['level'].lower() == 'high':
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

def generate_correlation_score(g1,g2,total_count):

    tot = 0
    def get_level_num(level):
        level = level.lower()
        if level == 'low':
            return 1
        elif level == 'medium':
            return 2
        elif level == 'high':
            return 3
        else:
            return 0
    g2_names = list(map(lambda x: x['desc'],g2))

    #find common elements
    for idx,i1 in enumerate(g1):
        desc = i1['desc']
        score = 0
        if desc in g2_names:
            s1 = get_level_num(g1[idx]['level'])
            s2 = get_level_num(g2[g2_names.index(desc)]['level'])
            tot += (s1+s2)/3

    return tot/total_count/2

def generate_affinity_score(group1,group2):
    #determine max length
    max_score = len(group1)*3
    g1 = group1
    g2 = group2

    tot = 0

    def get_level_num(level):
        level = level.lower()
        if level == 'low':
            return 1
        elif level == 'medium':
            return 2
        elif level == 'high':
            return 3
        else:
            return 0
    g2_names = list(map(lambda x: x['desc'],g2))

    for idx,i1 in enumerate(g1):
        desc = i1['desc']
        score = 0
        if desc in g2_names:
            s1 = get_level_num(g1[idx]['level'])
            s2 = get_level_num(g2[g2_names.index(desc)]['level'])
            score = (s1+s2)/2
        tot += score

    return tot/max_score

def component_correlation(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']
    com_dict = {}
    com_scores = {}
    coms = []
    reqs = set()
    for cr in com_req:
        coms.append(cr['name'])
        com_dict[cr['name']] = cr['requirements']
        for req in cr['requirements']:
            reqs.add(req['desc'])

    for com_pair in itertools.product(coms,coms):
        if com_pair[0] == com_pair[1]:
            continue
        key = '{}~.~{}'.format(com_pair[0],com_pair[1])
        if key not in com_scores:
            idx1 = coms.index(com_pair[0])
            idx2 = coms.index(com_pair[1])
            score = generate_correlation_score(com_req[idx1]['requirements'],com_req[idx2]['requirements'],len(reqs))
            if score > 0.0:
                com_scores[key] = score

    sorted_table =[('#','Correlation')]
    sorted_scores = []
    sorted_labels = []

    for i, x in enumerate(sorted(com_scores.items(), key=itemgetter(1), reverse=True)):
        comps = '{}: {:.2%}'.format(x[0].replace('~.~',' -> '),x[1])
        sorted_table.append((str(i+1),comps))
        sorted_scores.append(x[1]*100)
        sorted_labels.append(str(i+1))

    labels_tuple = tuple(sorted_labels[:20])
    y_pos = np.arange(len(labels_tuple))
    plt.clf()
    plt.barh(y_pos, sorted_scores[:20], align='center', alpha=0.5)
    plt.yticks(y_pos, labels_tuple)
    plt.xlabel('Component Composition')

    plt.title('Component Correlation')
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table



def requirement_correlation(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']
    req_dict = {}
    req_scores = {}
    reqs = []
    for cr in com_req:
        for req in cr['requirements']:
            if req['desc'] not in reqs:
                reqs.append(req['desc'])
                req_dict[req['desc']] = []
            req_dict[req['desc']].append({'desc':cr['name'],'level':req['level']})

    for req_pair in itertools.product(reqs,reqs):
        if req_pair[0] == req_pair[1]:
            continue
        key = '{}~.~{}'.format(req_pair[0],req_pair[1])
        if key not in req_scores:

            score = generate_correlation_score(req_dict[req_pair[0]],req_dict[req_pair[1]], len(com_req))
            if score > 0.0:
                req_scores[key] = score

    sorted_table =[('#','Correlation')]
    sorted_scores = []
    sorted_labels = []

    for i, x in enumerate(sorted(req_scores.items(), key=itemgetter(1), reverse=True)):
        comps = '{}: {:.2%}'.format(x[0].replace('~.~', ' -> '),x[1])
        sorted_table.append((str(i+1),comps))
        sorted_scores.append(x[1]*100)
        sorted_labels.append(str(i+1))

    #sorted_scores = [(str(i),x[0].replace('~.~','->')+': '+str(x[1])) for i,x in enumerate(sorted(com_scores.items(), key=itemgetter(1),reverse=True))]
    labels_tuple = tuple(sorted_labels[:20])
    y_pos = np.arange(len(labels_tuple))
    plt.clf()
    plt.barh(y_pos, sorted_scores[:20], align='center', alpha=0.5)
    plt.yticks(y_pos, labels_tuple)
    plt.xlabel('Requirement Composition')

    plt.title('Requirement Correlation')
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table

def component_affinity(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']
    com_dict = {}
    com_scores = {}
    coms = []
    reqs = set()
    for cr in com_req:
        coms.append(cr['name'])
        com_dict[cr['name']] = cr['requirements']
        for req in cr['requirements']:
            reqs.add(req['desc'])

    for com_pair in itertools.product(coms, coms):
        if com_pair[0] == com_pair[1]:
            continue
        key = '{}~.~{}'.format(com_pair[0], com_pair[1])
        if key not in com_scores:
            idx1 = coms.index(com_pair[0])
            idx2 = coms.index(com_pair[1])
            score = generate_affinity_score(com_req[idx1]['requirements'], com_req[idx2]['requirements'])
            if score > 0.0:
                com_scores[key] = score

    sorted_table =[('#','Correlation')]
    sorted_scores = []
    sorted_labels = []

    for i, x in enumerate(sorted(com_scores.items(), key=itemgetter(1), reverse=True)):
        comps = '{}: {:.2%}'.format(x[0].replace('~.~', ' -> '),x[1])
        sorted_table.append((str(i+1),comps))
        sorted_scores.append(x[1]*100)
        sorted_labels.append(str(i+1))

    labels_tuple = tuple(sorted_labels[:20])
    y_pos = np.arange(len(labels_tuple))
    plt.clf()
    plt.barh(y_pos, sorted_scores[:20], align='center', alpha=0.5)
    plt.yticks(y_pos, labels_tuple)
    plt.xlabel('Requirement Composition')

    plt.title('Requirement Correlation')
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table

def requirement_affinity(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']
    req_dict = {}
    req_scores = {}
    reqs = []
    for cr in com_req:
        for req in cr['requirements']:
            if req['desc'] not in reqs:
                reqs.append(req['desc'])
                req_dict[req['desc']] = []
            req_dict[req['desc']].append({'desc':cr['name'],'level':req['level']})

    for com_pair in itertools.product(reqs,reqs):
        if com_pair[0] == com_pair[1]:
            continue
        key = '{}~.~{}'.format(com_pair[0],com_pair[1])
        if key not in req_scores:
            l1 = req_dict[com_pair[0]]
            l2 = req_dict[com_pair[1]]
            score = generate_affinity_score(l1,l2)
            if score > 0.0:
                req_scores[key] = score

    sorted_table =[('#','Correlation')]
    sorted_scores = []
    sorted_labels = []

    for i, x in enumerate(sorted(req_scores.items(), key=itemgetter(1), reverse=True)):
        comps = '{}: {:.2%}'.format(x[0].replace('~.~', ' -> '),x[1])
        sorted_table.append((str(i+1),comps))
        sorted_scores.append(x[1]*100)
        sorted_labels.append(str(i+1))

    #sorted_scores = [(str(i),x[0].replace('~.~','->')+': '+str(x[1])) for i,x in enumerate(sorted(com_scores.items(), key=itemgetter(1),reverse=True))]
    labels_tuple = tuple(sorted_labels[:20])
    y_pos = np.arange(len(labels_tuple))
    plt.clf()
    plt.barh(y_pos, sorted_scores[:20], align='center', alpha=0.5)
    plt.yticks(y_pos, labels_tuple)
    plt.xlabel('Requirement Composition')

    plt.title('Requirement Correlation')
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table

statisticViews = {
    'Scatter Plot':scatter_plot,
    'Component Proportion': component_proportion,
    'Requirement Proportion': requirement_proportion,
    'Component Influence': component_influence,
    'Requirement Influence': requirement_influence,
    'Component Affinity': component_affinity,
    'Requirement Affinity': requirement_affinity,
    'Component Correlation': component_correlation,
    'Requirement Correlation': requirement_correlation,
}