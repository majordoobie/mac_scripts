"""
Script was created for the purpose of gracefully killing hung SSH terminals
from when the laptop closes down for travel and the SSH tunnels were not closed
properly.

Add to the TERMINATION_LIST the cmd_line string to look for.
"""

import psutil
from sys import argv

# List of cmd_line string to compare against
TERMINATION_LIST = (
        "ssh jumpbox",
        )


def main() -> None:
    """
    Terminate process that contain the cmd line string specified in the 
    TERMINATION_LIST. The ZombieProcess and NoSuchProcess exception are
    uniquely required for macOS as it seems like PIDs are reused and throw
    errors as specified in:

    https://stackoverflow.com/questions/12051485/killing-processes-with-psutil

    :raises NoSuchProcess, ZombieProcess: As mentioned above; required for macOS

    :raises AccessDenied: Root required to query process data
    """
    for process in psutil.process_iter():
        try:
            cmd_string = " ".join(process.cmdline())
            for target_string in TERMINATION_LIST:
                if cmd_string.startswith(target_string):
                    print(f"Killing process {process.pid} - {cmd_string}")
                    process.terminate()
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            exit("In order for process data to be queried, this script must "
                f"be ran with root priveledges.\nTry:\nsudo python3 {argv[0]}")


if __name__ == "__main__":
    main()
