import re
from typing import Iterable, Optional, List, NamedTuple
from functools import lru_cache

_VERSION_RE = re.compile(r"^\d+(?:\.\d+)*(?:-\d+(?:\.\d+)*)?$").match
_is_ver = _VERSION_RE


def _to_list(v: str) -> List[int]:
    return [int(x) for x in v.split(".")] if v else []


def _cmp(a: List[int], b: List[int]) -> int:
    n = max(len(a), len(b))
    a += [0] * (n - len(a))
    b += [0] * (n - len(b))
    return (a > b) - (a < b)


class _VersionRange:
    """Одиночная версия, диапазон a‑b, 'last' или wildcard (None)."""

    __slots__ = ("raw", "kind", "lo", "hi", "single")

    def __init__(self, raw: Optional[str]):
        self.raw = raw             # None == wildcard
        if raw is None:
            self.kind = "wild"
            return
        if raw.lower() == "last":
            self.kind = "single_last"
            return
        if "-" in raw:
            self.kind = "range"
            lo, hi = raw.split("-", 1)
            self.lo = _to_list(lo)
            self.hi = _to_list(hi)
        else:
            self.kind = "single"
            self.single = _to_list(raw)

    def contains(self, ver: Optional[str]) -> bool:  # noqa: C901
        if self.kind == "wild":
            return True
        ver = ver or "last"
        if self.kind == "single_last":
            return ver.lower() == "last"
        if ver.lower() == "last":
            return False
        v = _to_list(ver)
        if self.kind == "single":
            return _cmp(self.single[:], v) == 0
        return _cmp(self.lo[:], v) <= 0 <= _cmp(v, self.hi[:])

    # for debugging / logs
    def __str__(self) -> str:
        return self.raw or "last"


class _Pat(NamedTuple):
    gn_ver: _VersionRange
    p1_name: Optional[str]
    p1_ver: _VersionRange
    p1_need_last: bool
    p2_name: Optional[str]
    p2_ver: _VersionRange
    p2_need_last: bool


@lru_cache(maxsize=2048)
def _compile_full_pattern(pat: str) -> _Pat:
    t = pat.split(":")
    gn_ver = _VersionRange(None)
    if t and t[0].lower() == "gn":
        t.pop(0)
        gn_ver = _VersionRange(t.pop(0)) if t and (_is_ver(t[0]) or t[0].lower() == "last") else _VersionRange(None)

    p2_name = p2_ver = p1_name = p1_ver = None
    p2_need_last = p1_need_last = False

    if t:
        if _is_ver(t[-1]) or t[-1].lower() == "last":
            p2_ver = _VersionRange(t.pop())
        else:
            p2_need_last = True
        p2_name = t.pop() if t else None

    if t:
        if _is_ver(t[-1]) or t[-1].lower() == "last":
            p1_ver = _VersionRange(t.pop())
        else:
            p1_need_last = True
        p1_name = t.pop() if t else None

    if t:
        raise ValueError(f"bad pattern {pat!r}")

    return _Pat(
        gn_ver=gn_ver,
        p1_name=None if p1_name is None else p1_name.lower(),
        p1_ver=p1_ver or _VersionRange(None),
        p1_need_last=p1_need_last,
        p2_name=None if p2_name is None else p2_name.lower(),
        p2_ver=p2_ver or _VersionRange(None),
        p2_need_last=p2_need_last,
    )


class _LeafPat(NamedTuple):
    name: Optional[str]
    ver: _VersionRange
    need_last: bool


@lru_cache(maxsize=4096)
def _compile_leaf_pattern(pat: str) -> _LeafPat:
    """
    pattern ::= NAME
              | NAME ':' VERSION
              | VERSION             (# имя опущено)
    """
    if ":" not in pat:
        if _is_ver(pat) or pat.lower() == "last":
            return _LeafPat(name=None, ver=_VersionRange(pat), need_last=False)
        return _LeafPat(name=pat.lower(), ver=_VersionRange(None), need_last=True)

    name, ver = pat.split(":", 1)
    name = name.lower() or None
    need_last = False
    if not ver:
        need_last = True
        ver_range = _VersionRange(None)
    else:
        ver_range = _VersionRange(ver)
    return _LeafPat(name=name, ver=ver_range, need_last=need_last)


class GNProtocol:
    """
    Строка формата  gn[:gnVer]:transport[:ver1]:route[:ver2]
    """

    __slots__ = (
        "raw",
        "gn_ver_raw",
        "gn_ver",
        "trnsp_name",
        "trnsp_ver_raw",
        "trnsp_ver",
        "route_name",
        "route_ver_raw",
        "route_ver",
        "_gn_leaf",
        "_trnsp_leaf",
        "_route_leaf",
    )

    # ---------------------------------------------------------------- init ---
    def __init__(self, raw: str):
        self.raw = raw
        self._parse()
        self._gn_leaf = self._LeafProto("gn", self.gn_ver_raw)
        self._trnsp_leaf = self._LeafProto(self.trnsp_name, self.trnsp_ver_raw)
        self._route_leaf = self._LeafProto(self.route_name, self.route_ver_raw)

    # ---------------------------------------------------------------- parse --
    @staticmethod
    def _take_ver(tokens: List[str]) -> Optional[str]:
        return tokens.pop(0) if tokens and (_is_ver(tokens[0]) or tokens[0].lower() == "last") else None

    def _parse(self) -> None:
        t = self.raw.split(":")
        if not t or t[0].lower() != "gn":
            raise ValueError("must start with 'gn'")
        t.pop(0)

        self.gn_ver_raw = self._take_ver(t)
        self.gn_ver = _VersionRange(self.gn_ver_raw)

        if not t:
            raise ValueError("missing transport proto")
        self.trnsp_name = t.pop(0).lower()
        self.trnsp_ver_raw = self._take_ver(t)
        self.trnsp_ver = _VersionRange(self.trnsp_ver_raw)

        if not t:
            raise ValueError("missing route proto")
        self.route_name = t.pop(0).lower()
        self.route_ver_raw = self._take_ver(t)
        self.route_ver = _VersionRange(self.route_ver_raw)

        if t:
            raise ValueError(f"extra tokens: {t!r}")

    def structure(self) -> dict:
        return {
            "gn": {"version": str(self.gn_ver)},
            self.trnsp_name: {"version": str(self.trnsp_ver)},
            self.route_name: {"version": str(self.route_ver)},
        }

    def matches_any(self, patterns: Iterable[str]) -> bool:
        gv = self.gn_ver_raw
        c_name, c_ver = self.trnsp_name, self.trnsp_ver_raw
        r_name, r_ver = self.route_name, self.route_ver_raw

        for pat in patterns:
            gn_v, p1n, p1v, p1need, p2n, p2v, p2need = _compile_full_pattern(pat)

            # gn
            if not gn_v.contains(gv):
                continue

            # transport
            if p1n and p1n != c_name:
                continue
            if p1need:
                if c_ver is not None:
                    continue
            elif not p1v.contains(c_ver):
                continue

            # route
            if p2n and p2n != r_name:
                continue
            if p2need:
                if r_ver is not None:
                    continue
            elif not p2v.contains(r_ver):
                continue

            return True
        return False

    class _LeafProto:
        __slots__ = ("_name", "_ver_raw")

        def __init__(self, name: str, ver_raw: Optional[str]):
            self._name = name
            self._ver_raw = ver_raw  # None == 'last'

        def protocol(self) -> str:
            return self._name

        def version(self) -> str:
            return self._ver_raw or "last"

        def matches_any(self, *patterns) -> bool:
            if len(patterns) == 1 and not isinstance(patterns[0], str):
                patterns_iter = patterns[0]
            else:
                patterns_iter = patterns

            nm = self._name
            vr = self._ver_raw

            for p in patterns_iter:
                pat = _compile_leaf_pattern(p)

                if pat.name is not None and pat.name != nm:
                    continue

                if pat.need_last:
                    if vr is not None:
                        continue
                    return True

                if pat.ver.contains(vr):
                    return True

            return False

        def __repr__(self) -> str:
            return f"<Proto {self._name}:{self.version()}>"

    @property
    def gn(self) -> _LeafProto:
        """Top‑level 'gn' protocol."""
        return self._gn_leaf

    @property
    def transport(self) -> _LeafProto:
        return self._trnsp_leaf

    @property
    def route(self) -> _LeafProto:
        return self._route_leaf

    def __repr__(self) -> str:
        return (
            f"<GNProtocol gn:{self.gn_ver_raw or 'last'} "
            f"{self.trnsp_name}:{self.trnsp_ver_raw or 'last'} "
            f"{self.route_name}:{self.route_ver_raw or 'last'}>"
        )
