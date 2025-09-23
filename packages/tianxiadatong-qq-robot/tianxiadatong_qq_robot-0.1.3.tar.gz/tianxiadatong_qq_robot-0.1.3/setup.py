# # setup.py
# from setuptools import setup, find_packages
# from setuptools.command.build_py import build_py as _build_py
# import compileall, pathlib, os, shutil
#
# class build_pyc_only(_build_py):
#     """build 阶段：把 .py 编译成 .pyc 并删除源码"""
#     def run(self):
#         super().run()                       # 先复制包结构
#         for pkg_dir in self.packages:
#             build_path = pathlib.Path(self.build_lib) / pkg_dir.replace('.', '/')
#             compileall.compile_dir(build_path, legacy=True, quiet=1)  # 生成 __pycache__/*.pyc
#             # 把 pyc 提到同级目录，并删除 py
#             for pyc in build_path.rglob('*.pyc'):
#                 target = pyc.parent / (pyc.stem.split('.')[0] + '.pyc')
#                 pyc.rename(target)
#             for py in build_path.rglob('*.py'):
#                 py.unlink(missing_ok=True)
#
# setup(
#     name='tianxiadatong_qq_robot',
#     version='0.1.0',
#     packages=find_packages(),
#     cmdclass={'build_py': build_pyc_only},
#     zip_safe=False,
# )

import setuptools
setuptools.setup(
    name='tianxiadatong_QQ_robot',
    version='0.0.2',
    description='this is a program for dia',
    author='',
    author_email='',
    packages=setuptools.find_packages(),
   )