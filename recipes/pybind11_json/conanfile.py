"""
Recipe for pybind11_json package.
"""

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.1"


class Pybind11JsonConan(ConanFile):
    name = "pybind11_json"
    version = "tci-0.2.15"
    homepage = "https://github.com/pybind/pybind11_json"
    description = "An nlohmann_json to pybind11 bridge"
    topics = (
        "conan",
        "header-only",
        "json",
        "nlohmann_json",
        "pybind11",
        "pybind11_json",
        "python",
        "python-binding",
    )
    no_copy_source = True
    license = "BSD-3-Clause"

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def requirements(self):
        self.requires("nlohmann_json/3.11.3")
        self.requires("pybind11/tci-2.13.6@tket/stable")

    def source(self):
        get(
            self,
            f"https://github.com/pybind/pybind11_json/archive/0.2.15.tar.gz",
            destination=self.source_folder,
            strip_root=True,
        )

    def package(self):
        copy(
            self,
            "LICENSE*",
            self.source_folder,
            os.path.join(self.package_folder, "licenses"),
        )
        copy(
            self,
            "*",
            os.path.join(self.source_folder, "include"),
            os.path.join(self.package_folder, "include"),
        )

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "pybind11_json")
        self.cpp_info.set_property("cmake_target_name", "pybind11_json::pybind11_json")
        self.cpp_info.set_property("pkg_config_name", "pybind11_json")
