""" Pure-Python tool for naively mapping multidimensional parameter spaces """

import copy
import collections.abc
from random import shuffle
from .parametermap import ParameterMap

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

    def lhc(self, N, **kw):
        """ Sample a latin hypercube with `N::int` divisions along each
        parameter """
        names = [p.name for p in self.parameters]
        values = [p.partition(N) for p in self.parameters]
        for v in values:
            shuffle(v)

        pmap = ParameterMap(names, values, **kw)
        for i in range(N):
            combo = tuple([v[i] for v in values])
            parameter_dict = copy.copy(self.default_dict)
            for p, val in zip(self.parameters, combo):
                parameter_dict[p.name] = val
            res = self.model_call(parameter_dict)
            pmap.set(combo, res)

        return pmap

    def fillspace(self, N, **kw):
        """ `N::list,dict,int` specifies the number of realizations to add """
        names, values = self._getdivisions(N)
        pmap = ParameterMap(names, values, **kw)

        for combo in pmap.combinations():
            parameter_dict = copy.copy(self.default_dict)
            for p, val in zip(self.parameters, combo):
                parameter_dict[p.name] = val
            res = self.model_call(parameter_dict)
            pmap.set(combo, res)

        return pmap

