'''
Created on 17.03.2017

@author: michael
'''
import os
from django.core.management import execute_from_command_line
from alex_test_utils import TestEnvironment

if __name__ == '__main__':
    
    testenv = TestEnvironment()
    os.environ.setdefault("ALEX_CONFIG", testenv.config_file_name)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alexandriaweb.settings")

    execute_from_command_line(['manage.py', 'test'])

    testenv.cleanup()
