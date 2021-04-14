import numpy as np
import os
from pyAgrum.pyAgrum import IDGenerator
from pylab import *
import matplotlib.pyplot as plt
from IPython.core.display import Math, display,HTML
import math
import pyAgrum as gum
import warnings
import andOrGraph
from functools import lru_cache


class BranchAndBoundLIMIDInference():

    def __init__(self,ID,OrdreDecision):
        self.ID=ID
        self.ordreDecision=OrdreDecision
        #self.IDRelaxe=self.createRelaxation_Temporaire()
        #self.andOrGraph=andOrGraph(self.ID,None)
        #self.root=None

    
    #ids of parents of current decisionNode,andOrGraph.chanceNode(parents[0],domain)
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
            node=andOrGraph.chanceNode(parents[1],domainbis,root,d)
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
                node=andOrGraph.decisionNode(decisionNodeID,contexteTemp,root,self.getDomain(decisionNodeID),self.andOrGraph.getIDNoeudDecisionAndOr())
                couche.append(node)
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
                    if type(parent)==andOrGraph.chanceNode:
                        parent.getInference().posterior(node.getNodeID())
                        parent.setValeur()#prendre probabilités posterieures
                    break
    def branchAndBound(self):
        index=0
        decisionNodeID=self.ordreDecision[index]#Prendre le premier noeud de décision dans l'ordre de décision défini
        #--on récupère les parents qui sont des noeuds chances dans l'ID du noeud de décision courant--
        parents_chanceID=self.getParents_chanceID(decisionNodeID)
        self.root=andOrGraph.chanceNode(parents_chanceID[0],self.getDomain(parents_chanceID[0]),None,None)#racine de l'arbre ET/OU
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
                    root=andOrGraph.chanceNode(parents_chanceID[0],self.getDomain(parents_chanceID[0]),nodeADev,dom)
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
        decisionNodeID=self.ordreDecision[index]#Prendre le premier noeud de décision dans l'ordre de décision défini
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
            #TODO: finir l'algorithme
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
            if(relaxedID.isUtilityNode(node)):
                relaxedID.utility(node).fillWith(gum.Potential(self.ID.utility(node)))
        return relaxedID
        


##################################################################################################################################################################################################################
##################################################################################################################################################################################################################
##################################################################################################################################################################################################################
##################################################################################################################################################################################################################
    #ID->DAG (sans neouds utilités)->graphe moralisé ancestral ou on doit trouver l'ensemble de noeuds
    #séparant X et Y
    def SIS_ID(self,decisionNodeID,ID):
        #--Construction du graphe moralisé sur lequel appliquer l'algorithme--
        return self.SIS(*self.fromIDToMoralizedAncestral2(decisionNodeID,ID))

    def SIS(self,moralizedAncestral,id_source,id_puit):
        labelledScanned="labelledScanned"
        labelledUnscanned="labelledUnscanned"
        unlabelled="unlabelled"

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

        y=id_puit
        x=id_source
        ##print("x",x,"y",y)
        while(True):
            #Step 1
            ##print(1)
            doesProceedStep4=None
            doesProceedStep7=None
            workGraph.setLabel_Positive(y,y)
            queue=[]
            queue.append(y)
            workGraph.setState(y,labelledUnscanned)
            
        
            #Step 2 
            while(True):
                ##print("2")
                ##print("2 queue:",queue)
                
                """for node in queue:
                    if workGraph.getNode(node).getState()==labelledUnscanned:
                        u=node
                        queue.remove(u)
                        break"""
                u=queue.pop()
                #print("u",u,self.getNameFromID(u))
                #1
                if(workGraph.getIN(u)==False):
                    print(2.1)
                    #print(2.1,"queue before",queue)
                    workGraph.fsearch(u,queue) # on a rajouté queue dans fsearch
                    """for node in workGraph.getNodes():
                        if node.getLabel_Positive()!=None:
                            ##print(node.toString())
                    ##print("\n")
                    for node in workGraph.getNodes():
                        if node.getState()!=unlabelled:
                            ##print(node.toString())
                    ##print("\n")
                    for edge in workGraph.getEdges():
                        if(edge.getMarked()==True):
                            ##print(edge.toString())"""
                    #print("2.1 queue after:",queue)
                    ###print(workGraph.toString())
                #2
                """if(workGraph.getIN(u)==True and workGraph.getLabel_Negative(u)==None and workGraph.getLabel_Positive(u)!=None):
                    workGraph.bsearch(u,queue)
                    print(2.2)"""
                if(workGraph.getIN(u)==True and workGraph.getLabel_Negative(u)==None and workGraph.getLabel_Positive(u)!=None):
                    workGraph.bsearch(u,queue)
                    print(2.2)
                #3
                if(workGraph.getIN(u)==True and workGraph.getLabel_Negative(u)!=None):
                    workGraph.fsearch(u,queue)
                    workGraph.bsearch(u,queue)
                    print(2.3)
                #4
                ##print(2.4)
                workGraph.setState(u,labelledScanned)
                doesProceedStep4=workGraph.getState(x)!=unlabelled
                doesProceedStep7=queue==[] and workGraph.getState(x)==unlabelled
                if ( doesProceedStep7 or doesProceedStep4):

                    #print(3,"proceed4?",doesProceedStep4,"proceed7?",doesProceedStep7)
                    break

            if(doesProceedStep4):
                #print(4)
                #Step 4
                u=x
                w=x
                
                while(True):
                    ##print(5)
                    #Step 5
                    z=None
                    #5.1
                    #print("5.1 u:",u,"pos label",workGraph.getLabel_Positive(u),"neg label",workGraph.getLabel_Negative(u))
                    if(workGraph.getLabel_Positive(u)!=None and workGraph.getLabel_Negative(u)==None):
                        print(5.1)
                        z=workGraph.getLabel_Positive(u)
                        #print("5.1 u:",u,"z: ",z)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(True)
                        u_z.setDir([z,u])
                        if(z!=y):
                            workGraph.setIN(z,True)
                            print("5.1.1")
                    #5.2
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)==None):
                        print(5.2)
                        z=workGraph.getLabel_Negative(u)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(False)
                        if(workGraph.getLabel_Negative(z)!=None and workGraph.getLabel_Positive(z)==None):
                            workGraph.setIN(z,False)
                    #5.3
                    """if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Negative(w) and z==workGraph.getLabel_Positive(u)):
                        print(5.3)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(True)
                        u_z.setDir([z,u])
                        if(z!=y):
                            workGraph.setIN(z,True)
                    #5.4
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Positive(w) and z==workGraph.getLabel_Negative(u)):
                        print(5.4)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(False)"""
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Negative(w) ):
                        z=workGraph.getLabel_Positive(u)
                        print(5.3)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(True)
                        u_z.setDir([z,u])
                        if(z!=y):
                            workGraph.setIN(z,True)
                    #5.4
                    if(workGraph.getLabel_Negative(u)!=None and workGraph.getLabel_Positive(u)!=None and u==workGraph.getLabel_Positive(w)):
                        z=workGraph.getLabel_Negative(u)
                        print(5.4)
                        u_z=workGraph.getEdge(u,z)
                        u_z.setMarked(False)
                    #Step 6
                    ##print(6)
                    if(z!=y):
                        print(6.1)
                        w=u
                        u=z
                    else:#z==y
                        print(6.2)
                        queue=[]
                        workGraph.eraseLabels()
                        break
            elif(doesProceedStep7):
                ##print(7)
                break
        #Step 7
        ##print(7,"vrai")
        ensembleSeparant=[]
        y=id_puit
        
        """for edge in workGraph.getEdgesConnectedToNode(y):
            if(edge.getMarked()):
                if(edge.getNodes()[1]!=y):
                    u=edge.getNodes()[1]
                else:
                    u=edge.getNodes()[0]
                if(workGraph.getLabel_Positive(u)==None and workGraph.getLabel_Negative(u)==None):
                    #print(7.2," u=",u,self.getNameFromID(u))
                    ensembleSeparant.append(u)
                if(workGraph.getLabel_Positive(u)!=None or workGraph.getLabel_Negative(u)!=None):
                    ##print(7.3)
                    res=workGraph.step7(u,y)
                    ensembleSeparant.append(res)
                    #print(7.3," u=",res)"""
        """for edge in workGraph.getEdgesConnectedToNode(y):
            if(edge.getMarked()):
                if(edge.getNodes()[1]!=y):
                    u=edge.getNodes()[1]
                else:
                    u=edge.getNodes()[0]
                #print("7.2BIS, LOOKING ",workGraph.getState(u)==unlabelled,u,self.getNameFromID(u),"pos",workGraph.getLabel_Positive(u),'neg',workGraph.getLabel_Negative(u))
                if(workGraph.getState(u)==unlabelled):
                    #print(7.2," ADDING u=",u,self.getNameFromID(u))
                    ensembleSeparant.append(u)
                elif(workGraph.getState(u)!=unlabelled):
                    #print(7.3," LOOKING FROM u=",u,self.getNameFromID(u))
                    res=workGraph.step7(u,y)
                    #print(7.3,"ADDING res=",res,self.getNameFromID(res))
                    ensembleSeparant.append(res)"""
        
        connectedToY=workGraph.getEdgesConnectedToNode(y)
        ensembleSeparant=[]
        #print(7)
        for edge in connectedToY:
            if(y!=edge.getNodes()[0]):
                u=edge.getNodes()[0]
            else:
                u=edge.getNodes()[1]
            if(edge.getMarked()):
                print("+1")
                ##print("in 7BIS, LOOKING ",workGraph.getState(u)==unlabelled,u,self.getNameFromID(u),"pos",workGraph.getLabel_Positive(u),'neg',workGraph.getLabel_Negative(u))
                if(workGraph.getState(u)==unlabelled):
                    print(" 1 u quon ajoute:",u)
                    #print("in 7.1, adding ",u,self.getNameFromID(u),"pos",workGraph.getLabel_Positive(u),'neg',workGraph.getLabel_Negative(u))
                    ensembleSeparant.append(u)
                    continue
                elif(workGraph.getState(u)!=unlabelled):
                    print(" 2 u quon regarde:",u)
                    ##print(7.3," LOOKING u=",u,self.getNameFromID(u))
                    #res=self.getSISNode(u,workGraph,y)
                    res=self.step7VAvril(u,workGraph,[y])
                    ##print(7.3," ADDING res=",res,self.getNameFromID(res))
                    ensembleSeparant.append(res)

        return ensembleSeparant
####################################################################################################################################################################################
####################################################################################################################################################################################
####################################################################################################################################################################################
####################################################################################################################################################################################

    def step7VAvril(self,u,workgraph,oldus):
        #print("------")
        connectedToU=workgraph.getEdgesConnectedToNode(u)
        valeur=None
        for edge in connectedToU:
            i=0
            for oldu in oldus:
                if(oldu not in edge.getNodes()):
                    i+=1
            if(i==len(oldus)):
            
                if(u!=edge.getNodes()[0]):
                    v=edge.getNodes()[0]
                else:
                    v=edge.getNodes()[1]
                print("v",v)
                if(edge.getMarked()):
                    #print(workgraph.getEdge(u,v).toString())
                    valeur=self.step7VAvril(v,workgraph,[u]+oldus)
                    break
        if(valeur==None and workgraph.getState(u)=="unlabelled"):
            return u
        else:
            return valeur
                
    #f(u,workGraph,y)
    def getSISNode(self,u,workGraph,oldu):
        ##print(oldu,self.getNameFromID(oldu))
        ##print(u,self.getNameFromID(u))
        if(workGraph.getState(oldu)!="unlabelled" and workGraph.getState(u)=="unlabelled"):
            return oldu
        connectedToU=workGraph.getEdgesConnectedToNode(u)
        for edge in connectedToU:
            if(edge.getMarked() and oldu not in edge.getNodes()):
                if(u!=edge.getNodes()[0]):
                    v=edge.getNodes()[0]
                else:
                    v=edge.getNodes()[1]
                return self.getSISNode(v,workGraph,u)

    def f(self,u,workGraph,y):

        connectedToU=workGraph.getEdgesConnectedToNode(u)
        #print("---------------------------")
        i=0
        m=[]
        for edge in connectedToU:
            if(y not in edge.getNodes()):
                if(u!=edge.getNodes()[0]):
                    v=edge.getNodes()[0]
                else:
                    v=edge.getNodes()[1]

                #print("u",u,"v",v,"marked",edge.getMarked())
                if edge.getMarked() :
                    i=i+1
                    m.append(edge.getNodes())

        #print(i,m)



    #ID->DAG(\noeuds utilités ?)->MoralizedAncestral H-> DAG H~ +source+puit
    def fromIDToMoralizedAncestral2(self,decisionNodeID,ID):
        #--Construction de X={D1,..,Dj} où Dj est le noeud de décision pour lequel on veut le SIS
        X=[]
        for nodeID in ID.nodes():
            if(ID.isDecisionNode(nodeID)):
                if(self.ordreDecision.index(nodeID)<=self.ordreDecision.index(decisionNodeID)): #prendre tous les noeuds de décision si il precède dj ou égal dans l'ordre
                    X=X+list(ID.family(nodeID)).copy()
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
        for (nodeID,node2ID) in MoralizedAncestral.edges():#Connection source
            if(nodeID in X and node2ID in X):
                continue
            if(nodeID in X or node2ID in X):
                if(node2ID in X):
                    if(nodeID not in X and not MoralizedAncestral.existsEdge(alphaXid,nodeID) ):
                        MoralizedAncestral.addEdge(alphaXid,nodeID)
                if(nodeID in X):
                    if(node2ID not in X and not MoralizedAncestral.existsEdge(alphaXid,node2ID)):
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
        



    #Page 5 - 2012 Yuan&Hensen - Colonne de droite - 2ème paragraphe
    def fromIDToMoralizedAncestral(self,decisionNodeID,ID):
        """
        Fonction qui transforme l'ID en graphe moralisé ancestral pour appliquer Acid&Campos

        ID le diagramme d'influence étudié
        decisionNodeID est l'identifiant du noeud de décision pour lequel on veut trouver le SIS

        renvoi le graphe moralisé ancestral (version undigraph) et les identifiants des noeuds sources et puits
        """
        #--construction de X=fa(Delta_j)--
        #(reunion des familles des noeuds de decisions précedant decisionNode selon l'ordre "ordre")
        X=[]
        for nodeID in ID.nodes():
            if(ID.isDecisionNode(nodeID)):
                if(self.ordreDecision.index(nodeID)<=self.ordreDecision.index(decisionNodeID)): #si il precède dj ou égal dans l'ordre
                    X=X+list(ID.family(nodeID)).copy()

        #--Construction de Y=Noeuds Utilités qui sont des descendants de decisionNodeID--
        Y=list(ID.descendants(decisionNodeID)).copy()
        ytemp=Y.copy()
        for nodeID in ytemp:
            if(not ID.isUtilityNode(nodeID)):
                Y.remove(nodeID)
        XUY=self.unionList(X,Y)
        XUYNames=self.getNamesFromID(XUY,ID)

        #--Construction du graphe ancestral moralisé--
        #un undigraph avec des noeuds de mêmes identifiants que ceux du diagramme d'influences
        MoralizedAncestral=ID.moralizedAncestralGraph(XUYNames)

        #--Ajout des noeuds sources(alpha) et puit (beta) et de leurs aretes
        alphaXid=MoralizedAncestral.addNode()
        BetaYid=MoralizedAncestral.addNode()

        #Construction de la liste des ancêtres de Y descendant de D_j
        temp=[]
        for y in Y:
            temp=self.unionList(temp,list(ID.ancestors(y)))
        desc=ID.descendants(decisionNodeID)
        t=temp.copy()
        for nodeID in t:
            if(nodeID not in desc):
                temp.remove(nodeID)

        #Connection des sources et des puits
        for nodeID in temp: #Connection puit
            if( not MoralizedAncestral.existsEdge(BetaYid,nodeID)):
                MoralizedAncestral.addEdge(nodeID,BetaYid)
        for (nodeID,node2ID) in MoralizedAncestral.edges():#Connection source
            if(nodeID in X and node2ID in X):
                continue
            if(nodeID in X or node2ID in X):
                if(node2ID in X):
                    if(nodeID not in X and not MoralizedAncestral.existsEdge(alphaXid,nodeID)):
                        MoralizedAncestral.addEdge(alphaXid,nodeID)
                if(nodeID in X):
                    if(node2ID not in X and not MoralizedAncestral.existsEdge(alphaXid,node2ID)):
                        MoralizedAncestral.addEdge(alphaXid,node2ID)
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
                ##print("in warning")
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
        ###print("fsearch : u: ",u)
        for edge in self.edgeList:
            if(u in edge.getNodes()):
                
                if(u==edge.getNodes()[0]):
                    v=edge.getNodes()[1]
                else:
                    v=edge.getNodes()[0]
                ###print("fSearch in 1, this v:",v)
                if(self.getState(v)=="unlabelled" and not self.getEdge(u,v).getMarked()):
                    ###print("fSearch in 2")
                    self.setLabel_Positive(v,u)
                    self.setState(v,"labelledUnscanned")
                    queue.append(v)
    def bsearch(self,u,queue):
        ##print("bSearch")
        for edge in self.edgeList:
            if(u in edge.getNodes()):
                if(u==edge.getNodes()[0]):
                    t=edge.getNodes()[1]
                else:
                    t=edge.getNodes()[0]
                if(self.getEdge(u,t).getMarked() and self.getEdge(u,t).getDir()==[t,u]):
                    
                    if(self.getLabel_Negative(t)==None):
                        #Erreur de frappe dans le texte ?????????  self.setLabel_Negative(y,u)
                        print("IM IN HERE")
                        self.setLabel_Negative(t,u)
                        #queue.append(t)
                    elif(self.getState(t)=="labelledScanned"):
                        print("IM IN HERE2")
                        self.setState(t,"labelledUnscanned")
                        queue.append(t)
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
        if( not label_positive==None and self.state=="unlabelled"):
            self.setState("labelledUnscanned")

    def setLabel_Negative(self,label_negative):
        self.label_negative=label_negative
        if( not label_negative==None and self.state=="unlabelled"):
            self.setState("labelledUnscanned")
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