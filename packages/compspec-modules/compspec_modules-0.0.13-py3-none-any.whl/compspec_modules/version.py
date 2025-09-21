__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2024, Vanessa Sochat"
__license__ = "MIT"

__version__ = "0.0.13"
AUTHOR = "Vanessa Sochat"
AUTHOR_EMAIL = "vsoch@users.noreply.github.com"
NAME = "compspec-modules"
PACKAGE_URL = "https://github.com/compspec/compspec-modules"
KEYWORDS = "compatibility, compspec, modules, subsystem, scheduling, hpc"
DESCRIPTION = "Subsystem graph generation for environment modules"
LICENSE = "LICENSE"

################################################################################
# Global requirements

INSTALL_REQUIRES = (("compspec", {"min_version": "0.1.0"}),)

TESTS_REQUIRES = (("pytest", {"min_version": "4.6.2"}),)
INSTALL_REQUIRES_ALL = INSTALL_REQUIRES + TESTS_REQUIRES
