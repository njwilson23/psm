""" Pure-Python tool for naively mapping multidimensional parameter spaces """

import copy
import collections.abc
from math import log, exp, floor
from random import shuffle, random
from .parametermap import ParameterMap

class Parameter(object):

    def __init__(self, name, bounds, min_step=None):
        self.scale = "linear"
        self.distribution = "uniform"
        self.name = name
        self.bounds = bounds
        self.values = []
        if min_step is None:
            self.min_step = (bounds[1] - bounds[0])/100.0
        else:
            self.min_step = min_step
        return

    def __repr__(self):
        return "<Parameter[{0}]({1}:{2})>".format(self.name,
                                                  self.bounds[0],
                                                  self.bounds[1])

    def partition(self, n):
        if n < 2:
            raise ValueError("Partitions must be greater than 1")
        elif n > self.npossible():
            raise ValueError("Only {0} partitions possible".format(self.npossible()))

        if self.scale == "linear":
            dx = (self.bounds[1] - self.bounds[0]) / (n-1)
            self.values = [self.bounds[0]+dx*i for i in range(n)]
        elif self.scale == "log":
            dx = (log(self.bounds[1]) - log(self.bounds[0])) / (n-1)
            self.values = [exp(log(self.bounds[0])+dx*i) for i in range(n)]
        return self.values

    def npossible(self):
        return int(floor((self.bounds[1] - self.bounds[0]) / self.min_step))+1

    def fixed_at_index(self, i):
        return FixedParameter(self.name, self.values[i])

class FixedParameter(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "<FixedParameter[{0}]({1})>".format(self.name, self.value)

class ParameterSpace(collections.abc.Container):

    def __init__(self, parameters, model_call, default_dict=None):
        """ ParameterSpace manages a suite of model runs.
        
        Arguments:
        ----------
        `parameters::list` should be a set of parameters to vary.

        `model_call::function` should be a callable that accepts a dictionary
        of parameters, performs a model run, and return a solution or a
        reference to a solution.
        """
        assert(hasattr(parameters, "__iter__"))
        assert(hasattr(model_call, "__call__"))
        self.parameters = parameters
        self.model_call = model_call
        if default_dict is None:
            self.default_dict = {p.name:None for p in parameters}
        else:
            self.default_dict = default_dict
        return

    def __contains__(self, name):
        return any(p.name == name for p in self.parameters)

    def _getdivisions(self, N):
        if isinstance(N, int):
            if any(N > p.npossible() for p in self.parameters):
                raise ValueError("N is too large for at least one variable")
            names = [p.name for p in self.parameters]
            values = [p.partition(N) for p in self.parameters]

        elif hasattr(N, "keys"):
            names = [p.name for p in self.parameters if p.name in N]
            values = []
            for name in names:
                found = False
                for p in self.parameters:
                    if p.name == name:
                        values.append(p.partition(N[name]))
                        found = True
                        break
                if found is False:
                    raise KeyError("Parameter '{0}' not found".format(name))

        elif hasattr(N, "__iter__"):
            if len(N) != len(self.parameters):
                raise Exception("Have {0} parameters but recieved {1} "
                                "values".format(len(self.parameters), len(N)))
            names = [p.name for p in self.parameters]
            values = [p.partition(N[i]) for i,p in enumerate(self.parameters)]

        return names, values

    def lhc(self, N):
        """ Sample a latin hypercube with `N::int` divisions along each
        parameter """
        names = [p.name for p in self.parameters]
        values = [p.partition(N) for p in self.parameters]
        for v in values:
            shuffle(v)

        pmap = ParameterMap(names, values)
        for i in range(N):
            combo = tuple([v[i] for v in values])
            parameter_dict = copy.copy(self.default_dict)
            for p, val in zip(self.parameters, combo):
                parameter_dict[p.name] = val
            res = self.model_call(parameter_dict)
            pmap[combo] = res

        return pmap

    def fillspace(self, N):
        """ `N::list,dict,int` specifies the number of realizations to add """
        names, values = self._getdivisions(N)
        pmap = ParameterMap(names, values)

        for combo in pmap.combinations():
            parameter_dict = copy.copy(self.default_dict)
            for p, val in zip(self.parameters, combo):
                parameter_dict[p.name] = val
            res = self.model_call(parameter_dict)
            pmap.set(combo, res)

        return pmap

