__author__ = "McRussian Andrey"
# -*- coding: utf8 -*-

from typing import Dict, List

from .node import ArgumentNode
from GeneticProgramming.genetic_programming.gp_lib import ListArgumentsException, NodeException

class ListArguments:

    def __init__(self):
        self._args: Dict[str, ArgumentNode] = dict()

    def AppendArgument(self, arg: ArgumentNode):
        if type(arg) != ArgumentNode:
            raise ListArgumentsException(1, 'Uncorrect Type Argument to Append')

        name = arg.GetName()
        if name not in self._args:
            self._args[name] = arg

    def SetValueArgument(self, name: str = None, value: float = None):
        if name is None or value is None:
            raise ListArgumentsException(5, 'Unknown arguments for SetValueArgument')

        if name not in self._args.keys():
            raise ListArgumentsException(7, 'Unknown Name of Argument')

        self._args[name].SetValue(value)

    def GetListNameArguments(self) -> list:
        return list(self._args.keys())

    def GetValueArgument(self, name) -> float:
        if name not in self._args.keys():
            raise ListArgumentsException(21, 'Unknown Name for Argument')

        try:
            value = self._args[name]()
        except NodeException as err:
            raise ListArgumentsException(23, 'Unknown Value for Argument ' + name)

        return value

    def __len__(self) -> int:
        return len(self._args)

    def __call__(self, args = None) -> list:
        if args is None:
            ls = []
            for item in self._args.values():
                ls.append(item())
            return ls

        if type(args) != ListArguments:
            raise ListArgumentsException(13, 'Unknown Type Arguments')

        values = list()
        ls = args.GetListNameArguments()
        for name in self._args.keys():
            if name not in ls:
                raise ListArgumentsException(15, 'Not Value for Argument ' + name)

            try:
                self._args[name].SetValue(args.GetValueArgument(name))
                values.append(self._args[name]())
            except ArgumentNodeException as err:
                raise ListArgumentsException(17, 'No Value for Argument ' + name)

        return values

    def __eq__(self, other):
        if type(other) != ListArguments:
            raise ListArgumentsException(11, 'Uncorrect Type Argument to Compare')

        return set(self._args.keys()).difference(set(other._args.keys())) == set() \
               and set(other._args.keys()).difference(set(self._args.keys())) == set()