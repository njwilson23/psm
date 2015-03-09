import collections.abc
import copy
import itertools
from functools import reduce
import operator
import sqlite3

class ParameterMap(object):
    """ Organized as a stack of parameter combinations and solutions. """

    def __init__(self, parameters, solntype=None):
        self.names = [p.name for p in parameters]
        self.values = [[] for p in parameters]
        self.solutions = []
        self.solntype = solntype
        return

    def __repr__(self):
        if self.solntype is None:
            childtypestr = "None"
        else:
            childtypestr = ".".join([self.solntype.__module__,
                                     self.solntype.__name__])
        return "ParameterMap[{0}]".format(childtypestr)

    def __getitem__(self, key):
        i = 0
        while i < len(self):
            found = True
            for j,k in enumerate(key):
                if self.values[j][i] != k:
                    found = False
                    break

            if found:
                return self.solutions[i]
            else:
                i += 1

        raise KeyError("No solution exists for parameters {0}".format(key))

    def __setitem__(self, key, soln):
        if len(key) != len(self.values):
            raise KeyError("Key length must equal ParameterMap dimension "
                           "({0})".format(len(self.values)))
        if (type(soln) is not self.solntype) and (soln is not None):
            if self.solntype is None:
                self.solntype = type(soln)
            else:
                raise TypeError("Solutions must be of type {0} or "
                                "None".format(self.solntype))
        for j,k in enumerate(key):
            self.values[j].append(k)
        self.solutions.append(soln)
        return

    def set(self, key, soln):
        return self.__setitem__(key, soln)

    def __iter__(self):
        return (soln for soln in self.solutions)

    def __len__(self):
        return len(self.solutions)

    def copy(self):
        return copy.deepcopy(self)

    def apply(self, func, *args, **kwargs):
        """ Apply `func::function` to solutions and return a new ParameterMap.
        """
        newmap = self.copy()
        for i in range(len(newmap)):
            newmap.solutions[i] = func(newmap.solutions[i], *args, **kwargs)
        return newmap

    def fix_parameters(self, *fixparams):
        """ Return a view only containing solutions with *fixparams* set. """
        fixnames = [p.name for p in fixparams]
        fix_indices = [self.names.index(n) for n in fixnames]

        npars = len(self.names)
        solns, values = [], []
        for i, soln in enumerate(self.solutions):
            for idx in fix_indices:
                if fixparams[idx].value == self.values[idx][i]:
                    solns.append(soln)
                    values.append([self.values[j][i] for j in range(npars)])

        remaining_names = [n for n in self.names if n not in fixnames]
        newmap = ParameterMap([])
        newmap.names = remaining_names
        newmap.solutions = solns
        newmap.values = values
        newmap.solntype = self.solntype
        return newmap

# class TreeParameterMap(collections.abc.MutableMapping):
#     """ Implements a tree-based map through a potentially sparse parameter space.
# 
#     Each branch of the tree contains a child branch called "idx", plus additional
#     children with integer keys. The "idx" branch is a dictionary of parameter keys
#     and values.
# 
#                 parent
#               /   |    \
#             idx   0     1
#                   |      \
#                 soln    soln
#     """
#     def __init__(self, names, values=None, solntype=None):
#         self.names = names
#         self.values = values
#         self.solntype = solntype
#         if self.values is not None:
#             self.tree = _buildtree(self.values)
#         return
# 
#     def __repr__(self):
#         if self.solntype is None:
#             childtypestr = "None"
#         else:
#             childtypestr = ".".join([self.solntype.__module__,
#                                      self.solntype.__name__])
#         return "ParameterMap[{0}]".format(childtypestr)
# 
#     def __getitem__(self, addr):
#         return _getleaf(self.tree, addr)
# 
#     def __setitem__(self, addr, solution):
#         if self.solntype is None:
#             self.solntype = type(solution)
#         elif not isinstance(solution, self.solntype):
#             raise TypeError("Cannot assign type {0} to ParameterMap of type "
#                             "{1}".format(type(solution), self.solntype))
#         _setleaf(self.tree, addr, solution)
#         return
# 
#     def __delitem__(self, addr):
#         _delleaf(self.tree, addr)
# 
#     def __iter__(self):
#         return _iteraddr(self.tree, len(self.names))
# 
#     def __len__(self):
#         return reduce(operator.mul, (len(v) for v in self.values))
# 
#     def copy(self):
#         return copy.deepcopy(self)
# 
#     def get(self, valaddr):
#         return _getleafbyvalue(self.tree, valaddr)
# 
#     def set(self, valaddr, solution):
#         if self.solntype is None:
#             self.solntype = type(solution)
#         elif not isinstance(solution, self.solntype):
#             raise TypeError("Cannot assign type {0} to ParameterMap of type "
#                             "{1}".format(type(solution), self.solntype))
#         return _setleafbyvalue(self.tree, valaddr, solution)
# 
#     @property
#     def solutions(self):
#         return [self[addr] for addr in self]
# 
#     def parameters(self, name):
#         i = self.names.index(name)
#         # need to check index at branch to get parameter value
#         # return [addr[i] for addr in self]
# 
#     def apply(self, func, *args, **kwargs):
#         """ Apply `func::function` to solutions and return a new ParameterMap.
#         """
#         newmap = ParameterMap(self.names, self.values)
#         for addr in self:
#             newmap[addr] = func(self[addr], *args, **kwargs)
#         return newmap
# 
#     def extract_array(self, fixparams=None):
#         """ Converts parameter map to an array presenting a view of the
#         parameter space. If `fixparams::list` is a list of FixedParameters,
#         those paramters are held constant and the dimensionality of the
#         returned array is reduced.
#         """
#         from numpy import empty
#         if fixparams is None:
#             fixparams = []
#         elif not hasattr(fixparams, "__iter__"):
#             fixparams = [fixparams]
# 
#         def almost(a, b):
#             return abs(a-b) < 1e-6 * a
# 
#         fixnames = [p.name for p in fixparams]
#         size = [len(v) for n,v in zip(self.names, self.values)
#                        if n not in fixnames]
#         arr = empty(size, dtype=self.solntype)
# 
#         for addr in self:
#             sorted_addr = []
#             for i,a in enumerate(addr):
#                 if i == 0:
#                     a_ = self.tree["idx"].index(self.values[i][a])
#                 else:
#                     a_ = self[addr[:i]]["idx"].index(self.values[i][a])
#                 sorted_addr.append(a_)
#             arr[tuple(sorted_addr)] = self[addr]
#         return arr
# 
#     def array(self, fixparams=None):
#         return self.extract_array(fixparams)
# 
#     def combinations(self):
#         return itertools.product(*self.values)
# 
#     def fix_parameters(self, fixparameters):
#         """ Return a pruned ParameterMap with *fixparameters* held constant. """
#         fixdepths = [self.names.index(p.name) for p in fixparameters]
#         fixvalues = [p.value for p in fixparameters]
# 
#         # cut away parameter values not in fixedparameters
#         newmap = self.copy()
#         for depth, value in zip(fixdepths, fixvalues):
#             _pruneexcept(newmap.tree, depth, value)
# 
#         # update names and values lists
#         for p in fixparameters:
#             i = newmap.names.index(p.name)
#             j = newmap.values[i].index(p.value)
#             for jx in reversed(range(len(newmap.values[i]))):
#                 if j != jx:
#                     del newmap.values[i][jx]
#         return newmap
# 
# def _buildtree(values):
#     """ Given a list of parameter values, pre-initialize a tree spanning all values. """
#     if len(values) == 0:
#         return None
#     else:
#         n = len(values[0])
#         tree = {i: _buildtree(values[1:]) for i in range(n)}
#         tree["idx"] = Index(values[0])
#         return tree
# 
# def _getleaf(tree, addr):
#     if len(addr) == 1:
#         return tree[addr[0]]
#     else:
#         return _getleaf(tree[addr[0]], addr[1:])
# 
# def _getleafbyvalue(tree, valaddr):
#     if len(valaddr) == 1:
#         return tree[tree["idx"].index(valaddr[0])]
#     else:
#         return _getleafbyvalue(tree.get(valaddr[0]), valaddr[1:])
# 
# def _setleaf(tree, addr, val):
#     if len(addr) == 1:
#         tree[addr[0]] = val
#     else:
#         _setleaf(tree[addr[0]], addr[1:], val)
# 
# def _setleafbyvalue(tree, valaddr, val):
#     if valaddr[0] not in tree["idx"]:
#         n = len(tree["idx"])
#         tree["idx"].append(valaddr[0])
#         tree[n] = {"idx": []}
# 
#     if len(valaddr) == 1:
#         tree[tree["idx"].index(valaddr[0])] = val
#     else:
#         _setleafbyvalue(tree[tree["idx"].index(valaddr[0])], valaddr[1:], val)
# 
# def _delleaf(tree, addr):
#     if len(addr) == 1:
#         del tree[addr[0]]
#     else:
#         _delleaf(tree[addr[0]], addr[1:])
# 
# def _pruneexcept(tree, depth, val):
#     """ Prune all branches from *tree* at *depth* except those matching *val*.
# 
#     Example:
#     given tree T,
#         _pruneexcept(T, 2, pi)
#     will remove all great-grandchildren of T with value pi.
#     """
#     if depth != 0:
#         for branch in tree:
#             if branch != "idx":
#                 _pruneexcept(tree[branch], depth-1, val)
#     else:
#         i = tree["idx"].index(val)
#         deadbranches = set(tree.keys()).difference((i, "idx"))
#         for br in deadbranches:
#             del tree[br]
#         tree["idx"] = [tree["idx"][i]]
# 
# def _iteraddr(tree, depth):
#     if depth != 1:
#         for k,v in tree.items():
#             if k != "idx":
#                 for addr in _iteraddr(v, depth-1):
#                     addr.insert(0, k)
#                     yield addr
#     else:
#         for k,v in tree.items():
#             if k != "idx":
#                 yield [k]
# 
# class Index(object):
#     def __init__(self, keys, values=None):
#         self.keys = []
#         self.values = []
# 
#     def __getitem__(self, key):
#         for k,v in zip(self.keys, self.values):
#             if k == key:
#                 return v
# 
#     def __setitem__(self, key, value):
#         if value in self.values:
#             previouskey = self.keys[self.values.index(value)]
#             raise ValueError("Value already indexed at {0}".format(previouskey))
#         elif key in self.keys:
#             self.values[self.keys.index(key)] = value
#         else:
#             self.keys.append(key)
#             self.values.append(value)

