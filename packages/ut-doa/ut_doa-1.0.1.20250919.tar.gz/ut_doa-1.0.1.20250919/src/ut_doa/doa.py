# coding=utf-8
from collections.abc import Callable
from typing import Any

from ut_dic.dic import Dic

TyAny = Any
TyArr = list[Any]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyDoA = dict[Any, TyArr]
TyAoD = list[TyDic]
TyKey = Any
TyKeys = Any | TyArr
TyStr = str
TyTup = tuple[Any, ...]
TyArrTup = TyArr | TyTup

TnAny = None | Any
TnArr = None | TyArr
TnDoA = None | TyDoA
TnCallable = None | TyCallable
TnDic = None | TyDic
TyDoAoD = dict[Any, TyAoD]
TnKey = None | TyKey
TnKeys = None | TyKeys


class DoA:
    """
    Manage Dictionary of Arrays
    """
    @staticmethod
    def append_by_key(
            doa: TyDoA, key: TyAny, value: TnAny, item: TnAny = None) -> None:
        """
        append the item to the value of the dictionary of Arrays
        for the given key if the item is not contained in the value.
        """
        if item is None:
            item = []
        elif not isinstance(item, list):
            item = [item]
        if key not in doa:
            doa[key] = item
        doa[key].append(value)

    @staticmethod
    def append_unique_by_key(
            doa: TyDoA, key: TyAny, value: TnAny, item: TnAny = None) -> None:
        """assign item to dictionary defined as value
           for the given keys.
        """
        if item is None:
            item = []
        elif not isinstance(item, list):
            item = [item]
        if key not in doa:
            doa[key] = item
        if value not in doa[key]:
            doa[key].append(value)

    @staticmethod
    def sh_union(doa: TyDoA) -> TyArr:
        arr_new = []
        for _key, _arr in doa.items():
            arr_new.extend(_arr)
        return arr_new

    @staticmethod
    def extend_by_keys(
            doa: TyDoA, keys: TyKeys, value: TyAny) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _doa = Dic.locate_before_last(doa, keys)

        # last keys element
        key = keys[-1]
        if isinstance(value, str):
            value = [value]
        if key not in _doa:
            _doa[key] = value
        else:
            _doa[key].extend(value)

    @staticmethod
    def extend_by_key(
            dic: TnDoA, key: TnKey, value: TyAny, item: TnAny = None
    ) -> None:
        """
        Add the item with the key as element to the dictionary if the key
        is undefined in the dictionary. Extend the element value with the
        value if it supports the extend function.
        """
        # def extend_value(
        if not dic:
            return
        if not isinstance(value, (list, tuple)):
            value = [value]
        if item is None:
            item = []
        # last element
        if key not in dic:
            dic[key] = item
        if isinstance(dic[key], (list, tuple)):
            dic[key].extend(value)

    @classmethod
    def apply_by_keys(
            cls, dic: TyDoA, keys: TyArr, fnc: TyCallable, value: TyAny, item: TnAny
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        # def apply(
        #        fnc: TyCallable, doa: TyDic, keys: TyArr, item: TyAny, item0: TnAny
        if item is None:
            item = []
        if keys is None:
            return
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _doa = cls.locate(dic, keys[:-1])
        cls.append_by_key(_doa, keys[-1], value, item)
        fnc(dic[keys[:-1]], item)

    @classmethod
    def append_unique_by_keys(
            cls, dic: TyDic, keys: TyArrTup, value: Any, item: TnAny = None
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        if dic is None or not keys:
            return
        if value is None:
            value = []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _doa = Dic.locate_before_last(dic, keys)
        DoA.append_unique_by_key(_doa, keys[-1], value, item)

    @classmethod
    def append_by_keys(
            cls, dic: TnDic, keys: TnKeys, value: Any, item: TnAny = None
    ) -> None:
        """
        Apply the function "append with key" to the last key of the key
        list amd the dictionary localized by that key.
        """
        if dic is None or not keys:
            return
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _doa = Dic.locate_before_last(dic, keys)
        DoA.append_by_key(_doa, keys[-1], value, item)
