from enum import StrEnum


class IdSource(StrEnum):
    HEADER = "header"
    STATE = "state"


class OperationType(StrEnum):
    RESOURCE = "resource"
    REQUEST = "request"
    SYSTEM = "system"
    WEBSOCKET = "websocket"


class SystemOperationType(StrEnum):
    BACKGROUND_JOB = "background_job"
    CONFIGURATION_UPDATE = "configuration_update"
    CRON_JOB = "cron_job"
    DATABASE_CONNECTION = "database_connection"
    DISPOSAL = "disposal"
    HEALTH_CHECK = "health_check"
    HEARTBEAT = "heartbeat"
    METRIC_REPORT = "metric_report"
    INITIALIZATION = "initialization"
    STARTUP = "startup"
    SHUTDOWN = "shutdown"
    SYSTEM_ALERT = "system_alert"


class WebSocketOperationType(StrEnum):
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    ERROR = "error"
    RECEIVE = "receive"
    SEND = "send"


class ResourceOperationType(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class ResourceOperationCreateType(StrEnum):
    NEW = "new"
    RESTORE = "restore"


class ResourceOperationUpdateType(StrEnum):
    DATA = "data"
    STATUS = "status"


class ResourceOperationDataUpdateType(StrEnum):
    FULL = "full"
    PARTIAL = "partial"


class ResourceOperationStatusUpdateType(StrEnum):
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    RESTORE = "restore"
    DELETE = "delete"


class Origin(StrEnum):
    SERVICE = "service"
    CLIENT = "client"
    UTILITY = "utility"


class Layer(StrEnum):
    INFRASTRUCTURE = "infrastructure"
    CONFIGURATION = "configuration"
    UTILITY = "utility"
    MIDDLEWARE = "middleware"
    CONTROLLER = "controller"
    SERVICE = "service"
    REPOSITORY = "repository"
    INTERNAL = "internal"
    OTHER = "other"


class Target(StrEnum):
    MONITORING = "monitoring"
    CACHE = "cache"
    CONTROLLER = "controller"
    DATABASE = "database"
    INTERNAL = "internal"
    MICROSERVICE = "microservice"
    SERVICE = "service"
    REPOSITORY = "repository"
    THIRD_PARTY = "third_party"
