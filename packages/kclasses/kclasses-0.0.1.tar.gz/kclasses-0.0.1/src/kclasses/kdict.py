from kclasses.klist import klist
from typing import Callable


class kdict(dict):
    """Extension of dict class including functions I thought would be helpful"""
    def foreach_key(self, f: Callable) -> 'kdict':
        """Return a kdict where function 'f(x) -> y' is applied to each key of kdict (map(f, kdict.keys()))"""
        ret: kdict = kdict()
        for k, v in self.items():
            ret[f(k)] = v
        return ret
    
    def foreach_value(self, f: Callable) -> 'kdict':
        """Return a kdict where function 'f(x) -> y' is applied to each value of kdict (map(f, kdict.values()))"""
        ret: kdict = kdict()
        for k, v in self.items():
            ret[k] = f(v)
        return ret
    
    def where_key(self, f: Callable) -> 'kdict': 
        """Return a kdict where function 'f(x) -> bool' is true for all keys (filter(f, kdict.keys()))"""
        ret: kdict = kdict()
        for k, v in self.items():
            if f(k): ret[k] = v
        return ret
    
    def where_value(self, f: Callable) -> 'kdict': 
        """Return a kdict where function 'f(x) -> bool' is true for all values (filter(f, kdict.values()))"""
        ret: kdict = kdict()
        for k, v in self.items():
            if f(v): ret[k] = v
        return ret 
    
    def length(self) -> int:
        """Return the length of the kdict (len)"""
        return len(self)
    
    def swap_kv(self) -> 'kdict':
        """Return a kdict where the keys and values are swapped"""
        ret: kdict = kdict()
        for k, v in self.items():
            ret[v] = k
        return ret
    
    def swap_kv_hashmap(self) -> 'kdict':
        """Return a kdict where the keys and values are swapped; values should be a list"""
        v = list(self.values())[0]
        if isinstance(v, (tuple, list, set)): return self.__swap_kv_hashmap_value_is_list()
        return self.__swap_kv_hashmap_group_keys()
    
    def __swap_kv_hashmap_value_is_list(self) -> 'kdict':
        """Helper function; value is list (proper hashmap)"""
        ret: kdict = kdict()
        for k, v in self.items():
            for e in v:
                ret[e] = k
        return ret
    
    def __swap_kv_hashmap_group_keys(self) -> 'kdict':
        """Helper function; values are categorical and keys should be grouped into values (make hashmap)"""
        ret: kdict = kdict()
        for k, v in self.items():
            if v in ret: ret[v].append(k)
            else: ret[v] = klist([k])
        return ret