from setuptools import setup, find_packages, Extension

# Try to import Cython and numpy, fallback if not available
try:
    from Cython.Build import cythonize
    import numpy as np
    USE_CYTHON = True
except ImportError:
    USE_CYTHON = False
    print("Warning: Cython not available, installing without compiled extensions")

# Extensions for Cython compilation (only if Cython available)
if USE_CYTHON:
    extensions = [
        Extension(
            "adaptive_formula.core",
            ["adaptive_formula/core.pyx"],
            include_dirs=[np.get_include()],
            language="c++",
            compiler_directives={'language_level': "3"}
        )
    ]
    ext_modules = cythonize(extensions, compiler_directives={'language_level': "3"})
else:
    ext_modules = []

# Read README for long description
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "Adaptive Formula SDK - Cognitive Programming Infrastructure"

setup(
    name="adaptive-formula",
    version="0.4.2",  # Synchronized version
    author="Jaime Alexander Jimenez Lozano",
    author_email="jaimeajl@hotmail.com",
    description="Cognitive Programming SDK - Eliminate conditionals with adaptive formulas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jaimeajl/adaptive-formula",
    packages=find_packages(),
    ext_modules=ext_modules,
    setup_requires=["cython>=0.29.0", "numpy>=1.20.0"] if USE_CYTHON else [],
    install_requires=[
        "numpy>=1.20.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": ["pytest", "black", "mypy", "twine", "wheel", "cython"],
        "test": ["pytest", "pytest-cov"],
        "build": ["cython>=0.29.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers", 
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    zip_safe=False,
    include_package_data=True,
    package_data={
        'adaptive_formula': ['*.pyx', '*.pxd'],
    },
    entry_points={
        'console_scripts': [
            # 'adaptive-formula=adaptive_formula.cli:main',
        ],
    },
)