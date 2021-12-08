"""
For some reason whenever 1password updates it prevents the browser extension
in safari from working. I contacted agile and they said that they are trying
to workout the bug with Apple. For now, we can just kill the processes after
a reboot
"""

import psutil
from sys import argv

# List of cmd_line string to compare against
TERMINATION_LIST = (
        "/Applications/1Password 7.app/Contents/MacOS/1Password 7",
        "/Applications/1Password 7.app/Contents/PlugIns/1PasswordSafariAppExtension.appex/Contents/MacOS/1PasswordSafariAppExtension",
        "agilebits.onepassword7-helper"
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
                if target_string in cmd_string:
                    print(f"Killing process {process.pid} - {cmd_string}")
                    process.terminate()
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            exit("In order for process data to be queried, this script must "
                f"be ran with root priveledges.\nTry:\nsudo python3 {argv[0]}")


if __name__ == "__main__":
    main()
