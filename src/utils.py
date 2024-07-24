from enum import Enum


class TagsEnum(str, Enum):
    MAIN = 'main'


tags_metadata = [
    {
        'name': TagsEnum.MAIN,
        'description': 'General purpose routes',
    },
]
