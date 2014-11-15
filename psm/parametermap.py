
import collections.abc
import itertools
from functools import reduce
import operator

class ParameterMap(collections.abc.MutableMapping):
    """ Tree structure for storing parameter realizations and model
    solutions. """
    def __init__(self, names, values):
        self.names = names
        self.values = values
        self.tree = _buildtree(self.values)
        return

    def __getitem__(self, addr):
        return _getleaf(self.tree, addr)

    def __setitem__(self, addr, solution):
        _setleaf(self.tree, addr, solution)
        return

    def __delitem__(self, addr):
        _delleaf(self.tree, addr)

    def __iter__(self):
        return _iteraddr(self.tree, len(self.names))

    def __len__(self):
        return reduce(operator.mul, (len(v) for v in self.values))

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
        arr = empty(size, dtype=type(self.solutions[0]))

        for addr in self:
            daddr = {}
            for i,v in enumerate(addr):
                daddr[self.names[i]] = v
            if all(almost(daddr[fp.name], fp.value) for fp in fixparams):
                aaddr = [self.values[i].index(v) for i,v in enumerate(addr)
                           if self.names[i] not in fixnames]
                arr[tuple(aaddr)] = self[addr]
        return arr

    def array(self, name1, name2):
        # 2d for now
        raise DeprecationWarning()
        from numpy import array
        v1 = self.values[self.names.index(name1)]
        v2 = self.values[self.names.index(name2)]
        data = [[self[(a,b)] for b in v2] for a in v1]
        return array(data)

    def combinations(self):
        return itertools.product(*self.values)

    def fix_parameters(self, fixparameters):
        fixnames = [p.name for p in fixparameters]
        fixvalues = [p.value for p in fixparameters]

        newnames = [name for name in self.names if name not in fixnames]
        newvalues = [v for n,v in zip(self.names, self.values) if n in newnames]
        newmap = ParameterMap(newnames, newvalues)
        newmapkey = {name: i for i, name in enumerate(newnames)}

        for newaddr in newmap:
            # construct the old address
            oldaddr = tuple(newaddr[newmapkey[name]] if name in newnames \
                                else fixvalues[fixnames.index(name)] \
                                for name in self.names)
            newmap[newaddr] = self[oldaddr]
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
    if len(addr) == 1:
        return tree[tree["idx"].index(valaddr[0])]
    else:
        return _getleafbyvalue(tree[addr[0]], addr[1:])

def _setleaf(tree, addr, val):
    if len(addr) == 1:
        tree[addr[0]] = val
    else:
        _setleaf(tree[addr[0]], addr[1:], val)

def _setleafbyvalue(tree, valaddr, val):
    if len(addr) == 1:
        tree[tree["idx"].index(valaddr[0])] = val
    else:
        _setleaf(tree[addr[0]], addr[1:], val)

def _delleaf(tree, addr):
    if len(addr) == 1:
        del tree[addr[0]]
    else:
        _delleaf(tree[addr[0]], addr[1:])

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
