from random import shuffle, random
import itertools
from .parametermap import ParameterMap

def combinations(parameters, N):
    """ Returns all combinations of parameters with *N* subdivisions. *N* may
    be of any form accepted by `core.getdividions` """
    values = getdivisions(parameters, N)
    return itertools.product(*values)

def fillspace(model_call, parameters, divisions, **kw):
    """ `N::list,dict,int` specifies the number of realizations to add """
    names, values = getdivisions(parameters, divisions)
    pmap = ParameterMap(parameters, **kw)

    for combo in combinations(values):
        parameter_dict = {}
        for p, val in zip(parameters, combo):
            parameter_dict[p.name] = val
        res = model_call(parameter_dict)
        pmap.set(combo, res)

    return pmap


def latin_hypercube(model_call, parameters, divisions, **kw):
    """ Sample a latin hypercube with `divisions::int` divisions along each
    parameter """
    pmap = ParameterMap(parameters, **kw)

    names = [p.name for p in parameters]
    values = [p.partition(divisions) for p in parameters]
    for v in values:
        shuffle(v)

    for i in range(divisions):
        combo = tuple([v[i] for v in values])
        parameter_dict = {}
        for p, val in zip(parameters, combo):
            parameter_dict[p.name] = val
        res = model_call(parameter_dict)
        pmap.set(combo, res)

    return pmap


def getdivisions(parameters, N):
    """ Given a set of parameters and an integer/list/dictionary N, return a
    pair of lists containing parameter names and parameter values.
    """
    if isinstance(N, int):
        values = [p.partition(N) for p in parameters]

    elif hasattr(N, "keys"):
        names = [p.name for p in parameters]
        values = []
        for name in names:
            found = False
            for p in parameters:
                if p.name == name:
                    values.append(p.partition(N[name]))
                    found = True
                    break
            if found is False:
                raise KeyError("Parameter '{0}' not found".format(name))

    elif hasattr(N, "__iter__"):
        if len(N) != len(parameters):
            raise Exception("Have {0} parameters but recieved {1} "
                            "values".format(len(parameters), len(N)))
        values = [p.partition(N[i]) for i,p in enumerate(parameters)]

    return values
