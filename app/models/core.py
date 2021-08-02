from sqlalchemy import Column, Integer, DateTime, func


class IdMixin(object):
    id = Column(Integer, primary_key=True, index=True)


class TimeStampMixin(object):
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())


class CommonModel(IdMixin, TimeStampMixin):
    pass
