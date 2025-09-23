from enum import StrEnum


class Granularity(StrEnum):
    BASIC = "basic"
    STANDARD = "standard"
    FULL = "full"


class IdentifierType(StrEnum):
    ID = "id"
    UUID = "uuid"
    KEY = "key"
    NAME = "name"


class Key(StrEnum):
    REGULAR = "regular"
    INTERNAL = "internal"
    CLIENT = "client"
    PARTNER = "partner"
    VENDOR = "vendor"
    GOVERNMENT = "government"
    HOSPITAL_SYSTEM = "hospital_system"
    HOSPITAL = "hospital"
    MEDICAL_GROUP = "medical_group"
    DEPARTMENT = "deparment"
    DIVISION = "division"
    CLINIC = "clinic"
    PRIMARY_HEALTH_CARE = "primary_health_care"
    BRANCH = "branch"
    NETWORK = "network"
    UNIT = "unit"
    CORPORATION = "corporation"
    SUBSIDIARY = "subsidiary"
    REGIONAL_OFFICE = "reginal_office"
    APPLICATION = "application"
