from enum import Enum


class RoleEnum(str, Enum):
    SUPER_USER = "ROLE_SUPERUSER"
    ADMIN = "ROLE_ADMIN"
    LECTURER = "ROLE_LECTURER"
    STUDENT = "ROLE_STUDENT"
