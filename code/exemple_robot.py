
from pylab import *
import math
import pyAgrum as gum
import pyAgrum.lib.notebook as gnb
import numpy as np
from bandbLIMID import BranchAndBoundLIMIDInference
import time 

def createRandomID(nbDecisionNodes:int,nbChanceNodes:int,nbUtilityNode:int,nbArc:int,nbAppel=0,verbose=False)->gum.InfluenceDiagram:
    """creates a random ID
    Parameters
    ----------
    nbDecisionNodes : int
        number of decision nodes
    nbChanceNodes : int
        number of chance nodes
    nbUtilityNode : int
        number of utility nodes
    nbArc : int
        number of arcsnodes
    Returns
    -------
    gum.InfluenceDiagram
        the random ID
    """
    if(verbose):
        print(f"try n°{nbAppel+1}")
    dagTestCycle=gum.DAG()
    stringID=""
    dec=dict()
    chance=dict()
    utility=dict()
    for i in range(nbDecisionNodes):
        #ID.addDecisionNode(gum.LabelizedVariable(aName=f"d{i}",aDesc="",nbrLabel=np.random.randint(0,6)))
        stringID+=f"*d{i};"
        dec[f'd{i}']=dagTestCycle.addNode()
    for i in range(nbChanceNodes):
        #ID.addChanceNode(gum.LabelizedVariable(aName=f"c{i}",aDesc="",nbrLabel=np.random.randint(0,6)))
        stringID+=f"c{i};"
        chance[f'c{i}']=dagTestCycle.addNode()
    for i in range(nbUtilityNode):
        #ID.addUtilityNode(gum.LabelizedVariable(aName=f"u{i}",aDesc="",nbrLabel=1))
        stringID+=f"$u{i};"
        utility[f'u{i}']=dagTestCycle.addNode()
    for i in range(nbArc):
        debut=time.time()
        if(time.time()-debut>0.000001 and nbAppel<=3):
            return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
        elif(time.time()-debut>0.000001 and nbAppel>3):
            raise Exception("Echec de construction d'ID, veuillez recommencer")
        r=np.random.randint(1,5)
        found=False
        # while(r==0 and not found):
        #     print("1")
        #     print("°")
        #     d1=np.random.randint(0,nbDecisionNodes)
        #     d2=np.random.randint(0,nbDecisionNodes)
        #     if(time.time()-debut>0.000001 and nbAppel<=3):
        #         return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
        #     try:
        #         dagTestCycle.addArc(dec[f"d{d1}"],dec[f"d{d2}"])
        #         stringID+=f"d{d1}->d{d2};"
        #         found=True
        #     except:
        #         found=False
        while(r==1 and not found):
            print("2")
            print("°")
            d=np.random.randint(0,nbDecisionNodes)
            c=np.random.randint(0,nbChanceNodes)
            if(time.time()-debut>0.000001 and nbAppel<=3):
                return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
            try:
                dagTestCycle.addArc(dec[f"d{d}"],chance[f"c{c}"])
                stringID+=f"d{d}->c{c};"
                found=True
            except:
                found=False
        while(r==2 and not found):
            print("3")
            print("°")
            d=np.random.randint(0,nbDecisionNodes)
            c=np.random.randint(0,nbChanceNodes)
            if(time.time()-debut>0.000001 and nbAppel<=3):
                return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
            try:
                dagTestCycle.addArc(chance[f"c{c}"],dec[f"d{d}"])
                stringID+=f"c{c}->d{d};"
                found=True
            except:
                found=False
        while(r==3 and not found):
            print("4")
            print("°")
            c1=np.random.randint(0,nbChanceNodes)
            c2=np.random.randint(0,nbChanceNodes)
            if(time.time()-debut>0.000001 and nbAppel<=3):
                return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
            try:
                dagTestCycle.addArc(chance[f"c{c1}"],chance[f"c{c2}"])
                stringID+=f"c{c1}->c{c2};"
                found=True
            except:
                found=False
        # while(r==4 and not found):
        #     print("5")
        #     print("°")
        #     c=np.random.randint(0,nbChanceNodes)
        #     u=np.random.randint(0,nbUtilityNode)
        #     if(time.time()-debut>0.000001 and nbAppel<=3):
        #         return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
        #     try:
        #         dagTestCycle.addArc(chance[f"c{d}"],utility[f"u{u}"])
        #         stringID+=f"c{c}->u{u};"
        #         found=True
        #     except:
        #         found=False
        while(r==4 and not found):
            print("5")
            print("°")
            d=np.random.randint(0,nbDecisionNodes)
            u=np.random.randint(0,nbUtilityNode)
            if(time.time()-debut>0.000001 and nbAppel<=3):
                return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
            try:
                dagTestCycle.addArc(dec[f"d{d}"],utility[f"u{u}"])
                stringID+=f"d{d}->u{u};"
                found=True
            except:
                found=False
    try:
        ID=gum.fastID(stringID)
        for node in ID.nodes():
            if(ID.isUtilityNode(node) and not ID.parents(node)):
                nodeID=np.random.choice([nodeID for nodeID in ID.nodes() if not ID.isUtilityNode(nodeID)],size=1)
                print("choices",nodeID[0],node,type(nodeID[0]),type(node))
                ID.addArc(int(nodeID[0]),node)
    except:
        if(nbAppel<=3):
            return createRandomID(nbDecisionNodes,nbChanceNodes,nbUtilityNode,nbArc,nbAppel=nbAppel+1)
    
    return ID
    
def createIDRobot(n,xInitial,yInitial,maze):
    """Function that allows to create the ID given as an exemple in the 2013 "solving limited memory influence diagram" paper

    Parameters
    ----------
    n : int
        number of stage in the exemple
    xInitial : int
        the x axis initial position of the robot
    yInitial : int
        the y axis initial position of the robot
    maze : str
        the maze for which we create the example, it chances the values of the CPT

    Returns
    -------
    InfluenceDiagram
        the example ID
    """    
    
    """
    chances contient tous les identifiants des noeuds chance de l'ID, par convention, si l'ID est égal à
    0 mod(6) --> le noeud est un x
    1 mod(6) --> le noeud est un y
    2 mod(6) --> le noeud est un n
    3 mod(6) --> le noeud est un e
    4 mod(6) --> le noeud est un s
    5 mod(6) --> le noeud est un w

    decision contient tous les identifiants des noeuds décisions de l'ID, par convention, si l'ID est égal à 
    6*n+i pour tout i appartenant à 0,...,n-1, le noeud est le noeud décision de la ième étape.
    """

    """
    Méthode permettant de créer le diagramme d'influence de l'exemple du robot vu dans l'article "2013_Solving_Limited_Memory_Influence_Diagrams_Using_BranchAndBound"

    Entrée : 
    n - nombre de stage
    xInitial - coordonnée x initial où on dépose le robot
    yInitial - coordonnée y initial où on dépose le robot
    Sortie :
    ID - le diagramme d'influence correspondant à la modélisation du problème
    """

    #gris est l'ensemble des coordonnées des cases grises
    cases,gris,caseObj,nbLignes,nbColonnes=getCasesAndGris2(maze)
    #listes qui énumère les cases ou on peut faire un pas dans une certaine direction (càd pas de mur dans cette direction quand on est sur cette case)
    casesOuPossibleAllerGauche=[]
    casesOuPossibleAllerHaut=[]
    casesOuPossibleAllerDroite=[]
    casesOuPossibleAllerBas=[]

    #constructions des listes ci-dessus
    for x in range(nbLignes):
        for y in range(nbColonnes):
            if(cases[x,y,0]==0):
                casesOuPossibleAllerGauche.append([x,y])
            if(cases[x,y,1]==0):
                casesOuPossibleAllerHaut.append([x,y])
            if(cases[x,y,2]==0):
                casesOuPossibleAllerDroite.append([x,y])
            if(cases[x,y,3]==0):
                casesOuPossibleAllerBas.append([x,y])
    #création de l'ID
    ID=gum.fastID("")
    #tous les noeuds chances, regroupés selon leur stages (0 étant celui du premier stage)
    chances=np.zeros((n,6))
    #tous les noeuds décisions, celui à l'indice 0 étant celui du premier stage
    decision=np.zeros(n)
   
    for i in range(n):
        #définition des noms, pour eviter les opérations non necessaires
        x=f"x_{i}"
        y=f"y_{i}"
        ns=f"ns_{i}"
        es=f"es_{i}"
        ss=f"ss_{i}"
        ws=f"ws_{i}"
        d=f"d_{i}"

        #Création des noeuds 
        #ajout noeuds position x
        chances[i][0]=int(ID.addChanceNode(gum.LabelizedVariable(x,"",nbLignes),6*i))
        #ajout noeuds position y
        chances[i][1]=int(ID.addChanceNode(gum.LabelizedVariable(y,"",nbColonnes),6*i+1))
        #ajout noeuds capteurs selon coordonnées cardinales
        chances[i][2]=ID.addChanceNode(gum.LabelizedVariable(ns,"",2),6*i+2)
        chances[i][3]=ID.addChanceNode(gum.LabelizedVariable(es,"",2),6*i+2+1)
        chances[i][4]=ID.addChanceNode(gum.LabelizedVariable(ss,"",2),6*i+2+2)
        chances[i][5]=ID.addChanceNode(gum.LabelizedVariable(ws,"",2),6*i+2+3)
        #ajout noeud de décision
        decision[i]=int(ID.addDecisionNode(gum.LabelizedVariable(d,"",5),i+50000))


        

        #Creation des arcs entre x,y et les capteurs de l'étape courante
        ID.addArc(x,y)
        ID.addArc(x,ns)
        ID.addArc(x,es)
        ID.addArc(x,ss)
        ID.addArc(x,ws)
        ID.addArc(y,ns)
        ID.addArc(y,es)
        ID.addArc(y,ss)
        ID.addArc(y,ws)

        #Création des arcs depuis TOUS les noeuds chances des capteurs vers le noeud de décision courant
        #de l'étape
        for stage in range(i+1):
            ID.addArc(int(chances[(stage)][2]),ID.idFromName(d))
            ID.addArc(int(chances[(stage)][3]),ID.idFromName(d))
            ID.addArc(int(chances[(stage)][4]),ID.idFromName(d))
            ID.addArc(int(chances[(stage)][5]),ID.idFromName(d))
        #Création des arcs depuis x_i-1 vers x_i et de y_i-1 vers y_i (seulement à partir de la deuxième étape)
        if(i>0):
            ID.addArc(f"x_{i-1}",y)
            ID.addArc(f"x_{i-1}",x)
            ID.addArc(f"y_{i-1}",y)
            ID.addArc(f"y_{i-1}",x)
            ID.addArc(f"d_{i-1}",f"d_{i}")

            #Création des arcs entre le noeud de décision de la i-1 ème étape vers x_i et y_i
            ID.addArc(f"d_{i-1}",x)
            ID.addArc(f"d_{i-1}",y)


        #ajout potentiels des noeuds chance capteur ns es ss ws, de support {0=pas mur,1=mur}
        for h in range(nbLignes):
            for j in range(nbColonnes):
                if([h,j] in casesOuPossibleAllerHaut):
                    ID.cpt(ns)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(ns)[{x:h,y:j}]=[0,1]
                if([h,j] in casesOuPossibleAllerBas):
                    ID.cpt(ss)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(ss)[{x:h,y:j}]=[0,1]
                if([h,j] in casesOuPossibleAllerDroite):
                    ID.cpt(es)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(es)[{x:h,y:j}]=[0,1]
                if([h,j] in casesOuPossibleAllerGauche):
                    ID.cpt(ws)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(ws)[{x:h,y:j}]=[0,1]
                if [h,j] in gris:
                    ID.cpt(ns)[{x:h,y:j}]=[0,1]
                    ID.cpt(es)[{x:h,y:j}]=[0,1]
                    ID.cpt(ss)[{x:h,y:j}]=[0,1]
                    ID.cpt(ws)[{x:h,y:j}]=[0,1]
        

    """#ajout potentiels des noeuds positions x y au premier stage
        if(i==0):
            ID.cpt(x)[xInitial]=1
            ID.cpt(y)[{x:xInitial,y:yInitial}]=1
    #ajout potentiels des noeuds positions x y aux stages qui ne sont pas le premier stage
        else:
            remplirID(ID,x,fillX,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)
            remplirID(ID,y,fillY,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)"""
    
        

    #Ajout des arcs entre le dernier noeud décision, les derniers noeuds chances x et y avec le noeud utilité
    xn=f"x_{n}"
    yn=f"y_{n}"
    ID.addArc(int(decision[n-1]),ID.addChanceNode(gum.LabelizedVariable(xn,"",nbLignes)))
    ID.addArc(int(decision[n-1]),ID.addChanceNode(gum.LabelizedVariable(yn,"",nbColonnes)))
    ID.addArc(xn,yn)
    ID.addUtilityNode(gum.LabelizedVariable("u","",1))
    ID.addArc(xn,"u")
    ID.addArc(yn,"u")
    ID.addArc(f"x_{n-1}",xn)
    ID.addArc(f"y_{n-1}",xn)
    ID.addArc(f"x_{n-1}",yn)
    ID.addArc(f"y_{n-1}",yn)
    #ajout potentiels des derniers noeuds chances et du noeud d'utilité
    """remplirID(ID,xn,fillX,n,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)
    remplirID(ID,yn,fillY,n,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)
    """
    ID.utility(ID.idFromName("u"))[{f"x_{n}":caseObj[0],f"y_{n}":caseObj[1]}]=1
    l=[]
    for k in range(n):
        x=f"x_{k}"
        y=f"y_{k}"
        l.append(x)
        l.append(y)
    l=l+[xn,yn]
    for node in l:
        for i in ID.cpt(node).loopIn():
            ID.cpt(node).set(i,np.random.rand())
        ID.cpt(node).normalizeAsCPT()
    return ID


def remplirID(ID,NomNoeud,fonctionFill,stage,casesOuPossibleAllerGauche,

    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris):
    
    """
    Méthode qui sert à remplir le tableau de potentiel des noeuds positions x et y aux stages après au premier stage
    Entrée : 
        InfluenceDiagram ID - le diagramme d'influence sur lequel trouver tous les noeuds
        String NomNoeud - le nom du noeud qu'on veut remplir le tableau de potentiel 
        function fonctionFill - la fonction utilisée afin de remplir les cases du tableau
        Integer stage - entier qui identifie le stage courant
    Sortie:
        void
    """
    I=gum.Instantiation(ID.cpt(NomNoeud))
    while not I.end():
        ID.cpt(NomNoeud).set(I,fonctionFill(I,stage,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris))
        I.inc()

def fillX(I,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris):
    valeurXStageDavant,valeurYStageDavant,valeurX,decisionDStageDavant=[I.val(nomNoeud) for nomNoeud in [f"x_{i-1}",f"y_{i-1}",f"x_{i}",f"d_{i-1}"]]
    """
    Méthode qui sert à déterminer quelle probabilité on introduit dans la case d'un certain tableau de potentiel d'un noeud chance correspondant à la position X (abscisse) du robot à un certain stage.
    Entrée :
        Instantiation I - correspond à une certaine case du tableau de potentiel qu'on remplit, on fait des tests dessus afin de savoir quelle                           probabilité donner à cette case.
        Integer i - entier correspondant au stage courant.
    """ 
    if([valeurXStageDavant,valeurYStageDavant] in gris):
        return 0
    if(abs(valeurX-valeurXStageDavant)>1):
        return 0
    #-----------------------    
    if(decisionDStageDavant==0): #decision = gauche
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
            if(valeurX==valeurXStageDavant-1):
                return 0.89+0.01
            if(valeurX==valeurXStageDavant):
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite): #on teste en plus si on peut aller à droite pour savoir si on peut mettre une proba dessus
                return 0.01
        else:
            if(valeurX==valeurXStageDavant-1): #(je sais que c'est de base à 0 mais je garde pour la compréhension du code)
                return 0
            if(valeurX==valeurXStageDavant):
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    #-----------------------             
    if(decisionDStageDavant==1): #decision = haut
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerHaut):
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant):
                return 0.89+0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
        else:
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant): #pas sur sur la proba à mettre 0.89 ou 0.089 ou 0??
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    #-----------------------  
    if(decisionDStageDavant==2): #decision = droite
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant):
                return 0.089
            if(valeurX==valeurXStageDavant+1):
                return 0.01+0.89
        else:
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant): #pas sur sur la proba à mettre 0.89 ou 0.089 ou 0??
                return 0.089
            if(valeurX==valeurXStageDavant+1):
                return 0
    #-----------------------  
    if(decisionDStageDavant==3): #decision = bas
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerBas):
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant):
                return 0.89+0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
        else:
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant): #pas sur sur la proba à mettre 0.89 ou 0.089 ou 0??
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    #-----------------------  
    if(decisionDStageDavant==4): #decision = rester sur place
        if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
        if(valeurX==valeurXStageDavant):
                return 0.89
        if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    return 0





def fillY(I,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris):
    valeurXStageDavant,valeurYStageDavant,valeurX,valeurY,decisionDStageDavant=[I.val(nomNoeud) for nomNoeud in [f"x_{i-1}",f"y_{i-1}",f"x_{i}",f"y_{i}",f"d_{i-1}"]]
    """
    Méthode qui sert à déterminer quelle probabilité on introduit dans la case d'un certain tableau de potentiel d'un noeud chance correspondant à la position Y (ordonnée) du robot à un certain stage.
    Entrée :
        Instantiation I - correspond à une certaine case du tableau de potentiel qu'on remplit, on fait des tests dessus afin de savoir quelle                           probabilité donner à cette case.
        Integer i - entier correspondant au stage courant.
    """ 
    if([valeurXStageDavant,valeurYStageDavant] in gris):
        return 0
    if(abs(valeurX-valeurXStageDavant)>1 or abs(valeurY-valeurYStageDavant)>1):
        return 0
    #-----------------------  
    if(decisionDStageDavant==0): #decision = gauche
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
            if(valeurX==valeurXStageDavant): #X n'a pas bougé
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.089
                if(valeurY==valeurYStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                    return 0.001
            if(valeurX==valeurXStageDavant-1): #X a fait un pas à gauche
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.89
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu (on regarde bien valeurX pas valeurXStageDavant car X a bougé)
                    return 0.001
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite): #X fait pas à droite
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 1-0.001
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu 
                    return 0.001
    #-----------------------  
    if(decisionDStageDavant==1): #decision = haut
        if([valeurX,valeurYStageDavant] in casesOuPossibleAllerHaut): #ON REGARDE DIRECTEMENT VALEURX
            if(valeurY==valeurYStageDavant-1):#Y a bougé en haut
                return 0.89
            if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                return 0.089
            if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                return 0.001
    #-----------------------  
    if(decisionDStageDavant==2): #decision = droit
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
            if(valeurX==valeurXStageDavant): #X n'a pas bougé
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.089
                if(valeurY==valeurYStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                    return 0.001
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche): #X fait pas à gauche
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 1-0.001
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu (on regarde bien valeurX pas valeurXStageDavant car X a bougé)
                    return 0.001
            if(valeurX==valeurXStageDavant+1 ): #X fait pas à droite
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.89
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu 
                    return 0.001
    #-----------------------  
    if(decisionDStageDavant==3): #decision = bas
        if([valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):
            if(valeurY==valeurYStageDavant+1):#Y a bougé en bas
                return 0.89
            if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                return 0.089
            if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                return 0.001
    #-----------------------  
    if(decisionDStageDavant==4): #decision = rester sur place
        if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):
            return 0.001
    return 0
def getCasesAndGris2(maze):
    """
    Fonction qui retourne deux tableau :
    gris : tableau de tableau de taille deux qui est l'ensemble des coordonnées des cases grisées
    cases : tableau de 3 dimensions qui stocke, pour chaque direction cardinale, pour chaque case, si on peut faire un pas dans cette 
            direction (c'est à dire qu'il n'y pas de mur) 
            convention : cases[x,y,i]=0 si il n'y a pas de mur dans la direction i quand on est dans la case x,y et cases[x,y,i]=1 sinon. i                appartient à [0,1,2,3] qui correspondent à ouest,nord,est,surd respectivement.
    """
    nbLignes=len(maze)
    nbColonnes=len(maze[0])
    cases=np.zeros((nbLignes,nbColonnes,4)) #cases est qui stocke, selon les directions, si on peut faire le pas dans la direction ou non (0 oui, 1 non)
    gris=[]
    for ligne in range(nbLignes):
        cases[ligne,0,0]=1#quand on est sur la premiere colonne, on ne peut pas aller a gauche
        cases[ligne,nbColonnes-1,2]=1#quand on est sur la deniere colonne, on ne peut pas aller a droite
        for colonne in range(nbColonnes):
            cases[0,colonne,1]=1#quand on est sur la premiere ligne, on ne peut pas monter
            cases[nbLignes-1,colonne,3]=1#quand on est sur la derniere ligne, on ne peut pas descendre
            if(maze[ligne][colonne]=="|" or maze[ligne][colonne]=="-"):
                gris.append([ligne,colonne])
                cases[ligne,colonne,0]=1#si on est dans un mur, on peut aller nulle part
                cases[ligne,colonne,1]=1
                cases[ligne,colonne,2]=1
                cases[ligne,colonne,3]=1
                if colonne>0 :
                    cases[ligne,colonne-1,2]=1 # on regarde à droite (la cases[ligne,colonne-1] est à gauche de maze[ligne][colonne] )
                if ligne<nbLignes-1 :
                    cases[ligne+1,colonne,1]=1 #haut
                if ligne>0 :
                    cases[ligne-1,colonne,3]=1 #bas
                if colonne<nbColonnes-1 :
                    cases[ligne,colonne+1,0]=1 #gauche
            elif maze[ligne][colonne]=="$" :
                caseObj=[ligne,colonne]
    return cases,gris,caseObj,nbLignes,nbColonnes

#--Code pour créer un labyrinthe, calculer la relaxation et les afficher dans un notebook 
# maze=["---------",
#       "--     --",
#       "-  - -  -",
#       "-- - - --",
#       "-  - - $-",
#       "--     --",
#       "---------"]
# nbStage=4
# xInitial=3
# yInitial=2
# ID=createIDRobot(nbStage,xInitial,yInitial,maze)
# gnb.showInfluenceDiagram(ID)
# ordre=[]
# for i in range(nbStage):
#     ordre.append(ID.idFromName("d_"+str(i)))
# bnb=BranchAndBoundLIMIDInference(ID,ordre)
#gnb.showInfluenceDiagram(bnb.IDRelaxe)

#Fonctions pour calculer taille+temps
def run():
    xInitial = 7
    yInitial = 4
    for level in range(2, 5):
        robot = createIDRobot(level, 2, 2,maze)
        start = time.time()
        ie = gum.ShaferShenoyLIMIDInference(robot)
        mid = time.time()
        ie.makeInference()
        stop = time.time()
        print(f"{level} : {mid-start:10.3f}s - {stop-mid:10.3f}s")


def human_readable(n):
    def div1024(x): return x//1024, x % 1024
    res = ""

    for s in ["o", "Ko", "Mo", "Go"]:
        n, r = div1024(n)
        if r > 0:
            res = f"{r}{s} {res}"
        if n == 0:
            return res

    return f"{n}To {res}"


def nbParamInClique(model, jt, n):
    nb = 8  # size of python's float
    for i in jt.clique(n):
        nb *= model.variable(i).domainSize()
    return nb


def simule():
    xInitial = 7
    yInitial = 4
    timeInf=[]
    timeJonc=[]
    largeurArbre=[]
    tailleMem=[]
    for level in range(2, 11):
        robot = createIDRobot(level, 2, 2,maze)

        start = time.time()
        ie = gum.ShaferShenoyLIMIDInference(robot)

        mid = time.time()
        jt = ie.junctionTree()
        maxtw = max([len(jt.clique(n)) for n in jt.nodes()])
        maxsize = max([nbParamInClique(robot, jt, n) for n in jt.nodes()])

        stop = time.time()
        timeInf.append(mid-start)
        timeJonc.append(stop-mid)
        largeurArbre.append(maxtw)
        tailleMem.append(human_readable(maxsize))
        print(f"{level} : {mid-start:7.3f}s - {stop-mid:7.3f}s - treewidth={maxtw} - size= {human_readable(maxsize)}")
    return timeInf,timeJonc,largeurArbre,tailleMem

maze=["---------",
      "--     --",
      "-  - -  -",
      "-- - - --",
      "-  - - $-",
      "--     --",
      "---------"]

nbStage=2
xInitial=3
yInitial=2
ID=createIDRobot(nbStage,xInitial,yInitial,maze)




def createLIMIDRobot(n,xInitial,yInitial,maze):
    
    """
    permet de créer l'ID relaxé sans calculer les SIS

    chances contient tous les identifiants des noeuds chance de l'ID, par convention, si l'ID est égal à
    0 mod(6) --> le noeud est un x
    1 mod(6) --> le noeud est un y
    2 mod(6) --> le noeud est un n
    3 mod(6) --> le noeud est un e
    4 mod(6) --> le noeud est un s
    5 mod(6) --> le noeud est un w

    decision contient tous les identifiants des noeuds décisions de l'ID, par convention, si l'ID est égal à 
    6*n+i pour tout i appartenant à 0,...,n-1, le noeud est le noeud décision de la ième étape.
    """

    """
    Méthode permettant de créer le diagramme d'influence de l'exemple du robot vu dans l'article "2013_Solving_Limited_Memory_Influence_Diagrams_Using_BranchAndBound"

    Entrée : 
    n - nombre de stage
    xInitial - coordonnée x initial où on dépose le robot
    yInitial - coordonnée y initial où on dépose le robot
    Sortie :
    ID - le diagramme d'influence correspondant à la modélisation du problème
    """

    #gris est l'ensemble des coordonnées des cases grises
    cases,gris,caseObj,nbLignes,nbColonnes=getCasesAndGris2(maze)
    #listes qui énumère les cases ou on peut faire un pas dans une certaine direction (càd pas de mur dans cette direction quand on est sur cette case)
    casesOuPossibleAllerGauche=[]
    casesOuPossibleAllerHaut=[]
    casesOuPossibleAllerDroite=[]
    casesOuPossibleAllerBas=[]

    #constructions des listes ci-dessus
    for x in range(nbLignes):
        for y in range(nbColonnes):
            if(cases[x,y,0]==0):
                casesOuPossibleAllerGauche.append([x,y])
            if(cases[x,y,1]==0):
                casesOuPossibleAllerHaut.append([x,y])
            if(cases[x,y,2]==0):
                casesOuPossibleAllerDroite.append([x,y])
            if(cases[x,y,3]==0):
                casesOuPossibleAllerBas.append([x,y])
    #création de l'ID
    ID=gum.fastID("")
    #tous les noeuds chances, regroupés selon leur stages (0 étant celui du premier stage)
    chances=np.zeros((n,6))
    #tous les noeuds décisions, celui à l'indice 0 étant celui du premier stage
    decision=np.zeros(n)
   
    for i in range(n):
        #définition des noms, pour eviter les opérations non necessaires
        x=f"x_{i}"
        y=f"y_{i}"
        ns=f"ns_{i}"
        es=f"es_{i}"
        ss=f"ss_{i}"
        ws=f"ws_{i}"
        d=f"d_{i}"

        #Création des noeuds 
        #ajout noeuds position x
        chances[i][0]=int(ID.addChanceNode(gum.LabelizedVariable(x,"",nbLignes),6*i))
        #ajout noeuds position y
        chances[i][1]=int(ID.addChanceNode(gum.LabelizedVariable(y,"",nbColonnes),6*i+1))
        #ajout noeuds capteurs selon coordonnées cardinales
        chances[i][2]=ID.addChanceNode(gum.LabelizedVariable(ns,"",2),6*i+2)
        chances[i][3]=ID.addChanceNode(gum.LabelizedVariable(es,"",2),6*i+2+1)
        chances[i][4]=ID.addChanceNode(gum.LabelizedVariable(ss,"",2),6*i+2+2)
        chances[i][5]=ID.addChanceNode(gum.LabelizedVariable(ws,"",2),6*i+2+3)
        #ajout noeud de décision
        decision[i]=int(ID.addDecisionNode(gum.LabelizedVariable(d,"",5),i+50000))


        

        #Creation des arcs entre x,y et les capteurs de l'étape courante
        ID.addArc(x,y)
        ID.addArc(x,ns)
        ID.addArc(x,es)
        ID.addArc(x,ss)
        ID.addArc(x,ws)
        ID.addArc(y,ns)
        ID.addArc(y,es)
        ID.addArc(y,ss)
        ID.addArc(y,ws)

        #Création des arcs depuis TOUS les noeuds chances des capteurs vers le noeud de décision courant
        #de l'étape
        stage=i
        ID.addArc(int(chances[(stage)][2]),ID.idFromName(d))
        ID.addArc(int(chances[(stage)][3]),ID.idFromName(d))
        ID.addArc(int(chances[(stage)][4]),ID.idFromName(d))
        ID.addArc(int(chances[(stage)][5]),ID.idFromName(d))
        #Création des arcs depuis x_i-1 vers x_i et de y_i-1 vers y_i (seulement à partir de la deuxième étape)
        if(i>0):
            ID.addArc(f"x_{i-1}",y)
            ID.addArc(f"x_{i-1}",x)
            ID.addArc(f"y_{i-1}",y)
            ID.addArc(f"y_{i-1}",x)
            #ID.addArc(f"d_{i-1}",f"d_{i}")

            #Création des arcs entre le noeud de décision de la i-1 ème étape vers x_i et y_i
            ID.addArc(f"d_{i-1}",x)
            ID.addArc(f"d_{i-1}",y)


        #ajout potentiels des noeuds chance capteur ns es ss ws, de support {0=pas mur,1=mur}
        for h in range(nbLignes):
            for j in range(nbColonnes):
                if([h,j] in casesOuPossibleAllerHaut):
                    ID.cpt(ns)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(ns)[{x:h,y:j}]=[0,1]
                if([h,j] in casesOuPossibleAllerBas):
                    ID.cpt(ss)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(ss)[{x:h,y:j}]=[0,1]
                if([h,j] in casesOuPossibleAllerDroite):
                    ID.cpt(es)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(es)[{x:h,y:j}]=[0,1]
                if([h,j] in casesOuPossibleAllerGauche):
                    ID.cpt(ws)[{x:h,y:j}]=[1,0]
                else:
                    ID.cpt(ws)[{x:h,y:j}]=[0,1]
                if [h,j] in gris:
                    ID.cpt(ns)[{x:h,y:j}]=[0,1]
                    ID.cpt(es)[{x:h,y:j}]=[0,1]
                    ID.cpt(ss)[{x:h,y:j}]=[0,1]
                    ID.cpt(ws)[{x:h,y:j}]=[0,1]
        

    """#ajout potentiels des noeuds positions x y au premier stage
        if(i==0):
            ID.cpt(x)[xInitial]=1
            ID.cpt(y)[{x:xInitial,y:yInitial}]=1
    #ajout potentiels des noeuds positions x y aux stages qui ne sont pas le premier stage
        else:
            remplirID(ID,x,fillX,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)
            remplirID(ID,y,fillY,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)"""

    #Ajout des arcs entre le dernier noeud décision, les derniers noeuds chances x et y avec le noeud utilité
    xn=f"x_{n}"
    yn=f"y_{n}"
    ID.addArc(int(decision[n-1]),ID.addChanceNode(gum.LabelizedVariable(xn,"",nbLignes)))
    ID.addArc(int(decision[n-1]),ID.addChanceNode(gum.LabelizedVariable(yn,"",nbColonnes)))
    ID.addArc(xn,yn)
    ID.addUtilityNode(gum.LabelizedVariable("u","",1))
    ID.addArc(xn,"u")
    ID.addArc(yn,"u")
    ID.addArc(f"x_{n-1}",xn)
    ID.addArc(f"y_{n-1}",xn)
    ID.addArc(f"x_{n-1}",yn)
    ID.addArc(f"y_{n-1}",yn)
    #ajout potentiels des derniers noeuds chances et du noeud d'utilité
    """remplirID(ID,xn,fillX,n,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)
    remplirID(ID,yn,fillY,n,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris)"""
    l=[]
    ID.utility(ID.idFromName("u"))[{f"x_{n}":caseObj[0],f"y_{n}":caseObj[1]}]=1
    for k in range(n):
        x=f"x_{k}"
        y=f"y_{k}"
        l.append(x)
        l.append(y)
    l=l+[xn,yn]
    for node in l:
        for i in ID.cpt(node).loopIn():
            ID.cpt(node).set(i,np.random.rand())
        ID.cpt(node).normalizeAsCPT()
    return ID


def remplirID(ID,NomNoeud,fonctionFill,stage,casesOuPossibleAllerGauche,

    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris):
    I=gum.Instantiation(ID.cpt(NomNoeud))
    """
    Méthode qui sert à remplir le tableau de potentiel des noeuds positions x et y aux stages après au premier stage
    Entrée : 
        InfluenceDiagram ID - le diagramme d'influence sur lequel trouver tous les noeuds
        String NomNoeud - le nom du noeud qu'on veut remplir le tableau de potentiel 
        function fonctionFill - la fonction utilisée afin de remplir les cases du tableau
        Integer stage - entier qui identifie le stage courant
    Sortie:
        void
    """
    while not I.end():
        ID.cpt(NomNoeud).set(I,fonctionFill(I,stage,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris))
        I.inc()

def fillX(I,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris):
    valeurXStageDavant,valeurYStageDavant,valeurX,decisionDStageDavant=[I.val(nomNoeud) for nomNoeud in [f"x_{i-1}",f"y_{i-1}",f"x_{i}",f"d_{i-1}"]]
    """
    Méthode qui sert à déterminer quelle probabilité on introduit dans la case d'un certain tableau de potentiel d'un noeud chance correspondant à la position X (abscisse) du robot à un certain stage.
    Entrée :
        Instantiation I - correspond à une certaine case du tableau de potentiel qu'on remplit, on fait des tests dessus afin de savoir quelle                           probabilité donner à cette case.
        Integer i - entier correspondant au stage courant.
    """ 
    if([valeurXStageDavant,valeurYStageDavant] in gris):
        return 0
    if(abs(valeurX-valeurXStageDavant)>1):
        return 0
    #-----------------------    
    if(decisionDStageDavant==0): #decision = gauche
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
            if(valeurX==valeurXStageDavant-1):
                return 0.89+0.01
            if(valeurX==valeurXStageDavant):
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite): #on teste en plus si on peut aller à droite pour savoir si on peut mettre une proba dessus
                return 0.01
        else:
            if(valeurX==valeurXStageDavant-1): #(je sais que c'est de base à 0 mais je garde pour la compréhension du code)
                return 0
            if(valeurX==valeurXStageDavant):
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    #-----------------------             
    if(decisionDStageDavant==1): #decision = haut
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerHaut):
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant):
                return 0.89+0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
        else:
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant): #pas sur sur la proba à mettre 0.89 ou 0.089 ou 0??
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    #-----------------------  
    if(decisionDStageDavant==2): #decision = droite
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant):
                return 0.089
            if(valeurX==valeurXStageDavant+1):
                return 0.01+0.89
        else:
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant): #pas sur sur la proba à mettre 0.89 ou 0.089 ou 0??
                return 0.089
            if(valeurX==valeurXStageDavant+1):
                return 0
    #-----------------------  
    if(decisionDStageDavant==3): #decision = bas
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerBas):
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant):
                return 0.89+0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
        else:
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
            if(valeurX==valeurXStageDavant): #pas sur sur la proba à mettre 0.89 ou 0.089 ou 0??
                return 0.089
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    #-----------------------  
    if(decisionDStageDavant==4): #decision = rester sur place
        if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
                return 0.01
        if(valeurX==valeurXStageDavant):
                return 0.89
        if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
                return 0.01
    return 0





def fillY(I,i,casesOuPossibleAllerGauche,
    casesOuPossibleAllerHaut,
    casesOuPossibleAllerDroite,
    casesOuPossibleAllerBas,gris):
    valeurXStageDavant,valeurYStageDavant,valeurX,valeurY,decisionDStageDavant=[I.val(nomNoeud) for nomNoeud in [f"x_{i-1}",f"y_{i-1}",f"x_{i}",f"y_{i}",f"d_{i-1}"]]
    """
    Méthode qui sert à déterminer quelle probabilité on introduit dans la case d'un certain tableau de potentiel d'un noeud chance correspondant à la position Y (ordonnée) du robot à un certain stage.
    Entrée :
        Instantiation I - correspond à une certaine case du tableau de potentiel qu'on remplit, on fait des tests dessus afin de savoir quelle                           probabilité donner à cette case.
        Integer i - entier correspondant au stage courant.
    """ 
    if([valeurXStageDavant,valeurYStageDavant] in gris):
        return 0
    if(abs(valeurX-valeurXStageDavant)>1 or abs(valeurY-valeurYStageDavant)>1):
        return 0
    #-----------------------  
    if(decisionDStageDavant==0): #decision = gauche
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche):
            if(valeurX==valeurXStageDavant): #X n'a pas bougé
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.089
                if(valeurY==valeurYStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                    return 0.001
            if(valeurX==valeurXStageDavant-1): #X a fait un pas à gauche
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.89
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu (on regarde bien valeurX pas valeurXStageDavant car X a bougé)
                    return 0.001
            if(valeurX==valeurXStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite): #X fait pas à droite
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 1-0.001
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu 
                    return 0.001
    #-----------------------  
    if(decisionDStageDavant==1): #decision = haut
        if([valeurX,valeurYStageDavant] in casesOuPossibleAllerHaut): #ON REGARDE DIRECTEMENT VALEURX
            if(valeurY==valeurYStageDavant-1):#Y a bougé en haut
                return 0.89
            if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                return 0.089
            if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                return 0.001
    #-----------------------  
    if(decisionDStageDavant==2): #decision = droit
        if([valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerDroite):
            if(valeurX==valeurXStageDavant): #X n'a pas bougé
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.089
                if(valeurY==valeurYStageDavant+1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                    return 0.001
            if(valeurX==valeurXStageDavant-1 and [valeurXStageDavant,valeurYStageDavant] in casesOuPossibleAllerGauche): #X fait pas à gauche
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 1-0.001
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu (on regarde bien valeurX pas valeurXStageDavant car X a bougé)
                    return 0.001
            if(valeurX==valeurXStageDavant+1 ): #X fait pas à droite
                if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                    return 0.89
                if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu 
                    return 0.001
    #-----------------------  
    if(decisionDStageDavant==3): #decision = bas
        if([valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):
            if(valeurY==valeurYStageDavant+1):#Y a bougé en bas
                return 0.89
            if(valeurY==valeurYStageDavant):#Y n'a pas bougé
                return 0.089
            if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):#Y a descendu
                return 0.001
    #-----------------------  
    if(decisionDStageDavant==4): #decision = rester sur place
        if(valeurY==valeurYStageDavant+1 and [valeurX,valeurYStageDavant] in casesOuPossibleAllerBas):
            return 0.001
    return 0
def getCasesAndGris2(maze):
    """
    Fonction qui retourne deux tableau :
    gris : tableau de tableau de taille deux qui est l'ensemble des coordonnées des cases grisées
    cases : tableau de 3 dimensions qui stocke, pour chaque direction cardinale, pour chaque case, si on peut faire un pas dans cette 
            direction (c'est à dire qu'il n'y pas de mur) 
            convention : cases[x,y,i]=0 si il n'y a pas de mur dans la direction i quand on est dans la case x,y et cases[x,y,i]=1 sinon. i                appartient à [0,1,2,3] qui correspondent à ouest,nord,est,surd respectivement.
    """
    nbLignes=len(maze)
    nbColonnes=len(maze[0])
    cases=np.zeros((nbLignes,nbColonnes,4)) #cases est qui stocke, selon les directions, si on peut faire le pas dans la direction ou non (0 oui, 1 non)
    gris=[]
    for ligne in range(nbLignes):
        cases[ligne,0,0]=1#quand on est sur la premiere colonne, on ne peut pas aller a gauche
        cases[ligne,nbColonnes-1,2]=1#quand on est sur la deniere colonne, on ne peut pas aller a droite
        for colonne in range(nbColonnes):
            cases[0,colonne,1]=1#quand on est sur la premiere ligne, on ne peut pas monter
            cases[nbLignes-1,colonne,3]=1#quand on est sur la derniere ligne, on ne peut pas descendre
            if(maze[ligne][colonne]=="|" or maze[ligne][colonne]=="-"):
                gris.append([ligne,colonne])
                cases[ligne,colonne,0]=1#si on est dans un mur, on peut aller nulle part
                cases[ligne,colonne,1]=1
                cases[ligne,colonne,2]=1
                cases[ligne,colonne,3]=1
                if colonne>0 :
                    cases[ligne,colonne-1,2]=1 # on regarde à droite (la cases[ligne,colonne-1] est à gauche de maze[ligne][colonne] )
                if ligne<nbLignes-1 :
                    cases[ligne+1,colonne,1]=1 #haut
                if ligne>0 :
                    cases[ligne-1,colonne,3]=1 #bas
                if colonne<nbColonnes-1 :
                    cases[ligne,colonne+1,0]=1 #gauche
            elif maze[ligne][colonne]=="$" :
                caseObj=[ligne,colonne]
    return cases,gris,caseObj,nbLignes,nbColonnes