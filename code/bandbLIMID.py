import numpy as np
import os
from pylab import *
import matplotlib.pyplot as plt
from IPython.core.display import Math, display,HTML
import math
import pyAgrum as gum

class BranchAndBoundLIMIDInference():

    def __init__(self,ID,OrdreDecision):
        self.ID=ID
        self.ordreDecision=OrdreDecision

    #ID->DAG (sans neouds utilités)->graphe moralisé ancestral ou on doit trouver l'ensemble de noeuds
    #séparant X et Y
    def SIS(self,decisionNodeID):
        labelledScanned="labelledScanned"
        labelledUnscanned="labelledUnscanned"
        unlabelled="unlabelled"
        #--Construction du graphe moralisé sur lequel appliquer l'algorithme--
        moralizedAncestral,id_source,id_puit=self.fromIDToMoralizedAncestral(decisionNodeID)
        #--Construction du graphe de travail sur lequel on peut appliquer l'algorithme--
        workGraph=GraphForSIS()
        for id in moralizedAncestral.nodes():
            #All nodes unlabelled and IN property set to false
            workGraph.addNode(id,unlabelled,None,None,False)
        for edge in moralizedAncestral.edge():
            workGraph.addEdge(edge[0],edge[1],1,None,None)

        #---Algorithme----
        queue=[]
        while(True):
            #Step 1
            y=workGraph.getNode(id_puit)
            workGraph.setLabel_Positive(y,y)
            queue.append(y)
            workGraph.setState(y,labelledUnscanned)
            #Step 2 & 3
            x=id_source
            while(True):
                u=queue.pop()
                #1
                if(workGraph.getNode(u).getIN()==False):
                    workGraph.fsearch(u)
                #2
                if(workGraph.getNode(u).getIN()==True and workGraph.getNode(u).getLabel_Negative()==None and workGraph.getNode(u).getLabel_Positive()!=None):
                    workGraph.bsearch(u,y,queue)
                #3
                if(workGraph.getNode(u).getIN()==True and workGraph.getNode(u).getLabel_Negative()!=None):
                    workGraph.fsearch(u)
                    workGraph.bsearch(u,y,queue)
                #4
                workGraph.setState(u,labelledScanned)
                if ((len(queue)<=0 and workGraph.getState(x)==unlabelled) or workGraph.getState(x)==labelledScanned or workGraph.getState(x)==labelledUnscanned):
                    break
            if(workGraph.getState(x)==labelledScanned or workGraph.getState(x)==labelledUnscanned):
                #Step 4
                u=x
                w=x
                
                while(True):
                    #Step 5
                    z=None
                    #5.1
                    if(workGraph.getLabel_Positive(u)!=None and workGraph.getLabel_Negative(u)==None):
                        z=workGraph.getLabel_Positive(u)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(True)
                        u_z.setDir([z,u])
                        if(z!=y):
                            workGraph.setIN(z,True)
                    #5.2
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)==None):
                        z=workGraph.getLabel_Negative(u)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(False)
                        if(workGraph.getLabel_Negatif(z)!=None and workGraph.getLabel_Positive(z)==None):
                            workGraph.setIN(z,False)
                    #5.3
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Negative(w) and z==workGraph.getLabel_Positive(u)):
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(True)
                        u_z.setDir([z,u])
                        if(z!=y):
                            workGraph.setIN(z,True)
                    #5.4
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Positive(w) and z==workGraph.getLabel_Negative(u)):
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(False)
                    #Step 6
                    if(z!=y):
                        w=u
                        u=z
                    else:
                        queue=[]
                        workGraph.eraseLabels()
                        break
            if((len(queue)<=0 and workGraph.getState(x)==unlabelled)):
                break
        #Step 7
        ensembleSeparant=[]
        y=workGraph.getNode(id_puit)
        for edge in workGraph.getEdges():
            if(y in edge.getNodes() and edge.getMarked()):
                if(y==edge.getNodes()[0]):
                    u=edge.getNodes()[1]
                else:
                    u=edge.getNodes()[0]
                if(workGraph.getLabel_Positive(u)==None and workGraph.getLabel_Negative(u)==None):
                    ensembleSeparant.append(u)
                if(workGraph.getLabel_Positive(u)!=None or workGraph.getLabel_Negative(u)!=None):
                    pass









        

    
    def fromIDToMoralizedAncestral(self,decisionNodeID):
        """
        Fonction qui transforme l'ID en graphe moralisé ancestral pour appliquer Acid&Campos

        ID le diagramme d'influence étudié
        decisionNodeID est l'identifiant du noeud de décision pour lequel on veut trouver le SIS
        ordre est l'ordre de la prise de décision dans l'ID (identifiants des noeuds de décision)

        renvoi le graphe moralisé ancestral (version undigraph) et les identifiants des noeuds sources et puits
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
        return MoralizedAncestral,alphaXid,BetaYid     

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

class GraphForSIS:
    def __init__(self,nodeList,edgeList):
        self.nodeList=nodeList
        self.edgeList=edgeList
    def fsearch(self,u):
        for edge in self.edgeList:
            if(u in edge.getNodes()):
                v=np.abs(edge.getNodes().index(u)-1)
                if(self.getLabel_Positive(u)==None and self.getLabel_Negative(u)==None and not self.getEdge(u,v).getMarked()):
                    self.setLabel_p(v,u)
    def bsearch(self,u,y,queue):
        for edge in self.edgeList:
            if(u in edge.getNodes()):
                t=np.abs(edge.getNodes().index(u)-1)
                if(self.getEdge(u,t).getMarked() and self.getEdge(u,t).getDir()==[t,u]):
                    if(self.getLabel_Negative(t)==None):
                        self.setLabel_Negative(y)=u
                    if(self.getState(t)=="labelledScanned"):
                        self.setState(t,"labelledUnscanned")
                        queue.append(t)
    def eraseLabels(self):
        for node in self.nodeList:
            node.setLabel_Positive(None)
            node.getLabel_Negative(None)
    def getLabel_Positive(self,id):
        return self.getNode(id).getLabel_Positive()
    def getLabel_Negative(self,id):
        return self.getNode(id).getLabel_Negative()
    def setLabel_Positive(self,id,label):
        self.getNode(id).setLabel_Positive(label)
    def setLabel_Positive(self,id,label):
        self.getNode(id).setLabel_Negative(label)
    def getState(self,id):
        return self.getNode(id).getState()
    def setState(self,id,state):
        self.getNode(id).setState(state)
    def getIN(self,id):
        return self.getNode(id).getIN()
    def setIN(self,id,IN):
        self.getNode(id).setIN(IN)
    def getNodes(self):
        return self.nodeList
    def getNode(self,id):
        for node in self.nodeList:
            if(node.getID()==id):
                return node
    def getEdge(self,idNode1,idNode2):
        node1=self.getNode(idNode1)
        node2=self.getNode(idNode2)
        for edge in self.getEdges():
            if edge.getNodes==[node1,node2] or edge.getNodes==[node2,node1]:
                return edge
    def getEdges(self):
        return self.edgeList
    def addNode(self,node):
        self.nodeList.append(node)
    def addNode(self,id,state,label_positive,label_negative):
        self.nodeList.append(NodeForSIS(id,state,label_positive,label_negative))
    def addEdge(self,idNode1,idNode2,capacity):
        if(idNode1!=idNode2 and idNode1 in self.nodeList and idNode2 in self.nodeList and capacity>=1):
            self.edgeList.append(EdgeForSIS(idNode1,idNode2,capacity))
class NodeForSIS:
    def __init__(self,id,state,label_positive,label_negative,IN):
        self.id=id
        if(state in ["labelledScanned","labelledUnscanned","unlabelled"]):
            self.state=state
        else:
            state=None
        self.label_positive=label_positive
        self.label_negative=label_negative
        self.IN=IN
    def getIn(self):
        return self.IN
    def getID(self):
        return self.id
    def getState(self):
        return self.state
    def getLabel_Positive(self):
        return self.label_positive
    def getLabel_Negative(self):
        return self.label_negative
    def setIn(self,IN):
        self.IN=IN
    def setState(self,state):
        if(state in ["labelledScanned","labelledUnscanned","unlabelled"]):
            self.state=state
        else:
            state=None
    def setLabel_Positive(self,label_positive):
        self.label_positive=label_positive
    def setLabel_Negative(self,label_negative):
        self.label_negative=label_negative
    def copy(self,toCopy):
        self.id=toCopy.getID()
        self.state=toCopy.getState()
        self.label_positive=toCopy.getLabel_Positive()
        self.label_negative=toCopy.getLabel_Negative()
        self.IN=toCopy.getIN()
class EdgeForSIS:
    def __init__(self,idNode1,idNode2,capacity,marked,dir):
        self.idNode1=idNode1
        self.idNode2=idNode2
        self.capacity=capacity
        self.marked=marked
        self.dir=dir
    def getNodes(self):
        return [self.idNode1,self.idNode2]
    def getCapacity(self):
        return self.capacity
    def setNodes(self,idNode1,idNode2):
        self.idNode1=idNode1
        self.idNode2=idNode2
    def setCapacity(self,capacity):
        self.capacity=capacity
    def setMarked(self,mark):
        self.marked=mark
    def getMarked(self):
        return self.marked
    def setDir(self,dir):
        self.dir=dir
    def getDir(self):
        return self.dir