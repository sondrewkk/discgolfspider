import re
class BrandHelper:

    brands = [
        "Axiom",
        
        "Dino Discs",
        "Discmania",
        "Disctroyer",
        "Discraft",
        "Divergent Discs",
        "Dynamic Discs",
        
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
        "MVP",

        "Prodigy",
        "Prodiscus",

        "RPM Discs",
        
        "Streamline",
        
        "Thought Space Athletics",
        
        "Viking Discs",
        
        "Westside Discs",

        "Yikun Discs",
    ]

    @classmethod
    def normalize(cls, brand_name: str) -> str:
      if not brand_name:
        return None

      brand_name = brand_name.split(" ")[0]

      # Special case for brand name TSA
      if brand_name.lower() == "tsa":
        return "Thought Space Athletics"

      index = [i for i, brand in enumerate(cls.brands) if re.search(f"^{brand_name.lower()}", brand.lower())]

      if len(index) != 1:
        return None

      return cls.brands[index[0]]
