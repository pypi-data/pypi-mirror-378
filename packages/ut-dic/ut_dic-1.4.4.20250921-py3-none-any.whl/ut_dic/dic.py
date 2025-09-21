# import builtins
from collections.abc import Callable, Iterator
from typing import Any

# from ut_log.log import Log
from ut_obj.obj import Obj

TyAny = Any
TyArr = list[Any]
TyBool = bool
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAny_Dic = Any | TyDic
TyAoD = list[TyDic]
TyIterAny = Iterator[Any]
TyKey = Any
TyTup = tuple[Any, ...]
TyKeys = Any | TyArr | TyTup
TyStr = str
TyArrTup = TyArr | TyTup
TyToD = tuple[TyDic, ...]
TyToDD = tuple[TyDic, TyDic]

TnAny = None | Any
TnAny_Dic = None | TyAny_Dic
TnAoD = None | TyAoD
TnArr = None | TyArr
TnArrTup = None | TyArr | TyTup
TnBool = None | bool
TnCallable = None | TyCallable
TnDic = None | TyDic
TnKey = None | TyKey
TnKeys = None | TyKeys


class Dic:
    """
    Dictionary Management
    """
    loc_msg1 = "The 1. Parameter 'dic' is None or empty"
    loc_msg2 = "The 2. Parameter 'keys' is None or empty"
    loc_msg3 = "Key={} does not exist in Sub-Dictionary={} of Dictionary={}"
    loc_msg4 = "Value={} is not a Sub-Dictionary of Dictionary={}"

    @classmethod
    def add_counter_by_keys(
            cls, dic: TyDic, keys: TyKeys, counter: Any = None) -> None:
        """
        Apply the function "add_counter_with key" to the last key of the
        key list and the dictionary localized by that key.
        """
        # def add_counter_to_values(
        if not isinstance(keys, (list, tuple)):
            cls.add_counter_by_key(dic, keys, counter)
        else:
            _dic: TnDic = cls.locate(dic, keys[:-1])
            cls.add_counter_by_key(_dic, keys[-1], counter)

    @staticmethod
    def add_counter_by_key(
            dic: TnDic, key: TyKey, counter: TyAny) -> None:
        # def cnt(
        """
        Initialize the unintialized counter with 1 and add it to the
        Dictionary value of the key.
        """
        # def add_counter_to_value(
        if not dic:
            return
        if counter is None:
            counter = 1
        if key not in dic:
            dic[key] = 0
        dic[key] = dic[key] + counter

    @staticmethod
    def filter_by_keys(dic: TyDic, keys: TyKeys) -> TyDic:
        """
        Filter Dictionary by a single key or an Array of Keys
        """
        if isinstance(keys, str):
            keys = [keys]
        dic_new: TyDic = {}
        for key, value in dic.items():
            if key in keys:
                dic_new[key] = value
        return dic_new

    @staticmethod
    def get_as_array(dic: TyDic, key: TyKey) -> TyArr:
        """
        show array of key value found for given key in dictionary
        """
        if not dic or not key:
            return []
        value: None | Any | TyArr = dic.get(key)
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    @staticmethod
    def get_by_keys(dic: TnDic, keys: TyKeys, default: Any = None) -> TnAny_Dic:
        # def get
        if dic is None:
            return None
        if not isinstance(keys, (list, tuple)):
            if keys in dic:
                return dic[keys]
            return default
        _dic = dic
        value = None
        for _key in keys:
            value = _dic.get(_key)
            if value is None:
                return None
            if not isinstance(value, dict):
                return value
            _dic = value
        return value

    @staticmethod
    def get_value_yn(
            dic: TyDic, key: str, value_y: Any, value_n: Any) -> Any:
        # def get_yn_value(dic: TyDic, key: str, value_y, value_n) -> Any:
        """
        Return value value_y if key is in dictionary otherwise
        return value value_n
        """
        if key in dic:
            return value_y
        return value_n

    @staticmethod
    def get(dic: TyDic, key: TyKey, default: Any = None) -> TnAny:
        # def get
        """
        Loop thru the nested dictionary with the keys from the
        key list until the key is found. If the last key of the
        key list is found return the value of the key, otherwise
        return None.
        """
        if dic is None:
            return None
        return dic.get(key, default)

    @classmethod
    def increment_by_keys(
            cls, dic: TnDic, keys: TnKeys, item: Any = 1) -> None:
        # def increment(
        """
        Appply the function "increment_by_key" to the last key of
        the key list and the dictionary localized by that key.
        """
        # def increment_values(
        # def increment_by_keys(
        if not dic or keys is None:
            return
        if not isinstance(keys, list):
            keys = [keys]
        cls.increment_by_key(cls.locate(dic, keys[:-1]), keys[-1], item)

    @staticmethod
    def increment_by_key(
            dic: TnDic, key: Any, item: Any = 1) -> None:
        """
        Increment the value of the key if it is defined in the
        Dictionary, otherwise assign the item to the key.
        """
        # def increment_value(
        # def increment_by_key(
        # last element
        if not dic:
            pass
        elif key not in dic:
            dic[key] = item
        else:
            dic[key] += 1

    @staticmethod
    def is_not(dic: TyDic, key: TyStr) -> TyBool:
        """
        Return False if the key is defined in the Dictionary and
        the key value if not empty, othewise returm True.
        """
        if key in dic:
            if dic[key]:
                return False
        return True

    @classmethod
    def locate(cls, dic: TyDic, keys: TyKeys) -> TyAny:
        """
        Return the value of the key reached by looping thru the
        nested Dictionary with the keys from the key list until
        the value is None or the last key is reached.
        """
        if not dic:
            raise Exception(cls.loc_msg1)
        if keys is None:
            return dic
        _dic: TyAny = dic
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        for _key in keys:
            if isinstance(_dic, dict):
                _dic_new = _dic.get(_key)
                if _dic_new is None:
                    raise Exception(cls.loc_msg3.format(_key, _dic, dic))
                _dic = _dic_new
            else:
                raise Exception(cls.loc_msg4.format(_dic, dic))
        return _dic

    @classmethod
    def locate_secondlast(cls, dic: TyDic, keys: TyKeys) -> Any:
        """
        locate the value by keys in a nested dictionary
        """
        return cls.locate(dic, keys[:-1])

    @staticmethod
    def lstrip_keys(dic: TyDic, string: TyStr) -> TyDic:
        """
        Remove the first string found in the Dictionary keys.
        """
        dic_new: TyDic = {}
        for k, v in dic.items():
            k_new = k.replace(string, "", 1)
            dic_new[k_new] = v
        return dic_new

    @classmethod
    def new(cls, keys: TyKeys, value: Any) -> TnDic:
        """ create a new Dictionary from keys and value
        """
        if value is None or keys is None:
            return None
        dic_new: TyDic = {}
        if isinstance(keys, str):
            dic_new[keys] = value
            return dic_new
        cls.set_by_keys(dic_new, keys, value)
        return dic_new

    @staticmethod
    def new_normalize_values(dic: TyDic) -> TyDic:
        # def normalize_values(dic: TyDic) -> TyDic:
        """
        Replace every Dictionary value by the first list element
        of the value if it is a list with only one element.
        """
        # def normalize_value(dic: TyDic) -> TyDic:
        dic_new: TyDic = {}
        for k, v in dic.items():
            # The value is a list with 1 element
            if isinstance(v, list) and len(v) == 1:
                dic_new[k] = v[0]
            else:
                dic_new[k] = v
        return dic_new

    @staticmethod
    def new_by_fset_split_keys(dic: TyDic) -> TyToDD:
        # def sh_d_vals_d_cols(dic: TyDic) -> TyToDD:
        """
        Create new dictionary from old by creating the new keys as frozenset
        of the split of the old keys with comma as separator.
        """
        d_cols: TyDic = {}
        d_vals: TyDic = {}
        for key, value in dic.items():
            a_key = key.split("_")
            if len(a_key) == 1:
                key0 = a_key[0]
                d_vals[key0] = value
            else:
                key0 = a_key[0]
                key1 = a_key[1]
                if key1 not in d_cols:
                    d_cols[key1] = {}
                d_cols[key1][key0] = value
        return d_vals, d_cols

    @staticmethod
    def new_by_split_keys(dic: TyDic) -> TyDic:
        # def sh_dic(dic: TyDic) -> TyDic:
        """
        Create new nested dictionary from old by creating the new keys
        as the comma separator split of the old keys.
        """
        dic_new = {}
        for key, value in dic.items():
            f_key = frozenset(key.split(','))
            dic_new[f_key] = value
        return dic_new

    # @staticmethod
    # def new_d_filter(key: str, value: Any, method: str = 'df') -> TyDoFilter:
    #   """
    #   Create new filter dictionary with key, value and method pairs
    #   """
    #   d_filter = {}
    #   d_filter['key'] = key
    #   d_filter['value'] = value
    #   d_filter['method'] = method
    #   return d_filter

    @staticmethod
    def new_make_values2keys(dic: TyDic) -> TyDic:
        # def sh_value2keys(dic: TyDic) -> TyDic:
        _dic_new: TyDic = {}
        for _k, _v in dic.items():
            _k_new = _v
            _v_new = _k
            if _k_new not in _dic_new:
                _dic_new[_k_new] = []
            if _v_new not in _dic_new[_k_new]:
                _dic_new[_k_new].extend(_v_new)
        return _dic_new

    @staticmethod
    def new_prefix_keys(dic: TyDic, prefix: str) -> TyDic:
        # def sh_prefixed(dic: TyDic, prefix: str) -> TyDic:
        """
        Create new dictionary from old by using prefixed old keys as
        new keys and old values as new values.
        """
        _dic_new: TyDic = {}
        for _key, _value in dic.items():
            _key_new = f"{prefix}_{_key}"
            _dic_new[_key_new] = _value
        return _dic_new

    @staticmethod
    def new_rename_key(dic: TyDic, k_old: TyAny, k_new: TyAny) -> TyDic:
        # def rename_key(dic: TyDic, k_old: TyAny, k_new: TyAny) -> TyDic:
        """ rename old dictionary key with new dictionary key
        """
        _dic_new: TyDic = {k_new if k == k_old else k: v for k, v in dic.items()}
        return _dic_new

    @staticmethod
    def new_replace_string_in_keys(dic: TyDic, old: Any, new: Any) -> TyDic:
        # def replace_string_in_keys(
        # def replace_keys(
        if not dic:
            return dic
        dic_new = {}
        for key, value in dic.items():
            key_ = key.replace(old, new)
            dic_new[key_] = value
        return dic_new

    @staticmethod
    def new_round_values(dic: TyDic, keys: TnKeys, kwargs: TyDic) -> TyDic:
        # def round_values(
        # def round_value
        round_digits: int = kwargs.get('round_digits', 2)
        if not dic:
            msg = f"Parameter dic = {dic} is undefined"
            raise Exception(msg)
        if not keys:
            return dic
        dic_new: TyDic = {}
        for key, value in dic.items():
            if value is None:
                dic_new[key] = value
            else:
                if key in keys:
                    dic_new[key] = round(value, round_digits)
                else:
                    dic_new[key] = value
        return dic_new

    @staticmethod
    def nvl(dic: TnDic) -> TyDic:
        """
        nvl function similar to SQL NVL function
        """
        if dic is None:
            return {}
        return dic

    @classmethod
    def rename_key_by_kwargs(cls, dic: TnDic, kwargs: TyDic) -> TnDic:
        """ rename old dictionary key with new dictionary key by kwargs
        """
        # def rename_key(
        # Dictionary is None or empty
        if not dic:
            return dic
        key_old = kwargs.get("key_old")
        key_new = kwargs.get("key_new")
        return cls.new_rename_key(dic, key_old, key_new)

    @classmethod
    def set_by_keys(cls, dic: TyDic, keys: TyKeys, value: Any) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        _dic = cls.locate_secondlast(dic, keys)
        if not _dic:
            return
        cls.set_by_key(_dic, keys[-1], value)

    @staticmethod
    def set_by_key(dic: TyDic, key: TyKey, value: TnAny) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not dic:
            return
        if not key:
            return
        dic[key] = value

    @classmethod
    def add_by_keys(cls, dic: TyDic, keys: TyKeys, value: TnAny) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not dic:
            return
        if not keys:
            return
        _dic = cls.locate_secondlast(dic, keys)
        cls.add_by_key(_dic, keys[-1], value)

    @staticmethod
    def add_by_key(dic: TyDic, key: TyKey, value: TnAny) -> None:
        """
        Locate the values in a nested dictionary for the suceeding keys of
        a key array and replace the last value with the given value.
        """
        if not dic:
            return
        if not key:
            return
        if key not in dic:
            dic[key] = value

    # @classmethod
    # def set_kv_not_none(cls, dic: TyDic, key: TnAny, value: TnAny) -> None:
    #     """
    #     Set the given Dictionary key to the given value if both are not None.
    #     """
    #     if key is None:
    #         return
    #     if value is None:
    #         return
    #     dic[key] = value

    @staticmethod
    def set_by_key_pair(dic: TyDic, src_key: Any, tgt_key: Any) -> None:
        """
        Replace value of source key by value of target key.
        """
        if src_key in dic and tgt_key in dic:
            dic[tgt_key] = dic[src_key]

    # @classmethod
    # def set_if_none(cls, dic: TyDic, keys: TyKeys, value_last: Any) -> None:
    #     """
    #     Locate the values in a nested dictionary for the suceeding keys of a
    #     key array and assign the given value to the last key if that key does
    #     not exist in the dictionary.
    #     """
    #     if not isinstance(keys, (list, tuple)):
    #         keys = [keys]
    #     _dic = cls.locate(dic, keys[:-1])
    #     if not _dic:
    #         return
    #     # last element
    #     key_last = keys[-1]
    #     if key_last not in _dic:
    #         _dic[key_last] = value_last

    @staticmethod
    def set_by_div(dic: TnDic, key: str, key1: str, key2: str) -> None:
        """
        Replace the source key value by the division of the values of two
        target keys if they are of type float and the divisor is not 0.
        """
        # Dictionary is None or empty
        if not dic:
            return
        if key1 in dic and key2 in dic:
            _val1 = dic[key1]
            _val2 = dic[key2]
            if (isinstance(_val1, (int, float)) and
               isinstance(_val2, (int, float)) and
               _val2 != 0):
                dic[key] = _val1/_val2
            else:
                dic[key] = None
        else:
            dic[key] = None

    # @staticmethod
    # def set_divide(
    #         dic: TnDic, key: Any, key1: Any, key2: Any) -> None:
    #     """ divide value of key1 by value of key2 and
    #         assign this value to the key
    #     """
    #     # Dictionary is None or empty
    #     if not dic:
    #         return
    #     if key1 in dic and key2 in dic:
    #         _val1 = dic[key1]
    #         _val2 = dic[key2]
    #         if (isinstance(_val1, (int, float)) and
    #            isinstance(_val2, (int, float)) and
    #            _val2 != 0):
    #             dic[key] = _val1/_val2
    #         else:
    #             dic[key] = None
    #     else:
    #         dic[key] = None

    @staticmethod
    def set_format_value(dic: TnDic, key: Any, fmt: Any) -> None:
        """
        Replace the dictionary values by the formatted values by the given
        format string
        """
        if not dic:
            return
        if key in dic:
            value = dic[key]
            dic[key] = fmt.format(value)

    @staticmethod
    def set_multiply_with_factor(
            dic: TnDic, key_new: Any, key: Any, factor: Any) -> None:
        """
        Replace the dictionary values by the original value multiplied with the factor
        """
        # Dictionary is None or empty
        if not dic:
            return
        if key not in dic:
            return
        if dic[key] is None:
            dic[key_new] = None
        else:
            dic[key_new] = dic[key] * factor

    @classmethod
    def sh_bool(cls, dic: TyDic, keys: TyKeys, switch: bool = False) -> bool:
        """
        locate the value by keys in a nested dictionary
        """
        value = cls.locate(dic, keys)
        if value is None:
            return switch
        if isinstance(value, bool):
            return value
        return switch

    @staticmethod
    def sh_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        """
        show array of keys of key list found in dictionary.
        """
        if not dic or not keys:
            return []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        arr = []
        for key in keys:
            if key in dic:
                arr.append(key)
        return arr

    @staticmethod
    def show_sorted_keys(dic: TnDic) -> TyArr:
        """
        show sorted array of keys of dictionary.
        """
        if not dic:
            return []
        a_key: TyArr = list(dic.keys())
        a_key.sort()
        return a_key

    @staticmethod
    def sh_value_by_keys(dic: TyDic, keys: TyKeys, default: Any = None) -> Any:
        """
        """
        # def sh_value(dic: TyDic, keys: TyKeys, default: Any = None) -> Any:
        if not dic:
            return dic
        if not keys:
            return dic
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        _dic = dic
        value = None
        for key in keys:
            value = _dic.get(key)
            if value is None:
                return default
            if isinstance(value, dict):
                _dic = value
            else:
                if value is None:
                    return default
                return value
        return value

    @staticmethod
    def sh_values_by_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        # def sh_values_by_keys(dic: TyDic, keys: TyKeys) -> TyArr:
        """ locate the value for keys in a nested dictionary
        """
        # def sh_values
        if not dic or not keys:
            return []
        if not isinstance(keys, (list, tuple)):
            keys = [keys]
        arr = []
        for key in keys:
            if key in dic:
                arr.append(dic[key])
        return arr

    @staticmethod
    def split_by_key(dic: TnDic, key: TnAny) -> TyTup:
        # Dictionary is None or empty
        if not dic or not key:
            return dic, None
        dic_new = {}
        obj_new = None
        for k, v in dic.items():
            if k == key:
                obj_new = v
            else:
                dic_new[k] = v
        return obj_new, dic_new

    @staticmethod
    def split_by_value(dic: TyDic, value: Any) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        dic0 = {}
        dic1 = {}
        for k, v in dic.items():
            if v == value:
                dic0[k] = v
            else:
                dic1[k] = v
        return dic0, dic1

    @staticmethod
    def split_by_value_endswith(dic: TyDic, value: Any) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        dic0 = {}
        dic1 = {}
        for k, v in dic.items():
            if v.endswith(value):
                dic0[k] = v
            else:
                dic1[k] = v
        return dic0, dic1

    @staticmethod
    def split_by_value_is_int(dic: TyDic) -> TyTup:
        # Dictionary is None or empty
        if not dic:
            return dic, dic
        dic0 = {}
        dic1 = {}
        for k, v in dic.items():
            if v.isdigit():
                dic0[k] = v
            else:
                dic1[k] = v
        return dic0, dic1

    @staticmethod
    def to_aod(dic: TyDic, key_name: Any, value_name: Any) -> TyAoD:
        # def dic2aod(
        # Dictionary is None or empty
        if not dic:
            aod = [dic, dic]
        aod = []
        _dic = {}
        for k, v in dic.items():
            _dic[key_name] = k
            _dic[value_name] = v
            aod.append(_dic)
            _dic = {}
        return aod

    class Names:

        @staticmethod
        def sh(d_data: TyDic, key: str = 'value') -> Any:
            try:
                return Obj.extract_values(d_data, key)
            except Exception:
                return []

        @classmethod
        def sh_item0(cls, d_names: TyDic) -> Any:
            names = cls.sh(d_names)
            if not names:
                return None
            return names[0]

        @classmethod
        def sh_item0_if(cls, string: str, d_names: TyDic) -> Any:
            names = cls.sh(d_names)
            if not names:
                return None
            if string in d_names[0]:
                return names[0]
            return None

    # class Key:
    #
    #   @staticmethod
    #   def change(dic: TyDic, source_key: TyDic, target_key: TyDic) -> TyDic:
    #       if source_key in dic:
    #           dic[target_key] = dic.pop(source_key)
    #       return dic
    #
    # class Value:
    #
    #   @staticmethod
    #   def get(dic: TyDic, keys: TyKeys, default: Any = None) -> TnDic:
    #       if keys is None:
    #           return dic
    #       if not isinstance(keys, (list, tuple)):
    #           keys = [keys]
    #       if len(keys) == 0:
    #           return dic
    #       value = dic
    #       for key in keys:
    #           if key not in value:
    #               return default
    #           value = value[key]
    #           if value is None:
    #               break
    #       return value
    #
    #   @classmethod
    #   def set(cls, dic: TnDic, keys: TnKeys, value: Any) -> None:
    #       if value is None:
    #           return
    #       if dic is None:
    #           return
    #       if keys is None:
    #           return
    #
    #       if not isinstance(keys, (list, tuple)):
    #           keys = [keys]
    #
    #       value_curr = cls.get(dic, keys[:-1])
    #       if value_curr is None:
    #           return
    #       last_key = keys[-1]
    #       if last_key in value_curr:
    #           value_curr[last_key] = value
    #
    #   @staticmethod
    #   def is_empty_value(value: Any) -> bool:
    #       if value is None:
    #           return True
    #       if isinstance(value, str):
    #           if value == '':
    #               return True
    #       elif isinstance(value, (list, tuple)):
    #           if value == []:
    #               return True
    #       elif isinstance(value, dict):
    #           if value == {}:
    #               return True
    #       return False
    #
    #   @classmethod
    #   def is_empty(cls, dic: TnDic, keys: TyArrTup) -> bool:
    #       if dic is None:
    #           return True
    #       if not isinstance(keys, (tuple, list)):
    #           keys = [keys]
    #       if isinstance(keys, (list, tuple)):
    #           value = cls.get(dic, keys)
    #           return cls.is_empty_value(value)
    #       return False
    #
    #   @classmethod
    #   def is_not_empty(cls, dic: TnDic, keys: TyArrTup) -> bool:
    #       return not cls.is_empty(dic, keys)
