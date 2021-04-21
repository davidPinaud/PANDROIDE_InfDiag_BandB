from andOrGraph import decisionNode,chanceNode,andOrGraph
import numpy as np
import os
from pyAgrum.pyAgrum import IDGenerator
from pylab import *
import matplotlib.pyplot as plt
from IPython.core.display import Math, display,HTML
import math
import pyAgrum as gum
import warnings
from minindepset import MinimalDSep
from functools import lru_cache


class BranchAndBoundLIMIDInference():

    def __init__(self,ID,OrdreDecision):
        self.ID=ID
        self.SIS=dict()
        self.ordreDecision=OrdreDecision
        self.IDRelaxe=self.createRelaxation()
        self.andOrGraph=andOrGraph(self.ID,None)
        self.root=None

    
    #ids of parents of current decisionNode,chanceNode(parents[0],domain)
    def createCoucheChance(self,parents,root):
        """
        à partir d'une racine root, créer la couche de tous les descendants qui sont des noeuds chance dans l'arbre ET/OU
        Ces descendants sont les noeuds chances parents des noeuds de décision dans l'ID
        """
        if(len(parents)==0):
            return
        domain=self.getDomain(parents[0])
        self.andOrGraph.addNoeudChance(root)
        
        for d in domain:
            domainbis=self.getDomain(parents[0])
            node=chanceNode(parents[1],domainbis,root,d)
            root.addChild(d,node)
            self.createCoucheChance(self,parents[1:],node)
    #root,self.ordreDecision[i],[],dict()
    def createCoucheDecision(self,root,decisionNodeID,contexte,pile,couche):
        childs=root.getChilds()
        isFeuille=True if len(childs)==0 else False
        if(not isFeuille):
            for supportValue,child in childs.items():
                contexteTemp=dict(contexte)
                contexteTemp[child.getNodeID()]=supportValue
                self.createCoucheDecision(child,decisionNodeID,contexteTemp,pile)
        else:
            domain=self.getDomain(root.getNodeID())
            for d in domain:
                contexteTemp=dict(contexte)
                contexteTemp[root.getNodeID()]=d
                node=decisionNode(decisionNodeID,contexteTemp,root,self.getDomain(decisionNodeID),self.andOrGraph.getIDNoeudDecisionAndOr())
                couche.append(node)
                root.addChild(d,node)
                if(not self.ordreDecision.index(node.getNodeID())==len(self.ordreDecision)-1):#is node is a leaf
                    pile.append(node.getId_andOr())
                self.andOrGraph.addNoeudDecision(node)
        return couche

    #écrire l'algo pour l'induction arrière quand on se retrouve dans une couche feuille
    #écrire l'algo pour l'élagage

    #induction arriere : (on n'a pas a calculer la décision optimale car c'est fait dans addCouche)
    #Entrée <- couche courante
    #calculer les valeur des noeuds chances jusqu'a ce qu'on arrive à un noeud de décision
    #pour ce noeud de décision, regarder toutes ses bornes supérieures et élaguer si besoin les domaines dont on n'a pas besoin
    #continuer après le noeud de décision seulement si toute la couche après le noeud est évaluée (pas borne sup) tant qu'on arrive pas au self.root (racine de l'arbre)
    def inductionArriere(self,couche):
        #construire des doublets de noeuds de décision
        pass
    def induction(self,couche):
        for node in couche:
            for node2 in couche:
                if node.getParent()==node2.getParent():
                    parent=node.getParent()
                    if type(parent)==chanceNode:
                        parent.getInference().posterior(node.getNodeID())
                        parent.setValeur()#prendre probabilités posterieures
                    break
    def branchAndBound(self):
        index=0
        decisionNodeID=self.ordreDecision[index]#Prendre le premier noeud de décision dans l'ordre de décision défini
        #--on récupère les parents qui sont des noeuds chances dans l'ID du noeud de décision courant--
        parents_chanceID=self.getParents_chanceID(decisionNodeID)
        self.root=chanceNode(parents_chanceID[0],self.getDomain(parents_chanceID[0]),None,None)#racine de l'arbre ET/OU
        self.addCouche(index,self.root,dict(),parents_chanceID)
        index+=1
        pile=self.andOrGraph.IDNoeudDecisionAndOr().copy()
        while(not len(pile)==0):
            #Tant que la pile n'est pas vide :
                #prendre un noeud de décision dans la pile et l'enlever de la pile
                #pour tout element e du domaine du noeud de décision (sans ceux dans le doNotDevelop)
                    #appeler addCouche pour creer la nouvelle couche    
                        #si la couche est une couche feuille
                            #appeler induction arriere
                #sinon continuer
            nodeADev=self.andOrGraph.getNoeudDecisionAndOr(pile.pop())
            nodeADevID=nodeADev.getNodeID()
            domain=self.getDomain(nodeADevID)
            for dom in domain:
                if(dom not in nodeADev.getDoNotDevelop()):
                    parents_chanceID=self.getParents_chanceID(nodeADevID)
                    root=chanceNode(parents_chanceID[0],self.getDomain(parents_chanceID[0]),nodeADev,dom)
                    couche=self.addCouche(index,root,nodeADev.getContexte(),parents_chanceID,pile)
                    index+=1
                    if (index==len(self.ordreDecision)):#si on est sur une couche feuille
                        self.inductionArriere(couche)
                        #appeller induction arriere
            
    #dans la méthode du branch and bound
    #il faut creer root et le mettre comme fils du noeuds de décision correspondant
    def getParents_chanceID(self,decisionNodeID):
        temp=list(self.ID.parents(decisionNodeID))
        parents_chanceID=[]
        for t in temp:
            if self.ID.isChanceNode(temp):
                parents_chanceID.append(t)
        return parents_chanceID
    def addCouche(self,index,root,contexte_parentRoot,parents_chanceID,pile):
        #####Init#####
        decisionNodeID=self.ordreDecision[index]#Prendre le noeud de décision dans l'ordre de décision défini
        #--on récupère les parents qui sont des noeuds chances dans l'ID du noeud de décision courant--
        self.createCoucheChance(parents_chanceID[1:],root)#Creer toutes les alternatives d'instanciation des parents_chances possibles
        couche=self.createCoucheDecision(root,decisionNodeID,dict(),pile,[])
        coucheID=[c.getNodeID() for c in couche]
        #####END INIT#####
        ### Evaluation de la borneSup/borneInf######
        if(self.ordreDecision.index(decisionNodeID)<len(self.ordreDecision)-1):#si le noeud de décision n'est pas une feuille
            noeudsDecisions=self.andOrGraph.getNoeudDecision()
            for d in noeudsDecisions:
                if(d.getNodeID() in coucheID):#si elle est sur la couche courante
                    contextetemp={**d.getContexte(),**contexte_parentRoot}
                    d.setContexte(contextetemp)
                    domain=self.getDomain(d)
                    for dom in domain:
                        contextetemp=dict(d.getContexte())
                        contextetemp[decisionNodeID]=dom
                        ss=self.evaluate(self.IDRelaxe,d.getContexte(),contextetemp)
                        d.addBorneSup(key=dom,borneSup=(ss.MEU()["mean"],ss.MEU()["variance"]))
                        d.setInference(ss)
        else:#si le noeud de décision est une feuille
            noeudsDecisions=self.andOrGraph.getNoeudDecision()
            for d in noeudsDecisions:
                if(d.getNodeID() in coucheID):#si elle est sur la couche courante
                    contextetemp={**d.getContexte(),**contexte_parentRoot}
                    d.setContexte(contextetemp)
                    domain=self.getDomain(d)
                    for dom in domain:
                        contextetemp=dict(d.getContexte())
                        contextetemp[decisionNodeID]=dom
                        ss=self.evaluate(self.ID,d.getContexte(),contextetemp)
                        d.addEvaluation(key=dom,evaluation=(ss.MEU()["mean"],ss.MEU()["variance"]))
                        d.setInference(ss)
                #on peut directement choisir la décision optimale car c'est une feuille
                decisionOpt,valeurDecisionOptimale=self.getDecisionOpt(d)
                d.setDecisionOptimale(decisionOpt)
                d.setValeurDecisionOptimale(valeurDecisionOptimale)
        return couche

    def getDecisionOpt(self,decisionNode):
        eval=decisionNode.getEvaluation()
        decisionOpt=None
        valeurDecisionOptimale=None
        for decision,valeurDecision in eval.items():
            if(valeurDecisionOptimale==None or valeurDecision["mean"]>valeurDecisionOptimale["mean"]):
                valeurDecisionOptimale=valeurDecision
                decisionOpt=decision
        return decisionOpt,valeurDecisionOptimale
    

    def getDomain(self,NodeID):
        return self.ID.variable(NodeID).domain()[1:-1].split(',')

    
    #evaluationID(IDRelaxé,contexte.items())        
    def evaluationID(self,ID,evidence):
        ##print(evidence)
        ss=gum.ShaferShenoyLIMIDInference(ID)#---------- a changer a ID tout court
        ss.setEvidence(evidence)
        """
            items=list(evidence.items())
            for parentID,value in items:
            ss.addEvidence(parentID,value)"""
        ss.makeInference()
        ##print(ss.MEU())
        return ss

    def createCouche(self,parents,alternative):
        alternatives=[]
        if(len(parents)==0):
            return [alternative]
        domain=self.getDomain(parents[0])
        for d in domain:
            v=self.createCouche(parents[1:],[d]+alternative)
            for e in v:
                alternatives.append(e)
        return alternatives

    def createRelaxation_Temporaire(self):
        #copy l'ID dans relaxedID pour ensuite lui ajouter des arcs
        relaxedID=gum.InfluenceDiagram(self.ID)
        #Calculs des SIS des noeuds de décision et en faire des noeuds d'information aux noeuds de décision associés
        for i in range(len(self.ordreDecision)-1,-1,-1):
            x=f"x_{i}"
            y=f"y_{i}"
            sis=[self.ID.idFromName(x),self.ID.idFromName(y)]
            for nodeID in sis:
                if(not relaxedID.existsArc(nodeID,self.ordreDecision[i])):
                    relaxedID.addArc(nodeID,self.ordreDecision[i])
        #Enlever les noeuds non-requis
        #?
        relaxedID=gum.ShaferShenoyLIMIDInference(relaxedID).reducedLIMID()
        #relaxedID=relaxedID.reducedLIMID()
        for node in relaxedID.nodes():
            if(relaxedID.isChanceNode(node)):
                relaxedID.cpt(node).fillWith(gum.Potential(self.ID.cpt(node)))
            if(relaxedID.isUtilityNode(node)):
                relaxedID.utility(node).fillWith(gum.Potential(self.ID.utility(node)))
        return relaxedID


    def createRelaxation(self):
        relaxedID=gum.InfluenceDiagram(self.ID)
        #Calculs des SIS des noeuds de décision et en faire des noeuds d'information aux noeuds de décision associés
        for i in range(len(self.ordreDecision)-1,-1,-1):
            sis=list(self.SIS_ID(self.ordreDecision[i],relaxedID))
            #print("SIS de :",relaxedID.variable(self.ordreDecision[i]).name()," | ",self.getNamesFromID(list(sis),relaxedID))
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
            if(relaxedID.isUtilityNode(node)):
                relaxedID.utility(node).fillWith(gum.Potential(self.ID.utility(node)))
        return relaxedID
        

    #ID->DAG (sans neouds utilités)->graphe moralisé ancestral ou on doit trouver l'ensemble de noeuds
    #séparant X et Y
    def SIS_ID(self,decisionNodeID,ID):
        #--Construction du graphe moralisé sur lequel appliquer l'algorithme--
        graph,x,y=self.fromIDToMoralizedAncestral(decisionNodeID,ID)
        SIS=MinimalDSep(graph).find(y,x)
        self.SIS[decisionNodeID]=SIS
        return SIS


    #ID->DAG(\noeuds utilités ?)->MoralizedAncestral H-> DAG H~ +source+puit
    def fromIDToMoralizedAncestral(self,decisionNodeID,ID):
        #--Construction de X={D1,..,Dj} où Dj est le noeud de décision pour lequel on veut le SIS
        X=[]
        for nodeID in ID.nodes():
            if(ID.isDecisionNode(nodeID)):
                if(self.ordreDecision.index(nodeID)<=self.ordreDecision.index(decisionNodeID)): #prendre tous les noeuds de décision si il precède dj ou égal dans l'ordre
                    X=self.unionList(X,list(ID.family(nodeID)))
        #--Construction de Y={U inter de(Dj)} Descendants de Dj qui sont des noeuds d'utilités
        Y=list(ID.descendants(decisionNodeID)).copy()
        ytemp=Y.copy()
        for nodeID in ytemp:
            if(not ID.isUtilityNode(nodeID)):
                Y.remove(nodeID)
        XUY=self.unionList(X,Y)
        #--Construction de An(XUY)=XUY Union (Union des an(XUY_i)) Union de lui même et de l'union des ancêtres de ses élements
        ancestralSubset=XUY.copy()
        for x in XUY:
            ancestralSubset=self.unionList(ancestralSubset,list(ID.ancestors(x)))
        #--Construction du sous graphe
        ID_dag=ID.dag()
        for nodeID in ID.nodes():
            if nodeID not in ancestralSubset:
                ID_dag.eraseNode(nodeID)
        #--Moralisation du sous graphe
        MoralizedAncestral=ID_dag.moralGraph()
        #--Ajout de la source et du puit
        alphaXid=MoralizedAncestral.addNode()
        BetaYid=MoralizedAncestral.addNode()
        #--Ajouter des arêtes entre la source et les voisins de fa(X)
        descendantOfDecisionNode=list(ID.descendants(decisionNodeID))
        for (nodeID,node2ID) in MoralizedAncestral.edges():#Connection source
            if(nodeID in X and node2ID in X):
                continue
            if(nodeID in X or node2ID in X):
                if(node2ID in X):
                    if(nodeID not in X and not MoralizedAncestral.existsEdge(alphaXid,nodeID) and nodeID not in descendantOfDecisionNode):
                        MoralizedAncestral.addEdge(alphaXid,nodeID)
                if(nodeID in X):
                    if(node2ID not in X and not MoralizedAncestral.existsEdge(alphaXid,node2ID) and node2ID not in descendantOfDecisionNode):
                        MoralizedAncestral.addEdge(alphaXid,node2ID)
        #--Ajouter des arêtes entre le puit et de(Dj) Inter an(U inter de(Dj)) (les descendants de Dj qui sont les ancetre des noeuds d'utilités descendant Dj)
        temp=[] #an(U inter de(Dj))
        for y in Y:
            temp=self.unionList(temp,list(ID.ancestors(y)))
        desc=ID.descendants(decisionNodeID)#de(Dj)
        t=temp.copy()
        for nodeID in t:
            if(nodeID not in desc):
                temp.remove(nodeID)#de(Dj) Inter an(U inter de(Dj))
        for nodeID in temp: #Connection puit
            if( not MoralizedAncestral.existsEdge(BetaYid,nodeID)):
                MoralizedAncestral.addEdge(nodeID,BetaYid)
        
        return MoralizedAncestral,alphaXid,BetaYid 
        


    #--Méthodes utilitaires--
    def getNameFromID(self,idNode):
        for name in self.ID.names():
            if(self.ID.idFromName(name)==idNode):
                return name

    def unionList(self,list1,list2):
        union=list1.copy()
        for e in list2:
            if e not in union:
                union.append(e)
        return union
    def getNamesFromID(self,listId,ID):
        """
        retourne les noms des noeuds donnés sous forme d'identifiant (listId) dans le diagramme d'influence InDi
        """
        names=[]
        for name in ID.names():
            if(ID.idFromName(name) in listId):
                names.append(name)
        return names
