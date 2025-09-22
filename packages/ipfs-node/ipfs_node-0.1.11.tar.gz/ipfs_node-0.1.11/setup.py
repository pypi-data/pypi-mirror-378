import pip
from setuptools import setup, find_packages, Extension
import subprocess
import os
import platform
import sys
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.develop import develop

PROJ_DIR = os.path.dirname(os.path.abspath(__file__))


def compile_go_library():
    """Compile the Go shared library."""
    print("Compiling Go shared library...")

    # Define Go source directory
    libkubo_dir = os.path.join(PROJ_DIR, "src", "libkubo")

    # Check if Go is installed
    try:
        subprocess.check_call(
            ["go", "version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        raise RuntimeError("Go compiler not found. Please install Go 1.19 or later.")

    # Build shared library for the current platform
    if not os.path.exists(libkubo_dir):
        os.makedirs(libkubo_dir)

    # Determine the output file extension based on platform
    if platform.system() == "Windows":
        lib_name = "libkubo.dll"
    elif platform.system() == "Darwin":
        lib_name = "libkubo.dylib"
    else:
        lib_name = "libkubo_linux_x86_64.so"

    # Get Kubo library source code if not already fetched
    try:
        if not os.path.exists(os.path.join(libkubo_dir, "go.sum")):
            subprocess.check_call(["go", "mod", "tidy"], cwd=libkubo_dir)
    except subprocess.CalledProcessError as e:
        print(f"Error fetching Go dependencies: {e}")
        print("Continuing with existing code...")

    # Check if the output library already exists
    output_path = os.path.join(libkubo_dir, lib_name)
    if os.path.exists(output_path):
        print(f"Shared library already exists at {output_path}")
        return
    print("Compiling libkubo...")
    # Build the shared library
    build_cmd = ["go", "build", "-buildmode=c-shared", "-o", output_path, libkubo_dir]

    print(f"Running: {' '.join(build_cmd)}")
    subprocess.check_call(build_cmd, cwd=libkubo_dir)
    print(f"Successfully compiled shared library: {output_path}")


class BuildGoLibraryCommand(build_py):
    """Custom build command to compile Go code during build_py."""

    def run(self):
        compile_go_library()
        super().run()


class InstallCommand(install):
    """Custom install command to compile Go code during installation."""

    def run(self):
        compile_go_library()
        super().run()


class DevelopCommand(develop):
    """Custom develop command to compile Go code during development installation."""

    def run(self):
        compile_go_library()
        super().run()


# for some reason the following setup function can't handle the git URL in requirements.txt, so let's install it like so
pip.main(["install", "-r", os.path.join(PROJ_DIR, "requirements.txt")])

setup(
    name="ipfs_node",
    version="0.1.11",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "libkubo": ["*.dll", "*.dylib", "*.so", "*.h"],
    },
    include_package_data=True,
    cmdclass={
        "build_py": BuildGoLibraryCommand,
        "install": InstallCommand,
        "develop": DevelopCommand,
    },
    install_requires=["cffi>=1.15.0", "ipfs_tk"],
    author="Emendir",
    author_email="",
    description="Run an IPFS node inside of python using kubo as a library.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/emendir/py_ipfs_node",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
