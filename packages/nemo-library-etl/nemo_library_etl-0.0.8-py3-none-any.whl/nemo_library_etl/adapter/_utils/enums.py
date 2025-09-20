from enum import Enum


class ETLStep(Enum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"

class ETLAdapter(Enum):
    GEDYS = "gedys"
    HUBSPOT = "hubspot"
    ZENTIS = "zentis"
    GENERICODBC = "genericodbc"
    INFORCOM = "inforcom"


