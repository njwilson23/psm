
import collections.abc
import itertools
from functools import reduce
import operator

class ParameterMap(collections.abc.MutableMapping):
    """ Tree structure for storing parameter realizations and model solutions.
    """
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
        return {val: _buildtree(values[1:]) for val in values[0]}

def _getleaf(tree, addr):
    if len(addr) == 1:
        return tree[addr[0]]
    else:
        return _getleaf(tree[addr[0]], addr[1:])

def _setleaf(tree, addr, val):
    if len(addr) == 1:
        tree[addr[0]] = val
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
            for addr in _iteraddr(v, depth-1):
                addr.insert(0, k)
                yield addr
    else:
        addrs = []
        for k,v in tree.items():
            yield [k]

