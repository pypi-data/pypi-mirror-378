from uuid import UUID
from typing import Optional

from neurohub.base import BaseClient


class Managers():
    def __init__(self, base: BaseClient):
        self.base = base
    def upsert(self, manager_name: str, department_uuid: UUID | str, manager_uuid: Optional[UUID | str] = None, client_uuid: Optional[UUID | str] = None):
        client_uuid = self.base._handle_client_uuid(client_uuid)
        body = {
            'client_uuid': client_uuid,
            'manager_uuid': manager_uuid,
            'manager_name': manager_name,
            'department_uuid': department_uuid
        }
        resp = self.base.make_request('manager', 'POST', body)
        return UUID(resp['manager_uuid'])
    def delete(self, manager_uuid: UUID | str, client_uuid: Optional[UUID | str]) -> bool:
        client_uuid = self.base._handle_client_uuid(client_uuid)
        params = {
            'client_uuid': client_uuid,
            'manager_uuid': manager_uuid
        }
        resp = self.base.make_request('manager', 'DELETE', params=params)
        return resp['success']


    def get_by_uuid(self, manager_uuid: UUID | str, client_uuid: Optional[UUID | str] = None):
        """Get a single manager by UUID"""
        client_uuid = self.base._handle_client_uuid(client_uuid)
        params = {
            'client_uuid': str(client_uuid),
            'manager_uuid': str(manager_uuid)
        }
        resp = self.base.make_request('manager', 'GET', params=params)
        return resp

    def get_list(self, client_uuid: Optional[UUID | str] = None):
        """Get all managers for a client"""
        client_uuid = self.base._handle_client_uuid(client_uuid)
        params = {'client_uuid': client_uuid}
        resp = self.base.make_request('manager', 'GET', params=params)
        return resp
