import unittest
from todo.tests.test_send_due_tasks_email import SendDueTasksEmailTest
from todo.tests.test_user_analytics import UserAnalyticsTest
# from test_send_due_tasks_email import SendDueTasksEmailTest
# from test_login_request import LoginRequestTest

def suiteFunc():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(UserAnalyticsTest))
    suite.addTest(unittest.makeSuite(SendDueTasksEmailTest))
    # suite.addTest(unittest.makeSuite(LoginRequestTest))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suiteFunc())
