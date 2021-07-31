import re
from typing import Any
from sqlalchemy.ext.declarative import as_declarative, declared_attr


# def pluralize(word):
#     if re.search('[sxz]$', word):
#         return re.sub('$', 'es', word)
#     elif re.search('[^aeioudgkprt]h$', word):
#         return re.sub('$', 'es', word)
#     elif re.search('[aeiout]y$', word):
#         return re.sub('y$', 'ies', word)
#     else:
#         return word + 's'

@as_declarative()
class Base:
    id: Any
    __name__: str

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()
        # return pluralize(cls.__name__.lower())
