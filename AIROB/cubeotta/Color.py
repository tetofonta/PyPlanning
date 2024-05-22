from AIROB.domain import PDDLObject
from AIROB.domain.decorators import PDDLPredicate, PDDLType


@PDDLType
class Color(PDDLObject):
    def __init__(self, color):
        super().__init__()
        self.name = color
        self.__empty = False  # for the time being we assume that we never run out of color

    def get_id(self) -> str:
        return f"Color_{self.name}"

    @PDDLPredicate
    def empty(self: 'Color'):
        return self.__empty
