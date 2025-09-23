# coding=utf-8
from typing import Any, TypeAlias

import pandas as pd

# from ut_aod.aod import AoD
from ut_dic.dic import Dic
from ut_arr.aoa import AoA

TyArr = list[Any]
TyAoA = list[TyArr]
TyBool = bool
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyAoAoD = list[TyAoD]
TyPdDf: TypeAlias = pd.DataFrame
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[Any, TyPdDf]
TyKeys = str | TyArr
TyStr = str

TnAoA = None | TyAoA


class DoAoD:

    @staticmethod
    def is_dic_value_empty(
            doaod: TyDoAoD, key: TyStr, sw_raise: TyBool = False) -> TyBool:
        """Check if all keys of the given Dictionary of Arrays of Dictionaries
           are found in any Dictionary of the Array of Dictionaries and the
           value for the key is not empty.
        """
        # def dic_value_is_empty(doaod: TyDoAoD, key: str) -> bool:
        for _key, _aod in doaod.items():
            for _dic in _aod:
                if not _dic:
                    pass
                elif not _dic.get(key):
                    if not sw_raise:
                        return True
                    msg = f"Value for key={key} in dictionary of aod={_dic} is empty"
                    raise Exception(msg)
        return False

    # @classmethod
    # def sh_aod_unique(cls, doaod: TyDoAoD, keys: TyKeys) -> TyAoD:
    #     """Convert Dictionary of Arrays of Dictionaries to unique Array of
    #        Dictionaries.
    #     """
    #     aod: TyAoD = AoD.sh_unique(cls.sh_aod(doaod, keys))
    #     return aod

    # @staticmethod
    # def sh_aod(doaod: TyDoAoD, keys: TyKeys) -> TyAoD:
    #     """Convert Dictionary of Arrays of Dictionaries to Array of Dictionaries.
    #     """
    #     if isinstance(keys, str):
    #         keys = [keys]
    #     key0 = keys[0]
    #     aod: TyAoD = doaod[key0]
    #     for key in keys[1:]:
    #         aod = aod + doaod[key]
    #     return aod

    @staticmethod
    def sh_d_pddf(doaod: TyDoAoD) -> TyDoPdDf:
        d_df = {}
        for key, aod in doaod.items():
            df: TyPdDf = pd.DataFrame(aod)
            d_df[key] = df
        return d_df

    @staticmethod
    def sh_unique(doaod: TyDoAoD) -> TyDoAoD:
        """Convert Dictionary of Arrays of Dictionaries to Array of unique Dictionaries.
        """
        doaod_new: TyDoAoD = {}
        for key, aod in doaod.items():
            # doaod_new[key] = AoD.sh_unique(aod)
            doaod_new[key] = list(set(aod))
        return doaod_new

    @staticmethod
    def union_distinct_set_by_keys(doaod: TyDoAoD, keys: TyKeys) -> TyAoD:
        """Convert filtered Dictionary of Arrays of Dictionaries by keys to an Array
           of distinct Dictionaries
        """
        _aoa: TyAoA = Dic.sh_values_by_keys(doaod, keys)
        _aod: TyAoD = AoA.union_distinct_set(_aoa)
        return _aod

    @staticmethod
    def union_distinct_set(doaod: TyDoAoD) -> TyAoD:
        """Convert Dictionary of Arrays of Dictionaries to an Array
           of distinct Dictionaries
        """
        _aoaod: TyAoAoD = list(doaod.values())
        _aod: TyAoD = AoA.union_distinct_set(_aoaod)
        return _aod
