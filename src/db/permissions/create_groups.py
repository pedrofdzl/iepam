"""
Script to generate user groups with its permissions
"""

from django.contrib.auth.models import Group, Permission
from .permissions import ADMIN_PERMISSIONS, TEACHER_PERMISSIONS, STUDENT_PERMISSIONS

GROUP_NAMES = [
    'Administradores',
    'Capacitadores',
    'Estudiantes'
]

def create_groups():
    """
    Create all user groups and its permissions
    In case the group exists adds permissions only
    """

    for name in GROUP_NAMES:
        group = Group.objects.get_or_create(name=name)[0]
        
        # Clear all previous permissions
        group.permissions.clear()

        if name == 'Administradores':
            print(f'Creating {name} Group!')
            for permission in ADMIN_PERMISSIONS:
                perm = Permission.objects.get(codename=permission)
                group.permissions.add(perm)
        elif name == 'Capacitadores':
            print(f'Creating {name} Group!')
            for permission in TEACHER_PERMISSIONS:
                perm = Permission.objects.get(codename=permission)
                group.permissions.add(perm)
        elif name == 'Estudiantes':
            print(f'Creating {name} Group!')
            for permission in STUDENT_PERMISSIONS:
                perm = Permission.objects.get(codename=permission)
                group.permissions.add(perm)