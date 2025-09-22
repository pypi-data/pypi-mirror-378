# flake8-in-file-ignores: noqa: F401,F403,F405

# Copyright (c) 1994 Adam Karpierz
# SPDX-License-Identifier: Zlib

__all__ = (
    'is_windows', 'is_linux', 'is_macos', 'defined',
    'DLL_PATH', 'DLL', 'dlclose', 'CFUNC',
)

from utlx.platform import *
if is_windows:  # pragma: no cover
    from .windows import DLL_PATH, DLL, dlclose, CFUNC
elif is_linux:  # pragma: no cover
    from .linux import DLL_PATH, DLL, dlclose, CFUNC
elif is_macos:  # pragma: no cover
    from .macos import DLL_PATH, DLL, dlclose, CFUNC
else:  # pragma: no cover
    raise ImportError("Unsupported platform")
