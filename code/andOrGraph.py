import numpy as np


class orNode():
    def __init__(self, Id, childs):
        """
        Id l'id du orNode
        childs les ids des enfants
        """
        self.Id=Id
        self.childs=dict()
        for child in childs:
            self.childs[child.getNodeID()]=child
        
    def getChilds(self):
        return self.childs
    def getNodeID(self):
        return self.Id
    def addChild(self,child):
        """
        ajoute un enfant avec son identifiant
        """
        self.childs.append(child)

    def getValuation(self):
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
            elif(maxVal<valuation):
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

    def getChilds(self):
        return self.childs

    def getNodeID(self):
        return self.Id
    
    def addChild(self,child,probability):
        """
        ajoute un enfant avec son identifiant
        et sa probabilité associé
        """
        self.childs[child.getNodeID()]=child
        self.probabilities[child]=probability
        if(self.isLeaf):
            self.isLeaf=False
    
    def isLeaf(self):
        return self.isLeaf

    def getUtilityValue(self):
        if(self.isLeaf):
            return self.utilityValue

    def getValuation(self):
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
"""class andOrGraph():
    def __init__(self,ID,ordre):
        self.ID=ID
        self.ordre=ordre
        self.root=None
        
    def initialise():
        d0 = self.ordre[0]
        conditionneur = self.ID.parents(decisionNodes[d0])
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
        """
class andOrGraph():
    def __init__(self,ID,root):
        self.ID=ID
        self.root=root
        self.noeuds=[]
        self.noeudsChance=[] 
        self.noeudsDecision=[]
        self.IDNoeudDecisionAndOr=0
    def getIDNoeudDecisionAndOr(self):
        return self.IDNoeudDecisionAndOr
    def getID(self):
        return self.ID
    def setRoot(self,root):
        self.root=root
    def getRoot(self):
        return self.root
    def addNoeudChance(self,noeud):#id = contexte sous forme de liste
        self.noeudsChance.append(noeud)
        self.noeuds.append(noeud)
    def addNoeudDecision(self,noeud):
        self.noeudsChance.append(noeud)
        self.IDNoeudDecisionAndOr+=1
        self.noeuds.append(noeud)
    def getNoeudChance(self):
        return self.noeudsChance
    def getNoeudDecision(self):
        return self.noeudsDecision
    def getNoeudDecisionAndOr(self,id_andOr):
        for d in self.noeudsDecision:
            if d.getId_andOr()==id_andOr:
                return d
    def getNoeudDecisionIDs(self):
        return [i for i in range(self.IDNoeudDecisionAndOr)]
    def getNoeud(self):
        return self.noeuds
class chanceNode():
    def __init__(self,Id,support,parent,valeurParent):
        self.Id=Id
        self.support=support #le support du noeud
        self.childs=dict() #key = valeur du support, value=enfant
        self.valeur=None
        self.parent=parent
        self.valeurParent=valeurParent
        self.probabilitesPosteriori=dict()#key = valeur du support, value=proba

    def getParent(self):
        return self.parent
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

    def getNodeID(self):
        return self.Id
    
    def addChild(self,valeurSupportPourCetEnfant,child):
        """
        ajoute un enfant avec son identifiant
        """
        self.childs[valeurSupportPourCetEnfant]=child
    def getChilds(self):
        return self.childs
    def setChilds(self,childs):
        self.childs=childs
    def getProbabilitesPosteriori(self):
        return self.probabilitesPosteriori
    def setProbabilitesPosteriori(self,probabilitesPosteriori):
        self.probabilitesPosteriori=probabilitesPosteriori
#parents_chance ce sont les noeuds d'informations qui sont parents dans l'ID du noeud de décision
#parent_decision, c'est le noeud de décision du quel est issue ce noeud de décision dans le graphe ET/OU
#contexte est l'instanciation des parents_chance
class decisionNode():
    def __init__(self,Id,contexte,parent,support,id_andOr):
        self.id_andOr=id_andOr
        self.contexte=contexte
        self.Id=Id
        self.parent=parent
        self.borneSup=dict() #key= domainValue, value=(mean,variance)
        self.enfants=None
        self.evaluation=None #key= domainValue, value=(mean,variance)
        self.support=support
        self.decisionOptimale=None
        self.ValeurDecisionOptimale=None
        self.doNotDevelop=[]
        self.inference=None
    def setInference(self,inference):
        self.inference=inference
    def getInference(self):
        return self.inference
    def getId_andOr(self):
        return self.id_andOr
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
        
    def getNodeID(self):
        return self.Id    
    def addEnfant(self,enfant):
        """
        ajoute un enfant avec son identifiant
        """
        self.enfants.append(enfant)
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

