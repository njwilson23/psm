import unittest
from psm import Parameter, FixedParameter, DiscreteValueParameter
from psm import ParameterMap
import psm
from math import log


class PSMTests(unittest.TestCase):

    def setUp(self):
        def model(kw):
            return complex(kw["tuning knob"]**kw["toggle"] / log(kw["fudge factor"]))
        self.model = model
        return

    def test_get_divisions_integer(self):
        p = Parameter("param", [0, 10])
        v = psm.getdivisions([p], 5)
        self.assertEqual(len(v[0]), 5)
        self.assertEqual(min(v[0]), 0)
        self.assertEqual(max(v[0]), 10)
        return

    def test_get_divisions_list(self):
        knob = Parameter("tuning knob", [-5, 15])
        toggle = DiscreteValueParameter("toggle", [3, 4])
        fudge = Parameter("fudge factor", [2.0, 10.0])
        v = psm.getdivisions([knob, toggle, fudge], [5, 2, 3])
        self.assertEqual(len(v[0]), 5)
        self.assertEqual(len(v[1]), 2)
        self.assertEqual(len(v[2]), 3)
        pass

    def test_get_divisions_dict(self):
        knob = Parameter("tuning knob", [-5, 15])
        toggle = DiscreteValueParameter("toggle", [3, 4])
        fudge = Parameter("fudge factor", [2.0, 10.0])
        v = psm.getdivisions([knob, toggle, fudge], {"tuning knob": 5,
                                                     "toggle": 2,
                                                     "fudge factor": 4})
        self.assertEqual(len(v[0]), 5)
        self.assertEqual(len(v[1]), 2)
        self.assertEqual(len(v[2]), 4)
        pass

    def test_combinations(self):
        knob = Parameter("tuning knob", [-5, 15])
        toggle = DiscreteValueParameter("toggle", [3, 4])
        fudge = Parameter("fudge factor", [2.0, 10.0])

        C = psm.combinations([knob, toggle, fudge], {"tuning knob": 5, "toggle": 2, "fudge factor": 3})
        self.assertEqual(len(list(C)), 30)

        C2 = psm.combinations([knob, fudge], 5)
        self.assertEqual(len(list(C2)), 25)
        return


    # def test_fillspace(self):
    #     knob = Parameter("tuning knob", [-5, 15])
    #     toggle = DiscreteValueParameter("toggle", [3, 4])
    #     fudge = Parameter("fudge factor", [2.0, 10.0])
    #     pmap = psm.fillspace(self.model, [knob, toggle, fudge], [5, 2, 4])
    #     self.assertEqual(len(pmap), 40)
    #     return

    # def test_lhc(self):
    #     knob = Parameter("tuning knob", [-5, 15])
    #     toggle = Parameter("toggle", [0, 10])
    #     fudge = Parameter("fudge factor", [2.0, 10.0])
    #     pmap = psm.latin_hypercube(self.model, [knob, toggle, fudge], 5, solntype=complex)
    #     self.assertEqual(len(pmap), 125)
    #     self.assertEqual(len([addr for addr in pmap if pmap[addr] is not None]), 5)
    #     return

class ParameterMapTests(unittest.TestCase):

    def setUp(self):
        self.parameters = [Parameter("a", [0, 2]),
                           Parameter("b", [3, 5]),
                           Parameter("c", [6, 8])]
        self.pmap = ParameterMap(self.parameters)
        return

    def test_length(self):
        pmap = self.pmap.copy()
        self.assertEqual(len(pmap), 0)
        for combo in psm.combinations(self.parameters, 3):
            pmap.set(combo, None)
        self.assertEqual(len(pmap), 27)
        return

    # def test_construction(self):
    #     pmap = self.pmap.copy()
    #     pmap.set_null((3, 3, 3))
    #     pmap[(2, 0, 1)] = 3.141592
    #     self.assertEqual(pmap[(2,0,1)], 3.141592)
    #     self.assertTrue(3.141592 in pmap.solutions)
    #     del pmap[(2,0,1)]
    #     self.assertTrue(3.141592 not in pmap.solutions)
    #     return

    def test_fix_parameters1(self):
        # fix a top level parameter
        model = lambda p: p["a"]**2 + p["b"]**3
        pmap = psm.fillspace(model,
                             [Parameter("a", (0, 4)),
                              Parameter("b", (-2, 4))],
                             5)

        fp = FixedParameter("a", 1)
        fixed_pmap = pmap.fix_parameters(fp)
        self.assertEqual(len(fixed_pmap), 5)
        #self.assertEqual(len(fixed_pmap.tree.keys()), 2)
        #self.assertEqual(fixed_pmap.tree["idx"], [1])
        return

    # def test_fix_parameters2(self):
    #     # fix a parameter that isn't at the top level
    #     fp = FixedParameter("b", 5)
    #     fixed_pmap = self.pmap.fix_parameters([fp])
    #     self.assertEqual(len(fixed_pmap), 9)
    #     self.assertEqual(len(fixed_pmap.tree[0].keys()), 2)
    #     self.assertEqual(fixed_pmap.tree[0]["idx"], [5])
    #     return

    # def test_fix_multiple_parameters(self):
    #     # fix a list of parameters
    #     fps = [FixedParameter("b", 5), FixedParameter("c", 7)]
    #     fixed_pmap = self.pmap.fix_parameters(fps)
    #     self.assertEqual(len(fixed_pmap), 3)
    #     self.assertEqual(len(fixed_pmap.tree[0][2].keys()), 2)
    #     self.assertEqual(fixed_pmap.tree["idx"], [0, 1, 2])
    #     return


if __name__ == "__main__":
    unittest.main()
