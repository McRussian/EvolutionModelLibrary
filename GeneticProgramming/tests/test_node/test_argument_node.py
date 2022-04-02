from unittest import TestCase
from GeneticProgramming.genetic_programming.gp_lib import ArgumentNode
from GeneticProgramming.genetic_programming import NodeException


class TestArgumentNode(TestCase):
    def test_SetArgument(self):
        A = ArgumentNode('x')
        self.assertEqual('x', A.__str__())

        self.assertRaises(NodeException, ArgumentNode)
        self.assertRaises(NodeException, ArgumentNode, [11])

    def test_EqualArgument(self):
        A = ArgumentNode('x')
        B = ArgumentNode('y')
        C = ArgumentNode('y')
        self.assertEqual(B, C)
        self.assertNotEqual(A, B)

        self.assertRaises(NodeException, A.__eq__, [12])

    def test_SetValue(self):
        A = ArgumentNode('x')
        A.set_value(12)
        self.assertEqual(12, A())

        B = ArgumentNode('x')
        self.assertRaises(NodeException, B.set_value, ['qqq'])
        self.assertRaises(NodeException, B)

    def test_Call(self):
        A = ArgumentNode('x')
        self.assertRaises(NodeException, A)
        A.set_value(12)
        self.assertEqual(12, A())
        self.assertEqual(11, A(x=11))
        self.assertEqual(11, A(y=12, x=11, t=1))
        self.assertRaises(NodeException, A, y=12, t=11)
