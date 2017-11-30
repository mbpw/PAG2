# -*- coding: utf-8 -*-
import arcpy

print "Załadowałem arcpy"

arcpy.env.workspace = "D:/! PW/semestr 5/PAG/PAG2/dane_przestrzenne/BDOT_Torun/miasto"  # [zmienić na parametr]
outputWorkspace = arcpy.env.workspace  # [zmienić na parametr]
arcpy.env.overwriteOutput = True

# Nazwy plików // [zmienić na parametry]
inFC = "L4_1_BDOT10k__OT_SKJZ_L.shp"
vertFC = "vertices.shp"
edgeFC = "edges.shp"

# Usuwanie ewentualnych istniejących plików
if arcpy.Exists(vertFC):
    arcpy.Delete_management(vertFC)
if arcpy.Exists(edgeFC):
    arcpy.Delete_management(edgeFC)

# Tworzenie nowych plików
sr = arcpy.SpatialReference(102173)
arcpy.CreateFeatureclass_management(outputWorkspace, vertFC, "POINT", spatial_reference=sr)
arcpy.CreateFeatureclass_management(outputWorkspace, edgeFC, "POLYLINE", spatial_reference=sr)

# Dodawanie pól (id, x, y) do kolekcji wierzchołków
arcpy.AddField_management(vertFC, 'VID', 'LONG', 9)
arcpy.AddField_management(vertFC, 'X', 'DOUBLE')
arcpy.AddField_management(vertFC, 'Y', 'DOUBLE')
# Dodawanie pól (id, id_from, id_to, id_jezdni) do kolekcji krawędzi
arcpy.AddField_management(edgeFC, 'EID', 'LONG', 9)
arcpy.AddField_management(edgeFC, 'id_from', 'LONG', 9)
arcpy.AddField_management(edgeFC, 'id_to', 'LONG', 9)
arcpy.AddField_management(edgeFC, 'id_jezdni', 'LONG', 9)

# Tworzenie kursorów do wypełniania kolekcji
inVCursor = arcpy.da.InsertCursor(vertFC, ["SHAPE@XY", "VID", "X", "Y"])
inECursor = arcpy.da.InsertCursor(edgeFC, ["SHAPE@", "EID", "id_from", "id_to", "id_jezdni"])
print "Stworzyłem kursory"

# Licznik określający id krawędzi
count_edge = 0

# Pętla przez istniejące jezdnie
# Wypełnia pliki "vertices.shp" oraz "edges.shp" tworząc kolekcje wierzchołków i krawędzi
for row in arcpy.da.SearchCursor(inFC, ["OID@", "SHAPE@"]):
    # Punkt początkowy odcinka jezdni
    startpt = row[1].firstPoint
    startx = startpt.X
    starty = startpt.Y
    # Tworzenie identyfikatora składającego się z 4 ostatnich cyfr wsp. X oraz 5 ostatnich cyfr wsp. Y
    a = str(startx).split('.')
    b = str(starty).split('.')
    startid = long("".join(a)[-4:] + "".join(b)[-5:])
    # Wstawienie punktu
    sptValues = ((startx, starty), startid, startx, starty)
    inVCursor.insertRow(sptValues)

    # Punkt końcowy odcinka jezdni
    endpt = row[1].lastPoint
    endx = endpt.X
    endy = endpt.Y
    # Tworzenie identyfikatora (patrz wyżej)
    a = str(endx).split('.')
    b = str(endy).split('.')
    endid = long("".join(a)[-4:] + "".join(b)[-5:])
    # Wstawienie punktu
    eptValues = ((endx, endy), endid, endx, endy)
    inVCursor.insertRow(eptValues)

    # Wstawienie krawędzi
    inECursor.insertRow((row[1], count_edge, startid, endid, row[0]))
    count_edge += 1

# Usunięcie zduplikowanych wierzchołków
arcpy.DeleteIdentical_management(vertFC, "SHAPE")
# Czyszczenie pamięci
del inVCursor
del inECursor
