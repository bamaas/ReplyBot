import unittest
from DataRunner import DataRunner
from DataRunner import actions

class TestDataRunner(unittest.TestCase):

    username = "set_username_here"
    password = "set_password_here"

    # Quickly test all the DataRunner actions in one test (dirty fix)
    def test_all_datarunner_actions(self):
        for action in actions:
            DataRunner().run(username=self.username, password=self.password, action=action)

if __name__ == '__main__':
    unittest.main()