from enum import Enum
import strawberry


@strawberry.enum
class PlasticType(str, Enum):
    PTHALATE = "PTHALATE"
    PTHALATE_SUBSTITUTE = "PTHALATE_SUBSTITUTE"
    BISPHENOL = "BISPHENOL"
