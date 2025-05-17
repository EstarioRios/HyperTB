import os
import json

pathname = os.path.join(os.path.dirname(__file__), "languages.json")

data = [
    {"lan": "English", "wellcome_text": "Hello Wellcome to our "},
    {},
]


with open(pathname, "w", encoding="utf-8") as file:
    json.dump(
        ensure_ascii=True,
        obj=data,
        indent=4,
    )
    