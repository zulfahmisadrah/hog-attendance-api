from app.crud.base import CRUDBase
from app.models.domains import Schedule
from app.models.schemas.schedule import ScheduleCreate, ScheduleUpdate


class CRUDSchedule(CRUDBase[Schedule, ScheduleCreate, ScheduleUpdate]):
    pass


schedule = CRUDSchedule(Schedule)
