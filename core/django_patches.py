"""Runtime compatibility patches for Django behavior.

This patch fixes a Python 3.14 incompatibility with Django 4.2.x BaseContext.__copy__.
"""

from copy import copy
from django.template import context as template_context


def patch_base_context_copy():
    BaseContext = template_context.BaseContext

    def __copy__(self):
        duplicate = self.__class__.__new__(self.__class__)
        if hasattr(self, '__dict__'):
            duplicate.__dict__.update(self.__dict__)
        duplicate.dicts = self.dicts[:]
        return duplicate

    BaseContext.__copy__ = __copy__


patch_base_context_copy()
