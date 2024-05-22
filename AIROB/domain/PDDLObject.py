import uuid


class PDDLObject:
    def __init__(self):
        self.__id = f"inst_{str(uuid.uuid1()).replace('-', '')}"

    def get_id(self) -> str:
        return self.__id

    def __eq__(self, other) -> bool:
        if isinstance(other, PDDLObject):
            return self.__id == other.__id
        return False
