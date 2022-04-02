__author__ = "McRussian Andrey"

# -*- coding: utf8 -*-

from typing import Dict, List

from .node import ArgumentNode
from GeneticProgramming.genetic_programming.gp_lib import ListArgumentsException, NodeException


class ListArguments:
    def __init__(self):
        self._args: Dict[str, ArgumentNode] = dict()

    def append_argument(self, arg: ArgumentNode):
        if type(arg) != ArgumentNode:
            raise ListArgumentsException(1, 'Uncorrected Type Argument to Append')

        name = arg.get_name()
        if name not in self._args:
            self._args[name] = arg

    def set_value_argument(self, name: str = None, value: float = None):
        if name is None or value is None:
            raise ListArgumentsException(5, 'Unknown arguments for SetValueArgument')

        if name not in self._args.keys():
            raise ListArgumentsException(7, 'Unknown Name of Argument')

        self._args[name].set_value(value)

    def get_name_arguments(self) -> List[str]:
        return list(self._args.keys())

    def get_value_argument(self, name) -> float:
        if name not in self._args.keys():
            raise ListArgumentsException(21, 'Unknown Name for Argument')

        try:
            value = self._args[name]()
        except NodeException as err:
            raise ListArgumentsException(23, f'Unknown Value for Argument {name}')

        return value

    def __len__(self) -> int:
        return len(self._args)

    def __call__(self, args=None) -> Dict[str, float]:
        if args is not None and type(args) != ListArguments:
            raise ListArgumentsException(13, 'Unknown Type Arguments')

        if args is not None:
            ls = args.get_name_arguments()
            for name, arg in self._args.items():
                try:
                    if name in ls:
                        self._args[name].set_value(args.get_value_argument(name))
                except NodeException:
                    raise ListArgumentsException(31, f"Can't Set Value of Argument {name}")

        values: Dict[str, float] = dict()

        for name, arg in self._args.items():
            try:
                values[name] = arg()
            except NodeException:
                raise ListArgumentsException(17, f'No Value for Argument {name}')

        return values

    def __eq__(self, other):
        if type(other) != ListArguments:
            raise ListArgumentsException(11, 'Uncorrected Type Argument to Compare')

        return set(self._args.keys()) == set(other._args.keys())
