# PSM

psm is a pure-Python package used to run and analyze ensembles of models.

## Example

This shows how psm should work, not necessarily how it does.

Define a set of parameters:

```python
    from psm import Parameter
    parameters = [Parameter("gravity", (4.9, 14.7), scale="linear"),
                  Parameter("density", (1e-2, 1e3), scale="log"),
                  DiscreteValuedParameter("color", ("red", "green"))]
```

Wrap a model in a function that can be called with a dictionary of parameter
values:

```python
    def model_call(pars):
        # [do stuff to initialize model]
        [...]
        some_foreign_function(args, result)
        return result
```

Run the model with parameters chosen from the parameter space:

```python
    from psm import fillspace
    pmap = fillspace(model_call, parameters,
                    {"gravity": 5, "density": 6, "color": 2})

    from psm import latin_hypercube
    sparse_pmap = latin_hypercube(model_call, parameters, 20)
```

This returns a `ParameterMap` object, which is a tree of model runs organized by
run parameters used. The raw model results can be obtained from
`pmap.solutions`. Now, apply some analytical function to the ensemble of
solutions:

```python
    def square_result(soln):
        """ Square the solution! """
        return soln**2

    pmap_squared = pmap.apply(square_result)
```

Select a slice of the parameter space:

```python
    from psm import FixedParameter

    # Get all solutions run with density == 1.0
    subset = pmap.fix_parameters([FixedParameter("density", 1.0)]).solutions
```

