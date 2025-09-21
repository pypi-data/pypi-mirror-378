# setup.py
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext
import os
import platform

# ----- configuration flags (define FIRST!) -----
PURE_PY = os.environ.get("KOEGELBRUNF_PURE_PY", "0") == "1"
PLAT = platform.system()
BUILD_C_EXT = (not PURE_PY) and (PLAT in {"Darwin", "Linux"})

# ----- optional Cython extension discovery -----
ext_modules = []
if BUILD_C_EXT:
    try:
        from Cython.Build import cythonize
        sources = ["src/koegelbrunf/_square.pyx"]
        ext_modules = cythonize(
            [
                Extension(
                    name="koegelbrunf._square",
                    sources=sources,
                    extra_compile_args=["-O3"],
                )
            ],
            language_level="3",
        )
    except Exception:
        # If you pre-generate C later, you can switch to:
        # sources = ["src/koegelbrunf/_square.c"]
        # ext_modules = [Extension("koegelbrunf._square", sources=sources, extra_compile_args=["-O3"])]
        ext_modules = []  # fall back to pure Python

# ----- soft-fail build_ext so install never breaks -----
class OptionalBuildExt(build_ext):
    def run(self):
        try:
            if ext_modules:
                super().run()
        except Exception as e:
            self.announce(
                f"Building C extension failed: {e}\nFalling back to pure Python.",
                level=3,
            )

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as e:
            self.announce(
                f"Extension {ext.name} build failed: {e}\nUsing pure Python fallback.",
                level=3,
            )

# ----- standard setup() -----
setup(
    name="koegelbrunf",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    ext_modules=ext_modules,
    cmdclass={"build_ext": OptionalBuildExt},
)
