"""
Script was created for the purpose of gracefully killing hung SSH terminals
from when the laptop closes down for travel and the SSH tunnels were not closed
properly.

Add to the TERMINATION_LIST the cmd_line string to look for.
"""

import psutil
from time improt sleep
from sys import argv

# List of cmd_line string to compare against
TERMINATION_LIST = (
        "logioptionsplus_agent",
        )


def get_process(processes: dict = {}) -> dict:
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
            for target_string in TERMINATION_LIST:
                if process.name() == target_string:
                    if processes.get(process.name()):
                        processes[process.name()]["new_pid"] = process.pid
                    else:
                        processes[process.name()] = {"process": process, "old_pid": process.pid, "new_pid": 0}
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            continue
        except psutil.AccessDenied:
            exit("In order for process data to be queried, this script must "
                f"be ran with root priveledges.\nTry:\nsudo python3 {argv[0]}")

    return processes


def main() -> None:
    processes = get_process()
    if not processes:
        exit("[!] Did not find any processes")

    for process in processes.keys():
        old_pid = processes[process].get("old_pid")
        proc = processes[process].get("process")
        cmd_line = proc.cmdline()
        print(f"Killing process {old_pid} - {cmd_line}")

        proc.send_signal(9)

    # Wait a few seconds for the processes to restart
    print("Waiting 2 seconds to allow processes to start...")
    sleep(2)

    processes = get_process(processes)
    for process in processes.keys():
        old_pid = processes[process].get("old_pid")
        new_pid = processes[process].get("new_pid")

        print(f"Process {new_pid} became {old_pid}")




if __name__ == "__main__":
    main()
