from unittest import TestCase
from GeneticProgramming.genetic_programming import ArgumentNode, ListArguments, ListArgumentsException

class TestArguments(TestCase):
    def test_AppendArgument(self):
        A = ListArguments()
        self.assertRaises(ListArgumentsException, A.AppendArgument, 12)
        self.assertRaises(ListArgumentsException, A.AppendArgument, ' ')
        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.AppendArgument(arg=arg)

        self.assertEqual(len(alph), len(A))

        alph = 'qwertyuiop'
        for char in alph:
            arg1 = ArgumentNode(char)
            A.AppendArgument(arg=arg1)
            arg2 = ArgumentNode(char)
            A.AppendArgument(arg=arg2)

        self.assertEqual(len(alph), len(A))


    def test_SetValueArgument(self):
        A = ListArguments()
        self.assertRaises(ListArgumentsException, A.SetValueArgument)
        self.assertRaises(ListArgumentsException, A.SetValueArgument, ' ', 4)
        self.assertRaises(ListArgumentsException, A.SetValueArgument, 4)

        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.AppendArgument(arg=arg)
            A.SetValueArgument(char, ord(char))

        self.assertRaises(ListArgumentsException, A.SetValueArgument, 'a', 12)


    def test_EqualListArguments(self):
        A = ListArguments()
        self.assertRaises(ListArgumentsException, A.__eq__, 2)

        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.AppendArgument(arg=arg)

        D = ListArguments()
        for char in alph[-1: : -1]:
            arg = ArgumentNode(char)
            D.AppendArgument(arg=arg)

        self.assertTrue(A == D)

        A.AppendArgument(ArgumentNode('z'))
        self.assertFalse(A == D)

        D.AppendArgument(ArgumentNode('a'))
        self.assertFalse(A == D)

    def test_GetListArguments(self):
        A = ListArguments()
        self.assertListEqual(A.GetListNameArguments(), [])
        alph = 'qwertyuiop'
        for char in alph:
            arg = ArgumentNode(char)
            A.AppendArgument(arg=arg)

        self.assertListEqual(A.GetListNameArguments(), list(alph))

    def test_GetValueArgument(self):
        A = ListArguments()

        alph = 'qwerty'
        for char in alph:
            arg = ArgumentNode(char)
            A.AppendArgument(arg=arg)
            A.SetValueArgument(char, ord(char))

            self.assertEqual(ord(char), A.GetValueArgument(name=char))

        self.assertRaises(ListArgumentsException, A.GetValueArgument, 'a')

    def test_Call(self):
        A = ListArguments()
        self.assertTrue(len(A()) == 0)
        self.assertRaises(ListArgumentsException, A, 12)
        self.assertRaises(ListArgumentsException, A, [1, 2, 3])

        alph = 'qwerty'
        for char in alph:
            arg = ArgumentNode(char)
            A.AppendArgument(arg=arg)

        self.assertRaises(ListArgumentsException, A)
        values = dict()
        for char in alph:
            A.SetValueArgument(char, ord(char))
            values[char] = ord(char)

        self.assertTrue(type(A()) == dict)
        self.assertEqual(values, A())

        D = ListArguments()
        for char in 'qwerty' + 'dkdxzvxc':
            arg = ArgumentNode(char)
            D.AppendArgument(arg=arg)
            D.SetValueArgument(char, ord(char))

        self.assertTrue(type(A(D)) == dict)
        self.assertEqual(values, A(D))

        D = ListArguments()
        for char in 'dkdxzvxc':
            arg = ArgumentNode(char)
            D.AppendArgument(arg=arg)
            D.SetValueArgument(char, ord(char))
        self.assertEqual(values, A(D))

        D = ListArguments()
        for char in 'qwerty':
            arg = ArgumentNode(char)
            D.AppendArgument(arg=arg)
            D.SetValueArgument(char, ord(char) + 10)
            values[char] = ord(char) + 10
        self.assertEqual(values, A(D))