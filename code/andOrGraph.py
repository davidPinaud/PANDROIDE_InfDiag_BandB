import numpy as np
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

