#!/usr/bin/env python3
# Copyright (c) 2019 Simeon Miteff <simeon@miteff.co>
# See LICENSE for license terms.

import python_pachyderm
import networkx as nx
import matplotlib.pyplot as plt

labeldict = {}

def get_inputs(i):
    if i.HasField('pfs'): return "pfs", i.pfs
    if i.HasField('cron'): return "cron", i.cron
    if i.HasField('git'): return "git", i.git
    if i.join: return "join", i.join
    if i.cross: return "cross", i.cross
    if i.union: return "union", i.union
    return None, None   

def print_input(input_type, inp, indent=""):
    try:
        print("{}{}[{}]".format(indent, input_type, inp.name))
    except AttributeError:
        print("{}{}".format(indent, input_type))
    try:
        for subinput in inp:
            input_type, inp = get_inputs(subinput)
            print_input(input_type, inp, "\t")
    except TypeError:
        pass

def graph_input(graph, input_type, inp):
    try:
        graph.add_node("repo_"+inp.name, input_type=input_type, name=inp.name, node_type="repo")
        labeldict["repo_"+inp.name] = inp.name
        return "repo_"+inp.name
    except AttributeError:
        pass
    subnames = []
    for input_set in inp:
        subnames.append(graph_input(graph, *get_inputs(input_set)))
    name = '-'.join(['inputset_'] + subnames)
    graph.add_node(name, input_type=input_type, node_type="input_set")
    labeldict[name] = input_type
    for subname in subnames:
        graph.add_edge(subname, name)
        
    return name
        

if __name__ == "__main__":
    graph = nx.DiGraph()
    client = python_pachyderm.Client()
    repos = client.list_repo()
    pipelines = client.list_pipeline()

    for p in pipelines.pipeline_info:
        name = p.pipeline.name
        graph.add_node("pipeline_"+name, name=name, node_type="pipeline")
        labeldict["pipeline_"+name] = 'Pipeline: '+name
        graph.add_node("repo_"+name, input_type='pfs', name=name, node_type="repo")
        labeldict["repo_"+name] = name
        graph.add_edge("pipeline_"+name, "repo_"+name)
        #print("============ {} ============".format(name))
        input_type, inp = get_inputs(p.input)
        #print_input(input_type, inp)
        input_name = graph_input(graph, input_type, inp)
        graph.add_edge(input_name, "pipeline_"+name)

    nx.draw(graph, labels=labeldict, with_labels=True)
    plt.show()
