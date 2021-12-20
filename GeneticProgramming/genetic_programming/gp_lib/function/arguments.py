__author__ = "McRussian Andrey"
# -*- coding: utf8 -*-

from typing import Dict, List, Optional

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

    def GetListNameArguments(self) -> List[str]:
        return list(self._args.keys())

    def GetValueArgument(self, name) -> float:
        if name not in self._args.keys():
            raise ListArgumentsException(21, 'Unknown Name for Argument')

        try:
            value = self._args[name]()
        except NodeException as err:
            raise ListArgumentsException(23, f'Unknown Value for Argument {name}')

        return value

    def __len__(self) -> int:
        return len(self._args)

    def __call__(self, args = None) -> Dict[str, float]:
        if not args is None and type(args) != ListArguments:
            raise ListArgumentsException(13, 'Unknown Type Arguments')

        if not args is None:
            ls = args.GetListNameArguments()
            for name, arg in self._args.items():
                try:
                    if name in ls:
                        self._args[name].SetValue(args.GetValueArgument(name))
                except NodeException:
                    raise ListArgumentsException(31, f"Can't Set Value of Argument {name}")

        values: Dict[str, float] = dict()

        for name, arg in self._args.items():
            try:
                values[name] = self._args[name]()
            except NodeException:
                raise ListArgumentsException(17, f'No Value for Argument {name}')

        return values

    def __eq__(self, other):
        if type(other) != ListArguments:
            raise ListArgumentsException(11, 'Uncorrect Type Argument to Compare')

        return set(self._args.keys()) == set(other._args.keys())