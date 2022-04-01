import re


class BrandHelper:

    brands = [
        "Alfa Discs",
        "Axiom",
        "Dino Discs",
        "Disc Golf UK",
        "Discmania",
        "Disctroyer",
        "Discraft",
        "Divergent Discs",
        "Dynamic Discs",
        "Elevation",
        "EV-7",
        "Gateway Discs",
        "Guru",
        "Innova",
        "Infinite Discs",
        "Kastaplast",
        "Latitude 64",
        "Launch",
        "Legacy Discs",
        "Løft",
        "Millenium Discs",
        "Momentum Disc Golf",
        "MVP",
        "Prodigy",
        "Prodiscus",
        "RPM Discs",
        "Streamline",
        "Thought Space Athletics",
        "Viking Discs",
        "Westside Discs",
        "Wild Discs",
        "X-COM",
        "Yikun Discs",
    ]

    @classmethod
    def normalize(cls, brand_name: str) -> str:
        if not brand_name:
            return None

        brand_name = brand_name.split(" ")[0].lower()

        # Special case for brand name TSA
        if brand_name == "tsa":
            return "Thought Space Athletics"

        if brand_name == "disc":
            return "Disc Golf UK"

        index = [i for i, brand in enumerate(cls.brands) if re.search(f"^{brand_name}", brand.lower())]
        if len(index) != 1:
            return None

        return cls.brands[index[0]]
