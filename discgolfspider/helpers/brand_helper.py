import re


class BrandHelper:

    brands = [
        "Alfa Discs",
        "Axiom",
        "Birdie Disc Golf Supply",
        "Clash Discs",
        "DGA",
        "Dino Discs",
        "Disc Golf UK",
        "Discmania",
        "Disctroyer",
        "Discraft",
        "Divergent Discs",
        "Dynamic Discs",
        "Elevation",
        "EV-7",
        "Finish Line",
        "Gateway Discs",
        "Guru",
        "Hooligan Discs",
        "Innova",
        "Infinite Discs",
        "Kastaplast",
        "Latitude 64",
        "Launch",
        "Legacy Discs",
        "Lone Star",
        "Løft",
        "Millennium Discs",
        "Mint Discs",
        "Momentum Disc Golf",
        "MVP",
        "Northstar",
        "Prodigy",
        "Prodiscus",
        "RPM Discs",
        "Sacred Discs",
        "Streamline",
        "Thought Space Athletics",
        "Trash Panda",
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
        if brand_name in ("tsa", "thought", "thoght"):
            return "Thought Space Athletics"

        if brand_name == "disc":
            return "Disc Golf UK"

        index = [i for i, brand in enumerate(cls.brands) if re.search(f"^{brand_name}", brand.lower())]
        if len(index) != 1:
            return None

        return cls.brands[index[0]]
