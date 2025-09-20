"""https://www.zabbix.com/documentation/5.0/en/manual/api/reference/auditlog/object"""
from zabbix_enums import _ZabbixEnum


class AuditLogAction(_ZabbixEnum):
    """
    https://www.zabbix.com/documentation/5.0/en/manual/api/reference/auditlog/object#audit-log

    Audit log entry action.
    """
    ADD = 0
    UPDATE = 1
    DELETE = 2
    LOGIN = 3
    LOGOUT = 4
    ENABLE = 5
    DISABLE = 6
    EXECUTE = 7


class AuditLogResourceType(_ZabbixEnum):
    """
    https://www.zabbix.com/documentation/5.0/en/manual/api/reference/auditlog/object#audit-log

    Audit log entry resource type.
    """
    USER = 0
    CONFIGURATION_OF_ZABBIX = 2
    MEDIA_TYPE = 3
    HOST = 4
    ACTION = 5
    GRAPH = 6
    GRAPH_ELEMENT = 7
    USER_GROUP = 11
    APPLICATION = 12
    TRIGGER = 13
    HOST_GROUP = 14
    ITEM = 15
    IMAGE = 16
    VALUE_MAP = 17
    SERVICE = 18
    MAP = 19
    SCREEN = 20
    WEB_SCENARIO = 22
    DISCOVERY_RULE = 23
    SLIDE_SHOW = 24
    SCRIPT = 25
    PROXY = 26
    MAINTENANCE = 27
    REGULAR_EXPRESSION = 28
    MACRO = 29
    TEMPLATE = 30
    TRIGGER_PROTOTYPE = 31
    ICON_MAPPING = 32
    DASHBOARD = 33
    EVENT_CORRELATION = 34
    GRAPH_PROTOTYPE = 35
    ITEM_PROTOTYPE = 36
    HOST_PROTOTYPE = 37
    AUTOREGISTRATION = 38
    MODULE = 39
