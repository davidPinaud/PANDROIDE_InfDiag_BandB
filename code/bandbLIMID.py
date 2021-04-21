"""File containing a class that allows the encapsulation of an influence diagram and its resolution by a branch and bound method
"""

from andOrGraph import decisionNode,chanceNode,andOrGraph
from pylab import *
import pyAgrum as gum
from minindepset import MinimalDSep


class BranchAndBoundLIMIDInference():
    """Class that allows the encapsulation of an influence diagram and its resolution by a branch and bound method

    Attributes
    ----------
    ID : pyAgrum.InfluenceDiagram
        The influence diagram to encapsulate
    OrdreDecision : list of decision node ids in the order in which the decisions are taken in the influence diagram
    """
    def __init__(self,ID,OrdreDecision):
        """Initializez the class

        Parameters
        ----------
        ID : pyAgrum.InfluenceDiagram
            The influence diagram to encapsulate
        OrdreDecision : list
            list of decision node ids in the order in which the decisions are taken in the influence diagram
        """        
        self.ID=ID
        self.sis=dict()
        self.ordreDecision=OrdreDecision
        self.IDRelaxe=self.createRelaxation()
        self.andOrGraph=andOrGraph(self.ID,None)
        self.root=None

    
    #ids of parents of current decisionNode,chanceNode(parents[0],domain)
    def createCoucheChance(self,parents,root):
        """[summary]

        Parameters
        ----------
        parents : [type]
            [description]
        root : [type]
            [description]
        """        
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
                        ss=self.evaluate(self.IDRelaxe,contextetemp)
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
                        ss=self.evaluate(self.ID,contextetemp)
                        d.addEvaluation(key=dom,evaluation=(ss.MEU()["mean"],ss.MEU()["variance"]))
                        d.setInference(ss)
                #on peut directement choisir la décision optimale car c'est une feuille
                decisionOpt,valeurDecisionOptimale=self.getDecisionOpt(d)
                d.setDecisionOptimale(decisionOpt)
                d.setValeurDecisionOptimale(valeurDecisionOptimale)
        return couche

    def getDecisionOpt(self,decisionNode):
        """Function that, given a decisionNode from the And/Or Graph, returns the optimal decision and its MEU value.
        It is ONLY used internally and is part of the branch and bound algorithm. It is used only on 
        decision nodes that are leaf nodes in the And/Or Graph that are already evaluated. Do NOT use this function 
        to get the optimal decision of a decision Node.

        Parameters
        ----------
        decisionNode : andOrGraph.decisionNode
            the decision node, part of the And/Or Graph

        Returns
        -------
        decisionOpt : Object
            The optimum decision
        valeurDecisionOptimale : float
            the value of the optimal decision
        """        
        eval=decisionNode.getEvaluation()
        decisionOpt=None
        valeurDecisionOptimale=None
        for decision,valeurDecision in eval.items():
            if(valeurDecisionOptimale==None or valeurDecision["mean"]>valeurDecisionOptimale["mean"]):
                valeurDecisionOptimale=valeurDecision
                decisionOpt=decision
        return decisionOpt,valeurDecisionOptimale
    

    def getDomain(self,NodeID):
        """Function that returns the domain in which this node can instanciate

        Parameters
        ----------
        NodeID : int
            the id of the node

        Returns
        -------
        list
            Domain of the node
        """        
        return self.ID.variable(NodeID).domain()[1:-1].split(',')

    
    def evaluate(self,ID,evidence):
        """Function that makes the inference over an ID given evidence

        Parameters
        ----------
        ID : pyAgrum.InfluenceDiagram
            The influence diagram to evaluate
        evidence : set of {key:nodeID,value:probability} (cpt)
            the evidence to set in the inference

        Returns
        -------
        pyAgrum.ShaferShenoyLIMIDInference
            The inference object with makeInference() already called
        """        
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


    def createRelaxation(self):
        """Function that creates the relaxation of the encapsulated influence diagram by adding informations to the ID through the 
        SIS and removing non-required arcs

        Returns
        -------
        pyAgrum.InfluenceDiagram
            The relaxed influence diagram
        """        
        relaxedID=gum.InfluenceDiagram(self.ID)
        #Calculs des SIS des noeuds de décision et en faire des noeuds d'information aux noeuds de décision associés
        for i in range(len(self.ordreDecision)-1,-1,-1):
            sis=self.SIS(self.ordreDecision[i],relaxedID)
            #print("SIS de :",relaxedID.variable(self.ordreDecision[i]).name()," | ",self.getNamesFromID(list(sis)))
            for nodeID in sis:
                if(not relaxedID.existsArc(nodeID,self.ordreDecision[i]) and nodeID in relaxedID.nodes()):
                    relaxedID.addArc(nodeID,self.ordreDecision[i])
        #Enlever les noeuds non-requis
        relaxedID=gum.ShaferShenoyLIMIDInference(relaxedID).reducedLIMID()
        #Remplir les CPT
        for node in relaxedID.nodes():
            if(relaxedID.isChanceNode(node)):
                relaxedID.cpt(node).fillWith(gum.Potential(self.ID.cpt(node)))
            if(relaxedID.isUtilityNode(node)):
                relaxedID.utility(node).fillWith(gum.Potential(self.ID.utility(node)))
        return relaxedID
        

    #ID->DAG (sans neouds utilités)->graphe moralisé ancestral ou on doit trouver l'ensemble de noeuds
    #séparant X et Y
    def SIS(self,decisionNodeID,ID):
        """Function that returns the Sufficient information set for a given decision node and influence diagram

        Parameters
        ----------
        decisioNodeID : int
            the id of the decision node
        ID : pyAgrum.InfluenceDiagram
            the ID on which to base the creation of the graph

        Returns
        -------
        SIS : set of ints
            The sufficient information set of the given decision node in the given influence diagram
        """        
        #--Construction du graphe moralisé sur lequel appliquer l'algorithme--
        graph,x,y=self.fromIDToMoralizedAncestral(decisionNodeID,ID)
        SIS=MinimalDSep(graph).find(y,x) #a set
        self.sis[decisionNodeID]=SIS
        return SIS


    #ID->DAG(\noeuds utilités ?)->MoralizedAncestral H-> DAG H~ +source+puit
    def fromIDToMoralizedAncestral(self,decisionNodeID,ID):
        """Function that, given an influence diagram and a decision node id, creates the corresponding
        moralized ancestral undirected graph and adds a source and a well node. It is used to generate a graph on
        which the SIS algorithm can work to return the SIS of the decision node given.

        Parameters
        ----------
        decisioNodeID : int
            the id of the decision node
        ID : pyAgrum.InfluenceDiagram
            the ID on which to base the creation of the graph

        Returns
        -------
        MoralizedAncestral : pyAgrum.UndiGraph
            the moralized ancestral undirected graph generated
        alphaXid,BetaYid : int
            the source and well added to the graph
        """        
        #--Construction de X=Fa({D1,..,Dj}) où Dj est le noeud de décision pour lequel on veut le SIS
        X=set()
        for nodeID in self.ordreDecision[:self.ordreDecision.index(decisionNodeID)+1]:
            X=X.union(ID.family(nodeID))
        #--Construction de Y={U inter de(Dj)} Descendants de Dj qui sont des noeuds d'utilités
        Y=ID.descendants(decisionNodeID)
        Y_temp=Y.copy()
        for nodeID in Y_temp:
            if(not ID.isUtilityNode(nodeID)):
                Y.remove(nodeID)
        XUY=X.union(Y)
        #--Construction de An(XUY)=XUY Union (Union des an(XUY_i)) Union de lui même et de l'union des ancêtres de ses élements
        ancestralSubset=XUY.copy()
        for nodeID in XUY:
            ancestralSubset=ancestralSubset.union(ID.ancestors(nodeID))
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
        descendantOfDecisionNode=ID.descendants(decisionNodeID)
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
        temp=set() #an(U inter de(Dj))
        for y in Y:
            temp=temp.union(ID.ancestors(y))
        desc=ID.descendants(decisionNodeID)#de(Dj)
        temp=temp.intersection(desc)
        for nodeID in temp: #Connection puit
            if( not MoralizedAncestral.existsEdge(BetaYid,nodeID)):
                MoralizedAncestral.addEdge(nodeID,BetaYid)
        
        return MoralizedAncestral,alphaXid,BetaYid 
        


    #--Méthodes utilitaires--

    def getNameFromID(self,idNode):
        """Function that returns the name of a node in the ID from its id

        Parameters
        ----------
        idNode : int
            the id of the node

        Returns
        -------
        str
            the name of the node
        """        
        return self.ID.variable(idNode).name()
    def getNamesFromID(self,listId):
        """Function that returns the name of nodes in the influence diagram given their ids

        Parameters
        ----------
        listId : list of int
            list of the ids of the node

        Returns
        -------
        list of str
            list of the names of the nodes
        """        
        """
        retourne les noms des noeuds donnés sous forme d'identifiant (listId) dans le diagramme d'influence InDi
        """
        return [self.ID.variable(idNode).name() for idNode in listId]
    def getSIS(self,decisioNodeID):
        """Function that returns the Sufficient Information Set of a decision node

        Parameters
        ----------
        decisioNodeID : int
            the id of the decision node

        Returns
        -------
        set of ints
            the Sufficient Information Set of the decision Node
        """        
        if(self.ID.isDecisionNode(decisionNode)):
            return self.sis[decisioNodeID]
