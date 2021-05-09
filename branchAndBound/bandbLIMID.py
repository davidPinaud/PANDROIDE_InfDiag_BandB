"""File containing a class that allows the encapsulation of an influence diagram and its resolution by a branch and bound method
"""
from andOrGraph import decisionNode,chanceNode,andOrGraph
from pylab import *
import pyAgrum as gum
from minindepset import MinimalDSep
from queue import LifoQueue
import random



class BranchAndBoundLIMIDInference():
    """Class that allows the encapsulation of an influence diagram and its resolution by a branch and bound method

    Attributes
    ----------
    ID : pyAgrum.InfluenceDiagram
        The influence diagram to encapsulate
    OrdreDecision : list of decision node ids in the order in which the decisions are taken in the influence diagram
    """
    def __init__(self,ID,OrdreDecision,verbose=False):
        """Initializes the class

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
        self.bn=self.getBNFromID(ID)
        self.ie=gum.LazyPropagation(self.bn)
        self.nbCoupe=0
        self.verbose=verbose
    #ids of parents of current decisionNode,chanceNode(parents[0],domain)            
    def branchAndBound(self):
        """Function that executes the branch and bound algorithm.
        It generated the and or graph on the fly and calculates the MEU for every decision nodes/chance nodes for every instanciation possible
        """        
        index=0
        decisionNodeID=self.ordreDecision[index]#Prendre le premier noeud de décision dans l'ordre de décision défini
        #--on récupère les parents qui sont des noeuds chances dans l'ID du noeud de décision courant--
        parents_chanceID=self.getParents_chanceID(decisionNodeID,None)
        if(len(parents_chanceID)>0):
            self.root=chanceNode(parents_chanceID[0],self.getDomain(parents_chanceID[0]),None,None,dict(),self.andOrGraph.getIDNoeudAndOr())#racine de l'arbre ET/OU
            self.andOrGraph.addNoeudChance(self.root)
        pile=[]
        if(len(parents_chanceID)>0):
            coucheInit=self.addCouche(index,self.root,parents_chanceID,pile)
        couches=dict() #key=decision node #value : list of decision nodes
        if(len(parents_chanceID)>0):
            couches["coucheInit"]=coucheInit
        indexPile=0
        nb=0
        #while(not pile.empty()):
        while(not self.isAllDecisionNodeProcessed(couches)):
            nb+=1
            if(self.verbose):
                print("####################################################################################################################")
                print("####################################################################################################################")
                print("####################################################################################################################")
                print("####################################################################################################################")
                print("Nouvelle Branche, nombre de branche au total:",nb,"nombre de branches coupées:",self.nbCoupe)

            #Tant que la pile n'est pas vide :
                #prendre un noeud de décision dans la pile et l'enlever de la pile
                #pour tout element e du domaine du noeud de décision (sans ceux dans le doNotDevelop)
                    #appeler addCouche pour creer la nouvelle couche    
                        #si la couche est une couche feuille
                            #appeler induction arriere
                #sinon continuer
            nodeADev=self.andOrGraph.getNoeudWithIdAndOr(pile[indexPile%len(pile)])
            indexPile+=1
            nodeADevID=nodeADev.getNodeID()
            domain=self.getDomain(nodeADevID)
            index=self.ordreDecision.index(nodeADevID)
            if(index<=len(self.ordreDecision)-2): #on veut pas developper 
                for dom in domain:
                    if(dom not in nodeADev.getDoNotDevelop() and dom not in nodeADev.getEnfantProcessed()):
                        if(self.verbose):
                            print("On va développer le noeud",self.getNameFromID(nodeADevID),"id",nodeADev.getId_andOr(),'On va donc chercher les parents du noeud',self.getNameFromID(self.ordreDecision[index+1]))
                            print("Le domaine de",self.getNameFromID(nodeADevID),":",domain,",les valeurs déjà processed:",nodeADev.getEnfantProcessed(),"ce qu'on va process :",dom)
                            print(self.getNameFromID(nodeADevID),"de contexte :")
                            for id,value in nodeADev.getContexte().items():
                                print(self.getNameFromID(id),":",value)
                            print(self.getNameFromID(nodeADevID),":",dom)
                        parents_chanceID=self.getParents_chanceID(self.ordreDecision[index+1],nodeADevID)
                        if(self.verbose):
                            print("Les parents de ",self.getNameFromID(self.ordreDecision[index+1])," sont : ",self.getNamesFromID(parents_chanceID))
                        contexteTemp=dict(nodeADev.getContexte())
                        contexteTemp[nodeADevID]=dom
                        root=chanceNode(parents_chanceID[0],self.getDomain(parents_chanceID[0]),nodeADev,dom,contexteTemp,self.andOrGraph.getIDNoeudAndOr())
                        nodeADev.addEnfant(root,dom)
                        nodeADev.addEnfantProcessed(dom)
                        self.andOrGraph.addNoeudChance(root)
                        couche=self.addCouche(index+1,root,parents_chanceID,pile)
                        #couches[nodeADev]=couche
                        couches[nodeADev]=couche if type(couche)==list else [couche,]
                        if (index+1==len(self.ordreDecision)-1):#si on est sur une couche feuille
                            a=self.inductionArriere(couche,pile,couches,indexPile)
                            indexPile=a if a!=None else indexPile
                            #pile.insert(0,nodeADev.getId_andOr())
                            #appeller induction arriere
                        # if(len(nodeADev.getEnfantProcessed())!=len(nodeADev.getEnfant())):
                        #     pile.insert(0,nodeADev.getId_andOr())
                        break
    
    def createCoucheChance(self,parents,root,contexte):
        """Function that builds a new branch by adding recursively layers of chance nodes (only, decision nodes are added with the createCoucheDecision function)

        Parameters
        ----------
        parents : list
            the set of parents of the decision node for which we are branching (not the one from where we branch but the ones that will be created)
        root : chanceNode
            the chance node that is the root of the subtree
        contexte : dict
            the instanciation path of the root
        """        
        if(len(parents)==0):
            return
        domain=self.getDomain(root.getNodeID())
        self.andOrGraph.addNoeudChance(root)
        
        for d in domain:
            domainbis=self.getDomain(parents[0])
            contexteTemp=dict(contexte)
            contexteTemp[root.getNodeID()]=d
            node=chanceNode(parents[0],domainbis,root,d,contexteTemp,self.andOrGraph.getIDNoeudAndOr())
            self.andOrGraph.addNoeudChance(node)
            root.addChild(d,node)
            self.createCoucheChance(parents[1:],node,contexteTemp)
    #root,self.ordreDecision[i],[],dict()
    def createCoucheDecision(self,root,decisionNodeID,contexte,pile,couche):
        """Function that builds the layer of decision node at the base of a new branch

        Parameters
        ----------
        root : chanceNode
            the root of the subtree
        decisionNodeID : int
            the id of the decision node (in the ID) for which we must build the layer
        contexte : dict
            the instanciation path of a decision node
        pile : list
            the list of decision nodes to expand during the branch and bound, new decisions nodes are added as they are created
        couche : list
            the branch for which we must create the layer

        Returns
        -------
        list
            the branch but now with a layer of decision nodes
        """        
        childs=root.getChilds()
        isFeuille=True if len(childs)==0 else False
        if(not isFeuille):
            for supportValue,child in childs.items():
                contexteTemp=dict(contexte)
                contexteTemp[root.getNodeID()]=supportValue
                self.createCoucheDecision(child,decisionNodeID,contexteTemp,pile,couche)
        else:
            domain=self.getDomain(root.getNodeID())
            for d in domain:
                contexteTemp=dict(contexte)
                contexteTemp[root.getNodeID()]=d
                node=decisionNode(decisionNodeID,contexteTemp,root,self.getDomain(decisionNodeID),self.andOrGraph.getIDNoeudAndOr())
                couche.append(node)
                root.addChild(d,node)
                if(not self.ordreDecision.index(node.getNodeID())==len(self.ordreDecision)-1):#is node is a leaf
                    pile.append(node.getId_andOr())
                self.andOrGraph.addNoeudDecision(node)
        #return couche
        return couche if type(couche)==list else [couche,]



    #induction arriere : (on n'a pas à calculer la décision optimale des feuilles car c'est fait dans addCouche)
    #Entrée <- couche courante
    #calculer les valeur des noeuds chances jusqu'a ce qu'on arrive à un noeud de décision
    #pour ce noeud de décision, regarder toutes ses bornes supérieures et élaguer si besoin les domaines dont on n'a pas besoin (ajouter dans le donotdevelop du noeud)
    #continuer après le noeud de décision seulement si toute la couche après le noeud est évaluée (pas borne sup) tant qu'on arrive pas au self.root (racine de l'arbre)
    def inductionArriere(self,couche,pile,couches,indexPile):
        """Function that is called when the algorithm arrives at decision nodes that are leafs in the and/or graph, it allows to go back up through the branch while computing the values of the chance nodes and the MEU of the decision nodes
        It also prunes branches that upper bound are smaller than the best evaluation. It is a recursive function that uses the induction function.

        Parameters
        ----------
        couche : list
            the branch we wish to go up through
        pile : list
            the list of decisions nodes to expand
        couches : list
            the list of branches present in the and/or tree
        indexPile : int
            the next decision node to expand

        Returns
        -------
        int or None
            if the algorithm reaches the root of the and or graph, it returns None and the algoritm has finished, otherwise, it returns an int that is the index of next decision node to expand in the pile
        """        
        if(self.verbose):
            print("induction arrière")
        parents=self.induction(couche)
        while(len(parents)>1):
            parents=self.induction(parents)#on arrive au fils d'un noeud de décision
        root=parents[0]
        if(root==self.root):
            return
        noeudDecision=root.getParent()
        valeurDomRoot=root.getValeurParent()#Valeur de l'instiation de noeud décision pour root
        noeudDecision.addEvaluation(valeurDomRoot,(root.getValeur(),None))

        if(root.getValeur()!=None and (noeudDecision.getValeurDecisionOptimale()==None or root.getValeur()>noeudDecision.getValeurDecisionOptimale()[0])):
            #noeudDecision.addDoNotDevelop(noeudDecision.getDecisionOptimale())
            noeudDecision.setDecisionOptimale(valeurDomRoot)
            noeudDecision.setValeurDecisionOptimale([root.getValeur()])
            if(self.verbose):
                print("changement de valeur optimale pour le noeud ",self.getNameFromID(noeudDecision.getNodeID()),"change à ",valeurDomRoot,"pour la valeur",root.getValeur())
            for DomainValue,ss in noeudDecision.getBorneSup().items():#Pour tous les frères
                for d,child in noeudDecision.getEnfants().items():
                    if(child==root):
                        domainRoot=d
                        break
                if(DomainValue!=domainRoot):#Pas le noeud qu'on vient juste d'évaluer
                    isEvalue=False
                    for d2,ss2 in noeudDecision.getEvaluation().items():
                        if(d2==DomainValue):
                            isEvalue=True
                            break
                    if(not isEvalue):#pas encore évalué
                        if(self.verbose):
                            print("On regarde un voisin pas encore évalué (mais la borne sup est là")
                            print("Sa borne sup:",ss,"l'évaluation qu'on a :",root.getValeur(),f"root de contexte {root.getContexte()}")
                        if(ss[0]<=root.getValeur()):
                            if(self.verbose):
                                print("on coupe")
                            noeudDecision.addDoNotDevelop(child.getContexte()[noeudDecision.getNodeID()])
                            self.nbCoupe+=1
                        else:
                            if(self.verbose):
                                print("on ne coupe pas")
        for node in couche:#On enlève de la pile ce qu'on vient d'évaluer
            if( node in couche and node.getId_andOr() in pile):
                del pile[pile.index(node.getId_andOr())]
        if(len(noeudDecision.getEvaluation())+len(noeudDecision.getDoNotDevelop())<len(noeudDecision.getBorneSup())):#PAS tous les enfants ont été processed
            if(self.verbose):
                print("in not all processed")
            #indexPile=pile.index(noeudDecision.getId_andOr())# on refait le même noeud de décision
            indexPile-=1
            return indexPile
        else:
            if(self.verbose):
                print("in all processed")
            coucheParent=self.findCoucheDeNoeudDeDecision(noeudDecision,couches)
            isAllProcessed=True
            for decisionNode in coucheParent:
                isAllProcessed=isAllProcessed and decisionNode.isProcessed()
            if(isAllProcessed):
                if(self.verbose):
                    print("recursive call")
                self.inductionArriere(coucheParent,pile,couches,indexPile)


    def induction(self,ligne):
        """Function that allows to go up through a layer in a branch given a layer ligne. It calculates the values of the chance nodes when the layer consist of chance nodes and the MEU of decision nodes when it consist decision node

        Parameters
        ----------
        ligne : list
            layer in which we want to start the going up process

        Returns
        -------
        list
            the layer above the layer ligne
        """        
        if(self.verbose):
            print("induction")
        parents=self.findLigneAuDessus(ligne)
        if(self.verbose):
            print("parents (ligne au dessus)",self.getNamesFromID([p.getNodeID() for p in parents]),len(parents))
        #print("parents des parents : ")
        if(not (len(parents)==1 and parents[0].getId_andOr()==self.root.getId_andOr())):
            self.ie.eraseAllEvidence()
            for parent in parents:
                self.ie.setEvidence(parent.getContexte())
                self.ie.makeInference()
                try:
                    parent.setProbabilitiesPosteriori(self.ie.posterior(parent.getNodeID()))
                except :
                    if(self.verbose):
                        print(f"Erreur dans le postérieur, noeud : {self.getNameFromID(parent.getNodeID())}")
                    break
                self.ie.eraseAllEvidence()
                s=0
                for ValeurDuSupport,enfant in parent.getChilds().items():
                    
                    if(self.ID.isChanceNode(enfant.getNodeID())):
                        if(enfant.getValeur()!=None):
                            s+=parent.getProbabilitiesPosteriori()[{self.getNameFromID(parent.getNodeID()):ValeurDuSupport}]*enfant.getValeur()
                    else:
                        if(enfant.getValeurDecisionOptimale()!=None):
                            s+=parent.getProbabilitiesPosteriori()[{self.getNameFromID(parent.getNodeID()):ValeurDuSupport}]*enfant.getValeurDecisionOptimale()[0]
                parent.setValeur(s)
        return parents
    def addCouche(self,index,root,parents_chanceID,pile):
        """Function that creates a new branch given a root node and the index of the decision node that is the bottom layer to be

        Parameters
        ----------
        index : int
            index of the decision node that is going to be the bottom layer in the branch
        root : chanceNode
            the node that serves as a root of the subtree
        parents_chanceID : list
            list of the parents of the decision node, used to build the tree before adding the decisions nodes as bottom layer
        pile : list
            the list of decision nodes still to be processed

        Returns
        -------
        list
            the list of nodes that constitutes the new branch
        """              
        #####Init#####
        decisionNodeID=self.ordreDecision[index]#Prendre le noeud de décision dans l'ordre de décision défini
        #--on récupère les parents qui sont des noeuds chances dans l'ID du noeud de décision courant--
        self.createCoucheChance(parents_chanceID[1:],root,root.getContexte())#Creer toutes les alternatives d'instanciation des parents_chances possibles
        couche=self.createCoucheDecision(root,decisionNodeID,root.getContexte(),pile,[])
        if(self.verbose):
            #print("ajout d'une couche, de racine,",self.getNameFromID(root.getNodeID()),"avec les noeuds de décisions crées étants :",self.getNamesFromID([node.getNodeID() for node in couche]),"de taille",len(couche))
            print("ajout d'une couche, de racine,",self.getNameFromID(root.getNodeID()),"avec les noeuds de décisions crées étants :",self.getNamesFromID([node.getNodeID() for node in couche]),"de taille",len(couche),"et d'id",[node.getId_andOr() for node in couche])
        #####END INIT#####
        ### Evaluation de la borneSup/borneInf######
        
        if(self.ordreDecision.index(decisionNodeID)+1<len(self.ordreDecision)):#si le noeud de décision n'est pas une feuille
            if(self.verbose):
                print("Calcul des bornes pour les noeuds de décisions")
            for d in couche:
                #print((couche.index(d)+1)*100/len(couche),'%')
                domain=self.getDomain(d.getNodeID())
                for dom in domain:
                    contextetemp=dict(d.getContexte())
                    contextetemp[decisionNodeID]=dom
                    ss=self.evaluate(self.IDRelaxe,contextetemp)
                    d.addBorneSup(key=dom,borneSup=(ss.MEU()["mean"],ss.MEU()["variance"]))
                    d.setInference(ss)
                #print(f"borne sup {self.getNameFromID(d.getNodeID())}, d'id {d.getId_andOr()} : {d.getBorneSup()}")
        else:#si le noeud de décision est une feuille
            if(self.verbose):
                print("Calcul des évaluations pour les noeuds de décisions")
            for d in couche:
                #print((couche.index(d)+1)*100/len(couche),'%')
                domain=self.getDomain(d.getNodeID())
                for dom in domain:
                    contextetemp=dict(d.getContexte())
                    contextetemp[decisionNodeID]=dom
                    ss=self.evaluate(self.ID,contextetemp)
                    d.addEvaluation(key=dom,evaluation=(ss.MEU()["mean"],ss.MEU()["variance"]))
                    d.setInference(ss)
                #print(f"Évaluation {self.getNameFromID(d.getNodeID())}, d'id {d.getId_andOr()} : {d.getEvaluation()}")
                #on peut directement choisir la décision optimale car c'est une feuille
                decisionOpt,valeurDecisionOptimale=self.getDecisionOpt(d)
                d.setDecisionOptimale(decisionOpt)
                d.setValeurDecisionOptimale(valeurDecisionOptimale)
        return couche




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
                relaxedID.cpt(node).fillWith(self.ID.cpt(node))
                relaxedID.cpt(node).normalizeAsCPT()
            if(relaxedID.isUtilityNode(node)):
                relaxedID.utility(node).fillWith(self.ID.utility(node))
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
    def viewAndOrGraph(self):
        """Creates a BN that allows to visualize the and or graph (without branches that have been cut)

        Returns
        -------
        BayesNet
            the BN
        """        
        bn=gum.BayesNet()
        alreadyIn=[]
        s=''
        nodeIDs=dict()
        for node in self.andOrGraph.getNoeud():
            if(node not in alreadyIn):
                nodeIDs[node.getId_andOr()]=bn.add(self.ID.variable(node.getNodeID()).name()+s,4)
                alreadyIn.append(node)
                s+=' '
        for node in self.andOrGraph.getNoeud():
            if(type(node)==chanceNode):
                for value,child in node.getChilds().items():#getChild
                    if(not bn.existsArc(nodeIDs[node.getId_andOr()],nodeIDs[child.getId_andOr()])):
                        bn.addArc(nodeIDs[node.getId_andOr()],nodeIDs[child.getId_andOr()])
            else:
                for value,child in node.getEnfants().items(): #getEnfant
                    if(not bn.existsArc(nodeIDs[node.getId_andOr()],nodeIDs[child.getId_andOr()])):
                        bn.addArc(nodeIDs[node.getId_andOr()],nodeIDs[child.getId_andOr()])
        return bn

    def viewAndOrGraphNoCuts(self):
        """Creates a BN that allows to visualize the complete and or graph (with branches that have been cut).

        Returns
        -------
        BayesNet
            the BN
        """        
        #init:
        bn=gum.BayesNet()
        s=''
        #root node :
        decisionNode=self.ordreDecision[0]
        parents=self.getParents_chanceID(decisionNode,None)
        idNodeID=parents[0]
        idNodeBN=bn.add(self.ID.variable(idNodeID).name()+s,self.ID.variable(idNodeID).domainSize())
        #create the couche for the d0
        self.viewCreateCoucheChance(bn,s,parents[1:],idNodeID,idNodeBN)
        decisionNodeCreated=self.viewCreateDecisionCouche(bn,decisionNode,root=idNodeBN)
        #creates the rest of the tree
        self.createRest(bn,decisionNodeCreated,i=0)        
        return bn

        
    #--Méthodes utilitaires--
     #dans la méthode du branch and bound
    #il faut creer root et le mettre comme fils du noeuds de décision correspondant


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
            #print(f"Decision : {decision}, valeur: {valeurDecision}, decision optimal courante {decisionOpt}, valeur : {valeurDecisionOptimale}")
            if(valeurDecisionOptimale==None or valeurDecision[0]>valeurDecisionOptimale[0]):
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
        ss=gum.ShaferShenoyLIMIDInference(ID)
        ss.setEvidence(evidence)
        ss.makeInference()
        return ss
    def createRest(self,bn,decisionNodeCreated,i):
        """Function that creates the rest of the BN for viewAndOrGraphNoCuts

        Parameters
        ----------
        bn : pyAgrum.BayesNet
            the BN
        decisionNodeCreated : list
            the decision created in a layer
        i : int
            the index of the current decision node that is being developped
        """        
        i+=1
        d=decisionNodeCreated.copy()
        for IDdecisionNodeBN in d:
            decisionNode=self.ordreDecision[i]
            parents=self.getParents_chanceID(decisionNode,None)
            for domainValue in range(bn.variable(IDdecisionNodeBN).domainSize()):
                idNodeID=parents[0] #chance node
                s=''
                while( self.checkNameTaken(bn,self.ID.variable(idNodeID).name()+s)):
                    s+=' '
                idNodeBN=bn.add(self.ID.variable(idNodeID).name()+s,self.ID.variable(idNodeID).domainSize())
                bn.addArc(IDdecisionNodeBN,idNodeBN)
                self.viewCreateCoucheChance(bn,s,parents[1:],idNodeID,idNodeBN)
                decisionNodeCreated=self.viewCreateDecisionCouche(bn,decisionNode,root=idNodeBN)
                if(i+1<len(self.ordreDecision)):
                    self.createRest(bn,decisionNodeCreated,i)
                

    def checkNameTaken(self,bn,name):
        """Utility function for viewAndOrGraphNoCuts, checks if a name is taken in the BN (we need it because the and or tree has a lot of nodes with the same name)

        Parameters
        ----------
        bn : pyAgrum.BayesNet
            the bn to check
        name : str
            the name to check

        Returns
        -------
        bool
            true if the name is in the bn
        """        
        names=[bn.variable(node).name() for node in bn.nodes()]
        return name in names
    def viewCreateDecisionCouche(self,bn,decisionNode,root):
        """creates a layer of decision node for viewAndOrGraphNoCuts

        Parameters
        ----------
        bn : pyAgrum.BayesNet
            the bn in which to add the nodes
        decisionNode : int
            the id of the decision node to add in the layer
        root : int
            the id of the root of the layer (a chance node)

        Returns
        -------
        list
            list of ids of the decision node in the bn
        """        
        s=''
        decisionNodeCreated=[]
        if(len(bn.descendants(root))!=0):
            for node in bn.descendants(root):
                if len(bn.descendants(node))==0:
                    for domain in range(bn.variable(root).domainSize()):
                        while( self.checkNameTaken(bn,self.ID.variable(decisionNode).name()+s)):
                            s+=' '
                        IDdecisionNodeBN=bn.add(self.ID.variable(decisionNode).name()+s,self.ID.variable(decisionNode).domainSize())
                        bn.addArc(node,IDdecisionNodeBN)
                        decisionNodeCreated.append(IDdecisionNodeBN)
            return decisionNodeCreated
        else:
            for domain in range(bn.variable(root).domainSize()):
                while( self.checkNameTaken(bn,self.ID.variable(decisionNode).name()+s)):
                    s+=' '
                IDdecisionNodeBN=bn.add(self.ID.variable(decisionNode).name()+s,self.ID.variable(decisionNode).domainSize())
                bn.addArc(root,IDdecisionNodeBN)
                decisionNodeCreated.append(IDdecisionNodeBN)
            return decisionNodeCreated
    def viewCreateCoucheChance(self,bn,s,parents,idNodeIDParent,idNodeBNParent):
        """creates a layer of chance node for viewAndOrGraphNoCuts

        Parameters
        ----------
        bn : pyAgrum.BayesNet
            the bn in which to add the nodes
        s : str
            utility string to modulate the name of the nodes (prevent reuse)
        parents : list
            list of chance nodes that are parents of the decision node
        idNodeIDParent : int
            id in the influence diagram of the parent of the chance node that is being developped
        idNodeBNParent : int
            id in the bayesian network of the parent of the chance node that is being developped
        """        
        if(len(parents)==0):
            return
        print(idNodeIDParent)
        for domain in self.getDomain(idNodeIDParent):
            print("in")
            idNodeIDChild=parents[0]
            while( self.checkNameTaken(bn,self.ID.variable(idNodeIDChild).name()+s)):
                s+=' '
            idNodeBNChild=bn.add(self.ID.variable(idNodeIDChild).name()+s,self.ID.variable(idNodeIDChild).domainSize())
            bn.addArc(idNodeBNParent,idNodeBNChild)
            self.viewCreateCoucheChance(bn,s,parents[1:],idNodeIDChild,idNodeBNChild)
    def getParents_chanceID(self,decisionNodeID,nodeADevID):
        """Function that returns the parents of a decision node (that is the leaf the branch we want to create)

        Parameters
        ----------
        decisionNodeID : int
            the id of the decision node in the and or graph
        nodeADevID : int
            the id of the decision node in the ID

        Returns
        -------
        list
            list of parents of the decision node
        """        
        if(nodeADevID==None):
            temp=self.ID.parents(decisionNodeID)
            parents_chanceID=[]
            for t in temp:
                if self.ID.isChanceNode(t):
                    parents_chanceID.append(t)
            return parents_chanceID
        else:
            temp=self.ID.parents(decisionNodeID)
            temp2=self.ID.parents(nodeADevID)
            parents_chanceID=[]
            for t in temp:
                if self.ID.isChanceNode(t) and t not in temp2:
                    parents_chanceID.append(t)
            return parents_chanceID
    def isAllDecisionNodeProcessed(self,couches):
        """Function that checks if all the decision nodes are processed

        Parameters
        ----------
        couches : list of list
            list of all the branches in the and or graph

        Returns
        -------
        bool
            true if all the decision nodes are processed, false otherwise
        """        
        for decisionNode,couche in couches.items():
            for decision in couche:
                if(not decision.isProcessed()):
                    return False
        return True
    def findLigneAuDessus(self,ligne):
        """function that allows to find the layer above the layer "ligne" in a branch

        Parameters
        ----------
        ligne : list
            the layer of nodes (chance of decision nodes) for which we wish to find the layer above

        Returns
        -------
        list
            the layer of nodes above
        """        
        parents=[]
        for node in ligne:
                parent=node.getParent()
                if parent not in parents:
                    parents.append(parent)
        return parents
    def findCoucheDeNoeudDeDecision(self,decisionNode,couches):
        """Utility function that allows to find the branch of a certain decision node

        Parameters
        ----------
        decisionNode : decisionNode
            the decision node for which we want to find the branch
        couches : list
            the list of all the branches in the and/or tree

        Returns
        -------
        list or None   
            the branch where the decision node is 
        """        
        for decision,couche in couches.items():
            if decisionNode in couche:
                return couche
    def setVerbose(self,verbose:bool)->None:
        """Function that allows to set the verbose parameter, true will print the trace, false will not

        Parameters
        ----------
        verbose : bool
            the parameter
        """        
        self.verbose=verbose
    def getBNFromID(self,idiag:gum.InfluenceDiagram):
        """Function that gives us the bayesian network for finding posterior probability when 
        doing the backwards inductio, part of the branch and bound

        Parameters
        ----------
        idiag : pyAgrum.InfluenceDiagram
            the ID for which we want the bayesian network

        Returns
        -------
        pyAgrum.BayesNet()
            the bayesian network generated
        """        
        bn=gum.BayesNet()
        for i in idiag.nodes():
            if not idiag.isUtilityNode(i):
                bn.add(idiag.variable(i),i)
        for i in bn.nodes():
            if idiag.isChanceNode(i):
                for j in idiag.parents(i):
                    bn.addArc(j,i)
                bn.cpt(i).fillWith(idiag.cpt(i))
            else:
                bn.cpt(i).fillWith(1).normalize()
        return bn

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
