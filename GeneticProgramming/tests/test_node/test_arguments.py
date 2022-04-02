from unittest import TestCase
from GeneticProgramming.genetic_programming import ArgumentNode, ListArguments, ListArgumentsException


class TestArguments(TestCase):
    def test_AppendArgument(self):
        A = ListArguments()
        self.assertRaises(ListArgumentsException, A.append_argument, 12)
        self.assertRaises(ListArgumentsException, A.append_argument, ' ')
        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.append_argument(arg=arg)

        self.assertEqual(len(alph), len(A))

        alph = 'qwertyuiop'
        for char in alph:
            arg1 = ArgumentNode(char)
            A.append_argument(arg=arg1)
            arg2 = ArgumentNode(char)
            A.append_argument(arg=arg2)

        self.assertEqual(len(alph), len(A))


    def test_SetValueArgument(self):
        A = ListArguments()
        self.assertRaises(ListArgumentsException, A.set_value_argument)
        self.assertRaises(ListArgumentsException, A.set_value_argument, ' ', 4)
        self.assertRaises(ListArgumentsException, A.set_value_argument, 4)

        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.append_argument(arg=arg)
            A.set_value_argument(char, ord(char))

        self.assertRaises(ListArgumentsException, A.set_value_argument, 'a', 12)


    def test_EqualListArguments(self):
        A = ListArguments()
        self.assertRaises(ListArgumentsException, A.__eq__, 2)

        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.append_argument(arg=arg)

        D = ListArguments()
        for char in alph[-1: : -1]:
            arg = ArgumentNode(char)
            D.append_argument(arg=arg)

        self.assertTrue(A == D)

        A.append_argument(ArgumentNode('z'))
        self.assertFalse(A == D)

        D.append_argument(ArgumentNode('a'))
        self.assertFalse(A == D)

    def test_GetListArguments(self):
        A = ListArguments()
        self.assertListEqual(A.get_name_arguments(), [])
        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.append_argument(arg=arg)

        self.assertListEqual(A.get_name_arguments(), list(alph))

    def test_GetValueArgument(self):
        A = ListArguments()

        alph = 'qwerty'
        for char in alph:
            arg = ArgumentNode(char)
            A.append_argument(arg=arg)
            A.set_value_argument(char, ord(char))

            self.assertEqual(ord(char), A.get_value_argument(name=char))

        self.assertRaises(ListArgumentsException, A.get_value_argument, 'a')

    def test_Call(self):
        A = ListArguments()
        self.assertTrue(len(A()) == 0)
        self.assertRaises(ListArgumentsException, A, 12)
        self.assertRaises(ListArgumentsException, A, [1, 2, 3])

        alph = 'qwerty'
        for char in alph:
            arg = ArgumentNode(char)
            A.append_argument(arg=arg)

        self.assertRaises(ListArgumentsException, A)
        values = dict()
        for char in alph:
            A.set_value_argument(char, ord(char))
            values[char] = ord(char)

        self.assertTrue(type(A()) == dict)
        self.assertEqual(values, A())

        D = ListArguments()
        for char in 'qwerty' + 'dkdxzvxc':
            arg = ArgumentNode(char)
            D.append_argument(arg=arg)
            D.set_value_argument(char, ord(char))

        self.assertTrue(type(A(D)) == dict)
        self.assertEqual(values, A(D))

        D = ListArguments()
        for char in 'dkdxzvxc':
            arg = ArgumentNode(char)
            D.append_argument(arg=arg)
            D.set_value_argument(char, ord(char))
        self.assertEqual(values, A(D))

        D = ListArguments()
        for char in 'qwerty':
            arg = ArgumentNode(char)
            D.append_argument(arg=arg)
            D.set_value_argument(char, ord(char) + 10)
            values[char] = ord(char) + 10
        self.assertEqual(values, A(D))