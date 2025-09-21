import argparse
import logging
import os
import shutil

import compspec.utils as utils
from compspec.create.jsongraph import JsonGraph
from compspec.plugin import PluginBase

import compspec_spack.defaults as defaults

logger = logging.getLogger("compspec-spack")


class SpackGraph(JsonGraph):
    def add_package(self, package_root):
        """
        Add package root to graph. Structure is the following
        (keeping it simple to start).

        spack root
          package --> name@version
          contains -- [lib] --> <library>
          contains -- [lib] --> <library>
          contains -- [bin] --> <binary>
        """

        # This has the binary / lib manifest - we can create nodes for each
        manifest_file = os.path.join(package_root, "install_manifest.json")

        # I'm not going to parse deps here, just the top level of each
        spec_file = os.path.join(package_root, "spec.json")

        # In practice, this can happen if software is actively being installed
        if not os.path.exists(manifest_file) or not os.path.exists(spec_file):
            logger.warning(
                f"Manifest or spec file missing for {package_root}, skipping."
            )
            return

        manifest = utils.read_json(manifest_file)
        spec = utils.read_json(spec_file)

        # This is the main package we are inspecting
        package = spec["spec"]["nodes"][0]

        # Metadata about the software that might be relevant
        metadata = {
            "name": package["name"],
            "version": package["version"],
            "platform": package["arch"]["platform"],
            "target": package["arch"]["target"]["name"],
            "os": package["arch"]["platform_os"],
            "vendor": package["arch"]["target"]["vendor"],
        }

        # Only supported for older versions of spack
        if "compiler" in package:
            metadata["compiler_version"] = package["compiler"]["version"]
            metadata["compiler"] = package["compiler"]["name"]

        # This could be parsed into separate spaces - e.g., compilers,
        # But I'm doing it simple for now and each of these is a node attribute
        # the metadata here gets added as attribute_<name>
        package_node = self.add_node(typ="package", attributes=metadata)

        # Separators for lib and bin
        libsep = os.sep + "lib" + os.sep
        binsep = os.sep + "bin" + os.sep

        # The path is from the parent package
        parent = package_node["label"]

        # Now we create package nodes that have libs / binaries, what we care about
        for path in manifest:
            # Skip pkgconfig stuff
            if "pkgconfig" in path:
                continue
            if libsep in path:
                library = path.split(libsep, 1)[-1]
                child = self.add_node(
                    typ="library", parent=parent, attributes={"name": library}
                )
                self.add_bidirectional_edge(parent, child["label"])
            elif binsep in path:
                binary = path.split(binsep, 1)[-1]
                child = self.add_node(
                    typ="binary", parent=parent, attributes={"name": binary}
                )
                self.add_bidirectional_edge(parent, child["label"])


class Plugin(PluginBase):
    """
    The spack extractor plugin
    """

    # These metadata fields are required (and checked for)
    description = "spack software subsystem"
    namespace = defaults.namespace
    version = defaults.spec_version
    plugin_type = "generic"

    def add_arguments(self, subparser):
        """
        Add arguments for the plugin to show up in argparse
        """
        spack = subparser.add_parser(
            self.name,
            formatter_class=argparse.RawTextHelpFormatter,
            description=self.description,
        )
        # Ensure these are namespaced to your plugin
        spack.add_argument(
            "spack_args",
            help="Arguments for spack (defaults to reasonable set if not defined)",
            nargs="*",
        )

    def check(self):
        """
        Check for spack either based on executable or SPACK_ROOT discovery.
        """
        spack_root = self.find_spack_root()
        if not spack_root or not os.path.exists(spack_root):
            return False
        return True

    def find_spack_root(self):
        """
        Find a spack root.
        """
        spack_path = shutil.which("spack")
        if spack_path:
            spack_root = os.path.dirname(os.path.dirname(spack_path))
        else:
            spack_root = os.environ.get("SPACK_ROOT")
        return spack_root

    def detect(self):
        """
        Headless extract entrypoint.
        """
        spack_root = self.find_spack_root()
        if spack_root is None:
            return
        return self._extract(spack_root)

    def extract(self, args, extra):
        """
        Search a spack install for installed software
        """
        if not args.spack_args:
            raise ValueError("Please provide a path to a spack install.")
        spack_root = os.path.abspath(args.spack_args[0])
        if not os.path.exists(spack_root):
            raise ValueError(f"Spack root {spack_root} does not exist.")
        return self._extract(spack_root, args.name)

    def _extract(self, spack_root, name=None):
        """
        Shared extraction.
        """
        # Recursive find of all spack metadata directories
        install_root = os.path.join(spack_root, "opt", "spack")
        paths = self.get_spack_metadata_paths(install_root)
        logger.info(f"Found {len(paths)} spack packages installed in {install_root}")

        # Create the spack graph
        # We could use args.name here, but "spack" is more accurate for the subsystem
        g = SpackGraph("spack")

        # Add metadata type->software, which is also defined at the root
        g.metadata["type"] = "software"

        # Add the root node for the spack subsystem
        # attributes need to identify the initial location, and that spack defines software
        g.generate_root(attributes={"root": spack_root}, typ="software")

        for package_root in paths:
            g.add_package(package_root)

        # Generate a dictionary with custom metadata
        return g.to_dict(
            {"install_name": name or self.name, "spack_root": install_root}
        )

    def get_spack_metadata_paths(self, root):
        """
        Given a root, return spack metadata paths
        """
        paths = list(utils.recursive_find(root, "[.]spack" + os.sep))
        paths = set(x.split(os.sep + ".spack")[0] for x in paths)
        return list(x + os.sep + ".spack" for x in paths)
