import sys
import subprocess
import logging
from dataclasses import dataclass
from typing import Union


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


def runsolver(solver_cmd: [str], config=DEFAULT_RUNSOLVER_CONFIGURATION, stderr=sys.stderr) -> (str, str):
    cmd = build_command(solver_cmd, config)

    logging.debug(f'start runsolver: "{" ".join(cmd)}"')
    proc = subprocess.Popen(cmd,
                            stderr=stderr,
                            stdout=subprocess.PIPE
                            )
    output, err = proc.communicate()

    return output, err


def build_command(solver_cmd: [str], config: RunsolverConfiguration) -> [str]:
    cmd = [config.runsolver_bin]

    runsolver_parameters = config.parameters()
    for n,v in runsolver_parameters.items():
        cmd += __add_cmd(n, v)

    cmd += solver_cmd

    return cmd


def __add_cmd(name: str, value: any) -> [str]:
    return [name, str(value)] if value else []