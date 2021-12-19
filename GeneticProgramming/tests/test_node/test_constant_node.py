from unittest import TestCase
from GeneticProgramming.genetic_programming.gp_lib import ConstantNode
from GeneticProgramming.genetic_programming import NodeException

class TestConstantNode(TestCase):
    def testValidConstant(self):
        const = ConstantNode(12)
        self.assertEqual(const(), 12.0)
        self.assertEqual(const.__str__(), '12.0')

    def testValidEqual(self):
        c = ConstantNode(12)
        b = ConstantNode(11)

        self.assertNotEqual(c, b)
        a = ConstantNode(12.0)
        self.assertEqual(c, a)

        self.assertNotEqual(c, 12)

    def testConstraintForConstant(self):
        a = ConstantNode()
        self.assertGreaterEqual(a(), -50)
        self.assertLessEqual(a(), 50)


    def testValidDefineConstant(self):
        c = ConstantNode('ddd')
        self.assertRaises(NodeException, c)
