import argparse
from dataclasses import dataclass
from typing import Union, List


@dataclass(frozen=True)
class OutModel:
    model: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str


class OutModelFactory:
    @staticmethod
    def from_cli(n: int = 1) -> Union[List["OutModel"], "OutModel"]:
        """Register arguments, parse CLI, and return immutable InModel."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--output-model-{i}",
                    dest=f"output_model_{i}",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minio_bucket",
                    dest=f"output_model_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minIO_URL",
                    dest=f"output_model_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minIO_ACCESS_KEY",
                    dest=f"output_model_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-model-{i}.minIO_SECRET_KEY",
                    dest=f"output_model_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    OutModel(
                        getattr(args, f"output_model_{i}"),
                        getattr(args, f"output_model_{i}_minio_bucket"),
                        getattr(args, f"output_model_{i}_minio_url"),
                        getattr(args, f"output_model_{i}_access_key"),
                        getattr(args, f"output_model_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--output-model", dest="output_model", type=str, required=True
            )
            parser.add_argument(
                "--output-model.minio_bucket",
                dest="output_model_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-model.minIO_URL",
                dest="output_model_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-model.minIO_ACCESS_KEY",
                dest="output_model_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-model.minIO_SECRET_KEY",
                dest="output_model_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return OutModel(
                model=args.output_model,
                minio_bucket=args.output_model_minio_bucket,
                minio_url=args.output_model_minio_url,
                access_key=args.output_model_access_key,
                secret_key=args.output_model_secret_key,
            )
