# coding=utf-8
from ut_log.log import LogEq
from ut_path.path import Path
from ut_path.dopath import DoPath

from typing import Any, TypedDict
TyAny = Any
TyDic = dict[Any, Any]
TyPath = str
TyDoPath = dict[Any, TyPath]
# TyDoDoPath = dict[Any, TyDoPath]


class TyDoDoPath(TypedDict):
    d_path: TyDoPath
    datetype: str


TyStr = str

TnDic = None | TyDic
TnPath = None | TyPath
TnStr = None | TyStr


class DoDoPath:

    @classmethod
    def sh_path(cls, dodopath: TyDoDoPath, kwargs: TyDic) -> TnPath:
        LogEq.debug("dodopath", dodopath)
        if not dodopath:
            return None
        _d_path: TnDic = dodopath.get('d_path')
        _datetype: TnStr = dodopath.get('datetype')
        LogEq.debug("_d_path", _d_path)
        LogEq.debug("_datetype", _datetype)
        if not _d_path:
            return None
        _path: TnPath = DoPath.sh_path(_d_path, kwargs)
        LogEq.debug("_path", _path)
        if _datetype:
            _path = Path.sh_path_by_datetype(_path, _datetype, kwargs)
        return _path
