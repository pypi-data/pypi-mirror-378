from upplib import *
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Union


def get_log_msg(contents: dict,
                default_tz: Optional[Union[str, timezone]] = None) -> str:
    """
    获得日志
    """
    # time
    # 2025-09-22T03:19:30+07:00
    _time_ = None
    for k in ['_time_', 'time', '__time___0']:
        if k in contents and contents[k] != 'null':
            _time_ = to_datetime_str(contents[k], default_tz=default_tz)
            break
    level = None
    if 'level' in contents and contents['level'] != 'null':
        level = contents['level']
    # content
    content = None
    for k in ['content', 'message', 'msg']:
        if k in contents and contents[k] != 'null':
            content = contents[k]
            break
    if content is not None and len(str(content).split(' ')) >= 2:
        time_str = ' '.join(str(content).split(' ')[0:2])
        time_1 = to_datetime(time_str, error_is_none=True)
        # content 中, 含有时间，是以时间开头的字符串
        if time_1 is not None and _time_ is not None:
            content = content[len(time_str):].strip()
    return ' '.join(filter(lambda s: s is not None, [_time_, level, content]))


def get_from_txt(file_name: str = '_start_time_end_time_str.txt',
                 second: int | float = 0.5) -> tuple[datetime | None, datetime | None]:
    """
        从配置文件中获得 datetime
        file_name : 指定文件, 自动忽略掉文件中的 # 开头的行
        second : 获得时间，在 second 基础上，前后冗余多少秒
        获得日志
    """
    date_list = to_list_from_txt(file_name)
    date_list = list(filter(lambda x: len(x) > 0 and not str(x).strip().startswith('#'), date_list))
    if len(date_list) == 0:
        return None, None
    date_time_list = []
    for date_one in date_list:
        date_time_list.append(to_datetime(date_one))
    date_time_list.sort()
    min_time = to_datetime_add(date_time_list[0], seconds=-second)
    max_time = to_datetime_add(date_time_list[-1], seconds=second)
    return min_time, max_time
