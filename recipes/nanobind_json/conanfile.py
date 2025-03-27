"""
Recipe for nanobind_json package.
"""

from conan import ConanFile
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout
import os

required_conan_version = ">=2.2"


class NanobindJsonConan(ConanFile):
    name = "nanobind_json"
    version = "tci-20250327"
    homepage = "https://github.com/ianhbell/nanobind_json"
    description = "nanobind wrappers of the nlohmann::json library"
    topics = (
        "conan",
        "header-only",
        "json",
        "nlohmann_json",
        "nanobind",
        "nanobind_json",
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
        self.requires("nanobind/tci-2.5.0@tket/stable")

    def source(self):
        get(
            self,
            f"https://github.com/ianhbell/nanobind_json/archive/e1953530697f61cbca9dc9b4f51561ea785cb09d.zip",
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
        self.cpp_info.set_property("cmake_file_name", "nanobind_json")
        self.cpp_info.set_property("cmake_target_name", "nanobind_json::nanobind_json")
        self.cpp_info.set_property("pkg_config_name", "nanobind_json")
