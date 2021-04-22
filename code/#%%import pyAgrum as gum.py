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
nbStage=3
xInitial=3
yInitial=2
ID=createIDRobot(nbStage,xInitial,yInitial,maze)
#gnb.showInfluenceDiagram(ID)
ordre=[]
for i in range(nbStage):
    ordre.append(ID.idFromName("d_"+str(i)))
bnb=BranchAndBoundLIMIDInference(ID,ordre)
#gnb.showInfluenceDiagram(bnb.IDRelaxe)
#%%
bnb.branchAndBound()
# %%
import pyAgrum as gum
import pyAgrum.lib.notebook as gnb
from bandbLIMID import BranchAndBoundLIMIDInference
from exemple_robot import createIDRobot
ID=gum.fastID('D->A->*B->F->$C')
bnb=BranchAndBoundLIMIDInference(ID,[ID.idFromName('B')])
bnb.branchAndBound()
andOrGraph,npCoupe=bnb.getAndOrGraph()
decisions=andOrGraph.getNoeudDecision()
print(len(decisions))
print(npCoupe)
for node in decisions:
    print(node.getContexte())
    print(node.getDecisionOptimale())
    print(node.getValeurDecisionOptimale())
bnb.fromAndORGraphToDiGraph()