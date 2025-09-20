# coding=utf-8
from ut_log.log import Log, LogEq
from ut_path.dodopath import DoDoPath

from typing import Any

TyDic = dict[Any, Any]
TyPath = str
TyAoPath = list[TyPath]
TyDoPath = dict[Any, TyPath]
TyDoDoPath = dict[Any, TyDoPath]
TyAoDoDoPath = list[TyDoDoPath]
TyBasename = str

TnPath = None | TyPath


class AoDoDoPath:
    """
    Manage Array of Path-Dictionaries
    """
    @staticmethod
    def sh_aopath(aododopath: TyAoDoDoPath, kwargs: TyDic) -> TyAoPath:
        _aopath: TyAoPath = []
        if not aododopath:
            msg = "Parameter 'aododopath' is None or empty"
            Log.error(msg)
            # raise Exception(msg)
            return _aopath
        LogEq.debug("aododopath", aododopath)
        for _dodopath in aododopath:
            _path: TnPath = DoDoPath.sh_path(_dodopath, kwargs)
            if _path:
                _aopath.append(_path)
        LogEq.debug("_aopath", _aopath)
        return _aopath
