from kclasses.klist import *
from typing import Callable


class ktuple(tuple):
    """Extension of tuple class including JS/C# type functions and more"""
    def foreach(self, f: Callable) -> 'ktuple':
        """Return a ktuple where function 'f(x) -> y' is applied to each element of ktuple (map)"""
        return ktuple(map(f, self))
    
    def where(self, f: Callable) -> 'ktuple': 
        """Return a ktuple where function 'f(x) -> bool' is true for all members (filter)"""
        return ktuple(filter(f, self))
    
    def reduce(self, f: Callable) -> object:
        """Apply function 'f(x, y) -> z' such that ktuple collapses to a single value"""
        def helper(f: Callable, arr: klist) -> object:
            if len(arr) == 0: return None
            elif len(arr) == 1: return arr[0]
            x, y = arr.pop(), arr.pop()
            arr.append(f([x, y]))
            return helper(f, arr)
        arr: klist = klist(self)
        return helper(f, arr)
    
    def flatten(self) -> 'ktuple':
        """Return a collapsed 1-D ktuple"""
        ret: klist = klist()
        for item in self:
            if isinstance(item, (tuple, list, ktuple, set)): ret.extend(klist(item).flatten())
            else: ret.append(item)
        return ktuple(ret)
    
    def length(self) -> int:
        """Return the length of the ktuple (len)"""
        return len(self)
    
    def zip_map(self, f: Callable[[tuple[object]], object], *args: tuple[object]) -> 'ktuple':  # TODO: should I raise or return errors?
        """Return a ktuple such that function f is called with the i-th element of each ktuple grouped together as the parameter (args) for f."""
        if ex := self.__match_lengths(args): raise ex
        kargs = ktuple(args).foreach(lambda arg : ktuple(arg))
        ret = klist()
        for idx in range(self.length()):
            params = klist([self[idx]])
            for karg in kargs:
                params.append(karg[idx])
            try: ret.append(f(ktuple(params)))
            except: 
                try: ret.append(f(ktuple(*params)))
                except: raise Exception()
        return ktuple(ret)
    
    def addition(self, *args: tuple[object]) -> 'ktuple': 
        """Return a ktuple where the i-th element of each ktuple is added together\n
        <code>(1, 8).addition((2, 1)) -> (3, 9)</code><br>
        <code>(1, 2, 3).addition((40)) -> err  # different shapes</code><br>
        <code>(1, 3, 4).addition((80, 9, 12), (9, 2, 1), (8, 8, 8)) -> (98, 22, 25)</code>"""
        return self.zip_map(lambda karg : sum(karg), *args)
        
    def subtraction(self, *args: tuple[object]) -> 'ktuple': 
        """Return a ktuple where the i-th element of each ktuple is subtracted from one another\n
        <code>(1, 8).subtraction((2, 1)) -> (-1, 7)</code><br>
        <code>(1, 2, 3).subtraction((40)) -> err  # different shapes</code><br>
        <code>(1, 3, 4).subtraction((80, 9, 12), (9, 2, 1), (8, 8, 8)) -> (-96, -16, -17)</code>"""
        def helper(karg: ktuple):
            ret = karg[0]
            for i in range(1, karg.length()): ret -= karg[i]
            return ret
        return self.zip_map(lambda karg : helper(karg), *args)
    
    def multiplication(self, *args: tuple[object]) -> 'ktuple': 
        """Return a ktuple where the i-th element of each ktuple is multiplied together\n
        <code>(1, 8).multiplication((2, 1)) -> (2, 8)</code><br>
        <code>(1, 2, 3).multiplication((40)) -> err  # different shapes</code><br>
        <code>(1, 3, 4).multiplication((80, 9, 12), (9, 2, 1), (8, 8, 8)) -> (5760, 432, 384)</code>"""
        def helper(karg: ktuple):
            ret = karg[0]
            for i in range(1, karg.length()): ret *= karg[i]
            return ret
        return self.zip_map(lambda karg : helper(karg), *args)
    
    def division(self, *args: tuple[object]) -> 'ktuple': 
        """Return a ktuple where the i-th element of each ktuple is divided by one another\n
        <code>(1, 8).division((2, 1)) -> (0.5, 8.0)</code><br>
        <code>(1, 2, 3).division((40)) -> err  # different shapes</code><br>
        <code>(1, 3, 4).division((80, 9, 12), (9, 2, 1), (8, 8, 8)) -> (0.00017361111111111112, 0.020833333333333332, 0.041666666666666664)</code>"""
        def helper(karg: ktuple):
            ret = karg[0]
            for i in range(1, karg.length()): ret /= karg[i]
            return ret
        return self.zip_map(lambda karg : helper(karg), *args)
    
    def floor_division(self, *args: tuple[object]) -> 'ktuple': 
        """Return a ktuple where the i-th element of each ktuple is floor divided by one another\n
        <code>(1, 8).floor_division((2, 1)) -> (0, 8)</code><br>
        <code>(1, 2, 3).floor_division((40)) -> err  # different shapes</code><br>
        <code>(1, 3, 4).floor_division((80, 9, 12), (9, 2, 1), (8, 8, 8)) -> (0, 0, 0)</code>"""
        def helper(karg: ktuple):
            ret = karg[0]
            for i in range(1, karg.length()): ret //= karg[i]
            return ret
        return self.zip_map(lambda karg : helper(karg), *args)
    
    def modulo(self, *args: tuple[object]) -> 'ktuple': 
        """Return a ktuple of remainders where the i-th element of each ktuple is divided by one another\n
        <code>(1, 8).modulo((2, 1)) -> (1, 0)</code><br>
        <code>(1, 2, 3).modulo((40)) -> err  # different shapes</code><br>
        <code>(1, 3, 4).modulo((80, 9, 12), (9, 2, 1), (8, 8, 8)) -> (1, 1, 0)</code>"""
        def helper(karg: ktuple):
            ret = karg[0]
            for i in range(1, karg.length()): ret %= karg[i]
            return ret
        return self.zip_map(lambda karg : helper(karg), *args)

    def __match_lengths(self, kargs: tuple[tuple[object]]) -> Exception | None: 
        """Return None if all args are collection-esque AND they all have the same length of self; an Exception otherwise"""
        if not isinstance(kargs, (ktuple, tuple, list, set)): 
            return Exception("kargs is not valid collection type")
        if not ktuple(kargs).where(lambda karg : ktuple(karg).length() == self.length()).length() == ktuple(kargs).length():
            return Exception("Not every 'karg' has the same length")
