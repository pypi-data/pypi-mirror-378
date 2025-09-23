import argparse
from dataclasses import dataclass
from typing import Callable, Union, List


@dataclass(frozen=True)
class InParam:
    param_value: bool | str | int | float
    param_name: str


class InParamFactory:

    @staticmethod
    def from_cli(
        name: str, required: bool, param_type: Callable, n: int = 1
    ) -> Union[List["InParam"], "InParam"]:
        parser = argparse.ArgumentParser(add_help=False)
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--{name}-{i}", dest=f"{name}_{i}", required=required, type=str
                )
            args = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    InParam(
                        f"{name}_{i}",
                        param_type(getattr(args, f"{name}_{i}")),
                    )
                )
            return objs
        else:
            parser.add_argument(
                f"--{name}", dest=f"{name}", required=required, type=str
            )
            args, _ = parser.parse_known_args()
            return InParam(f"{name}", param_type(getattr(args, f"{name}")))
