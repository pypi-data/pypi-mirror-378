from __future__ import annotations


# start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'wujihandpy.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

from ._core import __doc__, Hand, Finger, Joint
from ._version import __version__

__all__ = ["__doc__", "__version__", "Hand", "Finger", "Joint"]
