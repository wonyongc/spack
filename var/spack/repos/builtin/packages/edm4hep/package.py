# Copyright 2013-2024 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)


from spack.package import *


class Edm4hep(CMakePackage):
    """Event data model of Key4hep."""

    homepage = "https://github.com/wonyongc/EDM4hep"
    url = "https://github.com/wonyongc/EDM4hep/archive/v00-01.tar.gz"
    git = "https://github.com/wonyongc/EDM4hep.git"

    maintainers("vvolkl", "jmcarcell", "tmadlener")

    tags = ["hep", "key4hep"]

    license("Apache-2.0")

    version("master", branch="main")
    version("0.10.3", sha256="45cf616e7a4df12d0e9dc7a2eac19071c9406365")

    depends_on("cxx", type="build")  # generated

    _cxxstd_values = ("17", "20")
    variant(
        "cxxstd",
        default="17",
        values=_cxxstd_values,
        multi=False,
        description="Use the specified C++ standard when building.",
    )

    depends_on("cmake@3.3:", type="build")
    depends_on("cmake@3.23:", type="build", when="@0.10.3:")
    depends_on("python", type="build")

    depends_on("root@6.08:")
    depends_on("nlohmann-json@3.10.5:")
    depends_on("podio@1:", when="@0.99:")
    depends_on("podio@0.15:", when="@:0.10.5")
    for _std in _cxxstd_values:
        depends_on("podio cxxstd=" + _std, when="cxxstd=" + _std)

    depends_on("py-jinja2", type="build")
    depends_on("py-pyyaml", type="build")

    depends_on("hepmc3", type="test")
    depends_on("heppdt", type="test")
    depends_on("catch2@3.0.1:", type="test")

    # Corresponding changes in EDM4hep landed with https://github.com/key4hep/EDM4hep/pull/314
    extends("python", when="@0.10.6:")

    def cmake_args(self):
        args = []
        # C++ Standard
        args.append(self.define("CMAKE_CXX_STANDARD", self.spec.variants["cxxstd"].value))
        args.append(self.define("BUILD_TESTING", self.run_tests))
        return args

    def setup_run_environment(self, env):
        env.prepend_path("LD_LIBRARY_PATH", self.spec["edm4hep"].libs.directories[0])
        if self.spec.satisfies("@:0.10.5"):
            env.prepend_path("PYTHONPATH", self.prefix.python)

    def url_for_version(self, version):
        """Translate version numbers to ilcsoft conventions.
        in spack, the convention is: 0.1 (or 0.1.0) 0.1.1, 0.2, 0.2.1 ...
        in ilcsoft, releases are dashed and padded with a leading zero
        the patch version is omitted when 0
        so for example v01-12-01, v01-12 ...
        :param self: spack package class that has a url
        :type self: class: `spack.PackageBase`
        :param version: version
        :type param: str
        """
        base_url = self.url.rsplit("/", 1)[0]

        if len(version) == 1:
            major = version[0]
            minor, patch = 0, 0
        elif len(version) == 2:
            major, minor = version
            patch = 0
        else:
            major, minor, patch = version

        # By now the data is normalized enough to handle it easily depending
        # on the value of the patch version
        if patch == 0:
            version_str = "v%02d-%02d.tar.gz" % (major, minor)
        else:
            version_str = "v%02d-%02d-%02d.tar.gz" % (major, minor, patch)

        return base_url + "/" + version_str
