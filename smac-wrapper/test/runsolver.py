import unittest
from wrapper.runsolver import RunsolverConfiguration, runsolver, build_command


class TestRunsolver(unittest.TestCase):

    def test_build_command(self):
        config = self.__get_config()
        params = build_command(['solver', 'arg1'], config)
        expected = [config.runsolver_bin, '--vsize-limit', str(config.vsize_limit), '--wall-clock-limit', str(config.wall_clock_limit), 'solver', 'arg1']
        self.assertEqual(params, expected)

    def test_runsolver(self):
        config = self.__get_config()
        config.watcher_data = '/dev/null'
        expected = 42
        result = int(runsolver(['echo', f'"{expected}"'], config)[1:3])
        self.assertEqual(result, expected)

    def __get_config(self):
        return RunsolverConfiguration(runsolver_bin='runsolver/runsolver/src/runsolver', vsize_limit=1024, wall_clock_limit=60, watcher_data=None)


if __name__ == '__main__':
    unittest.main()
