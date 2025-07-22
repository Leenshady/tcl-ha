def try_read_as_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value == '1'

    if isinstance(value, int):
        return value == 1

    raise ValueError('[{}]无法被转为bool'.format(value))

def get_key_by_value(d, value):
    for key, val in d.items():
        if val == value:
            try:
                return int(key)
            except ValueError:
                # 如果转换失败，返回原字符串
                return key
    return None  # 如果没有找到，返回None
