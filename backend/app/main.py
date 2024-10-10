import base64

from .image_processor import get_food_from_image
from .types import PlasticType
from .schemas import Food, FoodImageInput, PlasticAmount
from fastapi import FastAPI
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv


@strawberry.type
class Query:
    @strawberry.field
    def foods(self) -> list[Food]:
        return [
            Food(
                name="test",
                plastic_amounts=[
                    PlasticAmount(plastic_type=PlasticType.PTHALATE, amount=1, unit="g")
                ],
            ),
        ]


@strawberry.type
class Mutation:
    @strawberry.mutation
    def get_food_from_image(self, food_image: FoodImageInput) -> Food | None:
        if not is_valid_base64_image(food_image.base_64_image):
            raise ValueError("Invalid base64 image")

        food = get_food_from_image(food_image.base_64_image)

        return food


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app: GraphQLRouter = GraphQLRouter(schema, graphiql=True)


load_dotenv()
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://1c33-2605-59c8-33c5-da10-3058-622c-dbd-b587.ngrok-free.app",
    ],  # Add your Next.js app's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Hello World"}


def is_valid_base64_image(base64_string):
    try:
        # Remove the header if it exists
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]

        # Decode the base64 string
        image_data = base64.b64decode(base64_string)

        # Try to open the image
        Image.open(BytesIO(image_data))

        return True
    except Exception as e:
        print(f"Error validating image: {str(e)}")
        return False
