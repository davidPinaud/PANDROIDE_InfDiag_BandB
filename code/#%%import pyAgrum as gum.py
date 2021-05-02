#%%import pyAgrum as gum
import pyAgrum.lib.notebook as gnb
from bandbLIMID import BranchAndBoundLIMIDInference
from exemple_robot import createIDRobot


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
#gnb.showInfluenceDiagram(ID)
ordre=[]
for i in range(nbStage):
    ordre.append(ID.idFromName("d_"+str(i)))
bnb=BranchAndBoundLIMIDInference(ID,ordre)

#gnb.sideBySide(*[ID.cpt(i) for i in ID.nodes() if ID.isChanceNode(i)])
#gnb.showInfluenceDiagram(bnb.IDRelaxe)
#%%
bnb.setVerbose(True)
bnb.branchAndBound()
# %%
import pyAgrum as gum
import pyAgrum.lib.notebook as gnb
from bandbLIMID import BranchAndBoundLIMIDInference
from exemple_robot import createIDRobot
ID=gum.fastID('D->E->*K->A->T->*B->F->$C')
bnb=BranchAndBoundLIMIDInference(ID,[ID.idFromName('K'),ID.idFromName('B')])
bnb.branchAndBound()
andOrGraph,npCoupe=bnb.getAndOrGraph()
decisions=andOrGraph.getNoeudDecision()
gnb.sideBySide(ID,bnb.viewAndOrGraph())
gnb.sideBySide(*[ID.cpt(i) for i in ID.nodes() if ID.isChanceNode(i)])
print(len(decisions))
print(npCoupe)
for node in decisions:
    print(node.getContexte())
    print(node.getDecisionOptimale())
    print(node.getValeurDecisionOptimale())

# %%
