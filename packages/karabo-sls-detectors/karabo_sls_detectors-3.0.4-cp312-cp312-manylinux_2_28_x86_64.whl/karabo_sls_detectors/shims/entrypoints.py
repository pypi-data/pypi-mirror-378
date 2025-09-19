
import os
import sys

import karabo_sls_detectors

PACKAGE_PATH = os.path.abspath(karabo_sls_detectors.__path__[0])

def get_path(cmd : str) -> str:
    return f"{PACKAGE_PATH}/bin/{cmd}"


def create_runner(cmd : str):
    def runner():
        # we cannot use subprocess.xyz here. We need to replace the python
        # process with the underlying daemontools command for it to run
        # correctly!
        os.execvp(get_path(cmd), sys.argv)
    return runner

karabo_sls_detector_server=create_runner("karabo-sls-detector-server")
