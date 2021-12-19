__author__ = "McRussian Andrey"
# -*- coding: utf8 -*-


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

