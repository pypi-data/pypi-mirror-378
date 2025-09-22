import os

__base_version__ = "446"


def build_version():
    version = __base_version__
    # version = f'{version}.0.0'
    # build_id = os.environ.get("SOURCECRAFT_RUN_ID")
    build_id = os.environ.get("BUILD_ID")
    if build_id:
        version += f"rc{build_id}"
    # version = f'{__base_version__}.0.{build_id}'
    return version


__version__ = build_version()
