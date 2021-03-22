import numpy as np
import os
from pylab import *
import matplotlib.pyplot as plt
from IPython.core.display import Math, display,HTML
import math
import pyAgrum as gum
import warnings

class BranchAndBoundLIMIDInference():

    def __init__(self,ID,OrdreDecision):
        self.ID=ID
        self.ordreDecision=OrdreDecision

    
    def createRelaxation(self):
        relaxedID=gum.InfluenceDiagram(self.ID)
        #Calculs des SIS des noeuds de décision et en faire des noeuds d'information aux noeuds de décision associés
        for i in range(len(self.ordreDecision)-1,-1,-1):
            sis=self.SIS(self.ordreDecision[i],relaxedID)
            for nodeID in sis:
                if(not relaxedID.existsArc(nodeID,self.ordreDecision[i]) and nodeID in relaxedID.nodes()):
                    relaxedID.addArc(nodeID,self.ordreDecision[i])
        #Enlever les noeuds non-requis
        #?
        relaxedID=gum.ShaferShenoyLIMIDInference(relaxedID).reducedLIMID()
        #relaxedID=relaxedID.reducedLIMID()
        for node in relaxedID.nodes():
            if(relaxedID.isChanceNode(node)):
                relaxedID.cpt(node).fillWith(gum.Potential(self.ID.cpt(node)))
        return relaxedID
        


            

    #ID->DAG (sans neouds utilités)->graphe moralisé ancestral ou on doit trouver l'ensemble de noeuds
    #séparant X et Y
    def SIS(self,decisionNodeID,ID):
        labelledScanned="labelledScanned"
        labelledUnscanned="labelledUnscanned"
        unlabelled="unlabelled"
        #--Construction du graphe moralisé sur lequel appliquer l'algorithme--
        moralizedAncestral,id_source,id_puit=self.fromIDToMoralizedAncestral(decisionNodeID,ID)

        #--Construction du graphe de travail sur lequel on peut appliquer l'algorithme--
        nodeList=[]
        edgeList=[]
        workGraph=GraphForSIS(nodeList,edgeList)
        for id in moralizedAncestral.nodes():
            #All nodes unlabelled and IN property set to false
            workGraph.addNode(id,unlabelled,None,None,False)
        for edge in moralizedAncestral.edges():
            workGraph.addEdge(edge[0],edge[1],1,False,None)
        
        #---Algorithme----
        
        queue=[]
        y=id_puit
        x=id_source
        while(True):
            #Step 1
            #print(1)
            doesProceedStep4=None
            doesProceedStep7=None
            workGraph.setLabel_Positive(y,y)
            queue.append(y)
            workGraph.setState(y,labelledUnscanned)
            
        
            #Step 2 
            while(True):
                #print("2")
                #print("2 queue:",queue)
                
                for node in queue:
                    if workGraph.getNode(node).getState()==labelledUnscanned:
                        u=node
                        queue.remove(u)
                        break
                #1
                if(workGraph.getIN(u)==False):
                    #print(2.1)
                    workGraph.fsearch(u,queue) # on a rajouté queue dans fsearch
                    """for node in workGraph.getNodes():
                        if node.getLabel_Positive()!=None:
                            #print(node.toString())
                    #print("\n")
                    for node in workGraph.getNodes():
                        if node.getState()!=unlabelled:
                            #print(node.toString())
                    #print("\n")
                    for edge in workGraph.getEdges():
                        if(edge.getMarked()==True):
                            #print(edge.toString())"""
                    #print("2.1 queue:",queue)
                    ##print(workGraph.toString())
                #2
                if(workGraph.getIN(u)==True and workGraph.getLabel_Negative(u)==None and workGraph.getLabel_Positive(u)!=None):
                    workGraph.bsearch(u,y,queue)
                    #print(2.2)
                #3
                if(workGraph.getIN(u)==True and workGraph.getLabel_Negative(u)!=None):
                    workGraph.fsearch(u,queue)
                    workGraph.bsearch(u,y,queue)
                    #print(2.3)
                #4
                #print(2.4)
                workGraph.setState(u,labelledScanned)
                doesProceedStep4=workGraph.getState(x)==labelledScanned or workGraph.getState(x)==labelledUnscanned
                doesProceedStep7=(len(queue)<=0 and workGraph.getState(x)==unlabelled)
                if ( doesProceedStep7 or doesProceedStep4):
                    #print(3)
                    
                    break
            if(doesProceedStep4):
                #print(4)
                #Step 4
                u=x
                w=x
                
                while(True):
                    #print(5)
                    #Step 5
                    z=None
                    #5.1
                    #print("5.1 u:",u)
                    if(workGraph.getLabel_Positive(u)!=None and workGraph.getLabel_Negative(u)==None):
                        #print(5.1)
                        z=workGraph.getLabel_Positive(u)
                        #print("5.1 z: ",z)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(True)
                        u_z.setDir([z,u])
                        if(z!=y):
                            workGraph.setIN(z,True)
                            #print("5.1.1")
                    #5.2
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)==None):
                        #print(5.2)
                        z=workGraph.getLabel_Negative(u)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(False)
                        if(workGraph.getLabel_Negatif(z)!=None and workGraph.getLabel_Positive(z)==None):
                            workGraph.setIN(z,False)
                    #5.3
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Negative(w) and z==workGraph.getLabel_Positive(u)):
                        #print(5.3)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(True)
                        u_z.setDir([z,u])
                        if(z!=y):
                            workGraph.setIN(z,True)
                    #5.4
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Positive(w) and z==workGraph.getLabel_Negative(u)):
                        #print(5.4)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(False)
                    #Step 6
                    #print(6)
                    if(z!=y):
                        #print(6.1)
                        w=u
                        u=z
                    else:
                        #print(6.2)
                        queue=[]
                        workGraph.eraseLabels()
                        break
            elif(doesProceedStep7):
                #print(7)
                break
        #Step 7
        #print(7,"vrai")
        ensembleSeparant=[]
        y=id_puit
        for edge in workGraph.getEdgesConnectedToNode(y):
            if(edge.getMarked()):
                if(edge.getNodes()[1]!=y):
                    u=edge.getNodes()[1]
                else:
                    u=edge.getNodes()[0]
                if(workGraph.getLabel_Positive(u)==None and workGraph.getLabel_Negative(u)==None):
                    print(7.2," u=",u)
                    ensembleSeparant.append(u)
                if(workGraph.getLabel_Positive(u)!=None or workGraph.getLabel_Negative(u)!=None):
                    #print(7.3)
                    res=workGraph.step7(u,y)
                    ensembleSeparant.append(res)
                    print(7.3," u=",res)

        return ensembleSeparant

    










        

    
    def fromIDToMoralizedAncestral(self,decisionNodeID,ID):
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
        for nodeID in ID.nodes():
            if(ID.isDecisionNode(nodeID)):
                if(self.ordreDecision.index(nodeID)<=self.ordreDecision.index(decisionNodeID)): #si il precède dj dans l'ordre
                    X=X+list(ID.family(nodeID)).copy()
        #--Construction de Y--
        Y=list(ID.descendants(decisionNodeID)).copy()
        for nodeID in Y:
            if(not ID.isUtilityNode(nodeID)):
                Y.remove(nodeID)
        XUY=X+Y
        XUYNames=self.getNamesFromID(XUY,ID)
        #--Construction du graphe ancestral moralisé--
        MoralizedAncestral=ID.moralizedAncestralGraph(XUYNames)#un undigraph avec des noeuds de mêmes identifiants que ceux du diagramme d'influences
        #--Ajout des noeuds sources(alpha) et puit (beta) et de leurs aretes
        alphaXid=MoralizedAncestral.addNode()
        BetaYid=MoralizedAncestral.addNode()
        temp=[]#liste des ancestre de tous de y de Y
        for y in Y: #Y liste des descendant de DJ qui sont des noeuds d'utilité
            temp=temp+list(ID.ancestors(y))
        desc=ID.descendants(decisionNodeID)
        for nodeID in temp:
            if(nodeID not in desc):
                temp.remove(nodeID)
        for nodeID in MoralizedAncestral.nodes():
            for node2ID in MoralizedAncestral.nodes():
                if((nodeID,node2ID) in MoralizedAncestral.edges() or (node2ID,nodeID) in MoralizedAncestral.edges()):
                    if(node2ID in X and nodeID not in X):
                        MoralizedAncestral.addEdge(alphaXid,nodeID)
                        break
                    elif(nodeID in temp):
                        MoralizedAncestral.addEdge(BetaYid,nodeID)
                        break
        return MoralizedAncestral,alphaXid,BetaYid     

        
    #--Méthodes utilitaires--
    def getNamesFromID(self,listId,ID):
        """
        retourne les noms des noeuds donnés sous forme d'identifiant (listId) dans le diagramme d'influence InDi
        """
        names=[]
        for name in ID.names():
            if(ID.idFromName(name) in listId):
                names.append(name)
        return names
    def fromIDtoDAG(self,ID):
        """
        Rend un DAG pour un ID donné (ses noeuds ont les mêmes identifiants que ceux de l'ID)
        Le DAG rendu a un noeud correspondant à chaque noeud chance/decision mais pas pour les noeuds utilité. Il a aussi les mêmes arcs que l'ID (sans ceux vers les noeuds d'utilité bien sur car ils ne sont pas dans le DAG)
        """
        dag=gum.DAG()
        for nodeID in ID.nodes():
            if(not ID.isUtilityNode(nodeID)):
                dag.addNodeWithId(nodeID)
        for arc in ID.arcs():
            source=arc[0]
            destination=arc[1]
            if(not ID.isUtilityNode(source) and not self.ID.isUtilityNode(destination)):
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
    #TODO :TESTER CETTE FONCTION
    def step7(self,u,y):
        listVisite=[u]
        oldu=y
        while(True):
            for edge in self.getEdgesConnectedToNode(u):
                if(u==edge.getNodes()[0]):
                    v=edge.getNodes()[1]
                else:
                    v=edge.getNodes()[0]

                if(self.getEdge(u,v).getMarked() and v!=oldu):
                    if(self.getLabel_Positive(v)!=None or self.getLabel_Negative(v)!=None):
                        oldu=u
                        u=v
                        break
                
            return u
                        
            
            
            if(v in listVisite):
                #print("in warning")
                warnings.warn("Attention, ici, truc bizarre")
                return None
    def step7V2(self,u):
        listVisite=[u]
        while(True):
            hasVisitedNew=False
            for edge in self.edgeList:
                if (u in edge.getNodes()):
                    if(u==edge.getNodes()[0]):
                        v=edge.getNodes()[1]
                    else:
                        v=edge.getNodes()[0]
                    if(self.getEdge(u,v).getMarked() and v not in listVisite and (self.getLabel_Positive(v)!=None or self.getLabel_Negative(v)!=None)):
                        hasVisitedNew=True
                        listVisite.append(v)
                        u=v
                        break
                    if(not hasVisitedNew):
                        for i in range(len(listVisite)-1,-1,-1):
                            if(self.getLabel_Positive(listVisite[i])!=None or self.getLabel_Negative(listVisite[i])!=None):
                                return listVisite[i]
    def step7V3(self,u):
        pass
        
    def voisin(self,nodeID):
        voisin=[]
        for edge in self.edgeList:
            if (nodeID in edge.getNodes()):
                if(nodeID==edge.getNodes()[0]):
                    voisin.append(edge.getNodes()[1])
                else:
                    voisin.append(edge.getNodes()[0])
        return voisin
                
    def fsearch(self,u,queue):
        ##print("fsearch : u: ",u)
        for edge in self.edgeList:
            if(u in edge.getNodes()):
                
                if(u==edge.getNodes()[0]):
                    v=edge.getNodes()[1]
                else:
                    v=edge.getNodes()[0]
                ##print("fSearch in 1, this v:",v)
                if(self.getState(v)=="unlabelled" and not self.getEdge(u,v).getMarked()):
                    ##print("fSearch in 2")
                    self.setLabel_Positive(v,u)
                    self.setState(v,"labelledUnscanned")
                    queue.append(v)
    def bsearch(self,u,y,queue):
        #print("bSearch")
        for edge in self.edgeList:
            if(u in edge.getNodes()):
                if(u==edge.getNodes()[0]):
                    t=edge.getNodes()[1]
                else:
                    t=edge.getNodes()[0]
                if(self.getEdge(u,t).getMarked() and self.getEdge(u,t).getDir()==[t,u]):
                    if(self.getLabel_Negative(t)==None):
                        self.setLabel_Negative(y,u)
                        if(self.getState(t)=="labelledScanned"):
                            self.setState(t,"labelledUnscanned")
                            queue.append(t)
                        self.setState(y,"labelledUnscanned")
                    break
    def eraseLabels(self):
        for node in self.nodeList:
            node.setLabel_Positive(None)
            node.setLabel_Negative(None)
            node.setState("unlabelled")
    def getLabel_Positive(self,id):
        return self.getNode(id).getLabel_Positive()
    def getLabel_Negative(self,id):
        return self.getNode(id).getLabel_Negative()
    def setLabel_Positive(self,id,label):
        self.getNode(id).setLabel_Positive(label)
    def setLabel_Negative(self,id,label):
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
        for edge in self.getEdges():
            if edge.getNodes()==[idNode1,idNode2] or edge.getNodes()==[idNode2,idNode1]:
                return edge
    def getEdges(self):
        return self.edgeList
    def getEdgesConnectedToNode(self,nodeID):
        listEdges=[]
        for edge in self.getEdges():
            if(nodeID in edge.getNodes()):
                listEdges.append(edge)
        return listEdges
    def addNode(self,node):
        self.nodeList.append(node)
    def addNode(self,id,state,label_positive,label_negative,IN):
        self.nodeList.append(NodeForSIS(id,state,label_positive,label_negative,IN))
    def addEdge(self,idNode1,idNode2,capacity,marked,dir):
        nodeListID=[]
        for node in self.nodeList:
            nodeListID.append(node.getID())
        if(idNode1!=idNode2 and idNode1 in nodeListID and idNode2 in nodeListID and capacity>=1):
            self.edgeList.append(EdgeForSIS(idNode1,idNode2,capacity,marked,dir))
    def toString(self):
        return [self.nodeList[i].toString() for i in range(len(self.nodeList))]+[self.edgeList[i].toString() for i in range(len(self.edgeList))]

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
    def toString(self):
        return [self.id,self.state,self.label_positive,self.label_negative,self.IN]
    def getIN(self):
        return self.IN
    def getID(self):
        return self.id
    def getState(self):
        return self.state
    def getLabel_Positive(self):
        return self.label_positive
    def getLabel_Negative(self):
        return self.label_negative
    def setIN(self,IN):
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
    def toString(self):
        return [self.idNode1,
        self.idNode2,
        self.capacity,
        self.marked,
        self.dir]
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