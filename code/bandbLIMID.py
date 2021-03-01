import numpy as np
import os
from pylab import *
import matplotlib.pyplot as plt
from IPython.core.display import display,HTML
import math
import pyAgrum as gum

class BranchAndBoundLIMIDInference():

    def __init__(self,ID,OrdreDecision):
        self.ID=ID
        self.ordreDecision=OrdreDecision

    #ID-->DAG-->MoralizedAncestral(UndiGraph)-->MoralizedAncestral(DiGraph)
    #-->graphe auxilliaire-->Matrice représentative-->CoupeMin-->SIS
    def SIS(self,decisionNodeID):
        #ID-->DAG-->MoralizedAncestral(UndiGraph)-->MoralizedAncestral(DiGraph)
        moralizedAncestral,id_source,id_puit=self.fromIDToMoralizedAncestral(decisionNodeID)

        #TODO: verifier qu'il n'y ait pas d'arc entre alpha et X et entre Y et Beta dans F-F, mettre cap infini dans F-F

        #MoralizedAncestral(DiGraph)-->graphe auxilliaire
        graph_Auxilliaire,id_source_aux_plus,id_source_aux_moins,id_puit_aux_plus,id_puit_aux_moins=self.graphAuxilliaire(moralizedAncestral,id_source,id_puit)

        #-->graphe auxilliaire-->Matrice représentative
        GraphMatrix=self.getGraphMatrixWithCapacityOneFromDiGraph(graph_Auxilliaire)
        g=Graph(GraphMatrix)

        #Matrice représentative-->CoupeMin
        source=list(graph_Auxilliaire.nodes()).index(id_source_aux_moins)
        sink=list(graph_Auxilliaire.nodes()).index(id_puit_aux_plus)
        mincut=g.mincut(source, sink)

        mincutDansGrapheAux=[]
        for arc in mincut:
            #arcs en fonction des identifiants dans le graphe auxilliaire
            mincutDansGrapheAux.append([list(graph_Auxilliaire.nodes())[arc[0]],list(graph_Auxilliaire.nodes())[arc[1]]])

        #CoupeMin-->SIS
        SIS=[]
        maxList=len(list(moralizedAncestral.nodes()))
        for arc in mincutDansGrapheAux:
            if(arc[0]==arc[1]+maxList):
                SIS.append(arc[0])

        return SIS
    #1+2.a ID-->DAG-->MoralizedAncestral(UndiGraph)-->MoralizedAncestral(DiGraph)
    def fromIDToMoralizedAncestral(self,decisionNodeID):
        """
        Fonction qui transforme l'ID en graphe moralisé ancestral pour appliquer Acid&Campos

        ID le diagramme d'influence étudié
        decisionNodeID est l'identifiant du noeud de décision pour lequel on veut trouver le SIS
        ordre est l'ordre de la prise de décision dans l'ID (identifiants des noeuds de décision)

        renvoi le graphe moralisé ancestral (version digraphe) et les identifiants des noeuds sources et puits
        """
        #--construction de X=fa(Delta_j)--
        #(reunion des familles des noeuds de decisions précedant decisionNode selon l'ordre ordre)
        X=[]
        for nodeID in self.ID.nodes():
            if(self.ID.isDecisionNode(nodeID)):
                if(self.ordreDecision.index(nodeID)<=self.ordreDecision.index(decisionNodeID)): #si il precède dj dans l'ordre
                    X=X+list(self.ID.family(nodeID)).copy()
        #--Construction de Y--
        Y=list(self.ID.descendants(decisionNodeID)).copy()
        for nodeID in Y:
            if(not self.ID.isUtilityNode(nodeID)):
                Y.remove(nodeID)
        XUY=X+Y
        XUYNames=self.getNamesFromID(XUY)
        #--Construction du graphe ancestral moralisé--
        MoralizedAncestral=self.ID.moralizedAncestralGraph(XUYNames)#un undigraph avec des noeuds de mêmes identifiants que ceux du diagramme d'influences
        #--Ajout des noeuds sources(alpha) et puit (beta) et de leurs aretes
        alphaXid=MoralizedAncestral.addNode()
        BetaYid=MoralizedAncestral.addNode()
        for nodeID in MoralizedAncestral.nodes():
            for node2ID in MoralizedAncestral.nodes():
                if((nodeID,node2ID) in MoralizedAncestral.edges() or (node2ID,nodeID) in MoralizedAncestral.edges()):
                    if(node2ID in X):
                        MoralizedAncestral.addEdge(alphaXid,nodeID)
                        break
                    elif(nodeID in Y):
                        MoralizedAncestral.addEdge(BetaYid,nodeID)
                        break
        MoralizedAncestral_digraph=self.getDigraphFromUnDiGraph(MoralizedAncestral)
        return MoralizedAncestral_digraph,alphaXid,BetaYid   

    #MoralizedAncestral(DiGraph)-->Graph auxillaire
    def graphAuxilliaire(self,MoralizedAncestral_digraph,id_source,id_puit):
        """
        fonction qui retourne le graph auxilliaire a partir d'un graph non dirigé
        """
        graphAuxilliaire=gum.DiGraph()
        listNode=list(MoralizedAncestral_digraph.nodes())
        maxList=len(listNode)

        #Pour chaque noeud, ajouter deux noeud u+ et u-
        #dans graphe moral : [u0,u1,u2,u3,u4]
        #dans graphe auxilliaire : [u0+,u1+,u2+,u3+,u4+,u0-,u1-,u2-u3-,u4-]
        for i in range(len(listNode)):
            #Pour chaque noeud du dag, ajouter un noeud u+, u-
            graphAuxilliaire.addNodeWithId(listNode[i])
            graphAuxilliaire.addNodeWithId(listNode[i]+maxList) #assure qu'il n'y ait pas de conflit d'identifiants et permet de ne gérer qu'un seul vecteur
            if(listNode[i]==id_source):
                id_source_aux_plus=listNode[i]
                id_source_aux_moins=listNode[i]+maxList
            elif(listNode[i]==id_puit):
                id_puit_aux_plus=listNode[i]
                id_puit_aux_moins=listNode[i]+maxList
            #Creer un arc entre u+ et u-
            graphAuxilliaire.addArc(listNode[i],listNode[i]+maxList)

        #pour chaque arc u->v dans le digraph, créer un arc (u-)->v+
        for arc in list(MoralizedAncestral_digraph.arcs()):
            id_noeud_depart=arc[0]
            id_noeud_arrive=arc[1]
            id_noeud_depart_moins_dans_graphe_aux=id_noeud_depart+maxList
            id_noeud_arrive_plus_dans_graphe_aux=id_noeud_arrive
            graphAuxilliaire.addArc(id_noeud_depart_moins_dans_graphe_aux,id_noeud_arrive_plus_dans_graphe_aux)

        return graphAuxilliaire,id_source_aux_plus,id_source_aux_moins,id_puit_aux_plus,id_puit_aux_moins

    

    #--Méthodes utilitaires--
    def getNamesFromID(self,listId):
        """
        retourne les noms des noeuds donnés sous forme d'identifiant (listId) dans le diagramme d'influence InDi
        """
        names=[]
        for name in self.ID.names():
            if(self.ID.idFromName(name) in listId):
                names.append(name)
        return names
    def fromIDtoDAG(self):
        """
        Rend un DAG pour un ID donné (ses noeuds ont les mêmes identifiants que ceux de l'ID)
        Le DAG rendu a un noeud correspondant à chaque noeud chance/decision mais pas pour les noeuds utilité. Il a aussi les mêmes arcs que l'ID (sans ceux vers les noeuds d'utilité bien sur car ils ne sont pas dans le DAG)
        """
        dag=gum.DAG()
        for nodeID in self.ID.nodes():
            if(not self.ID.isUtilityNode(nodeID)):
                dag.addNodeWithId(nodeID)
        for arc in self.ID.arcs():
            source=arc[0]
            destination=arc[1]
            if(not self.ID.isUtilityNode(source) and not self.ID.isUtilityNode(destination)):
                dag.addArc(source,destination)
        return dag
    def getDigraphFromUnDiGraph(self,UnDiGraph):
        """
        fonction qui transforme un graph non dirige en graph dirige avec les mêmes identifiants
        """
        digraph=gum.DiGraph()
        for noeud in UnDiGraph.nodes():
            digraph.addNodeWithId(noeud)
        for arete in UnDiGraph.edges():
            digraph.addArc(arete[0],arete[1])
            digraph.addArc(arete[1],arete[0])
        return digraph

    def getGraphMatrixWithCapacityOneFromDiGraph(self,DiGraph):
        """
        rend une matrice représentative du graphe dirigé donné en paramètre avec 1 si il y a un arc entre 
        un noeud du graphe vers un autre et 0 sinon
        """
        list_noeud=list(DiGraph.nodes())
        nb_noeud=len(list_noeud)
        graph=np.zeros((nb_noeud,nb_noeud))
        for arc in DiGraph.arcs(): 
            depart=list_noeud.index(arc[0])
            arrive=list_noeud.index(arc[1])
            graph[depart,arrive]=1

        return graph

class Graph:

    def __init__(self, graph):
        self.graph = graph
        self. ROW = len(graph)
        self.visited=[]


    # Using BFS as a searching algorithm 
    def searching_algo_BFS(self, s, t, parent):

        self.visited = [False] * (self.ROW)
        queue = []

        queue.append(s)
        self.visited[s] = True

        while queue:

            u = queue.pop(0)

            for ind, val in enumerate(self.graph[u]):
                if self.visited[ind] == False and val > 0:
                    queue.append(ind)
                    self.visited[ind] = True
                    parent[ind] = u

        return True if self.visited[t] else False

    # Applying fordfulkerson algorithm
    def ford_fulkerson(self, source, sink):
        temp=[]
        for i in range(len(self.graph)):
            temp.append(self.graph[i].copy())
        parent = [-1] * (self.ROW)
        max_flow = 0

        while self.searching_algo_BFS(source, sink, parent):

            path_flow = float("Inf")
            s = sink
            while(s != source):
                path_flow = min(path_flow, self.graph[parent[s]][s])
                s = parent[s]

            # Adding the path flows
            max_flow += path_flow

            # Updating the residual values of edges
            v = sink
            while(v != source):
                u = parent[v]
                self.graph[u][v] -= path_flow
                self.graph[v][u] += path_flow
                v = parent[v]
        self.graph=temp
        return max_flow,self.visited
    
    def mincut(self,source, sink):
        column=len(self.graph[0])
        max_flow,marque=self.ford_fulkerson(source,sink)
        mincut=[]
        for i in range(len(marque)):
            #si le noeud numéro i est marqué
            if(marque[i]):
                for k in range(column):
                    #si il y a un arc entre le noeud i et le noeud k, il ne faut pas que le noeud k soit marqué
                    if(self.graph[i][k]>0 and not marque[k]):
                        mincut.append([i,k])
        return mincut




