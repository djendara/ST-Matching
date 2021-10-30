import networkx as nx
import xml.etree.ElementTree as ET
from qgis.core import QgsVectorLayer, QgsPointXY, QgsFeature, QgsGeometry, QgsProject

def Get_Traje_By_XmlFile():
    # path to the xml file for the trajectory
    xml_file = '/path_to_xml_file/trajectory.xml'
    # convert the xml file to a tree
    tree = ET.parse(xml_file)
    root = tree.getroot()
    # create id
    id=0
    # extract all the points from the xml file
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
    # create a layer of memory points
    Points_layer = QgsVectorLayer('Point', 'Points_Trajectory', "memory")
    Points_pr = Points_layer.dataProvider()
    # create a layer of memory segments
    Traje_layer = QgsVectorLayer('LineString', 'Trajectory', "memory")
    Traje_pr = Traje_layer.dataProvider()
    # create and add points and segments
    for i in range(1, len(T)):
        p1 = T[i - 1]
        p2 = T[i]
        point1 = QgsPointXY(p1['long'], p1['lat'])
        point2 = QgsPointXY(p2['long'], p2['lat'])
        # create and add point
        point = QgsFeature()
        point.setGeometry(QgsGeometry.fromPointXY(point1))
        Points_pr.addFeatures([point])
        # create and add the segment
        segment = QgsFeature()
        segment.setGeometry(QgsGeometry.fromPolylineXY([point1, point2]))
        Traje_pr.addFeatures([segment])
    # add the last point
    point = QgsFeature()
    point.setGeometry(QgsGeometry.fromPointXY(point2))
    Points_pr.addFeatures([point])
    # update
    Points_layer.updateExtents()
    Traje_layer.updateExtents()
    QgsProject.instance().addMapLayers([Traje_layer, Points_layer])

def Get_Graph_From_ShapeFile():
    # convert shapefile to a networkx graph, we specify the path of the shapefile file
    G = nx.read_shp(r'/ShapeFile/Oran_Map.shp')
    return G

def Draw_Graph(G):
    # extract Vertices (nodes) from Graph G
    Nodes = list(G.nodes)
    # extract Segments of Graph G
    Segments = list(G.edges())
    # create a layer of memory nodes
    Nodes_layer = QgsVectorLayer('Point', 'Nodes', "memory")
    Nodes_pr = Nodes_layer.dataProvider()
    # create a layer of memory segments
    Segments_layer = QgsVectorLayer('LineString', 'Segments', "memory")
    Segments_pr = Segments_layer.dataProvider()
    # Nodes
    for i in range(len(Nodes)):
        Node = QgsPointXY(Nodes[i][0], Nodes[i][1])
        # create and add the node
        point = QgsFeature()
        point.setGeometry(QgsGeometry.fromPointXY(Node))
        Nodes_pr.addFeatures([point])
    # Segments
    for i in range(len(Segments)):
        Start_Node = QgsPointXY(Segments[i][0][0], Segments[i][0][1])
        End_Node = QgsPointXY(Segments[i][1][0], Segments[i][1][1])
        if Start_Node.x() != End_Node.x() or Start_Node.y() != End_Node.y():
            # create and add the line
            segment = QgsFeature()
            segment.setGeometry(QgsGeometry.fromPolylineXY([Start_Node, End_Node]))
            Segments_pr.addFeatures([segment])
    Nodes_layer.updateExtents()
    Segments_layer.updateExtents()
    QgsProject.instance().addMapLayers([Nodes_layer, Segments_layer])
