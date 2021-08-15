from sqlalchemy import Column, BigInteger, DateTime, func, ForeignKey
from sqlalchemy.orm import declared_attr


class IdMixin(object):
    id = Column(BigInteger, autoincrement=True, primary_key=True, index=True)


class TimeStampMixin(object):
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class SoftDeleteMixin(object):
    @declared_attr
    def deleted_at(cls):
        return Column(DateTime)

    @declared_attr
    def deleted_by(cls):
        return Column(BigInteger, ForeignKey("user.id"))


class TimeStampByUserMixin(object):
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def updated_by(cls):
        return Column(BigInteger, ForeignKey("user.id"))


class CommonModel(IdMixin, TimeStampMixin):
    pass


class BlameModel(IdMixin, TimeStampByUserMixin):
    pass
