from upplib import *
from datetime import datetime, timezone, timedelta
from typing import Any, Optional, Union
from aliyun.log import LogClient, GetLogsRequest

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdklts.v2.region.lts_region import LtsRegion
from huaweicloudsdklts.v2 import *
from upplib import *


def query_sls_logs(logstore_name: str = '',
                   minute: int = 600,
                   limit: int = 500,
                   query: str = '',
                   config_name: str = '',
                   start_time: datetime | str | None = None,
                   end_time: datetime | str | None = None,
                   default_tz: str = '+07:00') -> None:
    if start_time is None and end_time is None:
        start_time, end_time = (t[0], t[1]) if (t := get_from_txt()) and t[0] is not None else (get_timestamp() - 60 * minute, get_timestamp())
    start_time = get_timestamp(start_time)
    end_time = get_timestamp(end_time)
    to_print_file(logstore_name, mode='w', file_path='', file_name=logstore_name)
    to_print_file(f'start_time: {to_datetime_str(start_time, tz=default_tz)}')
    to_print_file(f'end_time  : {to_datetime_str(end_time, tz=default_tz)}')
    to_print_file(query)
    c = get_config_data(config_name)
    response = (LogClient(c.get('endpoint'), c.get('access_key_id'), c.get('access_key_secret'))
                .get_logs(GetLogsRequest(c.get('project_name'), logstore_name, start_time, end_time, line=limit, query=query)))
    to_print_file(f"共 {response.get_count()} 条日志:")
    logs = response.get_logs()
    for log in reversed(logs):
        to_print_file(get_log_msg(log.contents, default_tz=default_tz))
    to_print_file('END__END')


def search_lts_logs(keywords: str | None = '',
                    limit: int = 500,
                    minute: int = 600,
                    containerName: str = '',
                    appName: str = '',
                    config_name: str = '',
                    default_tz: str = '-06:00',
                    start_time: datetime | str | None = None,
                    end_time: datetime | str | None = None,
                    ) -> None:
    if start_time is None and end_time is None:
        start_time, end_time = (t[0], t[1]) if (t := get_from_txt()) and t[0] is not None else (get_timestamp() - 60 * minute, get_timestamp())
    start_time = get_timestamp_ms(start_time)
    end_time = get_timestamp_ms(end_time)
    to_print_file(appName, mode='w', file_path='', file_name=appName)
    to_print_file(f'start_time: {to_datetime_str(start_time, tz=default_tz)}')
    to_print_file(f'end_time  : {to_datetime_str(end_time, tz=default_tz)}')
    c = get_config_data(config_name)
    credentials = BasicCredentials(c['ak'], c['sk'])
    client = LtsClient.new_builder().with_credentials(credentials).with_region(LtsRegion.value_of(c['region'])).build()
    list_logs_req = ListLogsRequest()
    list_logs_req.log_group_id = c['group_id']
    list_logs_req.log_stream_id = c['stream_id']
    list_logs_req.body = QueryLtsLogParams(
        limit=limit,
        keywords=keywords,
        is_count=False,
        highlight=False,
        is_desc=True,
        labels={
            "containerName": containerName,
            "appName": appName
        },
        start_time=str(start_time),
        end_time=str(end_time)
    )
    to_print_file(list_logs_req.body)
    logs = client.list_logs(list_logs_req)
    if logs and logs.logs:
        to_print_file(f"共找到 {len(logs.logs)} 条日志:")
        for log in logs.logs[::-1]:
            s1 = log.content.split('  ')
            to_print_file(f'{to_datetime_str(s1[0], default_tz=default_tz)} {log.content[len(s1[0]) + 2:]}')
    else:
        to_print_file("未查询到日志")
    to_print_file('END__END')
