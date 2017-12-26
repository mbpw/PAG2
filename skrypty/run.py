# -*- coding: utf-8 -*-
import os
from time import clock
import arcpy
import graf
from Astar import *

def secToTime(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return "%02dh %02dm %02ds" % (h, m, s)

def routeInfo(length, time, searches, edges):
    return u"Całkowita dlugość trasy: %.3fm \n Czas pokonania: %s \nPrzeszukano %s węzłów \nDługość: %i krawędzi" % (length, secToTime(time), searches, edges)

arcpy.env.workspace = arcpy.GetParameterAsText(0)
outputWorkspace = arcpy.env.workspace
arcpy.env.overwriteOutput = True
arcpy.AddMessage(u'Wczytałem bibliotekę ArcPy')

timer_on = clock()

# Nazwy plików
vertFC = "vertices.shp"
edgeFC = "edges.shp"
pathFC = "path.shp"
searchFC = "search.shp"

# Uruchomienie algorytmu A*
start_vid = arcpy.GetParameter(1) #837249756
goal_vid = arcpy.GetParameter(2) #346217664

came_from, cost_s, krawedzie, dlugosc, czas = astar(graf.graph, graf.xy, graf.edges, start_vid, goal_vid, arcpy.GetParameter(4), arcpy.GetParameter(3))
arcpy.AddMessage(type(dlugosc))
log = routeInfo(dlugosc, czas, len(came_from), len(krawedzie))
arcpy.AddMessage(log)

# Wizualizacja trasy
kraw = ", ".join(str(x) for x in krawedzie)
szuk = ", ".join(str(x) for x in came_from.keys())

arcpy.Select_analysis(edgeFC, pathFC, ' "EID" IN ('+kraw+')')
arcpy.Select_analysis(vertFC, searchFC, ' "VID" IN ('+szuk+')')
timer_off = clock() - timer_on
arcpy.AddMessage(u'Czas uruchomienia skryptu: %ss' % timer_off)

# Przygotowanie aktywnego dokumentu i DataFrame
if arcpy.GetParameter(5) == True:
    symbol_folder = arcpy.GetParameterAsText(6)
    mxd = arcpy.mapping.MapDocument("CURRENT")
    df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
    vLayer = arcpy.mapping.Layer(vertFC)
    eLayer = arcpy.mapping.Layer(edgeFC)
    sLayer = arcpy.mapping.Layer(searchFC)
    pLayer = arcpy.mapping.Layer(pathFC)

    # Symbology
    arcpy.ApplySymbologyFromLayer_management(vLayer, os.path.join(symbol_folder, 'vertices.lyr'))
    arcpy.ApplySymbologyFromLayer_management(eLayer, os.path.join(symbol_folder, 'edges.lyr'))
    arcpy.ApplySymbologyFromLayer_management(sLayer, os.path.join(symbol_folder, 'search.lyr'))
    arcpy.ApplySymbologyFromLayer_management(pLayer, os.path.join(symbol_folder, 'path.lyr'))

    # Dodanie plików shp do DataFrame
    arcpy.mapping.AddLayer(df, vLayer, "TOP")
    arcpy.mapping.AddLayer(df, eLayer, "TOP")
    arcpy.mapping.AddLayer(df, sLayer, "TOP")
    arcpy.mapping.AddLayer(df, pLayer, "TOP")

    # Odświeżenie
    arcpy.RefreshActiveView()
    arcpy.RefreshTOC()
    del mxd, df, vLayer, eLayer, pLayer, sLayer
