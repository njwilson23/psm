import unittest
from psm import Parameter, FixedParameter, DiscreteValueParameter
from psm import ParameterSpace, ParameterMap
import psm
from math import log


class PSMTests(unittest.TestCase):

    def setUp(self):
        def model(kw):
            return complex(kw["tuning knob"]**kw["toggle"] / log(kw["fudge factor"]))
        self.model = model
        return

    def test_fillspace(self):
        knob = Parameter("tuning knob", [-5, 15])
        toggle = DiscreteValueParameter("toggle", [3, 4])
        fudge = Parameter("fudge factor", [2.0, 10.0])
        pmap = psm.fillspace(self.model, [knob, toggle, fudge], [5, 2, 4])
        self.assertEqual(len(pmap), 40)
        return

    def test_lhc(self):
        knob = Parameter("tuning knob", [-5, 15])
        toggle = Parameter("toggle", [0, 10])
        fudge = Parameter("fudge factor", [2.0, 10.0])
        pmap = psm.latin_hypercube(self.model, [knob, toggle, fudge], 5, solntype=complex)
        self.assertEqual(len(pmap), 125)
        self.assertEqual(len([addr for addr in pmap if pmap[addr] is not None]), 5)
        return

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

        pmap = pspace.lhc(5, solntype=complex)
        self.assertEqual(len(pmap), 125)
        self.assertEqual(len([addr for addr in pmap if pmap[addr] is not None]), 5)
        return

class ParameterMapTests(unittest.TestCase):

    def setUp(self):
        self.pmap = ParameterMap(["a", "b", "c"],
                                 [list(range(3)), list(range(3,6)), list(range(6,9))])
        return


    def text_length(self):
        self.assertEqual(len(self.pmap), 27)

    def test_construction(self):
        pmap = self.pmap.copy()
        pmap[(2, 0, 1)] = 3.141592
        self.assertEqual(pmap[(2,0,1)], 3.141592)
        self.assertTrue(3.141592 in pmap.solutions)
        del pmap[(2,0,1)]
        self.assertTrue(3.141592 not in pmap.solutions)
        return

    def test_fix_parameters1(self):
        # fix a top level parameter
        fp = FixedParameter("a", 1)
        fixed_pmap = self.pmap.fix_parameters([fp])
        self.assertEqual(len(fixed_pmap), 9)
        self.assertEqual(len(fixed_pmap.tree.keys()), 2)
        self.assertEqual(fixed_pmap.tree["idx"], [1])
        return

    def test_fix_parameters2(self):
        # fix a parameter that isn't at the top level
        fp = FixedParameter("b", 5)
        fixed_pmap = self.pmap.fix_parameters([fp])
        self.assertEqual(len(fixed_pmap), 9)
        self.assertEqual(len(fixed_pmap.tree[0].keys()), 2)
        self.assertEqual(fixed_pmap.tree[0]["idx"], [5])
        return

    def test_fix_multiple_parameters(self):
        # fix a list of parameters
        fps = [FixedParameter("b", 5), FixedParameter("c", 7)]
        fixed_pmap = self.pmap.fix_parameters(fps)
        self.assertEqual(len(fixed_pmap), 3)
        self.assertEqual(len(fixed_pmap.tree[0][2].keys()), 2)
        self.assertEqual(fixed_pmap.tree["idx"], [0, 1, 2])
        return


if __name__ == "__main__":
    unittest.main()
