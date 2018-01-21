# -*- coding: utf-8 -*-
import math
from PriorityQueue import *
import arcpy

def heuristic(a, b, fastest):
    (x1, y1) = a
    (x2, y2) = b
    if fastest:
        return (math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2) / 1000) * czas('A')
    else:
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

# Funkcja zwracająca w jakim czasie (s) pokona się trasę 1km korzystając z drogi o określonej klasie
# Średnie prędkości uśrednione na podstawie https://pl.wikipedia.org/wiki/Klasy_i_kategorie_dr%C3%B3g_publicznych_w_Polsce
def czas(klasa):
    v_class = {u'A': 120, u'S': 100, u'D': 30, u'G': 60, u'GP': 80, u'I': 10, u'Z': 50, u'L': 40}
    return 3600.0 / (v_class[klasa])

# Implementacja algorytmu A* na postawie:
# https://www.redblobgames.com/pathfinding/a-star/implementation.html
def astar(graph, xy, edges, start_vid, goal_vid, dijkstra, fastest, alternative_path):
    frontier = PriorityQueue()  #### zbiór Q
    frontier.put(start_vid, 0)
    came_from = {}  #### p - poprzedniki
    cost_so_far = {}  #### d - koszty dojścia
    came_from[start_vid] = None
    cost_so_far[start_vid] = 0

    while not frontier.empty():
        current_vid = frontier.get()
        if current_vid == goal_vid:  #### warunek zakończenia algorytmu - napotkano wierzchołek docelowy
            break

        for next_edge in graph[current_vid]:  #### zbiór S - sąsiedzi wierzchołka
            priority = 0
            if edges[next_edge][0] != current_vid:
                next_vertex = edges[next_edge][0]
            else:
                next_vertex = edges[next_edge][1]
            length = edges[next_edge][3]  #### długość przeszukiwanej krawędzi

            v_FROM = edges[next_edge][0]  ### vertex FROM
            v_TO = edges[next_edge][1]  ### vertex TO
            arcpy.AddMessage("["+str(next_edge)+"] FROM " + str(edges[next_edge][0]) + "TO: " + str(edges[next_edge][1]))

            # Kierunkowość krawędzi
            kierunkowosc = edges[next_edge][5]
            if (kierunkowosc != 3) and ((kierunkowosc == 0) or (kierunkowosc == 1 and v_FROM == current_vid) or (kierunkowosc == 2 and v_TO == current_vid)):
                # Trasa najkrótsza
                if not fastest:
                    penalty = length*0.5
                    new_cost = cost_so_far[current_vid] + length
                # Trasa najszybsza
                else:
                    klasa = edges[next_edge][4]
                    time = length / 1000.0 * czas(klasa)
                    penalty = time * 0.5
                    new_cost = cost_so_far[current_vid] + time
                # Kara, jeśli krawędź pokrywa się z poprzednią trasą
                if next_edge in alternative_path:
                    new_cost += penalty
                # Dodanie wierzchołka do Q
                if next_vertex not in cost_so_far or new_cost < cost_so_far[next_vertex]:
                    cost_so_far[next_vertex] = new_cost
                    if not dijkstra:
                        priority += new_cost + heuristic(xy[goal_vid], xy[next_vertex], False)
                    else:
                        priority += new_cost + 0  #### Dijkstra
                    frontier.put(next_vertex, priority)
                    came_from[next_vertex] = current_vid

    # Odtworzenie ścieżki
    path_edges = []
    curr_vid = goal_vid
    time = 0
    distance = 0
    while curr_vid != start_vid:
        next_vid = came_from[curr_vid]
        for eid in graph[curr_vid]:
            if edges[eid][1] == next_vid or edges[eid][0] == next_vid:
                path_edges.append(eid)
                l = edges[eid][3]
                k = edges[eid][4]
                distance += l
                time += (l / 1000) * czas(k)
        curr_vid = next_vid

    # Przekazanie listy przeszukanych wierzchołków, krawędzi trasy, obliczonego dystansu oraz czasu
    return came_from, path_edges, distance, time
