"""Setup script for building Cython extensions."""

from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy as np
import os

# Define Cython extensions
extensions = [
    Extension(
        "good_common.utilities._collections_cy",
        ["src/good_common/utilities/_collections_cy.pyx"],
        include_dirs=[np.get_include()],
        language="c",
        extra_compile_args=["-O3", "-ffast-math", "-march=native"],
    ),
    Extension(
        "good_common.utilities._functional_cy",
        ["src/good_common/utilities/_functional_cy.pyx"],
        include_dirs=[np.get_include()],
        language="c",
        extra_compile_args=["-O3", "-ffast-math"],
    ),
    Extension(
        "good_common.utilities._strings_cy",
        ["src/good_common/utilities/_strings_cy.pyx"],
        include_dirs=[np.get_include()],
        language="c",
        extra_compile_args=["-O3"],
    ),
]

# Only build extensions if .pyx files exist
existing_extensions = []
for ext in extensions:
    if all(os.path.exists(src) for src in ext.sources):
        existing_extensions.append(ext)

if existing_extensions:
    setup(
        ext_modules=cythonize(
            existing_extensions,
            compiler_directives={
                'language_level': "3",
                'boundscheck': False,
                'wraparound': False,
                'cdivision': True,
                'initializedcheck': False,
            }
        ),
        zip_safe=False,
    )
else:
    setup()