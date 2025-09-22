import os

__base_version__ = "4.1.0"


def build_version():
    version = __base_version__
    build_id = os.environ.get("BUILD_ID")
    if build_id:
        version += f"rc{build_id}"
    return version


__version__ = build_version()
