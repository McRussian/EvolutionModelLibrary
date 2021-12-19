__author__ = "McRussian Andrey"
# -*- coding: utf8 -*-

from random import random

from GeneticProgramming.genetic_programming.gp_lib import NodeException

class BaseNode:
    '''
    Базовый класс для узла дерева-функции
    Любой объект-наследник должен определить методы
    __str__, __call__
    '''
    def __call__(self, *args, **kwargs):
        raise NotImplemented

    def __str__(self):
        raise NotImplemented


class ConstantNode (BaseNode):
    '''
    Объект этого класса представляет собой константу
    Значение константы задается при создании, либо в виде аргумента
    либо случайное число (-50, 50)
    Объект-функтор, при вызове его как функции возвращает значение константы
    '''

    def __init__(self, value: float = None):
        if value is None:
            self.__value = random() * 100.0 - 50.0
        else:
            if type(value) == float or type(value) == int:
                self.__value = float(value)
            else:
                self.__value = None

    def __call__(self, *args, **kwargs):
        if self.__value is None:
            raise NodeException(code=101, error='Value Constant not Define')

        return self.__value

    def __str__(self):
        return str(self.__value)

    def __eq__(self, other):
        if (type(other) != ConstantNode):
            return False
        return self.__value == other()

