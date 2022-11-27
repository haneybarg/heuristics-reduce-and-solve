import os
import time
import random as rd
import copy
import itertools

from matplotlib import colors as mcolors
import matplotlib.pyplot as plt
import networkx as nx

import graph

def parse_dimacs(path):
    """Yields cnf lines as lists from the file."""
    with open(path) as fp:
        for line in fp:
            if not line.startswith(('c', 'p')):
                items = list(map(int, line.split()[1:]))
                yield items

def get_maximal_independent_set(ADT):
# based on https://www.researchgate.net/publication/220567138_An_Optimal_Bit_Complexity_Randomized_Distributed_MIS_Algorithm
# implementation from https://github.com/je-suis-tm/graph-theory/blob/master/maximal%20independent%20set.ipynb
    # assign random value from uniform distribution to every vertex
    random_val=dict(zip(ADT.vertex(),
        [rd.random() for _ in range(ADT.order())]))

    # initialize
    maximal_independent_set=[]
    queue=[i for i in random_val]

    while len(queue)>0:
        for node in queue:

            #select the vertex which has larger value than all of its neighbors
            neighbor_vals=[random_val[neighbor] for neighbor in ADT.edge(node) if neighbor in random_val]
            if len(neighbor_vals)==0 or random_val[node]<min(neighbor_vals):

                #add to mis
                maximal_independent_set.append(node)

                #remove the vertex and its neighbors
                queue.remove(node)
                for neighbor in ADT.edge(node):
                    if neighbor in queue:
                        queue.remove(neighbor)

        #reassign random values to existing vertices
        random_val=dict(zip(queue,
                            [rd.random() for _ in range(len(random_val))]))

    return maximal_independent_set


def prune_and_solve(data_raw, instance):
    print(f'Starting instance {instance}')
    data = data_raw.copy()
    data_aux = data_raw.copy()

    colors = list(mcolors.CSS4_COLORS.values())
    q = 100
    nodes = set(itertools.chain.from_iterable(data))

    start = time.time()

    network = nx.Graph()
    network.add_nodes_from(nodes)
    ADT = graph.graph()
    for edge in data:
        ADT.append(edge[0], edge[1], 0) # vertex, vertex and weight (always 0 here)
        network.add_edge(edge[0], edge[1])
    d = nx.coloring.greedy_color(network, strategy='DSATUR')

    end = time.time()

    print('Chromatic number before pruning', len(set(d.values())), end - start)

    mis = get_maximal_independent_set(ADT)
    mis.sort()
    [data_aux.remove(value) for value in data if all(x in mis for x in value)]

    start = time.time()

    network = nx.Graph()
    network.add_nodes_from(nodes)
    # ADT = graph.graph()
    for edge in data_aux:
        # ADT.append(edge[0], edge[1], 0) # vertex, vertex and weight (always 0 here)
        network.add_edge(edge[0], edge[1])
    d = nx.coloring.greedy_color(network, strategy='DSATUR')

    end = time.time()

    print('Chromatic number after pruning', len(set(d.values())) + 1, end - start)
    print()

def main():
    instances = ['DSJC250.5', 'DSJC500.5', 'DSJC500.1', 'DSJC500.9', 'DSJC1000.1',
                 'DSJC1000.5', 'DSJC1000.9', 'DSJR500.1c', 'DSJR500.5', 'le450_15c',
                 'le450_15d', 'le450_25c', 'le450_25d']
    for i in instances:
        data_raw = list(parse_dimacs('data/' + i + '.col'))
        prune_and_solve(data_raw, i)

if __name__ == '__main__':
    main()
