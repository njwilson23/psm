
from .core import fillspace, latin_hypercube
from .parametermap import ParameterMap
from .parameters import Parameter, \
                        DiscreteValueParameter, \
                        FixedParameter

# Deprecated
from .parameterspace import ParameterSpace

__all__ = ["parameterspace", "parametermap", "core"]

