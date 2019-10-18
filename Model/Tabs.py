import json as JSON
from functools import partial
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

def get_requirement_score(reqs):
        t = 0
        if not reqs:
            return t

        if isinstance(reqs[0], dict):
            level_func = lambda x: x['level'].lower()
        elif isinstance(reqs[0], tuple):
            level_func = lambda x: x[1].lower()
        for req in reqs:
            if level_func(req) == 'low':
                t += 1
            if level_func(req) == 'medium':
                t += 2
            if level_func(req) == 'high':
                t += 3
        return t / 3

def average_requirement_score(reqs):
    t = 0
    if not reqs:
        return t

    if isinstance(reqs[0], dict):
        level_func = lambda x: x['level'].lower()
    elif isinstance(reqs[0], tuple):
        level_func = lambda x: x[1].lower()
    for req in reqs:
        if level_func(req) == 'low':
            t += 1
        if level_func(req) == 'medium':
            t += 2
        if level_func(req) == 'high':
            t += 3
    return t / 3 / len(reqs)

class Globals:
    g_num = 1
    g_ch_str = 'A'

def scatter_plot(json, args = None):
    if not json:
        json = test_json
    com_map = {}
    req_map  ={}
    requirements_apply(json, lambda r, c: set_dictionary_insert(req_map,r['desc'],(c['name'],r['level'])))
    requirements_apply(json, lambda r, c: set_dictionary_insert(com_map,c['name'],(r['desc'],r['level'])))

    if args and "order_by" in args:
        order_by = args["order_by"]
        if order_by == "comp_count":
            com_map = sorted(com_map.items(),key=lambda x: len(com_map[x[0]]),reverse=True)
            req_map = None
        elif order_by == "req_count":
            com_map = sorted(req_map.items(),key=lambda x: len(req_map[x[0]]),reverse=True)
        elif order_by == "comp_level":
            com_map = sorted(com_map.items(),key=lambda x: average_requirement_score(list(com_map[x[0]])),reverse=True)
            req_map = None
        elif order_by == "req_level":
            com_map = sorted(req_map.items(), key=lambda x: average_requirement_score(list(req_map[x[0]])),reverse=True)
    else:
        com_map = list(map(lambda x: x, com_map.items()))

    Globals.g_num = 1
    Globals.g_ch_str = 'A'
    def increment_num():
        num = Globals.g_num
        Globals.g_num = Globals.g_num +1
        return num
    def increment_char():
        chr_str = Globals.g_ch_str
        for i in range(len(Globals.g_ch_str)-1,-1,-1):
            ch = Globals.g_ch_str[i]
            if ch != 'Z':
                ch_list = list(Globals.g_ch_str)
                ch_list[i] = chr(ord(ch) + 1)
                Globals.g_ch_str = "".join(ch_list)
                return chr_str
        #add digit
        Globals.g_ch_str = 'A' + Globals.g_ch_str
        return chr_str

    unique_reqs = {}
    unique_comps = {}
    reqs_in_order = []
    color_map = {"high":'red', "medium":'orange', "low":'green'}

    for key, val_set in com_map:
        unique_x = unique_comps
        unique_y = unique_reqs
        inc_x = increment_char
        inc_y = increment_num
        if req_map:
            unique_x = unique_reqs
            unique_y = unique_comps
            inc_x = increment_num
            inc_y = increment_char
        if key not in unique_x:
            unique_x[key] = str(inc_x())
        for txt, lvl in val_set:
            if txt not in unique_y:
                unique_y[txt]=str(inc_y())
            if not req_map:
                reqs_in_order.append(
                    ([unique_x[key]], [unique_y[txt]], color_map[lvl.lower()])
                )
            else:
                reqs_in_order.append(
                    ([unique_y[txt]],[unique_x[key]], color_map[lvl.lower()])
                )

    plt.clf()
    if args and "desc" in args:
        plt.title("Scatterplot ({})".format(args["desc"]))
    else:
        plt.title('Scatterplot')

    for comp, req, clr in reqs_in_order:
        plt.scatter(comp, req, color=clr)

    # Plot bars and create text labels for the table
    cell_text = []
    for key,val in unique_reqs.items():
        cell_text.append([val,key])
    for key,val in unique_comps.items():
        cell_text.append([val,key])

    return FigureCanvasKivyAgg(plt.gcf()),cell_text, None

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

    plt.title('Component Proportion(Levels are Ignored)')
    return FigureCanvasKivyAgg(plt.gcf()),table_data, None

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

    plt.title('Requirement Proportion(Levels are Ignored)')
    return FigureCanvasKivyAgg(plt.gcf()), table_data, None

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

    plt.title('Component Influence (Levels are Weighted In)')
    return FigureCanvasKivyAgg(plt.gcf()),table_data, None

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

    plt.title('Requirement Influence(Levels are Weighted In)')
    return FigureCanvasKivyAgg(plt.gcf()), table_data, None

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
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table, (coms,reqs)



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
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table, None

def generate_comparison_score(control,other):
    max_score = len(control)*3
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
    other_names = {x[0]:x[1] for x in other}

    for idx,i1 in enumerate(control):
        desc = i1[0]
        score = 0
        if desc in other_names:
            s1 = get_level_num(i1[1])
            s2 = get_level_num(other_names[desc][1])
            score = (s1+s2)/2
        tot += score

    return tot/max_score

def component_comparison_reverse_args(base_comp, json):
    return component_comparison(json,base_comp)

def requirement_comparison_reverse_args(base_comp, json):
    return requirement_comparison(json,base_comp)

def component_comparison(json, base_cmp=None):
    if not json:
        json = test_json

    com_map = {}
    requirements_apply(json, lambda r, c: set_dictionary_insert(com_map, c['name'], (r['desc'], r['level'])))

    return_buttons = []
    table = []
    reverse_index = {}
    for idx,com in enumerate(com_map,start=1):
        table.append((idx,com))
        reverse_index[com] = idx
        return_buttons.append((str(idx),partial(component_comparison_reverse_args,com)))

    if not base_cmp:
        return None, table, return_buttons

    base_cmp_data = com_map[base_cmp]
    scores = [(base_cmp,1.0)]

    def insert_order_by_score(name, score):
        idx = 0
        for i in range(0, len(scores)):
            if score > scores[i][1]:
                break
            idx += 1
        scores.insert(idx,(name, score))

    for cmp in com_map:
        if cmp != base_cmp:
            reqs = com_map[cmp]
            score = generate_comparison_score(base_cmp_data, reqs)
            insert_order_by_score(cmp, score)

    labels = [reverse_index[tp[0]] for tp in scores]
    y_pos = np.arange(len(labels))
    plt.clf()
    fig, ax = plt.subplots()

    bar_plot = plt.barh(y_pos, [x[1] for x in scores], align='center', alpha=0.5)
    plt.yticks(y_pos, labels)
    plt.xlabel('Component Comparison Score')

    def autolabel(bars,names):
        for idx,(bar,name) in enumerate(zip(bars,names)):
            width = bar.get_width()
            ax.text(width*.05, bar.get_y() + bar.get_height()/2,
                    name)

    autolabel(bar_plot,[tp[0] for tp in scores])

    plt.title("Components Compared To '{}'".format(base_cmp))
    return FigureCanvasKivyAgg(plt.gcf()), table, return_buttons

def requirement_comparison(json,base_req=None):
    if not json:
        json = test_json

    req_map  ={}
    requirements_apply(json, lambda r, c: set_dictionary_insert(req_map,r['desc'],(c['name'],r['level'])))

    return_buttons = []
    table = []
    reverse_index = {}
    for idx,req in enumerate(req_map,start=1):
        table.append((idx,req))
        reverse_index[req] = idx
        return_buttons.append((str(idx),partial(requirement_comparison_reverse_args,req)))

    if not base_req:
        return None, table, return_buttons

    base_cmp_data = req_map[base_req]
    scores = [(base_req,1.0)]

    def insert_order_by_score(name, score):
        idx = 0
        for i in range(0, len(scores)):
            if score > scores[i][1]:
                break
            idx += 1
        scores.insert(idx,(name, score))

    for cmp in req_map:
        if cmp != base_req:
            reqs = req_map[cmp]
            score = generate_comparison_score(base_cmp_data, reqs)
            insert_order_by_score(cmp, score)

    labels = [reverse_index[tp[0]] for tp in scores]
    y_pos = np.arange(len(labels))
    plt.clf()
    fig, ax = plt.subplots()
    bar_plot = plt.barh(y_pos, [x[1] for x in scores], align='center', alpha=0.5)

    def autolabel(bars,names):
        for idx,(bar,name) in enumerate(zip(bars,names)):
            width = bar.get_width()
            ax.text(width*.05, bar.get_y() + bar.get_height()/2,
                    name)

    autolabel(bar_plot,[tp[0] for tp in scores])

    plt.yticks(y_pos, labels)
    plt.xlabel('Requirement Comparison Score')

    plt.title("Requirements Compared To '{}'".format(base_req))
    return FigureCanvasKivyAgg(plt.gcf()), table, return_buttons

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
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table, (coms,reqs)

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
    return FigureCanvasKivyAgg(plt.gcf()), sorted_table, None

def component_level_distributions(json):
    if not json:
        json = test_json
    com_req = JSON.loads(json)['components']
    high_dists = []
    med_dists = []
    low_dists = []
    coms = []
    for cr in com_req:
        coms.append(cr['name'])
        high_dists.append(0)
        med_dists.append(0)
        low_dists.append(0)
        for req in cr['requirements']:
            level = req['level'].lower()
            if level == 'high':
                high_dists[-1] += 1
            elif level == 'medium':
                med_dists[-1] += 1
            elif level == 'low':
                low_dists[-1] += 1

    barWidth = 0.25

    # Set position of bar on X axis
    r1 = np.arange(len(high_dists))
    r2 = [x + barWidth for x in r1]
    r3 = [x + barWidth for x in r2]

    labels = []
    table_data = [("'#'", "'Component Distibution'")]
    for idx, val in enumerate(coms, start=1):
        txt = '{}: {}'.format(idx, val)
        table_data.append((str(idx), txt))
        labels.append(str(idx))

    # Make the plot
    plt.clf()
    plt.bar(r1, high_dists, color='red', width=barWidth, edgecolor='white', label='High')
    plt.bar(r2, med_dists, color='yellow', width=barWidth, edgecolor='white', label='Medium')
    plt.bar(r3, low_dists, color='green', width=barWidth, edgecolor='white', label='Low')

    # Add xticks on the middle of the group bars
    plt.xlabel('group', fontweight='bold')
    plt.xticks([r + barWidth for r in range(len(high_dists))], labels)

    plt.title('Component Level Distribution')
    return FigureCanvasKivyAgg(plt.gcf()), table_data, None

def requirement_level_distributions(json):
    if not json:
        json = test_json

    req_map  ={}
    requirements_apply(json, lambda r, c: set_dictionary_insert(req_map,r['desc'],(c['name'],r['level'])))

    high_dists = []
    med_dists = []
    low_dists = []
    reqs = []
    for req, req_data in req_map.items():
        reqs.append(req)
        high_dists.append(0)
        med_dists.append(0)
        low_dists.append(0)
        for com_data in req_data:
            level = com_data[1].lower()
            if level == 'high':
                high_dists[-1] += 1
            elif level == 'medium':
                med_dists[-1] += 1
            elif level == 'low':
                low_dists[-1] += 1

    barWidth = 0.25

    # Set position of bar on X axis
    r1 = np.arange(len(high_dists))
    r2 = [x + barWidth for x in r1]
    r3 = [x + barWidth for x in r2]

    labels = []
    table_data = [("'#'", "'Component Distibution'")]
    for idx, val in enumerate(reqs, start=1):
        txt = '{}: {}'.format(idx, val)
        table_data.append((str(idx), txt))
        labels.append(str(idx))

    # Make the plot
    plt.clf()
    plt.bar(r1, high_dists, color='red', width=barWidth, edgecolor='white', label='High')
    plt.bar(r2, med_dists, color='yellow', width=barWidth, edgecolor='white', label='Medium')
    plt.bar(r3, low_dists, color='green', width=barWidth, edgecolor='white', label='Low')

    # Add xticks on the middle of the group bars
    plt.xlabel('group', fontweight='bold')
    plt.xticks([r + barWidth for r in range(len(high_dists))], labels)

    plt.title('Component Level Distribution')
    return FigureCanvasKivyAgg(plt.gcf()), table_data, None

statisticViews = {
    'Scatter Plots':(scatter_plot,[
         ('Comp Count',lambda x:scatter_plot(x,{'order_by':'comp_count',
                                                'desc':'Organized by requirement count in components'})),
         ('Req Count',lambda x:scatter_plot(x,{'order_by':'req_count',
                                                'desc':'Organized by component count in rquirements'})),
         ('Comp Lvl Avg', lambda x: scatter_plot(x, {'order_by': 'comp_level',
                                                'desc':'Organized by requirement level average in components'})),
         ('Req Lvl Avg', lambda x: scatter_plot(x, {'order_by': 'req_level',
                                                'desc':'Organized by component level average in requirements'})),
     ]),
    'Proportions': (component_proportion,[
        ('Comp Unweighted',component_proportion),
        ('Comp Weighted',component_influence),
        ('Req Unweighted',requirement_proportion),
        ('Req Weighted',requirement_influence),
    ]),
    'Correlations': (component_correlation, [
        ('Comp Affinity', component_affinity),
        ('Req Affinity',requirement_affinity),
        ('Comp Correlation', component_correlation),
        ('Req Correlation' ,requirement_correlation),
    ]),
    'Component Comparisons': (component_comparison, None),
    'Requirement Comparisons': (requirement_comparison, None),
    'Distributions': (component_level_distributions , [
        ('Comp Levels', component_level_distributions),
        ('Req Levels', requirement_level_distributions),
    ]),
}