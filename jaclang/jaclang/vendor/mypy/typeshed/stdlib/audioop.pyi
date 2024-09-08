from typing_extensions import TypeAlias

_AdpcmState: TypeAlias = tuple[int, int]
_RatecvState: TypeAlias = tuple[int, tuple[tuple[int, int], ...]]

class error(Exception): ...

def add(fragment1: bytes, fragment2: bytes, width: int, /) -> bytes: ...
def adpcm2lin(fragment: bytes, width: int, state: _AdpcmState | None, /) -> tuple[bytes, _AdpcmState]: ...
def alaw2lin(fragment: bytes, width: int, /) -> bytes: ...
def avg(fragment: bytes, width: int, /) -> int: ...
def avgpp(fragment: bytes, width: int, /) -> int: ...
def bias(fragment: bytes, width: int, bias: int, /) -> bytes: ...
def byteswap(fragment: bytes, width: int, /) -> bytes: ...
def cross(fragment: bytes, width: int, /) -> int: ...
def findfactor(fragment: bytes, reference: bytes, /) -> float: ...
def findfit(fragment: bytes, reference: bytes, /) -> tuple[int, float]: ...
def findmax(fragment: bytes, length: int, /) -> int: ...
def getsample(fragment: bytes, width: int, index: int, /) -> int: ...
def lin2adpcm(fragment: bytes, width: int, state: _AdpcmState | None, /) -> tuple[bytes, _AdpcmState]: ...
def lin2alaw(fragment: bytes, width: int, /) -> bytes: ...
def lin2lin(fragment: bytes, width: int, newwidth: int, /) -> bytes: ...
def lin2ulaw(fragment: bytes, width: int, /) -> bytes: ...
def max(fragment: bytes, width: int, /) -> int: ...
def maxpp(fragment: bytes, width: int, /) -> int: ...
def minmax(fragment: bytes, width: int, /) -> tuple[int, int]: ...
def mul(fragment: bytes, width: int, factor: float, /) -> bytes: ...
def ratecv(
    fragment: bytes,
    width: int,
    nchannels: int,
    inrate: int,
    outrate: int,
    state: _RatecvState | None,
    weightA: int = 1,
    weightB: int = 0,
    /,
) -> tuple[bytes, _RatecvState]: ...
def reverse(fragment: bytes, width: int, /) -> bytes: ...
def rms(fragment: bytes, width: int, /) -> int: ...
def tomono(fragment: bytes, width: int, lfactor: float, rfactor: float, /) -> bytes: ...
def tostereo(fragment: bytes, width: int, lfactor: float, rfactor: float, /) -> bytes: ...
def ulaw2lin(fragment: bytes, width: int, /) -> bytes: ...
