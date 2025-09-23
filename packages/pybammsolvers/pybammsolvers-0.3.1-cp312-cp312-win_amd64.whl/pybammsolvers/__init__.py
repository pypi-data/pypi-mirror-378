"""""" # start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pybammsolvers.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

import importlib.util as il


idaklu_spec = il.find_spec("pybammsolvers.idaklu")
idaklu = il.module_from_spec(idaklu_spec)
idaklu_spec.loader.exec_module(idaklu)
