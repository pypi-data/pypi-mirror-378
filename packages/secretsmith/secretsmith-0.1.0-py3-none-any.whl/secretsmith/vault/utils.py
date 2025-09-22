#   -------------------------------------------------------------
#   Secretsmith :: Vault :: Utilities
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   Project:        Nasqueron
#   License:        BSD-2-Clause
#   -------------------------------------------------------------


from typing import Tuple


def split_path(full_path: str) -> Tuple[str, str]:
    """
    Split a full path into mount point and secret path,
    assuming the first part of the full path is the mount point.
    """
    tokens = full_path.split("/")

    mount_point = tokens[0]
    secret_path = "/".join(tokens[1:])

    return mount_point, secret_path
