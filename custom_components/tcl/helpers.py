def try_read_as_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value == '1'

    if isinstance(value, int):
        return value == 1

    raise ValueError('[{}]无法被转为bool'.format(value))
