import sys
sys.path.append(r'c:\program files\python37\lib\site-packages')
sys.path.append(r'C:\Users\Azize Dje\Documents\QGIS\Python_Files')
from geopy.distance import great_circle as distance
from qgis.core import QgsGeometryUtils, QgsPoint, QgsPointXY
from geopy.point import Point
import networkx as nx
import Get_And_Draw as GaD
import math

# create id
id=0
    

def dist(P_long, P_lat, start_S_long, start_S_lat, end_S_long, end_S_lat):
    # find the point projected on the segment
    PRJ = QgsGeometryUtils.projectPointOnSegment(QgsPoint(P_long, P_lat), QgsPoint(start_S_long, start_S_lat), QgsPoint(end_S_long, end_S_lat))
    # creation of the points: projected and the trajectory
    P = Point(latitude=PRJ.y(), longitude=PRJ.x())
    R = Point(latitude=P_lat, longitude=P_long)
    # return the point projected on the segment and the geodesic distance between them
    return [distance(P, R), PRJ]

def GetCandidates(p, G, r):
    # id
    global id
    # get graph segments
    segments = list(G.edges())
    # as long as a point does not have a list of candidates, we loop
    while len(p['listCand']) == 0:
        # loop through segments
        for segment in segments:
            # avoid the error case of a conceded point as a segment
            if segment[0][0] != segment[1][0] or segment[0][1] != segment[1][1]:
                # get the point projected in the segment and the distance between them
                d, PRJ = dist(p['long'], p['lat'], segment[0][0], segment[0][1], segment[1][0], segment[1][1])
                # processes if the segment is in the circle of radius r of point p
                if d.meters <= r:
                    # add the candidate with its structure
                    p['listCand'].append( {'long': PRJ.x(), 'lat': PRJ.y(), 'dist':d.meters, 'id':id, 'parent_id':p['id']
                    , 'segCord':{'longlatStart': (segment[0][0], segment[0][1]), 'longlatEnd': (segment[1][0], segment[1][1])} } )
                    id=id+1
        # we progress the search by 50% of the circle radius
        r=r+r/2
    return p['listCand']

def V(c1, c2):
    T = GaD.Get_Traje_By_XmlFile()
    j=c1['parent_id']
    P = Point(latitude=T[j]['lat'], longitude=T[j]['long'])
    R = Point(latitude=T[j+1]['lat'], longitude=T[j+1]['long'])
    d = distance(P, R)
    v = d.meters
    return v

def N(c): #Normal distribution (Normal law)
    pi =math.pi
    s  =10
    m  =0
    xij=c['dist'] 
    N  =(1/math.sqrt(2*pi*s)) * math.exp(((xij-m)** 2)/(2*(s** 2)))                   
    return N

def Fs(c,ci): #Spatial Analysis
    fs= N(ci) * V(c, ci)
    return fs    

def Find_Matched_Sequence(listCands):
    # number of points of the trajectory
    n  = len(listCands)
    # the total number of all candidates obtained by each point
    nbrCands= listCands[-1][-1]['id']+1
    # allocate a memory space for the list f[] and pre[]  
    # a list f[] stores the score of each candidate
    f  = [None] * (nbrCands)
    # a list pre[] stores the predecessor of each candidate
    pre= [None] * (nbrCands)
    # fill in the lists f and pre
    Fill_lists_f_pre(listCands, n, f, pre)
    # initialize rList as an empty list
    rList=[None] * n
    # find the candidate with the highest score 
    c= Get_Candidat_With_Max_Scor(listCands, f)
    # fill rList with the max score path based on the list pre[] and in reverse
    for i in list(reversed(range(1,n))):
        rList[i]=c
        c=pre[c['id']]
    # fill in the first element    
    rList[0]=c
    return rList

def Fill_lists_f_pre(listCands, n, f, pre):
    # initialiser f[] par les valeur du premier partie du graphe dans la position s 
    for C1_s in listCands[0]:
        f[C1_s['id']]=N(C1_s)
    # browse the rset of the graph parts 
    for i in range(1,n):
        # browse the elements of a part of the graph 
        for Ci_s in listCands[i]:
            # - (infinity)
            max = sys.float_info.max*-1
            # ci-1_t
            for Cim1_t in listCands[i-1]:
                alt= f[Cim1_t['id']] + Fs(Cim1_t,Ci_s)
                if alt > max:
                    max= alt
                    pre[Ci_s['id']]= Cim1_t
                f[Ci_s['id']]= max
   
   
def Get_Candidat_With_Max_Scor(listCands, f):
    # la list du score des candidates de la dernier partie du graphe   
    listMaxScor= [{'Scor': f[node['id']],'candidate': node}  for node in listCands[-1]]
    # declare a max score
    MaxScor= {'Scor':sys.float_info.max*-1, 'c':None}
    # find the candidate who has the max score in the last part of the graph
    for i in range(len(listMaxScor)):        
        if listMaxScor[i]['Scor'] > MaxScor['Scor']:
            MaxScor=listMaxScor[i]
    # the candidate with the highest score in the last part of the graph
    return MaxScor['candidate']


def ST_Matching(G, T):
    # a list that represents the n-part graph of condidates
    tList =[]
    # preparation of the candidates and compilation of the list
    for i in range(len(T)):
        # find the list of candidates of a point i of the plot, a radius r=10 and in a graph G         s = GetCandidates(T[i], G, 10)
        # remplire les partie du graphe
        tList.append(s)
    # fill in the parts of the graph
    return Find_Matched_Sequence(tList)

# To Do:....
def Find_Trajectory(Tp,G):
    T=[]
    #g=G.copy
    segms=list(G.edges())
    # delete unresolve edges and add the new one
    for c in Tp:
        #G.remove_edge(c['segCord']['longlatStart'], c['segCord']['longlatEnd'])
        G.add_edges_from([
        ((c['long'], c['lat']), c['segCord']['longlatStart']), 
        ((c['long'], c['lat']), c['segCord']['longlatEnd'  ]) 
        ])
    # weigth for all segments of the graph
    for s in segms:
        G[s[0]][s[1]]['weight'] = distance(s[0][0], s[0][1], s[1][0], s[1][1]).meters
    for i in range(len(Tp)-1):
        #dijikstra
        path=nx.algorithms.shortest_paths.weighted.dijkstra_path(G, (Tp[i]['long'], Tp[i]['lat']), (Tp[i+1]['long'],Tp[i+1]['lat']), weight='weight')
        #T.append(Tp[i])
        #for node in path:
         #   T.append(node)
    return T
