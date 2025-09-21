import imu_service_pb2 as _imu_service_pb2
import rfid_service_pb2 as _rfid_service_pb2
import audio_service_pb2 as _audio_service_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class HealthCheckRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthCheckResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class OrchestratorStatusRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class OrchestratorStatusResponse(_message.Message):
    __slots__ = ("is_ready", "current_activity")
    IS_READY_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    is_ready: bool
    current_activity: str
    def __init__(self, is_ready: bool = ..., current_activity: _Optional[str] = ...) -> None: ...
