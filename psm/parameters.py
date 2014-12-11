from math import log, exp

class Parameter(object):

    def __init__(self, name, bounds, scale="linear"):
        """ Defines a named parameter that can be automatically varied over a
        range within *bounds*.

        Keyword arguments:
        `scale::string` is either "linear" or "log"
        """
        self.scale = scale
        self.distribution = "uniform"
        self.name = name
        self.bounds = bounds
        self.values = []
        return

    def __repr__(self):
        return "<Parameter[{0}]({1}:{2})>".format(self.name,
                                                  self.bounds[0],
                                                  self.bounds[1])

    def partition(self, n):
        if n < 2:
            raise ValueError("Partitions must be greater than 1")

        if self.scale == "linear":
            dx = (self.bounds[1] - self.bounds[0]) / (n-1)
            self.values = [self.bounds[0]+dx*i for i in range(n)]
        elif self.scale == "log":
            dx = (log(self.bounds[1]) - log(self.bounds[0])) / (n-1)
            self.values = [exp(log(self.bounds[0])+dx*i) for i in range(n)]
        return self.values

    def fixed_at_index(self, i):
        return FixedParameter(self.name, self.values[i])

class DiscreteValueParameter(Parameter):

    def __init__(self, name, values):
        """ Defines a named parameter that can be automatically varied over
        discrete values.
        """
        self.distribution = "discrete"
        self.name = name
        self.possiblevalues = values
        return

    def __repr__(self):
        return "<DiscreteValueParameter[{0}]{{1}}>".format(self.name,
                                                           len(self.possiblevalues))

    def partition(self, n):
        N = len(self.possiblevalues)
        if n < 2:
            raise ValueError("Partitions must be greater than 1")
        elif n > N:
            raise ValueError("Only {0} partitions possible".format(N))

        self.values = [self.possiblevalues[i] for i in range(0, N, N//n)]
        return self.values

class FixedParameter(object):

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __repr__(self):
        return "<FixedParameter[{0}]({1})>".format(self.name, self.value)


