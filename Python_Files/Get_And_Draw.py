import networkx as nx
import xml.etree.ElementTree as ET
from qgis.core import QgsVectorLayer, QgsPointXY, QgsFeature, QgsGeometry, QgsProject

def Get_Traje_By_XmlFile():
    # le chemine de fichier xml de la trajectoire
    xml_file = 'C:\\Users\\Azize Dje\\Documents\\QGIS\\Python_Files\\Xml_File\\trajectory.xml'
    # converter le fichier xml vers un arbre
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # création d'un identifiant
    id=0
    # extraire tout les points de puis le fichier xml
    T = []
    for child in root:
        for kid in child:
            T.append({'long': float(kid.attrib['lon'])
                    , 'lat': float(kid.attrib['lat'])
                    , 'id':id
                    , 'listCand': []})
            id+=1
    return T

def Draw_Trajectory(T):
    # creer une couche de points memoire
    Points_layer = QgsVectorLayer('Point', 'Points_Trajectory', "memory")
    Points_pr = Points_layer.dataProvider()
    # creer une couche de segments memoire
    Traje_layer = QgsVectorLayer('LineString', 'Trajectory', "memory")
    Traje_pr = Traje_layer.dataProvider()
    # creer et ajouter les points et les segments
    for i in range(1, len(T)):
        p1 = T[i - 1]
        p2 = T[i]
        point1 = QgsPointXY(p1['long'], p1['lat'])
        point2 = QgsPointXY(p2['long'], p2['lat'])
        # creer et ajouter le point
        point = QgsFeature()
        point.setGeometry(QgsGeometry.fromPointXY(point1))
        Points_pr.addFeatures([point])
        # creer et ajouter la segment
        segment = QgsFeature()
        segment.setGeometry(QgsGeometry.fromPolylineXY([point1, point2]))
        Traje_pr.addFeatures([segment])
    # ajouter le dernier point
    point = QgsFeature()
    point.setGeometry(QgsGeometry.fromPointXY(point2))
    Points_pr.addFeatures([point])
    # update
    Points_layer.updateExtents()
    Traje_layer.updateExtents()
    QgsProject.instance().addMapLayers([Traje_layer, Points_layer])

def Get_Graph_From_ShapeFile():
    # convert shapefile vers un graphe networkx ,on spécifiant le chemine du fichier shapefile
    G = nx.read_shp(r'C:\Users\Azize Dje\Documents\QGIS\ShapeFile\Oran_Map.shp')
    return G

def Draw_Graph(G):
    # extraire Les Sommets du Graphe G
    Nodes = list(G.nodes)
    # extraire Les Segments  du Graphe G
    Segments = list(G.edges())
    # creer une couche de Sommets memoire
    Nodes_layer = QgsVectorLayer('Point', 'Nodes', "memory")
    Nodes_pr = Nodes_layer.dataProvider()
    # creer une couche de Segments memoire
    Segments_layer = QgsVectorLayer('LineString', 'Segments', "memory")
    Segments_pr = Segments_layer.dataProvider()
    # les Sommets
    for i in range(len(Nodes)):
        Node = QgsPointXY(Nodes[i][0], Nodes[i][1])
        # creer et ajouter le Sommet
        point = QgsFeature()
        point.setGeometry(QgsGeometry.fromPointXY(Node))
        Nodes_pr.addFeatures([point])
    # les Segments
    for i in range(len(Segments)):
        Start_Node = QgsPointXY(Segments[i][0][0], Segments[i][0][1])
        End_Node = QgsPointXY(Segments[i][1][0], Segments[i][1][1])
        if Start_Node.x() != End_Node.x() or Start_Node.y() != End_Node.y():
            # creer et ajouter la line
            segment = QgsFeature()
            segment.setGeometry(QgsGeometry.fromPolylineXY([Start_Node, End_Node]))
            Segments_pr.addFeatures([segment])
    Nodes_layer.updateExtents()
    Segments_layer.updateExtents()
    QgsProject.instance().addMapLayers([Nodes_layer, Segments_layer])
