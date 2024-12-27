from tests import login_test , register_test , dashboard_test , DataManagment_test , BulkUpload_test , scheduler_test , GoogleLogin_test
import sys

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
    try:
        register_test()
        login_test()
        dashboard_test()
        DataManagment_test()
        BulkUpload_test()
        scheduler_test()
        print('all tests passed successfully')
        sys.exit(0)
    except Exception as e:
        print(f"Tests failed: {str(e)}")
        sys.exit(1)
    

    
    

