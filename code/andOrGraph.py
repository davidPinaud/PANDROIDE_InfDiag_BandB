import numpy as np

class andOrGraph():
    def __init__(self,ID,ordre):
        self.ID=ID
        self.ordre=ordre
        self.root=None
<<<<<<< HEAD
<<<<<<< HEAD

class orNode():
    def __init__(self, Id, childs):
=======
    

def class orNode():
    __init__(self,childs):
>>>>>>> 958c80f047209549b09cdabe71502dc7486c8b34
=======
        
    def fromID(self,ID): 
        sis = []
        # Récupération des noeuds de décision
        for nodeID in ID.nodes():
            if(ID.isDecisionNode(nodeID)):
                # Récupération des SIS de ces noeuds
                sis.append((nodeId, ID.SIS(nodeID,ID)))
         
        childs=orNode()
        for nodeD in sis:
            childs=andNode(childs)
        
        self.root=

def class orNode():
    __init__(self, Id, childs):
>>>>>>> d9506247497093978436ceafb2c1aab98cfd603f
        """
        Id l'id du orNode
        childs les ids des enfants
        """
        self.Id=Id
        self.childs=dict()
        for child in childs:
            self.childs[child.getNodeID()]=child
        
    def getChilds():
        return self.childs
    def getNodeID():
        return self.Id
    def addChild(child):
        """
        ajoute un enfant avec son identifiant
        """
        self.childs.append(child)

    def getValuation():
        """
        return the valuation and the childs from whom it came
        for this orNode
        """
        childValuations=dict()
        for child in self.childs:
            childValuations[child.getNodeID()]=child.getValuation()
        maxVal=None
        maxChild=None
        for childID,valuation in childValuations:
            if(maxVal==None):
                maxVal=valuation
                maxChild=childID
            elif(maxval<valuation):
                maxVal=valuation
                maxChild=childID
        return maxVal,self.childs[maxChild]


        
#Chance node
class andNode():
    def __init__(self,Id,childs,probabilities,isLeaf,utilityValue):
        """
        Id l'id du andNode
        childs les enfants
        probabilities les probablités associés aux arcs vers les enfants (somme à 1)
        """
        self.childs=dict()
        self.probabilities=dict()
        self.Id=Id
        if not isLeaf:
            for child in childs:
                self.childs[child.getNodeID()]=child
            #créer un dictionnaire pour mettre les probabilités des enfants
            #Remplir le dictionnaire
            for child in childs:
                self.probabilities[child.getNodeID()]=child

        self.isLeaf=isLeaf
        if(isLeaf):
            self.utilityValue=utilityValue

    def getChilds():
        return self.childs

    def getNodeID():
        return self.Id
    
    def addChild(child,probability):
        """
        ajoute un enfant avec son identifiant
        et sa probabilité associé
        """
        self.childs[child.getNodeID()]=child
        self.probabilities[child]=probability
        if(self.isLeaf):
            self.isLeaf=False
    
    def isLeaf():
        return self.isLeaf

    def getUtilityValue():
        if(self.isLeaf):
            return self.utilityValue

    def getValuation():
        if(self.isLeaf):
            return self.utilityValue
        else:
            valuation=0
            for child in self.childs:
                valuation+=child.getValuation()*self.probabilities[child.getNodeID()]
            return valuation

#special SAND node
class sandNode():
    pass






# Essai 2 : PB
class andOrGraph():
    def __init__(self,ID,ordre):
        self.ID=ID
        self.ordre=ordre
        self.root=None
        
    def initialise():
        d0 = self.ordre[0]
        conditionneur = self.ID.ancestors(desicionNodes[d0])
        support = support des conditionneurs
        
        self.root = chanceNode(0, conditionneur[0], support[0])
        
        noeud1 = chanceNode(1+len(support[0]), conditionneur[1], support[1])
        self.root.addChild(noeud1)
        
        noeud2 = ...
        
        # Donnerait qqch comme :
        ancienNoeud = noeud1
        cpt = len(support[0])+2
        for i in range(2, len(conditionneur)):
            newNoeud = chanceNode(cpt, conditionneur[i], support[i])
            ancienNoeud.addChild(newNoeud)
            
            cpt+= len(support[i])
            ancienNoeud = newNoeud
            
        # Puis on ajoute les évaluations du noeud de décision en cours
        newNoeud = decisionNode(cpt, d0)
        
        # Calcul des évaluations
        nbD0 = 1
        for i in range(len(support)):
            nbD0 = nbD0 * support[i]
            
        for i in range(nbD0):
            newNoeud.addValue(evaluation)
        ancienNoeud.addChild(newNoeud)
        
class chanceNode():
    def __init__(self,Id,noeud,support):
        self.support=support
        self.noeud=noeud
        self.Id=Id
        self.child=[]

    def getSupport():
        return self.support

    def getNodeID():
        return self.Id
    
    def addChild(child):
        """
        ajoute un enfant avec son identifiant
        """
        self.child.append(child)
        
class decisionNode():
    def __init__(self,Id,noeud):
        self.noeud=noeud
        self.Id=Id
        self.value=[]
        self.child=[]

    def getNodeID():
        return self.Id
    
    def addChild(child):
        """
        ajoute un enfant avec son identifiant
        """
        self.child.append(child)
        
    def addValue(val):
        self.value.append(val)

#Dans bandbLIMID : PB
def branchAndBound():
        # Récupération des noeuds de décision
        decisionNodes = [nodeID for nodeID in self.ID.nodes() if self.ID.isDecisionNode(nodeID)]
        di = 0 #Indice du noeud de décision en cours de traitement
        
        #Construction de l'arbre ET/OU
        conditionneurDi = self.ID.ancestors(desicionNodes[di])
        root = andNode(Id,childs,probabilities,isLeaf,utilityValue) 
        arbre = andOrGraph(ID,ordre,root)
        
        #child c'est (nb de valeurs pour le conditionneur en cours) fois le conditionneur suivant
        for i in range(nbValCond):
            child = andNode(Id,childs,probabilities,isLeaf,utilityValue) 
            root.addChild(child,probability)
            for i in range(nbValCond2):
                child2 = andNode(Id,childs,probabilities,isLeaf,utilityValue) # conditionneur suivant
                child.addChild(child,probability)
                
            etc. pour tous les conditionneurs
            
            A la fin on évalue la borne sup grace à la relaxation
            Puis on prend le meilleur de ces valeurs 
            
            Si il reste des decisionNodes, on fait di=i+1 pour continuer
            Si il n en reste plus, on met à jour la solution courante et on coupe les branches bornesup<solcourante
            
            Si il reste des branches, on reprend sinon on renvoie la meilleure sol (càd solcourante)
    