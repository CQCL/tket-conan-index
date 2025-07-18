"""
Recipe for catch2 package.
"""

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir, save
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=2.1"


class Catch2Conan(ConanFile):
    name = "catch2"
    version = "3.8.1"
    description = (
        "A modern, C++-native, header-only, framework for unit-tests, TDD and BDD"
    )
    license = "BSL-1.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/catchorg/Catch2"
    topics = ("catch2", "unit-test", "tdd", "bdd")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_prefix": [True, False],
        "default_reporter": [None, "ANY"],
        "console_width": [None, "ANY"],
        "no_posix_signals": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_prefix": False,
        "default_reporter": None,
        "console_width": "80",
        "no_posix_signals": False,
    }
    # disallow cppstd compatibility, as it affects the ABI in this library
    # see https://github.com/conan-io/conan-center-index/issues/19008
    extension_properties = {"compatibility_cppstd": False}

    @property
    def _min_console_width(self):
        # catch2 doesn't build if less than this value
        return 46

    @property
    def _default_reporter_str(self):
        return str(self.options.default_reporter).strip('"')

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def build_requirements(self):
        if Version(self.version) >= "3.8.0":
            self.tool_requires("cmake/[>=3.16 <4]")

    def validate(self):
        check_min_cppstd(self, 14)

        try:
            if int(self.options.console_width) < self._min_console_width:
                raise ConanInvalidConfiguration(
                    f"option 'console_width' must be >= {self._min_console_width}, "
                    f"got {self.options.console_width}. Contributions welcome if this should work!"
                )
        except ValueError as e:
            raise ConanInvalidConfiguration(
                f"option 'console_width' must be an integer, "
                f"got '{self.options.console_width}'"
            ) from e

    def source(self):
        get(
            self,
            f"https://github.com/catchorg/Catch2/archive/v{self.version}.tar.gz",
            strip_root=True,
        )

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_TESTING"] = False
        tc.cache_variables["CATCH_INSTALL_DOCS"] = False
        tc.cache_variables["CATCH_INSTALL_EXTRAS"] = True
        tc.cache_variables["CATCH_DEVELOPMENT_BUILD"] = False
        tc.variables["CATCH_CONFIG_PREFIX_ALL"] = self.options.with_prefix
        tc.variables["CATCH_CONFIG_CONSOLE_WIDTH"] = self.options.console_width
        if self.options.default_reporter:
            tc.variables["CATCH_CONFIG_DEFAULT_REPORTER"] = self._default_reporter_str
        tc.variables["CATCH_CONFIG_NO_POSIX_SIGNALS"] = self.options.no_posix_signals
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        for cmake_file in [
            "ParseAndAddCatchTests.cmake",
            "Catch.cmake",
            "CatchAddTests.cmake",
        ]:
            copy(
                self,
                cmake_file,
                src=os.path.join(self.source_folder, "extras"),
                dst=os.path.join(self.package_folder, "lib", "cmake", "Catch2"),
            )

        # TODO: to remove in conan v2 once legacy generators removed
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {
                "Catch2::Catch2": "catch2::_catch2",
                "Catch2::Catch2WithMain": "catch2::catch2_with_main",
            },
        )

    def _create_cmake_module_alias_targets(self, module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent(
                f"""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """
            )
        save(self, module_file, content)

    @property
    def _module_file_rel_path(self):
        return os.path.join("lib", "cmake", f"conan-official-{self.name}-targets.cmake")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Catch2")
        self.cpp_info.set_property("cmake_target_name", "Catch2::Catch2WithMain")
        self.cpp_info.set_property("pkg_config_name", "catch2-with-main")

        lib_suffix = "d" if self.settings.build_type == "Debug" else ""
        self.cpp_info.components["_catch2"].set_property(
            "cmake_target_name", "Catch2::Catch2"
        )
        self.cpp_info.components["_catch2"].set_property("pkg_config_name", "catch2")
        self.cpp_info.components["_catch2"].libs = ["Catch2" + lib_suffix]

        self.cpp_info.components["catch2_with_main"].builddirs.append(
            os.path.join("lib", "cmake", "Catch2")
        )
        self.cpp_info.components["catch2_with_main"].libs = ["Catch2Main" + lib_suffix]
        self.cpp_info.components["catch2_with_main"].requires = ["_catch2"]
        self.cpp_info.components["catch2_with_main"].system_libs = (
            ["log"] if self.settings.os == "Android" else []
        )
        self.cpp_info.components["catch2_with_main"].set_property(
            "cmake_target_name", "Catch2::Catch2WithMain"
        )
        self.cpp_info.components["catch2_with_main"].set_property(
            "pkg_config_name", "catch2-with-main"
        )
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["catch2_with_main"].system_libs.append("m")
        defines = []
        if self.options.with_prefix:
            defines.append("CATCH_CONFIG_PREFIX_ALL")
        if self.options.default_reporter:
            defines.append(
                f"CATCH_CONFIG_DEFAULT_REPORTER={self._default_reporter_str}"
            )
        self.cpp_info.components["catch2_with_main"].defines = defines
