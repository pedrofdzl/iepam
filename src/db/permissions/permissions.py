"""
    All default permissions for the user groups
"""

# Default permissions
# add_model: create
# view_model: read
# change_model: update
# delete_model: delete


ADMIN_PERMISSIONS = [
    "is_admin", 'is_teacher', 'is_student'
]


TEACHER_PERMISSIONS = [
    'is_teacher', 'is_student',
]

STUDENT_PERMISSIONS = [
    'is_student'
]
