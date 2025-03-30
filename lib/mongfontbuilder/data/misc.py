from typing import Literal, get_args

JoiningPosition = Literal["isol", "init", "medi", "fina"]
joiningPositions: list[JoiningPosition] = [*get_args(JoiningPosition)]
isol, init, medi, fina = joiningPositions
