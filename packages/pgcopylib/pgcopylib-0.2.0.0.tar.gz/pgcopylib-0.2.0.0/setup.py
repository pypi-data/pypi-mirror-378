# setup.py
from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import os

def find_cython_extensions():
    extensions = []
    for root, _, files in os.walk("src"):
        for file in files:
            if file.endswith(".pyx"):
                pyx_path = os.path.join(root, file)
                module_name = pyx_path.replace(os.path.sep, ".")[4:-4]
                extensions.append(
                    Extension(
                        module_name,
                        [pyx_path],
                        include_dirs=["src"]
                    )
                )
    return extensions

setup(
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    ext_modules=cythonize(find_cython_extensions(), language_level=3),
    package_data={
        "pgcopylib": ["*.pxd", "*.md", "*.txt"]
    },
)
