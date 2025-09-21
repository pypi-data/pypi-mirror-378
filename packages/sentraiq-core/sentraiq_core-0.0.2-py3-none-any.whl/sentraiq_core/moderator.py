import os
from typing import Dict, Any
from .config import ModerationConfig


class ContentModerator:

    def __init__(self, config: ModerationConfig):

        self.config = config
        print(f"ContentModerator initialized with sensitivity: {self.config.text_sensitivity}")

    def moderate_text(self, text: str) -> Dict[str, Any]:
        print(f"Moderating text: '{text[:30]}...'")
        prohibited_words = {"badword", "error", "danger"}
        found_words = {word for word in prohibited_words if word in text.lower()}

        if found_words:
            return {
                "is_acceptable": False,
                "reason": "Contains prohibited language.",
                "details": {"flagged_words": list(found_words)},
            }

        return {"is_acceptable": True, "reason": None, "details": {}}

    def moderate_image(self, image_path: str) -> Dict[str, Any]:
        print(f"Moderating image at: '{image_path}'")

        file_extension = os.path.splitext(image_path)[1].lstrip(".").lower()

        if file_extension not in self.config.image_allowed_formats:
            return {
                "is_acceptable": False,
                "reason": f"Image format '{file_extension}' is not allowed.",
                "details": {"allowed_formats": self.config.image_allowed_formats},
            }

        return {"is_acceptable": True, "reason": None, "details": {}}