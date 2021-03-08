from unittest.case import TestCase
import numpy as np
import os
from pylab import *
import matplotlib.pyplot as plt
from IPython.core.display import display,HTML
import math
import pyAgrum as gum
import sys
import unittest

#--temporaire--
#TODO: changer l'import de bandbLIMID (il faut faire un projet python)
sys.path.append('/Users/davidpinaud/GitHub/PANDROIDE_InfDiag_BandB/code')
from bandbLIMID import BranchAndBoundLIMIDInference



class LimidTestCase(unittest.TestCase):

   

    
    def test_SIS(self):
        ID1=gum.fastID("A->*B<-C->V->B->$U<-C")
        ID2=gum.fastID("A->*B<-C->V->B->$U<-C")
        ID3=gum.fastID("A->*B<-C->V->B->$U<-C")
        ID4=gum.fastID("A->*B<-C->V->B->$U<-C")
        ordre1=[self.ID1.idFromName("B")]
        ordre2=[self.ID2.idFromName("B")]
        ordre3=[self.ID3.idFromName("B")]
        ordre4=[self.ID4.idFromName("B")]
        bnb1=BranchAndBoundLIMIDInference(self.ID1,self.ordre1)
        bnb2=BranchAndBoundLIMIDInference(self.ID2,self.ordre2)
        bnb3=BranchAndBoundLIMIDInference(self.ID3,self.ordre3)
        bnb4=BranchAndBoundLIMIDInference(self.ID4,self.ordre4)
        x=1
        y=[]
        self.assertEqual(bnb1.SIS(x),y,'SIS 1 incorrect')
        self.assertEqual(bnb2.SIS(x),y,'SIS 2 incorrect')
        self.assertEqual(bnb3.SIS(x),y,'SIS 3 incorrect')
        self.assertEqual(bnb4.SIS(x),y,'SIS 4 incorrect')

    def test_fromIDToMoralizedAncestral(self):
        x=1
        MoralizedAncestral_digraph1,alphaXid1,BetaYid1=self.bnb1.fromIDToMoralizedAncestral(x)
        MoralizedAncestral_digraph2,alphaXid2,BetaYid2=self.bnb2.fromIDToMoralizedAncestral(x)
        MoralizedAncestral_digraph3,alphaXid3,BetaYid3=self.bnb3.fromIDToMoralizedAncestral(x)
        MoralizedAncestral_digraph4,alphaXid4,BetaYid4=self.bnb4.SIfromIDToMoralizedAncestral(x)

        
        #test???
    def test_graphAuxilliaire(self):
        pass

    """
    def test_MEU(self):
        self.bnb.makeInference()
        self.assertEqual(self.bnb.MEU(), ...,
                         'wrong maximum esperance utility')
    """
if __name__ == '__main__':
    unittest.main()