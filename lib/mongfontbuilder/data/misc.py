from typing import Literal, cast, get_args

JoiningPosition = Literal["isol", "init", "medi", "fina"]
joiningPositions: tuple[JoiningPosition] = get_args(JoiningPosition)

isol = cast(JoiningPosition, "isol")
init = cast(JoiningPosition, "init")
medi = cast(JoiningPosition, "medi")
fina = cast(JoiningPosition, "fina")
