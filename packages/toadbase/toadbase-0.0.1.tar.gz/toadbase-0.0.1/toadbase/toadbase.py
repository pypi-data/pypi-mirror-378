from typing import Any
from toadbase import models as shotgrid_models
import requests


class ToadBase:
    def __init__(
        self,
        project_id: int,
        user_id: int,
        url_base: str,
        api_key: str,
    ):
        self.project_id = project_id
        self.user_id = user_id
        self.url_base = url_base
        self.api_key = api_key

    def _do_request(self, url, payload):
        request_url = f'{self.url_base}/{url}'
        data = {
            'input': payload,
            'session_variables': self.session_vars
        }
        headers = {
            'X-Event-Secret': self.api_key,
            'mimetype': 'application/json'
        }
        response = requests.post(
            url=request_url,
            headers=headers,
            json=data,
        )
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def shotgrid_find(
        self,
        entity: str,
        filters: list[list[str]] | None = None,
        fields: list[str] | None = None
    ):
        return self._do_request(
            url='shotgrid/find',
            payload=shotgrid_models.FindInput(
                project_id=self.project_id,
                entity_type=entity,
                filters=filters if filters else [],
                fields=fields if fields else ['id', 'code']
            ).model_dump()
        )

    def shotgrid_find_one(
        self,
        entity: str,
        filters: list[list[str]] | None = None,
        fields: list[str] | None = None
    ):
        return self._do_request(
            url='shotgrid/find-one',
            payload=shotgrid_models.FindInput(
                project_id=self.project_id,
                entity_type=entity,
                filters=filters if filters else [],
                fields=fields if fields else ['id', 'code']
            ).model_dump()
        )

    def shotgrid_create(
        self,
        entity: str,
        data: dict[str, Any],
        return_fields: list[str] | None = None
    ):
        return self._do_request(
            url='shotgrid/create',
            payload=shotgrid_models.CreateInput(
                project_id=self.project_id,
                entity_type=entity,
                data=data,
                return_fields=return_fields if return_fields else ['id', 'code']
            ).model_dump()
        )

    def shotgrid_update(
        self,
        entity: str,
        entity_id: int,
        data: dict[str, Any],
    ):
        return self._do_request(
            url='shotgrid/update',
            payload=shotgrid_models.UpdateInput(
                project_id=self.project_id,
                entity_type=entity,
                entity_id=entity_id,
                data=data
            ).model_dump()
        )

    def shotgrid_delete(
        self,
        entity: str,
        entity_id: int,
    ):
        return self._do_request(
            url='shotgrid/delete',
            payload=shotgrid_models.DeleteInput(
                project_id=self.project_id,
                entity_type=entity,
                entity_id=entity_id,
            ).model_dump()
        )

    @property
    def session_vars(self):
        return {
            'x-hasura-user-id': self.user_id,
        }
