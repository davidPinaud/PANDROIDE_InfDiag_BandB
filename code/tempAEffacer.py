
#%%
import pyAgrum as gum
import pyAgrum.lib.notebook as gnb
from bandbLIMID import BranchAndBoundLIMIDInference
from exemple_robot import createLIMIDRobot
import numpy as np

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
ID=createLIMIDRobot(nbStage,xInitial,yInitial,maze)
#gnb.showInfluenceDiagram(ID)
ordre=[]
for i in range(nbStage):
    ordre.append(ID.idFromName("d_"+str(i)))

bnb=BranchAndBoundLIMIDInference(ID,ordre,verbose=True)
bnb.branchAndBound()
gnb.show(bnb.viewAndOrGraph())
gnb.show(bnb.viewAndOrGraphNoCuts())
# %%
