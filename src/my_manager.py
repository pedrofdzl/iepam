import os
import django


import sys

def main():
    from db.main import db

    if len(sys.argv) < 2:
        print('No valid command')
        sys.exit()

    commands = sys.argv[1:]

    if sys.argv[1] == 'permissions':
        db(*commands)
    else:
        print('No valid command')





if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iepam.settings')
    django.setup()

    main()