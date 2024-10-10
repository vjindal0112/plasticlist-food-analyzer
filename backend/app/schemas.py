import strawberry

from .types import PlasticType


@strawberry.input
class FoodImageInput:
    base_64_image: str


@strawberry.type
class PlasticAmount:
    plastic_type: PlasticType
    amount: int
    unit: str


@strawberry.type
class Food:
    name: str
    plastic_amounts: list[PlasticAmount]
