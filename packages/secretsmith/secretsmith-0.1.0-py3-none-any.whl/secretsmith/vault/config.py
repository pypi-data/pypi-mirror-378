#   -------------------------------------------------------------
#   Secretsmith :: Vault :: configuration
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Project:        Nasqueron
#   License:        BSD-2-Clause
#   -------------------------------------------------------------


import yaml


def load_config(path: str) -> dict:
    with open(path) as fd:
        return yaml.safe_load(fd)
