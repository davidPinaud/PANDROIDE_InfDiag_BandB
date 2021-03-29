import numpy as np

def class andOrGraph:
    def __init__(self,ID,ordre):
        self.ID=ID
        self.ordre=ordre
        self.root=None
        
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
def class andNode():
    __init__(self,Id,childs,probabilities,isLeaf,utilityValue):
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
def class sandNode():
    pass