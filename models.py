from pydantic import BaseModel
from typing import List

class BaseEntity(BaseModel):
    value: str

class Domain(BaseEntity):
    pass

class IPAddress(BaseEntity):
    pass

class Email(BaseEntity):
    pass

class Username(BaseEntity):
    pass

class Subdomain(BaseEntity):
    pass

class URL(BaseEntity):
    pass

class Port(BaseEntity):
    pass

class Service(BaseEntity):
    pass

class PhishingDomain(BaseEntity):
    pass

class PhoneNumber(BaseEntity):
    pass

class Technology(BaseEntity):
    pass

class ScreenshotFile(BaseEntity):
    pass

class EmailStatus(BaseEntity):
    pass

class Metadata(BaseEntity):
    pass

class GPSLocation(BaseEntity):
    pass
