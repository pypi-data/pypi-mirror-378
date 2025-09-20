from dataclasses import dataclass
from typing import final


@final
@dataclass(slots=True)
class D3SystemInfo:
    major: int
    minor: int
    patch: int
    build: int
    branch: str
    api_port: int


@final
@dataclass(slots=True)
class MachineHealthInfo:
    revision_number: int
    project_folder_check: bool
    project_folder_shared: bool
    is_service_running: bool
    is_buddy_running: bool
    can_see_storage_server: bool
    can_see_teamcity: bool


class AgentHandlerException(Exception):
    pass
