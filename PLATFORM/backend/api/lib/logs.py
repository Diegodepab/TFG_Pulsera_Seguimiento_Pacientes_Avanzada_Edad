import re
from urllib.parse import parse_qsl
from starlette.requests import Request
from models.logs import LogEntry


async def create_log_entry(request: Request, status_code: int = 200, app_version: str = '') -> LogEntry:
    body_str = (await request.body()) or None
    if body_str is not None and b'password' in body_str:
        body_str = re.sub(b'password=(\w*)', b'password=*****', body_str)

    log_entry = {
        'version': app_version,
        'x-forwarded-proto': request.headers.get('x-forwarded-proto'),
        'x-forwarded-host': request.headers.get('x-forwarded-host'),
        'proto': request.url.scheme,
        'client-ip': request.client.host,
        'agent': request.headers.get('user-agent', 'empty'),
        'method': request.method,
        'request': request.url.path,
        'query': parse_qsl(request.url.query),
        'status': status_code,
        'body': body_str
    }

    return LogEntry(**log_entry)
