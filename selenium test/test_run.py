from tests import login_test , register_test , dashboard_test , DataManagment_test , BulkUpload_test , scheduler_test , GoogleLogin_test


"""
login_test = tests the login functionality.
register_test = tests the register functionality.
dashboard_test = tests for single add domain , refresh all , domain deletion and logout functionality.
DataManagment_test = tests to see if 2 users are sharing the same dashboard.
BulkUpload_test = tests the bulk upload functionality.
scheduler_test = tests the scheduler functionality.
GoogleLogin_test = tests the google login functionality.

choose which of the tests you want to perform and add it to the list below
"""
if __name__ == "__main__":
    register_test()
    login_test()
    dashboard_test()
    DataManagment_test()
    BulkUpload_test()
    scheduler_test()
    GoogleLogin_test()
    

