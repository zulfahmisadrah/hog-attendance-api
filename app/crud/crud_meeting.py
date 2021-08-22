from app.crud.base import CRUDBase
from app.models.domains import Meeting
from app.models.schemas.meeting import MeetingCreate, MeetingUpdate


class CRUDMeeting(CRUDBase[Meeting, MeetingCreate, MeetingUpdate]):
    pass


meeting = CRUDMeeting(Meeting)
