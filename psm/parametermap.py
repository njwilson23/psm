
import collections.abc
import copy
import itertools
from functools import reduce
import operator

class ParameterMap(collections.abc.MutableMapping):
    """ Tree structure for storing parameter realizations and model
    solutions. """
    def __init__(self, names, values=None, solntype=None):
        self.names = names
        self.values = values
        self.solntype = solntype
        if self.values is not None:
            self.tree = _buildtree(self.values)
        return

    def __repr__(self):
        if self.solntype is None:
            childtypestr = "None"
        else:
            childtypestr = ".".join([self.solntype.__module__,
                                     self.solntype.__name__])
        return "ParameterMap[{0}]".format(childtypestr)

    def __getitem__(self, addr):
        return _getleaf(self.tree, addr)

    def __setitem__(self, addr, solution):
        if self.solntype is None:
            self.solntype = type(solution)
        elif not isinstance(solution, self.solntype):
            raise TypeError("Cannot assign type {0} to ParameterMap of type "
                            "{1}".format(type(solution), self.solntype))
        _setleaf(self.tree, addr, solution)
        return

    def __delitem__(self, addr):
        _delleaf(self.tree, addr)

    def __iter__(self):
        return _iteraddr(self.tree, len(self.names))

    def __len__(self):
        return reduce(operator.mul, (len(v) for v in self.values))

    def copy(self):
        return copy.deepcopy(self)

    def get(self, valaddr):
        return _getleafbyvalue(self.tree, valaddr)

    def set(self, valaddr, solution):
        if self.solntype is None:
            self.solntype = type(solution)
        elif not isinstance(solution, self.solntype):
            raise TypeError("Cannot assign type {0} to ParameterMap of type "
                            "{1}".format(type(solution), self.solntype))
        return _setleafbyvalue(self.tree, valaddr, solution)

    @property
    def solutions(self):
        return [self[addr] for addr in self]

    def apply(self, func, *args, **kwargs):
        """ Apply `func::function` to solutions and return a new ParameterMap.
        """
        newmap = ParameterMap(self.names, self.values)
        for addr in self:
            newmap[addr] = func(self[addr], *args, **kwargs)
        return newmap

    def extract_array(self, fixparams=None):
        """ Converts parameter map to an array presenting a view of the
        parameter space. If `fixparams::list` is a list of FixedParameters,
        those paramters are held constant and the dimensionality of the
        returned array is reduced.
        """
        from numpy import empty
        if fixparams is None:
            fixparams = []
        elif not hasattr(fixparams, "__iter__"):
            fixparams = [fixparams]

        def almost(a, b):
            return abs(a-b) < 1e-6 * a

        fixnames = [p.name for p in fixparams]
        size = [len(v) for n,v in zip(self.names, self.values)
                       if n not in fixnames]
        arr = empty(size, dtype=self.solntype)

        for addr in self:
            sorted_addr = []
            for i,a in enumerate(addr):
                if i == 0:
                    a_ = self.tree["idx"].index(self.values[i][a])
                else:
                    a_ = self[addr[:i]]["idx"].index(self.values[i][a])
                sorted_addr.append(a_)
            arr[tuple(sorted_addr)] = self[addr]
        return arr

    def array(self, fixparams=None):
        return self.extract_array(fixparams)

    def combinations(self):
        return itertools.product(*self.values)

    def fix_parameters(self, fixparameters):
        """ Return a pruned ParameterMap with *fixparameters* held constant. """
        fixdepths = [self.names.index(p.name) for p in fixparameters]
        fixvalues = [p.value for p in fixparameters]

        # cut away parameter values not in fixedparameters
        newmap = self.copy()
        for depth, value in zip(fixdepths, fixvalues):
            _pruneexcept(newmap.tree, depth, value)

        # update names and values lists
        for p in fixparameters:
            i = newmap.names.index(p.name)
            j = newmap.values[i].index(p.value)
            for jx in reversed(range(len(newmap.values[i]))):
                if j != jx:
                    del newmap.values[i][jx]
        return newmap

def _buildtree(values):
    if len(values) == 0:
        return None
    else:
        n = len(values[0])
        tree = {i: _buildtree(values[1:]) for i in range(n)}
        tree["idx"] = values[0]
        return tree

def _getleaf(tree, addr):
    if len(addr) == 1:
        return tree[addr[0]]
    else:
        return _getleaf(tree[addr[0]], addr[1:])

def _getleafbyvalue(tree, valaddr):
    if len(valaddr) == 1:
        return tree[tree["idx"].index(valaddr[0])]
    else:
        return _getleafbyvalue(tree.get(valaddr[0]), valaddr[1:])

def _setleaf(tree, addr, val):
    if len(addr) == 1:
        tree[addr[0]] = val
    else:
        _setleaf(tree[addr[0]], addr[1:], val)

def _setleafbyvalue(tree, valaddr, val):
    if valaddr[0] not in tree["idx"]:
        n = len(tree["idx"])
        tree["idx"].append(valaddr[0])
        tree[n] = {"idx": []}

    if len(valaddr) == 1:
        tree[tree["idx"].index(valaddr[0])] = val
    else:
        _setleafbyvalue(tree[tree["idx"].index(valaddr[0])], valaddr[1:], val)

def _delleaf(tree, addr):
    if len(addr) == 1:
        del tree[addr[0]]
    else:
        _delleaf(tree[addr[0]], addr[1:])

def _pruneexcept(tree, depth, val):
    """ Prune all branches from *tree* at *depth* except those matching *val*.

    Example:
    given tree T,
        _pruneexcept(T, 2, pi)
    will remove all great-grandchildren of T with value pi.
    """
    if depth != 0:
        for branch in tree:
            if branch != "idx":
                _pruneexcept(tree[branch], depth-1, val)
    else:
        i = tree["idx"].index(val)
        deadbranches = set(tree.keys()).difference((i, "idx"))
        for br in deadbranches:
            del tree[br]
        tree["idx"] = [tree["idx"][i]]

def _iteraddr(tree, depth):
    if depth != 1:
        addrs = []
        for k,v in tree.items():
            if k != "idx":
                for addr in _iteraddr(v, depth-1):
                    addr.insert(0, k)
                    yield addr
    else:
        addrs = []
        for k,v in tree.items():
            if k != "idx":
                yield [k]

