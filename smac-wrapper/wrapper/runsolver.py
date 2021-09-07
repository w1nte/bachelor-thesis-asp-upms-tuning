import sys
import subprocess
import logging
from dataclasses import dataclass
from typing import Union, List


@dataclass
class RunsolverConfiguration: 
    runsolver_bin: str = 'runsolver/runsolver/src/runsolver'
    vsize_limit: Union[int, None] = 1024  # megabyte
    wall_clock_limit: Union[int, None] = 60  # seconds
    watcher_data: Union[str, None] = '/dev/null'  # watcher file log

    def parameters(self):
        return {
            '--vsize-limit': self.vsize_limit,
            '--watcher-data': self.watcher_data,
            '--wall-clock-limit': self.wall_clock_limit
        }


DEFAULT_RUNSOLVER_CONFIGURATION = RunsolverConfiguration()


def runsolver(solver_cmd: List[str], config=DEFAULT_RUNSOLVER_CONFIGURATION, stderr=sys.stderr) -> str:
    """
    Execute a command with Runsolver. Be sure, that the configs runsolver binary location is correct.
    """
    cmd = build_command(solver_cmd, config)

    logging.debug(f'start runsolver: "{" ".join(cmd)}"')
    proc = subprocess.Popen(cmd,
                            stderr=stderr,
                            stdout=subprocess.PIPE
                            )
    output, _ = proc.communicate()

    return output


def build_command(solver_cmd: List[str], config: RunsolverConfiguration) -> List[str]:
    cmd = [config.runsolver_bin]

    runsolver_parameters = config.parameters()
    for n,v in runsolver_parameters.items():
        cmd += __add_cmd(n, v)

    cmd += solver_cmd

    return cmd


def __add_cmd(name: str, value: any) -> List[str]:
    return [name, str(value)] if value else []