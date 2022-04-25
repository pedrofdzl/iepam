from ast import arg
from .permissions.create_groups import create_groups

def db(*arguments):
    
    if len(arguments) < 2:
        print('Incorrect usage of "permissions" module')
    elif arguments[1] == 'creategroups':
        create_groups()
