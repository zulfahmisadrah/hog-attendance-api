from enum import Enum


class RoleEnum(str, Enum):
    SUPER_USER = "ROLE_SUPERUSER"
    ADMIN = "ROLE_ADMIN"
    LECTURER = "ROLE_LECTURER"
    STUDENT = "ROLE_STUDENT"


class DayOfWeek(int, Enum):
    Senin = 1
    Selasa = 2
    Rabu = 3
    Kamis = 4
    Jumat = 5
    Sabtu = 6
    Minggu = 7


class MeetingStatus(str, Enum):
    Terjadwal = "Terjadwal"
    Berlangsung = "Berlangsung"
    Selesai = "Selesai"


class AttendanceStatus(str, Enum):
    Absen = "Absen"
    Hadir = "Hadir"
    Izin = "Izin"
    Sakit = "Sakit"


class DatasetType(str, Enum):
    TRAINING = "train"
    VALIDATION = "val"


class MeetingType(str, Enum):
    NEAREST = "nearest"
    TODAY = "today"
    UPCOMING = "upcoming"
    FINISHED = "finished"
