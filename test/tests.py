from unittest.case import TestCase
from pylab import *
import pyAgrum as gum
import sys
import unittest
from numpy import random
#--temporaire--
#TODO: changer l'import de bandbLIMID (il faut faire un projet python)
sys.path.append('/Users/davidpinaud/GitHub/PANDROIDE_InfDiag_BandB/code')
from bandbLIMID import BranchAndBoundLIMIDInference
sys.path.append("/Users/davidpinaud/GitHub/PANDROIDE_InfDiag_BandB/code/minindepset.py")
from minindepset import MinimalDSep

class LimidTestCase(unittest.TestCase):

   

    
    def test_seperating_set(self):
        gen=gum.BNGenerator()
        for n in [10,30,50,100]:
            rand=random.randint(130,170+1,n)
            const=[rand[i]/100*n for i in range(10)]
            for l in range(10):
                bn=gen.generate(n_nodes=n,n_arcs=int(const[l]),n_modmax=4)
                src,dst=random.choice(range(n),replace=False,size=2)
                graph=bn.moralizedAncestralGraph({src,dst})
                m=MinimalDSep(graph,bn)
                separatingSet=m.find(dst,src)
                self.assertTrue(bn.isIndependent(src,dst,list(separatingSet)))

        

if __name__ == '__main__':
    unittest.main()