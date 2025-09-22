from setuptools import setup, find_packages, Extension
import warnings

# Optional Cython compilation
USE_CYTHON = False
ext_modules = []

try:
    from Cython.Build import cythonize
    try:
        import numpy as np
        USE_CYTHON = True
    except ImportError:
        pass
except ImportError:
    pass

if USE_CYTHON:
    try:
        extensions = [
            Extension(
                "adaptive_formula.core",
                ["adaptive_formula/core.pyx"],
                include_dirs=[np.get_include()],
                language="c++"
            )
        ]
        ext_modules = cythonize(extensions, compiler_directives={'language_level': "3"})
    except:
        ext_modules = []

# Read README
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except:
    long_description = "Adaptive Formula SDK"

setup(
    name="adaptive-formula",
    version="0.4.5",
    author="Jaime Alexander Jimenez Lozano",
    author_email="jaimeajl@hotmail.com",
    description="Cognitive Programming SDK - Eliminate conditionals with adaptive formulas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaimeajl/adaptive-formula",
    packages=find_packages(),
    ext_modules=ext_modules,
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "optimized": ["cython>=0.29.0", "numpy>=1.19.0"],
        "pandas": ["pandas>=1.0.0"],
        "full": ["cython>=0.29.0", "numpy>=1.19.0", "pandas>=1.0.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    zip_safe=False,
    include_package_data=True,
    package_data={
        'adaptive_formula': ['*.py', '*.pyx', '*.pxd'],
    },
)