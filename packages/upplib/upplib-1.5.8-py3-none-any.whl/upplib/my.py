from upplib import *
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Union
from aliyun.log import LogClient, GetLogsRequest


def query_sls_logs(logstore_name: str = '',
                   minute: int = 600,
                   query: str = '',
                   config_name: str = '',
                   default_tz: str = '+07:00') -> None:
    start_time, end_time = (t[0], t[1]) if (t := get_from_txt()) and t[0] is not None else (get_timestamp() - 60 * minute, get_timestamp())
    start_time = get_timestamp(start_time)
    end_time = get_timestamp(end_time)
    to_print_file(logstore_name, mode='w', file_path='', file_name=logstore_name)
    to_print_file(f'start_time: {to_datetime_str(start_time, tz=default_tz)}')
    to_print_file(f'end_time  : {to_datetime_str(end_time, tz=default_tz)}')
    to_print_file(query)
    c = get_config_data(config_name)
    response = (LogClient(c.get('endpoint'), c.get('access_key_id'), c.get('access_key_secret'))
                .get_logs(GetLogsRequest(c.get('project_name'), logstore_name, start_time, end_time, line=500, query=query)))
    to_print_file(f"共 {response.get_count()} 条日志:")
    logs = response.get_logs()
    for log in reversed(logs):
        to_print_file(get_log_msg_7(log.contents))

    to_print_file('END__END')
