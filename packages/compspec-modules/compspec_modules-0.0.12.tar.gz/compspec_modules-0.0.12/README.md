# Compspec Modules

<p align="center">
  <img height="300" src="https://raw.githubusercontent.com/compspec/spec/main/img/compspec-circle.png">
</p>

[![PyPI version](https://badge.fury.io/py/compspec-modules.svg)](https://badge.fury.io/py/compspec-modules)

A compspec (Composition spec) is a specification and model for comparing things. Compspec modules is
a plugin for extraction of environment modules subsystem metadata about software installed
on a system. This can be for the entire system or a user-specific install. The plugin exports json graph format (JGF) that can be used for scheduling and other purposes. To learn more:

 - [Compspec](https://github.com/compspec/compspec): the Python library that discovers and loads this plugin.

Note that I'm currently parsing environment modules, and very simply. We can extend to more complex / LMOD if needed.

## Usage

Install compspec and the plugin here:

```bash
pip install compspec
pip install compspec-modules
```

Here is an easy way (in the devcontainer) to get a bunch of testing modules.

```bash
git clone https://github.com/shawfdong/modulefiles /tmp/modulefiles
export MODULEPATH=$MODULEPATH:/tmp/modulefiles
export PATH=~/.local/bin:$PATH
```

Then run an extraction for your environment modules:

```bash
compspec extract modules
```

To save to file:

```bash
compspec extract --outfile module-subsystem.json modules
```

You can see the example [example/module-subsystem.json](example/module-subsystem.json).

<details>

<summary>compspec-modules output</summary>

```console
{
    "graph": {
        "nodes": {
            "environment-modules0": {
                "metadata": {
                    "type": "environment-modules",
                    "basename": "environment-modules",
                    "name": "environment-modules0",
                    "id": 0,
                    "uniq_id": 0,
                    "containment": {
                        "paths": "/environment-modules0"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false
                },
                "label": "environment-modules0"
            },
            "module1": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module0",
                    "id": 1,
                    "uniq_id": 1,
                    "containment": {
                        "paths": "/environment-modules0/module0"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "dot",
                        "software": "dot"
                    }
                },
                "label": "module1"
            },
            "module2": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module1",
                    "id": 2,
                    "uniq_id": 2,
                    "containment": {
                        "paths": "/environment-modules0/module1"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "module-info",
                        "software": "module-info"
                    }
                },
                "label": "module2"
            },
            "module3": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module2",
                    "id": 3,
                    "uniq_id": 3,
                    "containment": {
                        "paths": "/environment-modules0/module2"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "modules",
                        "software": "modules",
                        "version": "5.4.0"
                    }
                },
                "label": "module3"
            },
            "module4": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module3",
                    "id": 4,
                    "uniq_id": 4,
                    "containment": {
                        "paths": "/environment-modules0/module3"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "module-git",
                        "software": "module-git"
                    }
                },
                "label": "module4"
            },
            "module5": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module4",
                    "id": 5,
                    "uniq_id": 5,
                    "containment": {
                        "paths": "/environment-modules0/module4"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "use.own",
                        "software": "use.own"
                    }
                },
                "label": "module5"
            },
            "module6": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module5",
                    "id": 6,
                    "uniq_id": 6,
                    "containment": {
                        "paths": "/environment-modules0/module5"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "null",
                        "software": "null"
                    }
                },
                "label": "module6"
            },
            "module7": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module6",
                    "id": 7,
                    "uniq_id": 7,
                    "containment": {
                        "paths": "/environment-modules0/module6"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "python/intelpython2",
                        "software": "python"
                    }
                },
                "label": "module7"
            },
            "module8": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module7",
                    "id": 8,
                    "uniq_id": 8,
                    "containment": {
                        "paths": "/environment-modules0/module7"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "python/anaconda3",
                        "software": "python"
                    }
                },
                "label": "module8"
            },
            "module9": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module8",
                    "id": 9,
                    "uniq_id": 9,
                    "containment": {
                        "paths": "/environment-modules0/module8"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "python/anaconda2",
                        "software": "python"
                    }
                },
                "label": "module9"
            },
            "module10": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module9",
                    "id": 10,
                    "uniq_id": 10,
                    "containment": {
                        "paths": "/environment-modules0/module9"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "python/intelpython3",
                        "software": "python"
                    }
                },
                "label": "module10"
            },
            "module11": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module10",
                    "id": 11,
                    "uniq_id": 11,
                    "containment": {
                        "paths": "/environment-modules0/module10"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "python/rh-python36",
                        "software": "python"
                    }
                },
                "label": "module11"
            },
            "module12": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module11",
                    "id": 12,
                    "uniq_id": 12,
                    "containment": {
                        "paths": "/environment-modules0/module11"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "PrgEnv-intel/2019.1.053",
                        "software": "PrgEnv-intel",
                        "version": "2019.1.053"
                    }
                },
                "label": "module12"
            },
            "module13": {
                "metadata": {
                    "type": "module",
                    "basename": "module",
                    "name": "module12",
                    "id": 13,
                    "uniq_id": 13,
                    "containment": {
                        "paths": "/environment-modules0/module12"
                    },
                    "size": 1,
                    "unit": "",
                    "rank": 0,
                    "exclusive": false,
                    "attributes": {
                        "name": "PrgEnv-pgi/llvm_18.10",
                        "software": "PrgEnv-pgi",
                        "version": "18.10"
                    }
                },
                "label": "module13"
            },

...
    },
    "metadata": {
        "install_name": "compat-experiment"
    }
}
```
</details>


### Development

If you open the [Development container](.devcontainer) in VSCode, you'll find environment modules are installed:

```bash
$ module avail
```

This allows us to easily develop and test the compatibility plugin.


## License

HPCIC DevTools is distributed under the terms of the MIT license.
All new contributions must be made under this license.

See [LICENSE](https://github.com/converged-computing/cloud-select/blob/main/LICENSE),
[COPYRIGHT](https://github.com/converged-computing/cloud-select/blob/main/COPYRIGHT), and
[NOTICE](https://github.com/converged-computing/cloud-select/blob/main/NOTICE) for details.

SPDX-License-Identifier: (MIT)

LLNL-CODE- 842614
