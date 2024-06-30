from collections import defaultdict


class SuggestionError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class FlightSpecSuggester:
    @classmethod
    def find_suggestion(cls, discs: list) -> dict:
        # Group discs based on flight specs
        grouped = defaultdict(list)

        for disc in discs:
            grouped[(disc["speed"], disc["glide"], disc["turn"], disc["fade"])].append(disc)

        # Check how many groups there is. If there is more than one group, the suggestion can result in
        # data polution if the choosen group has wrong flight spec for the current disc
        number_of_groups = len(grouped.keys())

        if number_of_groups > 1:
            msg = f"To many groups. Chosen group can result in data polution. {grouped.keys()}"
            raise SuggestionError(msg)

        # Return suggested flight spec
        first_group = next(iter(grouped))
        suggestion_disc: dict = grouped[first_group][0]
        flight_spec = {k: v for k, v in suggestion_disc.items() if k in {"speed", "glide", "turn", "fade"}}

        return flight_spec
