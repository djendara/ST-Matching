import sys
sys.path.append(r'/Python_Files')
import Map_Matching as MpMt
import Get_And_Draw as GaD

# find the plot from an XML file
T  = GaD.Get_Traje_By_XmlFile()
# find the graph from a Shapefile
G  = GaD.Get_Graph_From_ShapeFile()
# find the right path from a graph G and a list T of the path
Tp = MpMt.ST_Matching(G, T)
# draw the graph
#GaD.Draw_Graph(G)
# draw the path
#GaD.Draw_Trajectory(T)
# draw the right path
GaD.Draw_Trajectory(Tp)

# To Do...
#t=MpMt.Find_Trajectory(Tp,G)