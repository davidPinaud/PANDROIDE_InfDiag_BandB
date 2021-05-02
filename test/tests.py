from unittest.case import TestCase
from pylab import *
import pyAgrum as gum
import sys
import unittest
import random

#--temporaire--
#TODO: changer l'import de bandbLIMID (il faut faire un projet python)
sys.path.append('/Users/davidpinaud/GitHub/PANDROIDE_InfDiag_BandB/code')
from bandbLIMID import BranchAndBoundLIMIDInference
sys.path.append("/Users/davidpinaud/GitHub/PANDROIDE_InfDiag_BandB/code/minindepset.py")
from minindepset import MinimalDSep,figure1,figure6,ID_Simple_Test

class LimidTestCase(unittest.TestCase):
    def setUpTestFigures(self,graph,src,dst,model=None,pdfname=None):

        dsep = MinimalDSep(graph,model)
        x=src
        y=dst
        return dsep.find(x, y)


    def testFigures_seperating_set(self):
        self.assertTrue(self.setUpTestFigures(*figure1())=={4})
        self.assertTrue(self.setUpTestFigures(*figure6())=={4, 5})
        self.assertTrue(self.setUpTestFigures(*ID_Simple_Test())=={3})



    
    # def test_seperating_set(self):
    #     gen=gum.BNGenerator()
    #     for n in [10,30,50,100]:
    #         rand=random.sample(list(range(130,171)),n)
    #         const=[(rand[i]/100)*n for i in range(10)]
    #         for l in range(10):
    #             bn=gen.generate(n_nodes=n,n_arcs=int(const[l]),n_modmax=4)
    #             #src,dst=npRandom.choice(list(bn.nodes()),replace=False,size=2)
    #             l=random.sample(bn.nodes(),2)
    #             src=l[0]
    #             dst=l[1]
    #             graph=bn.moralizedAncestralGraph({src,dst})
    #             m=MinimalDSep(graph,bn)
    #             separatingSet=m.find(src,dst)
    #             self.assertTrue(bn.isIndependent(src,dst,list(separatingSet)))

        

if __name__ == '__main__':
    unittest.main()