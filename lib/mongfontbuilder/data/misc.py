from typing import Literal, get_args

JoiningPosition = Literal["isol", "init", "medi", "fina"]
joiningPositions: tuple[JoiningPosition] = get_args(JoiningPosition)
