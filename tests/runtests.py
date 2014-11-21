import unittest
from psm import Parameter, DiscreteValueParameter, ParameterSpace
from psm import ParameterMap
from math import log


class ParameterSpaceTests(unittest.TestCase):

    def setUp(self):
        def model(kw):
            return complex(kw["tuning knob"]**kw["toggle"] / log(kw["fudge factor"]))
        self.model = model
        return

    def test_fillspace(self):
        knob = Parameter("tuning knob", [-5, 15])
        toggle = DiscreteValueParameter("toggle", [3, 4])
        fudge = Parameter("fudge factor", [2.0, 10.0])
        pspace = ParameterSpace([knob, toggle, fudge], model_call=self.model)

        pmap = pspace.fillspace([5, 2, 4])
        self.assertEqual(len(pmap), 40)
        return

    def test_lhc(self):
        knob = Parameter("tuning knob", [-5, 15])
        toggle = Parameter("toggle", [0, 10])
        fudge = Parameter("fudge factor", [2.0, 10.0])
        pspace = ParameterSpace([knob, toggle, fudge], model_call=self.model)

        pmap_lhc = pspace.lhc(5, solntype=complex)
        self.assertEqual(len(pmap_lhc), 125)
        self.assertEqual(len([addr for addr in pmap_lhc if pmap_lhc[addr] is not None]), 5)
        return

class ParameterMapTests(unittest.TestCase):

    def test_construction(self):
        pmap = ParameterMap(["a", "b", "c"], [list(range(3)),
                                              list(range(3,6)),
                                              list(range(6,9))])

        pmap[(2, 0, 1)] = 3.141592
        self.assertEqual(pmap[(2,0,1)], 3.141592)
        self.assertTrue(3.141592 in pmap.solutions)
        del pmap[(2,0,1)]
        self.assertTrue(3.141592 not in pmap.solutions)
        return

if __name__ == "__main__":
    unittest.main()
