import sys
sys.path.append(r'c:\program files\python37\lib\site-packages')
sys.path.append(r'C:\Users\Azize Dje\Documents\QGIS\Python_Files')
from geopy.distance import great_circle as distance
from qgis.core import QgsGeometryUtils, QgsPoint, QgsPointXY
from geopy.point import Point
import networkx as nx
import Get_And_Draw as GaD
import math

# création d'un identifiant
id=0
    

def dist(P_long, P_lat, start_S_long, start_S_lat, end_S_long, end_S_lat):
    # trouver le point projeté sur le segment
    PRJ = QgsGeometryUtils.projectPointOnSegment(QgsPoint(P_long, P_lat), QgsPoint(start_S_long, start_S_lat), QgsPoint(end_S_long, end_S_lat))
    # création du points:  projeté et de la trajectoire
    P = Point(latitude=PRJ.y(), longitude=PRJ.x())
    R = Point(latitude=P_lat, longitude=P_long)
    # retourner le point projeté sur le segment et la distance géodésique entre eux
    return [distance(P, R), PRJ]

def GetCandidates(p, G, r):
    # un identifiant
    global id
    # recuperation des segments du graphe
    segments = list(G.edges())
    # tantque un point il n'a pas une list des candidats on boucle
    while len(p['listCand']) == 0:
        # parcours sur les segments
        for segment in segments:
            # eviter le cas d'erreur d'un point concéder comme un segment
            if segment[0][0] != segment[1][0] or segment[0][1] != segment[1][1]:
                # recuperation du point projeté dans le segment et la distance entre eux
                d, PRJ = dist(p['long'], p['lat'], segment[0][0], segment[0][1], segment[1][0], segment[1][1])
                # traite si le segment est dans le cercle de rayon r du point p
                if d.meters <= r:
                    # ajouter le candidate avec sa structure
                    p['listCand'].append( {'long': PRJ.x(), 'lat': PRJ.y(), 'dist':d.meters, 'id':id, 'parent_id':p['id']
                    , 'segCord':{'longlatStart': (segment[0][0], segment[0][1]), 'longlatEnd': (segment[1][0], segment[1][1])} } )
                    id=id+1
        # on progresse la recherche par 50% du rayon de cercle
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

def N(c): #Loi normale
    pi =math.pi
    s  =10
    m  =0
    xij=c['dist'] #?
    N  =(1/math.sqrt(2*pi*s)) * math.exp(((xij-m)** 2)/(2*(s** 2)))                   
    return N

def Fs(c,ci): #Analyse Spatiale
    fs= N(ci) * V(c, ci)
    return fs    

def Find_Matched_Sequence(listCands):
    # nombre de points du trajectoire
    n  = len(listCands)
    # le nombre total de tous les candidats obtenu par chaque point
    nbrCands= listCands[-1][-1]['id']+1
    # allouer un espace mémoire pour les list f[] et pre[] 
    # une list f[] stocke le score de chaque candidate
    f  = [None] * (nbrCands)
    # une list pre[] stocke le prédécesseur de chaque candidate
    pre= [None] * (nbrCands)
    # remplire les listes f et pre
    Fill_lists_f_pre(listCands, n, f, pre)
    # initialiser rList comme une list vide
    rList=[None] * n
    # trouver le candidat avec le max score 
    c= Get_Candidat_With_Max_Scor(listCands, f)
    # remplire rList par le max score chemin en se basent sur la list pre[] et de façon inverse
    for i in list(reversed(range(1,n))):
        rList[i]=c
        c=pre[c['id']]
    # remplire le premire element    
    rList[0]=c
    return rList

def Fill_lists_f_pre(listCands, n, f, pre):
    # initialiser f[] par les valeur du premier partie du graphe dans la position s 
    for C1_s in listCands[0]:
        f[C1_s['id']]=N(C1_s)
    # parcourir le rset des partie du graphe 
    for i in range(1,n):
        # parcourir les elements d'un partie du graphe 
        for Ci_s in listCands[i]:
            # - (l'infini)
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
    # declarer un max score
    MaxScor= {'Scor':sys.float_info.max*-1, 'c':None}
    # trouver le candidate qui a le max score dans la dernier partie du graphe
    for i in range(len(listMaxScor)):        
        if listMaxScor[i]['Scor'] > MaxScor['Scor']:
            MaxScor=listMaxScor[i]
    # le candidats qui a le max score dans la dernier partie du graphe
    return MaxScor['candidate']


def ST_Matching(G, T):
    # une list qui représenté le graphe n-partie des condidats
    tList =[]
    # preparation des candidats et constrection du tList
    for i in range(len(T)):
        # trouver la liste des candidats d'un point i du traje, un rayon r=10 et dans un graphe G 
        s = GetCandidates(T[i], G, 10)
        # remplire les partie du graphe
        tList.append(s)
    # Trouver une séquence correspondante de notre traje
    return Find_Matched_Sequence(tList)

# n'est pas compleeeeeet
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
