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

timer_on = clock()

# Nazwy plików
vertFC = "vertices.shp"
edgeFC = "edges.shp"
pathFC = arcpy.GetParameterAsText(3)
searchFC = "search.shp"

# TRASA ALTERNATYWNA - lista krawędzi poprzedniej trasy
alt_path = []

# Wczytanie krawędzi ewentualnej poprzedniej trasy do listy
if arcpy.Exists(arcpy.GetParameterAsText(8)):
        altCursor = arcpy.da.SearchCursor(arcpy.GetParameterAsText(8), ["EID"])
        for row in altCursor:
            alt_path.append(row[0])

# Uruchomienie algorytmu A*
start_vid = arcpy.GetParameter(1)
goal_vid = arcpy.GetParameter(2)

came_from, krawedzie, dlugosc, czas = astar(graf.graph, graf.xy, graf.edges, start_vid, goal_vid, arcpy.GetParameter(5), arcpy.GetParameter(4), alt_path)
log = routeInfo(dlugosc, czas, len(came_from), len(krawedzie))
arcpy.AddMessage(log)

# Wizualizacja trasy
kraw = ", ".join(str(x) for x in krawedzie)
szuk = ", ".join(str(x) for x in came_from.keys())

# COPY ZAMIAST SELECTA - każda ścieżka w oddzielnym pliku
arcpy.Select_analysis(edgeFC, pathFC, ' "EID" IN ('+kraw+')')
arcpy.Select_analysis(vertFC, searchFC, ' "VID" IN ('+szuk+')')
timer_off = clock() - timer_on
arcpy.AddMessage(u'Czas uruchomienia skryptu: %ss' % timer_off)

# Przygotowanie aktywnego dokumentu i DataFrame
if arcpy.GetParameter(6) == True:
    symbol_folder = arcpy.GetParameterAsText(7)
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
