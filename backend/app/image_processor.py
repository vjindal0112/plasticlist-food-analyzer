import csv
import os
from pathlib import Path
import requests
from .schemas import Food, PlasticAmount
from .types import PlasticType
import numpy as np
import inflect

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
}

REPORTED_PACKAGING_INDEX = 3
PHTHALATES_INDEX = 7
PHTHALATES_SUB_INDEX = 8
BISPHENOLS_INDEX = 9


def get_food_from_image(base64_image: str) -> Food | None:
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What’s in this image? Give me only one word that describes the image best. Don't include any other text nor punctuation.",  # noqa E501
                    },
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 300,
    }
    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    csv_file_path = Path(__file__).parent.parent / "data" / "plasticlist.csv"

    # Initialize a list to store rows of data
    data = []

    # Read the CSV file
    with open(csv_file_path, mode="r") as file:
        reader = csv.reader(file, delimiter=",")
        _headers_not_needed = next(reader)  # Skip the header row
        for row in reader:
            if any(field.strip() for field in row):
                data.append(row)

    data_array = np.array(data)

    response_json = response.json()
    response_content = response_json["choices"][0]["message"]["content"]
    print("response_content: ", response_content)

    payload["messages"].append(
        {"role": "assistant", "content": [{"type": "text", "text": response_content}]}
    )

    # Initialize the inflect engine
    inflect_engine = inflect.engine()

    # Create singular and plural forms
    singular = inflect_engine.singular_noun(response_content) or response_content
    plural = inflect_engine.plural_noun(singular)

    # Extract the first column and the reported packaging column
    first_column = data_array[:, 0]
    reported_packaging = data_array[:, REPORTED_PACKAGING_INDEX]

    # Vectorized case-insensitive substring check for both forms
    mask_singular = np.char.find(np.char.lower(first_column), singular.lower()) != -1
    mask_plural = np.char.find(np.char.lower(first_column), plural.lower()) != -1

    # Combine masks
    mask = mask_singular | mask_plural

    # Get matching items and their corresponding reported packaging
    matches = np.array(
        [
            f"{item} |in| {packaging}"
            for item, packaging in zip(first_column[mask], reported_packaging[mask])
        ]
    )

    print("Matching items:", matches.tolist())

    ingredient_list = {"\n".join(matches.tolist())}

    prompt = f"""
    Given the following list of ingredients:
    {ingredient_list}

    Give me ONLY the matching ingredient from the list which best describes the image from earlier
    """

    payload["messages"].append(
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    )

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    response_json = response.json()
    response_content = response_json["choices"][0]["message"]["content"]
    print("response_content: ", response_content)
    final_response_content = response_content.split("|in|")[0].strip()

    # Find the matching row in data_array
    matching_row_index = np.where(
        np.char.lower(data_array[:, 0]) == final_response_content.lower()
    )[0]

    print()
    print()
    if matching_row_index.size > 0:
        matching_row = data_array[matching_row_index[0]]
        phthalates = matching_row[PHTHALATES_INDEX]
        phthalates_sub = matching_row[PHTHALATES_SUB_INDEX]
        bisphenols = matching_row[BISPHENOLS_INDEX]
        print("Phthalates: ", phthalates)
        print("Phthalates Sub: ", phthalates_sub)
        print("Bisphenols: ", bisphenols)
        return Food(
            name=final_response_content,
            plastic_amounts=[
                PlasticAmount(
                    plastic_type=PlasticType.PTHALATE, amount=phthalates, unit="ng"
                ),
                PlasticAmount(
                    plastic_type=PlasticType.PTHALATE_SUBSTITUTE,
                    amount=phthalates_sub,
                    unit="ng",
                ),
                PlasticAmount(
                    plastic_type=PlasticType.BISPHENOL, amount=bisphenols, unit="ng"
                ),
            ],
        )
    else:
        print("No matching row found for the response content.")

    return None
