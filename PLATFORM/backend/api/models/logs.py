from typing import Dict, Optional

from pydantic import Field

from bracelet_lib.models.common import CustomBaseModel


def get_log_entry_schema() -> Dict:
    return {
        'version': {
            'description' : 'Api version',
            'example'     : '0.2.7',
        },
        'x_forwarded_proto': {
            'description' : 'Forwarded protocol',
            'example'     : 'https',
            'alias'       : 'x-forwarded-proto'
        },
        'x_forwarded_host': {
            'description' : 'Forwarded host',
            'example'     : '192.168.128.25',
            'alias'       : 'x-forwarded-host'
        },
        'proto': {
            'description' : 'Request protocol',
            'example'     : 'http'
        },
        'client_ip': {
            'description' : 'Request client ip',
            'example'     : '192.168.1.102',
            'alias'       : 'client-ip'
        },
        'agent': {
            'description' : 'Request user agent',
            'example'     : 'Xiaomi M2003J15SC/Android 10 - Sdk 29 ActivAPP v0.3.0+16'
        },
        'method': {
            'description' : 'Request method',
            'example'     : 'GET',
        },
        'request': {
            'description' : 'Request path',
            'example'     : '/v1/rooms',
        },
        'query': {
            'description' : 'Request query params',
            'example'     : {'limit': 50, 'from_prev': False},
        },
        'status': {
            'description' : 'Response status',
            'example'     : 200
        },
        'body': {
            'description' : 'Received payload',
            'example'     : "{'name': 'Michael', 'age': 24}"
        }
    }


log_entry_schema = get_log_entry_schema()


class LogEntry(CustomBaseModel):
    version           : str  = Field(..., **log_entry_schema['version'])
    x_forwarded_proto : Optional[str] = Field(None, **log_entry_schema['x_forwarded_proto'])
    x_forwarded_host  : Optional[str] = Field(None, **log_entry_schema['x_forwarded_host'])
    proto             : str  = Field(..., **log_entry_schema['proto'])
    client_ip         : str  = Field(..., **log_entry_schema['client_ip'])
    agent             : str  = Field(..., **log_entry_schema['agent'])
    method            : str  = Field(..., **log_entry_schema['method'])
    request           : str  = Field(..., **log_entry_schema['request'])
    query             : Dict = Field(..., **log_entry_schema['query'])
    status            : int  = Field(..., **log_entry_schema['status'])
    body              : Optional[str] = Field(None, **log_entry_schema['body'])