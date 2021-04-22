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
#gnb.showInfluenceDiagram(bnb.IDRelaxe)
#%%
bnb.branchAndBound()
# %%
