from typing import List, Literal


class ModerationConfig:

    def __init__(
        self,
        api_key: str,
        text_sensitivity: Literal["low", "medium", "high"] = "medium",
        image_allowed_formats: List[str] = None,
    ):
        if not api_key:
            raise ValueError("An API key is required for moderation.")

        self.api_key = api_key
        self.text_sensitivity = text_sensitivity
        self.image_allowed_formats = image_allowed_formats or ["jpeg", "png", "webp"]