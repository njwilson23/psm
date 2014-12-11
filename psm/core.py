from random import shuffle, random
from .parametermap import ParameterMap

def fillspace(model_call, parameters, divisions, **kw):
    """ `N::list,dict,int` specifies the number of realizations to add """
    names, values = _getdivisions(parameters, divisions)
    pmap = ParameterMap(names, values, **kw)

    for combo in pmap.combinations():
        parameter_dict = {}
        for p, val in zip(parameters, combo):
            parameter_dict[p.name] = val
        res = model_call(parameter_dict)
        pmap.set(combo, res)

    return pmap


def latin_hypercube(model_call, parameters, divisions, **kw):
    """ Sample a latin hypercube with `divisions::int` divisions along each
    parameter """
    names = [p.name for p in parameters]
    values = [p.partition(divisions) for p in parameters]
    for v in values:
        shuffle(v)

    pmap = ParameterMap(names, values, **kw)
    for i in range(divisions):
        combo = tuple([v[i] for v in values])
        parameter_dict = {}
        for p, val in zip(parameters, combo):
            parameter_dict[p.name] = val
        res = model_call(parameter_dict)
        pmap.set(combo, res)

    return pmap


def _getdivisions(parameters, N):
    """ Given a set of parameters and an integer/list/dictionary N, return a
    pair of lists containing parameter names and parameter values.
    """
    if isinstance(N, int):
        names = [p.name for p in parameters]
        values = [p.partition(N) for p in parameters]

    elif hasattr(N, "keys"):
        names = [p.name for p in parameters if p.name in N]
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
        names = [p.name for p in parameters]
        values = [p.partition(N[i]) for i,p in enumerate(parameters)]

    return names, values
