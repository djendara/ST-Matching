import sys
sys.path.append(r'C:\Users\Azize Dje\Documents\QGIS\Python_Files')
import Map_Matching as MpMt
import Get_And_Draw as GaD

# trouver la traje depuis un fichier XML
T  = GaD.Get_Traje_By_XmlFile()
# trouver le graphe depuis un fichier Shapefile
G  = GaD.Get_Graph_From_ShapeFile()
# trouver la bon traje depuis un graphe G et une list T de la trajet
Tp = MpMt.ST_Matching(G, T)
# dessiner le graphe
#GaD.Draw_Graph(G)
# dessiner la trajet
#GaD.Draw_Trajectory(T)
# dessiner la bon trajet
GaD.Draw_Trajectory(Tp)
#t=MpMt.Find_Trajectory(Tp,G)