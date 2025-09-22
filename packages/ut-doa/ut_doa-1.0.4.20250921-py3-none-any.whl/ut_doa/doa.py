# coding=utf-8
from collections.abc import Callable
from typing import Any

from ut_dic.dic import Dic

TyAny = Any
TyArr = list[Any]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyDoA = dict[Any, TyArr]
TyKey = Any
TyTup = tuple[Any, ...]
TyKeys = Any | TyArr | TyTup

TnAny = None | Any
TnArr = None | TyArr
TnDoA = None | TyDoA
TnCallable = None | TyCallable
TnDic = None | TyDic
TnKey = None | TyKey
TnKeys = None | TyKeys


class Item:
    """
    Manage Dictionary of Arrays
    """
    @staticmethod
    def sh(item: TnAny = None) -> TyArr:
        if isinstance(item, list):
            return item
        if item is None:
            _item: TyArr = []
        else:
            _item = [item]
        return _item


class DoA:
    """
    Manage Dictionary of Arrays
    """
    @staticmethod
    def append_by_key(
            doa: TyDoA, key: TyKey, value: TnAny, item: TnAny = None) -> None:
        """
        append the item to the value of the dictionary of Arrays
        for the given key if the item is not contained in the value.
        """
        if doa is None or not key:
            return
        if key not in doa:
            doa[key] = Item.sh(item)
        doa[key].append(value)

    @classmethod
    def append_by_keys(
            cls, doa: TyDoA, keys: TyKeys, value: Any, item: TnAny = None
    ) -> None:
        """
        Apply the function "append with key" to the last key of the key
        list amd the dictionary localized by that key.
        """
        if isinstance(keys, (list, tuple)):
            _doa = Dic.locate_secondlast(doa, keys)
            cls.append_by_key(_doa, keys[-1], value, item)
        else:
            cls.append_by_key(doa, keys, value, item)

    @staticmethod
    def append_unique_by_key(
            doa: TyDoA, key: TyKey, value: TnAny, item: TnAny = None) -> None:
        """assign item to dictionary defined as value
           for the given keys.
        """
        if not doa or not key:
            return
        if key not in doa:
            doa[key] = Item.sh(item)
        if value not in doa[key]:
            doa[key].append(value)

    @classmethod
    def append_unique_by_keys(
            cls, doa: TyDoA, keys: TyKeys, value: Any, item: TnAny = None
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        if isinstance(keys, (list, tuple)):
            _doa = Dic.locate_secondlast(doa, keys)
            cls.append_unique_by_key(_doa, keys[-1], value, item)
        else:
            cls.append_unique_by_key(doa, keys, value, item)

    @classmethod
    def xapply_by_keys(
            cls, doa: TyDoA, keys: TyKeys, fnc: TyCallable, value: TyAny, item: TnAny
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
        _doa = Dic.locate(doa, keys[:-1])
        cls.append_by_key(_doa, keys[-1], value, item)
        fnc(doa[keys[:-1]], item)

    @staticmethod
    def extend_by_key(
            doa: TnDoA, key: TnKey, value: TyAny, item: TnAny = None
    ) -> None:
        """
        Add the item with the key as element to the dictionary if the key
        is undefined in the dictionary. Extend the element value with the
        value if it supports the extend function.
        """
        # def extend_value(
        if not doa:
            return
        if key not in doa:
            doa[key] = Item.sh(item)
        if isinstance(value, (list, tuple)):
            doa[key].extend(value)
        else:
            doa[key].extend([value])

    @classmethod
    def extend_by_keys(
            cls, doa: TyDic, keys: TnKeys, value: TyAny, item: TnAny = None
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        if isinstance(keys, (list, tuple)):
            _doa = Dic.locate_secondlast(doa, keys)
            cls.extend_by_key(_doa, keys[-1], value, item)
        else:
            cls.extend_by_key(doa, keys, value, item)

    @staticmethod
    def sh_union(doa: TyDoA) -> TyArr:
        arr_new = []
        for _key, _arr in doa.items():
            arr_new.extend(_arr)
        return arr_new
