from typing import Optional, List
from pydantic import BaseModel


class ShotgridCredentials(BaseModel):
    shotgrid_url: Optional[str] = None
    shotgrid_script_name: Optional[str] = None
    shotgrid_api_key: Optional[str] = None


class CreateInput(BaseModel):
    project_id: Optional[int] = None
    shotgrid_credentials: ShotgridCredentials | None = None
    entity_type: str
    data: dict
    return_fields: Optional[List[str]] = []


class FindInput(BaseModel):
    project_id: Optional[int] = None
    shotgrid_credentials: ShotgridCredentials | None = None
    entity_type: str
    filters: Optional[List[List[str]]] = []
    fields: Optional[List[str]] = []


class UpdateInput(BaseModel):
    project_id: Optional[int] = None
    shotgrid_credentials: ShotgridCredentials | None = None
    entity_type: str
    entity_id: int
    data: dict


class DeleteInput(BaseModel):
    project_id: Optional[int] = None
    shotgrid_credentials: ShotgridCredentials | None = None
    entity_type: str
    entity_id: int


# class CreateRequest(BaseModel):
#     input: CreateInput
#     session_variables: SessionVariables | None = None
#
#
# class FindRequest(BaseModel):
#     input: FindInput
#     session_variables: SessionVariables | None = None
#
#
# class UpdateRequest(BaseModel):
#     input: UpdateInput
#     session_variables: SessionVariables | None = None
#
#
# class DeleteRequest(BaseModel):
#     input: DeleteInput
#     session_variables: SessionVariables | None = None
