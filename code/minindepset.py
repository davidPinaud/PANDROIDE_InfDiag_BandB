from enum import Enum
from queue import Queue

import pydotplus as dot

import pyAgrum as gum


class NodeStates(Enum):
  SCANNED = 1
  UNSCANNED = 2
  UNLABELLED = 3


class NodeProperty:
  def __init__(self):
    self._label_p = None
    self._label_n = None
    self._state = NodeStates.UNLABELLED
    self._in = False

  def hasPLabel(self):
    return self._label_p is not None

  def getPLabel(self):
    return self._label_p

  def setPLabel(self, l):
    self._label_p = l

  def hasNLabel(self):
    return self._label_n is not None

  def getNLabel(self):
    return self._label_n

  def setNLabel(self, l):
    self._label_n = l

  def getState(self) -> NodeStates:
    return self._state

  def setState(self, st: NodeStates):
    self._state = st

  def getIn(self) -> bool:
    return self._in

  def setIn(self, b: bool):
    self._in = b

  def clearLabels(self):
    self.setPLabel(None)
    self.setNLabel(None)
    self._state = NodeStates.UNLABELLED 

  def todot(self, num: int, model=None, x=None, y=None):
    if num == x:
      color = "green"
    elif num == y:
      color = "red"
    else:
      color = "yellow"

    if model is None:
      lab = str(num)
    else:
      lab = f"{num}:{model.variable(num).name()}"

    res = f'    "{num}" [label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD colspan="3" BGCOLOR="{color}">{lab}</TD></TR><TR><TD BGCOLOR="burlywood">'

    if self.hasPLabel():
      res += f'p:{self.getPLabel()}'

    res += f'</TD><TD>{str(self.getState()).replace("NodeStates.", "").lower()}</TD><TD BGCOLOR="burlywood">'

    if self.hasNLabel():
      res += f'n:{self.getNLabel()}'

    res += '</TD></TR></TABLE>>];\n'

    return res


class EdgeProperty:
  def __init__(self):
    self._marked = False
    self._dir = None

  def isMarked(self) -> bool:
    return self._marked

  def setMarked(self, b: bool):
    self._marked = b
    if(not b):
      self.setDir(None)

  def getDir(self):
    return self._dir

  def setDir(self, d):
    self._dir = d

  def todot(self, name: str):
    res = f'    "{name}" [fontsize=8,label=<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0"><TR><TD>'

    if self._marked:
      res += "X"

    res += "</TD><TD>"

    if self._dir is not None:
      res += str(self._dir)

    res += "</TD></TR></TABLE>>];\n"

    return res


class MinimalDSep:
  def __init__(self, graph: gum.UndiGraph, model=None):
    """

    :param graph:
    :param model: used to find name of nodes
    """
    self.graph = graph
    self.model = model

    self.nProp = dict()
    self.eProp = dict()

    self.initProperties()

  def initProperties(self):
    for n in self.graph.nodes():
      self.nProp[n] = NodeProperty()
      for p in self.graph.neighbours(n):
        if p < n:
          self.eProp[p, n] = EdgeProperty()

  def prop(self, x: int, y: int = None):
    """
    get the right property

    :param x: nodeId
    :param y: nodeId
    :return: the corresponding NodeProperty for x (if y is None) or EdgeProperty for x,y
    """
    if y is None:
      return self.nProp[x]
    else:
      return self.eProp[min(x, y), max(x, y)]

  def clearLabels(self):
    for n in self.graph.nodes():
      self.prop(n).clearLabels()

  def todot(self, x=None, y=None):
    s = "graph {\n  node [shape=plain,margin=0,fontsize=8,color=grey];\n  edge [color=blue];\n\n"
    for i in self.graph.nodes():
      s += self.prop(i).todot(i, self.model, x, y)
    s += "\n"

    for i in self.graph.nodes():
      for j in self.graph.neighbours(i):
        if i < j:
          s += self.prop(i, j).todot(f"{i}_{j}")
    s += "\n"

    for i in self.graph.nodes():
      for j in self.graph.neighbours(i):
        if i < j:
          s += f'    "{i}"--"{i}_{j}"--"{j}";\n'

    s += "}"
    return s

  def find_fsearch(self, u: int, q: Queue):
    for v in self.graph.neighbours(u):
      if self.prop(v).getState() == NodeStates.UNLABELLED:
        if not self.prop(u, v).isMarked():
          self.prop(v).setPLabel(u)
          self.prop(v).setState(NodeStates.UNSCANNED)
          q.put(v)

  def find_bsearch(self, u: int, q: Queue):
    for t in self.graph.neighbours(u):
      if self.prop(u, t).isMarked() and self.prop(u, t).getDir() == (t, u):
        if not self.prop(t).hasNLabel():
          self.prop(t).setNLabel(u)
          q.put(t)
        if self.prop(u).getState() == NodeStates.SCANNED:
          self.prop(u).setState(NodeStates.UNSCANNED)
          q.put(t)
        break  # such t is unique

  def find_forward_procedure(self, q: Queue, x: int):
    """
    do the step2
    :param q: the queue
    :param x: the target
    """
    while not q.empty():
      u = q.get()
      # step 2.1
      if not self.prop(u).getIn():
        self.find_fsearch(u, q)
      else:
        # step 2.2
        if not self.prop(u).hasNLabel():
          self.find_bsearch(u,q)
        # step 2.3
        else:
          self.find_fsearch(u,q)
          self.find_bsearch(u,q)
      self.prop(u).setState(NodeStates.SCANNED)

      if self.prop(x).getState() != NodeStates.UNLABELLED:
        break

  def find_backward_procedure(self, x: int, y: int):
    u = w = x
    while True:
      z = None
      if self.prop(u).hasPLabel():
        if not self.prop(u).hasNLabel():
          # step 5.1
          z = self.prop(u).getPLabel()
          self.prop(u, z).setMarked(True)
          self.prop(u, z).setDir((z, u))
          if z != y:
            self.prop(z).setIn(True)
        else:
          # step 5.3
          if u == self.prop(w).getNLabel():
            z = self.prop(u).getPLabel()
            self.prop(u, z).setMarked(True)
            self.prop(u, z).setDir((z, u))
            if z != y:
              self.prop(z).setIn(True)
          # step 5.4
          if u == self.prop(w).getPLabel():
            z = self.prop(u).getNLabel()
            self.prop(u, z).setMarked(False)
      else:
        # step 5.2
        if self.prop(u).hasNLabel():
          z = self.prop(u).getNLabel()
          self.prop(u, z).setMarked(False)
          if self.prop(z).hasNLabel() and not self.prop(z).hasPLabel():
            self.prop(z).setIn(False)

      # step 6
      if z != y:
        if z is None:
          raise NotImplementedError("The algo should never come to this point ?")
        w = u
        u = z
      else:
        return

  def find_build_finalset(self, y: int):
    # step 7 (unfinished)
    res = set()
    for u in self.graph.neighbours(y):
      if self.prop(y, u).isMarked():
        if not self.prop(u).hasNLabel() and not self.prop(u).hasPLabel():
          if self.model is not None:
            res.add(self.model.variable(u).name())
          else:
            res.add(u)
        else:
          res.add(self.step7(u,[y]))

    return res

  def step7(self,u,oldU):
    for v in self.graph.neighbours(u):
      if(v not in oldU and self.prop(u,v).isMarked()):
        self.step7(v,oldU+[u])
        break #such that v is unique
    if(self.prop(u).hasNLabel() or self.prop(u).hasPLabel()):
      return u

  def find(self, x: int, y: int):
    """
    Do the job

    :param x: nodeId
    :param y: nodeId
    :return: Set(int)
    """
    # init
    self.initProperties()

    while True:
      # step 1
      self.clearLabels()
      q = Queue(maxsize=self.graph.size())

      self.prop(y).setPLabel(y)
      self.prop(y).setState(NodeStates.UNSCANNED)
      q.put(y)

      # step 2-3
      self.find_forward_procedure(q, x)

      if q.empty():
        # step 7
        return self.find_build_finalset(y)

      self.find_backward_procedure(x, y)

    raise NotImplementedError("The algo should never come to this point ?")


def test(graph,src,dst,model=None,pdfname=None):
  if pdfname is None:
    pdfname="debug"

  dsep = MinimalDSep(graph,model)

  if model is not None:
    x=model.idFromName(src)
    y=model.idFromName(dst)
  else:
    x=src
    y=dst

  print(f"{pdfname} : {dsep.find(x, y)}")

  dot.graph_from_dot_data(dsep.todot(x, y)).write_pdf(pdfname+".pdf")

def figure1():
  bn=gum.fastBN("X2->X3->X5->X7->X9->X10->X15->X17<-X16<-X14<-X6<-X3<-X1->X4->X5->X11->X12->X13;X6->X7;X9->X15;X10->X12;X14<-X8->X15->X18")
  src="X3"
  dst="X15"
  return bn.moralizedAncestralGraph({src,dst}),src,dst,bn,"figure1"

def figure6():
  g=gum.UndiGraph()
  for i in range(1,7):
    g.addNodeWithId(i)
  g.addEdge(1,2)
  g.addEdge(1,3)
  g.addEdge(2,4)
  g.addEdge(2,5)
  g.addEdge(3,4)
  g.addEdge(4,6)
  g.addEdge(5,6)

  return g,1,6,None,"figure6"
def ID_Simple_Test():
  #ID=gum.fastID('D->A->*B->F->$C') #test pour cet ID, le SIS de B devrait être {D} (normalement si j'ai bien compris le concept)
  #Le graphe moralisé ancestral correspondant :
  g=gum.UndiGraph()
  for i in range(0,8):
    g.addNodeWithId(i)
  g.addEdge(0,1)
  g.addEdge(1,2)
  g.addEdge(2,3)
  g.addEdge(3,4)
  #g.addEdge(3,6)
  g.addEdge(3,7)
  g.addEdge(4,5)
  g.addEdge(4,7)
  g.addEdge(6,0)
  return g,6,7,None,"ID_simple"

# test(*figure1())
# test(*figure6())
# test(*ID_Simple_Test())