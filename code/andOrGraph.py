import numpy as np
class andOrGraph():
    """Class that emulates an And/Or Graph (its really a tree)
    Attributes
    ----------
    ID : pyAgrum.InfluenceDiagram
        The influence diagram we use for the And/Or Graph
    root : andOrGraph.chanceNode
        the root of the And/Or Graph
    noeuds : list of andOrGraph.chanceNode and andOrGraph.decisionNode
        The list of nodes in the graph
    noeudsChance : list of andOrGraph.chanceNode
        The list of andOrGraph.chanceNode in the graph
    noeudsDecision : list of andOrGraph.decisionNode
        The list of andOrGraph.decisionNode in the graph
    IDNoeudDecisionAndOr : int
        Integer that serves to give ids to the decision nodes (different to their influence ids)
    """    
    def __init__(self,ID,root):
        """Class constructor

        Parameters
        ----------
        ID : pyAgrum.InfluenceDiagram
            The influence diagram we use for the And/Or Graph
        root : andOrGraph.chanceNode
            the root of the And/Or Graph
        """        
        self.ID=ID
        self.root=root
        self.noeuds=[]
        self.noeudsChance=[] 
        self.noeudsDecision=[]
        self.IDNoeudAndOr=0
    def getIDNoeudAndOr(self):
        """Getter function for the IDNoeudAndOr attribute

        Returns
        -------
        int
            Integer that serves to give ids to the decision nodes (different to their influence ids)
        """        
        return self.IDNoeudAndOr
    def getID(self):
        """Getter function for the ID attribute

        Returns
        -------
        pyAgrum.InfluenceDiagram
            The influence diagram we use for the And/Or Graph
        """        
        return self.ID
    def setRoot(self,root):
        """Setter function for the root attribute

        Parameters
        ----------
        root : andOrGraph.chanceNode
            the root of the And/Or Graph
        """        
        self.root=root
    def getRoot(self):
        """Getter function for the root attribute

        Returns
        -------
        andOrGraph.chanceNode
            the root of the And/Or Graph
        """        
        return self.root
    def addNoeudChance(self,noeud):#id = contexte sous forme de liste
        """Function that adds a andOrGraph.chanceNode to the And/Or Graph

        Parameters
        ----------
        noeud : andOrGraph.chanceNode 
            the chance node to add
        """        
        self.noeudsChance.append(noeud)
        self.IDNoeudAndOr+=1
        self.noeuds.append(noeud)
    def addNoeudDecision(self,noeud):
        """Function that adds a andOrGraph.decisionNode to the And/Or Graph
        It also sets its And/Or Graph id

        Parameters
        ----------
        noeud : andOrGraph.decisionNode 
            the decision node to add
        """    
        self.noeudsDecision.append(noeud)
        self.IDNoeudAndOr+=1
        self.noeuds.append(noeud)
    def getNoeudChance(self):
        """Getter function for the noeudsChance attribute

        Returns
        -------
        list of andOrGraph.chanceNode
            The list of andOrGraph.chanceNode in the graph
        """        
        return self.noeudsChance
    def getNoeudDecision(self):
        """Getter function for the ID attribute

        Returns
        -------
        pyAgrum.InfluenceDiagram
            The influence diagram we use for the And/Or Graph
        """        
        return self.noeudsDecision
    def getNoeudWithIdAndOr(self,id_andOr):
        """Getter function for that returns a decision node given its And/Or Graph id (not the Influence Diagram one)

        Returns
        -------
        andOrGraph.decisionNode
            the decision node corresponding to the given id
        """        
        for d in self.noeuds:
            if d.getId_andOr()==id_andOr:
                return d
    def getNoeudDecisionAndOrIDs(self):
        """Getter function that returns all the And/Or Graph ids

        Returns
        -------
        list of ints
            The ids of the nodes in the And/Or Graph
        """ 
        id=[]    
        for i in self.noeudsDecision :
            id.append(i.getId_andOr())
        return id
    def getNoeud(self):
        """Getter function that returns all the And/Or Graph nodes

        Returns
        -------
        list of andOrGraph.chanceNode and andOrGraph.decisionNode
            The list of nodes in the graph
        """   
        return self.noeuds
class chanceNode():
    def __init__(self,Id,support,parent,valeurParent,contexte,id_andOr):
        self.Id=Id
        self.support=support #le support du noeud
        self.childs=dict() #key = valeur du support, value=enfant
        self.valeur=None
        self.parent=parent
        self.valeurParent=valeurParent
        self.probabilitiesPosteriori=dict()#key = valeur du support, value=proba
        self.contexte=contexte
        self.id_andOr=id_andOr
    def __eq__(self, other):
        return self.id_andOr==other.getId_andOr()
    def getParent(self):
        return self.parent
    def getId_andOr(self):
        return self.id_andOr
    def setParent(self,parent):
        self.parent=parent
    def getValeurParent(self):
        return self.valeurParent
    def setValeurParent(self,valeurParent):
        self.valeurParent=valeurParent
    def getSupport(self):
        return self.support
    def setSupport(self,support):
        self.support=support
    def getContexte(self):  
        return self.contexte
    def getNodeID(self):
        return self.Id
    def setValeur(self,valeur):
        self.valeur=valeur
    def getValeur(self):
        return self.valeur
    def addChild(self,valeurSupportPourCetEnfant,child):
        """
        ajoute un enfant avec son identifiant
        """
        self.childs[valeurSupportPourCetEnfant]=child
    def getChilds(self):
        return self.childs
    def setChilds(self,childs):
        self.childs=childs
    def getProbabilitiesPosteriori(self):
        return self.probabilitiesPosteriori
    def setProbabilitiesPosteriori(self,probabilitiesPosteriori):
        self.probabilitiesPosteriori=probabilitiesPosteriori
#parents_chance ce sont les noeuds d'informations qui sont parents dans l'ID du noeud de décision
#parent_decision, c'est le noeud de décision du quel est issue ce noeud de décision dans le graphe ET/OU
#contexte est l'instanciation des parents_chance
class decisionNode():
    def __init__(self,Id,contexte,parent,support,id_andOr):
        self.id_andOr=id_andOr
        self.contexte=contexte#key= id du noeud (dans le diagramme d'influence, 
        #possible car on regarde le contexte dans l'ID, pas dans le graphe et/ou !), value=valeur d'instanciation
        self.Id=Id
        self.id_andOr=id_andOr
        self.parent=parent 
        self.borneSup=dict() #key= domainValue, value=(mean,variance)
        self.enfants=dict() #key=domainValue, value=child
        self.evaluation=dict() #key= domainValue, value=(mean,variance)
        self.support=support
        self.decisionOptimale=None
        self.ValeurDecisionOptimale=None
        self.doNotDevelop=[]
        self.inference=None
        self.enfantProcessed=[]
    def __hash__(self):
        return hash(self.id_andOr)
    def __eq__(self, other):
        return self.id_andOr==other.getId_andOr()
    def getParent(self):
        return self.parent
    def getID(self):
        return self.Id
    def setInference(self,inference):
        self.inference=inference
    def getInference(self):
        return self.inference
    def getId_andOr(self):
        return self.id_andOr
    def isProcessed(self):
        return len(self.doNotDevelop)+len(self.evaluation)==len(self.support)
    def getDoNotDevelop(self):
        return self.doNotDevelop
    def addDoNotDevelop(self,domainValue):
        self.doNotDevelop.append(domainValue)
    def getDecisionOptimale(self):
        return self.decisionOptimale
    def setDecisionOptimale(self,decisionOptimale):
        self.decisionOptimale=decisionOptimale
    def getValeurDecisionOptimale(self):
        return self.ValeurDecisionOptimale
    def setValeurDecisionOptimale(self,decisionOptimale):
        self.ValeurDecisionOptimale=decisionOptimale
    def getSupport(self):
        return self.support
    def setSupport(self,support):
        self.support=support
    def getEnfants(self):
        return self.enfants
    def getNodeID(self):
        return self.Id    
    def addEnfant(self,enfant,valeur):
        """
        ajoute un enfant avec son identifiant
        """
        self.enfants[valeur]=enfant
    def addEnfantProcessed(self,enfantID):
        self.enfantProcessed.append(enfantID)
    def getEnfantProcessed(self):
        return self.enfantProcessed
    def setContexte(self,contexte):
        self.contexte=contexte
    def getContexte(self):
        return self.contexte
    def getParent(self):
        return self.parent
    def addBorneSup(self,key,borneSup):
        self.borneSup[key]=borneSup
    def getBorneSup(self):
        return self.borneSup
    def addEvaluation(self,key,evaluation):
        self.evaluation[key]=evaluation
    def getEvaluation(self):
        return self.evaluation

