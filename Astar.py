# -*- coding: utf-8 -*-
import math
from PriorityQueue import *
from zmienne import *

def heuristic(a, b):
    (x1, y1) = a
    (x2, y2) = b
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def czas(klasa):
    cost_class = {u'A': 1, u'S': 2, u'D': 7, u'G': 4, u'GP': 3, u'I': 8, u'Z': 5, u'L': 6}
    return cost_class[klasa]

start = (474503.5, 575294.72)
goal = (470563.61, 573688.75)
start_vid = 745122475
goal_vid = 276201578

# Implementacja algorytmu A* na postawie:
# https://www.redblobgames.com/pathfinding/a-star/implementation.html
def Astar(graph, xy, edges, cost_class, start_vid, goal_vid):
    frontier = PriorityQueue() # zbiór S
    frontier.put(start_vid, 0)
    came_from = {} # p - poprzedniki
    cost_so_far = {} # d - koszty dojścia
    came_from[start_vid] = None
    cost_so_far[start_vid] = 0

    while not frontier.empty():
        current_vid = frontier.get()
        if current_vid == goal_vid:
            break

        for next_edge in graph[current_vid]: # zbiór Q - sąsiedzi wierzchołka
            if edges[next_edge][0] != current_vid:
                next_vertex = edges[next_edge][0]
            else:
                next_vertex = edges[next_edge][1]
            length = edges[next_edge][3]
            new_cost = cost_so_far[current_vid] + length  #### length
            if next_vertex not in cost_so_far or new_cost < cost_so_far[next_vertex]:
                cost_so_far[next_vertex] = new_cost
                priority = new_cost + heuristic(xy[goal_vid], xy[next_vertex])
                frontier.put(next_vertex, priority)
                came_from[next_vertex] = current_vid

    return came_from, cost_so_far

came_from, cost_s = Astar(graph, xy, edges, cost_class, start_vid, goal_vid)
print came_from
print came_from[goal_vid]

start_vid = 745122475
goal_vid = 276201578

curr_vid = goal_vid
while 1:
    print curr_vid
    if curr_vid != start_vid:
        curr_vid = came_from[curr_vid]
    else:
        break