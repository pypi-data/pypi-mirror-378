from osbot_utils.type_safe.Type_Safe__Primitive import Type_Safe__Primitive

class Timestamp_Now(Type_Safe__Primitive, int):
    def __new__(cls, value=None):
        from osbot_utils.utils.Misc import timestamp_now

        if value is None:
            value = timestamp_now()
        return int.__new__(cls, value)

    def __init__(self, value=None):
        from osbot_utils.utils.Misc import timestamp_now

        self.value = value if value is not None else timestamp_now()

    def __str__(self):
        return str(self.value)