from enum import Enum, unique


@unique
class Platforms(Enum):
    Windows = 'Windows'
    Linux = 'Linux'
    Darwin = 'Darwin'
