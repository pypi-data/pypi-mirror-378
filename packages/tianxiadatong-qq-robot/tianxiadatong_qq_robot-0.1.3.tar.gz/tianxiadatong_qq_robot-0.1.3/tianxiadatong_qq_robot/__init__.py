# # 显式导入所有子模块，供外部统一引用
# from . import db
# from . import handler
# from . import local_logger
# from . import main
# from . import message
# from . import processor
# from . import public
# from . import qqApp
from .qqApp import qqApp
# tianxiadatong_qq_robot/__init__.py
import importlib.util, pathlib, sys
import os, importlib.util
# 让 Windows 搜索当前包目录
pkg_dir = os.path.dirname(__file__)
if hasattr(os, 'add_dll_directory'):   # py3.8+
    os.add_dll_directory(pkg_dir)


def _load_pyd(name):
    file = pathlib.Path(__file__).with_name(f"{name}.cp{sys.version_info.major}{sys.version_info.minor}-win_amd64.pyd")
    spec = importlib.util.spec_from_file_location(name, file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[f"{__name__}.{name}"] = module
    spec.loader.exec_module(module)
    return module

public = _load_pyd("public")
processor = _load_pyd("processor")
qqApp = _load_pyd("qqApp")
public = _load_pyd("public")