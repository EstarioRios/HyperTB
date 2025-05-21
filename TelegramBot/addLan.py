import os
import json

pathname = os.path.join(os.path.dirname(__file__), "languages.json")

data = [
    {
        "languageName": "English",
        "language_form": "lang_en",
        "bad_request": "something get wrong",
    },
    {
        "languageName": "Parsi",
        "language_form": "lang_fa",
        "bad_request": "چیزی اشتباه شد",
    },
    {
        "languageName": "Arabic",
        "language_form": "lang_ar",
        "bad_request": "",
    },
]

with open(pathname, "w", encoding="utf-8") as file:
    json.dump(obj=data, fp=file, ensure_ascii=True, indent=4)
