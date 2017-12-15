# -*- coding: utf-8 -*-
import os
from time import clock
import arcpy
from graf import *
from Astar import *

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

came_from, cost_s, krawedzie, dlugosc, czas = astar(graph, xy, edges, start_vid, goal_vid, arcpy.GetParameter(4), arcpy.GetParameter(3))
log = u'Całkowita dlugosc trasy (%s): %.3fm \nCzas pokonania: %is \nPrzeszukano %s węzłów \nDługość: %i krawędzi' % (arcpy.GetParameter(3), dlugosc, czas, len(came_from), len(krawedzie))
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
