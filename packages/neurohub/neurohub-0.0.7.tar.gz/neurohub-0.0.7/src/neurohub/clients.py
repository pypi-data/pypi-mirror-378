from uuid import UUID
from typing import Optional
from .base import BaseClient


class Clients():
    def __init__(self, base: BaseClient):
        self._base = base
    def upsert(self, client_uuid: Optional[UUID], client_name: str):
        params = {
            'client_uuid': None if not client_uuid else str(client_uuid),
            'client_name': client_name
        }
        resp = self._base.make_request('client', 'POST', params=params)
        return UUID(resp['client_uuid'])
