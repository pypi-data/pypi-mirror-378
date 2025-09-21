import argparse
import logging
import os
import re

import compspec.utils as utils
from compspec.create.jsongraph import JsonGraph
from compspec.plugin import PluginBase

import compspec_modules.defaults as defaults

logger = logging.getLogger("compspec-modules")


class ModuleGraph(JsonGraph):
    def add_module(self, module_file, module_name):
        """
        Add module to graph. Structure is the following
        (keeping it simple to start):

        MODULEPATH
          module --> name@version
          contains -- [lib] --> <library>
          contains -- [lib] --> <library>
          contains -- [bin] --> <binary>

        Note that there appear to be two kinds of modules -
        "meta" modules that exist to load catother modules (and
        they have a name and version but not explicit libs/paths)
        and then those modules that do. For the first, we add the
        name and version and don't try to represent edges between
        modules because at the highest level, the user just wants to
        load the module by name / version.
        """
        # This sets a default version (ignore)
        if ".version" in module_file:
            return

        content = utils.read_file(module_file)

        # This indicates an environment modules module file
        # Note we will need to design this for both module softwares TODO
        if not content.startswith("#%Module"):
            return

        # We could also use: module avail --json
        # for environment modules
        paths = set()
        ld_library_paths = set()
        version = None

        # Try to parse versions etc.
        for line in content.split("\n"):
            # Do we have a version?
            if re.search(r"set(\s+)version", line):
                version = line.split("version")[-1].strip()

        # This assumes a bash shell, maybe not the case, OK for testing
        out = utils.run_command(f'/bin/bash -c "module display {module_file}"')
        if out["return_code"] != 0:
            logger.warning(f"Issue displaying {module_file}")
        else:
            for line in out["message"].split("\n"):
                if re.search(r"prepend-path(\s+)PATH", line):
                    paths.add(line.split("PATH")[-1].strip())

                elif re.search(r"prepend-path(\s+)LD_LIBRARY_PATH", line):
                    ld_library_paths.add(line.split("LD_LIBRARY_PATH")[-1].strip())

        # Assume that if a path separator is in the name, the last bit is the version
        basename = module_name
        if os.sep in module_name:
            basename = module_name.rsplit(os.sep, 1)[0]

        # Metadata about the software that might be relevant
        metadata = {"name": module_name, "software": basename}
        if version is not None:
            metadata["version"] = version
        module_node = self.add_node(typ="module", attributes=metadata)

        # The path is from the parent module
        parent = module_node["label"]

        self.add_child_set(paths, parent, "binary")
        self.add_child_set(ld_library_paths, parent, "library")

    def add_child_set(self, paths, parent, typ):
        """
        Given a listing (set) of path strings, add edges to
        the parent, but only for htose that exist.
        """
        # Now we create package nodes that have libs / binaries, what we care about
        for path in paths:
            # This seems dangeorus
            if path == ".":
                continue
            userpath = os.path.expanduser(path)

            # Skip paths that do not exist
            if not os.path.exists(userpath):
                continue

            basename = os.path.basename(".")
            if basename.startswith("."):
                continue

            for found in os.listdir(userpath):
                child = self.add_node(
                    typ=typ, parent=parent, attributes={"name": found}
                )
                self.add_bidirectional_edge(parent, child["label"])


def derive_module_paths(module_args):
    """
    Starting from a MODULEPATH string, split into separate paths.
    """
    module_paths = set()
    for module_path in module_args:
        [module_paths.add(x.strip()) for x in module_path.split(":") if x.strip()]
    return module_paths


class Plugin(PluginBase):
    """
    The environment module extractor plugin
    """

    # These metadata fields are required (and checked for)
    description = "module software subsystem"
    namespace = defaults.namespace
    version = defaults.spec_version
    plugin_type = "generic"

    def add_arguments(self, subparser):
        """
        Add arguments for the plugin to show up in argparse
        """
        modules = subparser.add_parser(
            self.name,
            formatter_class=argparse.RawTextHelpFormatter,
            description=self.description,
        )
        # Ensure these are namespaced to your plugin
        modules.add_argument(
            "module_args",
            help="Arguments for module plugin (uses MODULEPATH environment if not provided)",
            nargs="*",
        )

    def check(self):
        """
        Check for module install.
        """
        modulepath = os.environ.get("MODULEPATH")
        if not modulepath:
            return False

        modulepath = derive_module_paths([modulepath])

        # Add each module path to the graph
        for module_path in modulepath:
            if not os.path.exists(module_path):
                continue

            # If we find module directories, quickly return true
            paths = self.get_module_paths(module_path)
            if paths:
                return True

        # If we get here, nothing found
        return False

    def detect(self):
        """
        Detect runs a headless extraction
        """
        modulepath = os.environ.get("MODULEPATH")
        if not modulepath:
            return
        return self._extract(modulepath)

    def extract(self, args, extra):
        """
        Search module paths for modules.
        """
        # If a direct module path isn't provided, derive from the environment
        if not args.module_args:
            modulepath = os.environ.get("MODULEPATH")
            if not modulepath:
                raise ValueError("Please provide a module path or export MODULEPATH.")
            args.module_args = [modulepath]
        return self._extract(args.module_args, args.name)

    def _extract(self, module_args, name=None):
        """
        Shared extraction logic.
        """
        # Split into unique paths (based on : separator)
        module_paths = derive_module_paths(module_args)

        # Create the spack graph
        # We could use args.name here, but "spack" is more accurate for the subsystem
        g = ModuleGraph("environment-modules")
        g.metadata["type"] = "software"

        # Add the root node - assume module paths may change in availability
        g.generate_root()

        # Add each module path to the graph
        for module_path in module_paths:
            if not os.path.exists(module_path):
                logger.warning(f"Module path {module_path} does not exist.")
                continue

            # Recursive find of all module directories
            paths = self.get_module_paths(module_path)
            logger.info(f"Found {len(paths)} modules installed in {module_path}")

            for module_file in paths:
                # The module root or base should be at the top level
                # Ignore "private" or hidden directories
                relpath = os.path.relpath(module_file, module_path)
                if relpath.startswith("."):
                    continue

                # Provide the root and the full path to file,
                # which can be used to derive the name
                g.add_module(module_file, relpath)

        # Generate a dictionary with custom metadata
        return g.to_dict({"install_name": name or self.name})

    def get_module_paths(self, root):
        """
        Given a root, return module paths
        """
        return list(utils.recursive_find(root, ".*"))
