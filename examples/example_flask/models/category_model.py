from typing import List

from models.video_model import Video

# noinspection PyPackageRequirements
from pydantic import BaseModel


class Category(BaseModel):
    category: str
    image: str
    videos: List[Video]
