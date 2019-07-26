import Alior
import MBank
import SeleniumDrivers
import unittest
from loguru import logger

browsers = ["Chrome"]

for SeleniumDrivers.current_driver in browsers:
    logger.info("Importing in {}".format(SeleniumDrivers.current_driver))

    # initialize the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # add tests to the test suite
    suite.addTests(loader.loadTestsFromModule(MBank))
    suite.addTests(loader.loadTestsFromModule(Alior))

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)

if __name__ == "__main__":
    unittest.main()
