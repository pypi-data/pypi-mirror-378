from typing import Callable


class klist(list):
    """Extension of list class including JS/C# type functions"""
    def foreach(self, f: Callable) -> 'klist':
        """Return a klist where function 'f(x) -> y' is applied to each element of klist (map)"""
        return klist(map(f, self))
    
    def where(self, f: Callable) -> 'klist': 
        """Return a klist where function 'f(x) -> bool' is true for all members (filter)"""
        return klist(filter(f, self))
    
    def reduce(self, f: Callable) -> object:
        """Apply function 'f(x, y) -> z' such that klist collapses to a single value"""
        def helper(f: Callable, arr: 'klist') -> object:
            if len(arr) == 0: return None
            elif len(arr) == 1: return arr[0]
            x, y = arr.pop(), arr.pop()
            arr.append(f([x, y]))
            return helper(f, arr)
        arr: 'klist' = self.copy()
        return helper(f, arr)
    
    def flatten(self) -> 'klist':
        """Return a collapsed 1-D klist"""
        ret: 'klist' = klist()
        for item in self:
            if isinstance(item, (tuple, list, klist)): ret.extend(klist(item).flatten())
            else: ret.append(item)
        return ret
    
    def length(self) -> int:
        """Return the length of the klist (len)"""
        return len(self)