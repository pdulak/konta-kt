import MBank
import SeleniumDrivers
import unittest

browsers = ["Chrome"]

for SeleniumDrivers.current_driver in browsers:
    print("---------------------------------------------------------------------------")
    print("Importing in {}".format(SeleniumDrivers.current_driver))
    print("---------------------------------------------------------------------------")

    # initialize the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # add tests to the test suite
    suite.addTests(loader.loadTestsFromModule(MBank))

    # initialize a runner, pass it your suite and run it
    runner = unittest.TextTestRunner(verbosity=3)
    result = runner.run(suite)

if __name__ == "__main__":
    unittest.main()
