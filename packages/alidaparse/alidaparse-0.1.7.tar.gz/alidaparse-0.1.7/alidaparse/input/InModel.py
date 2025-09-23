import argparse
from dataclasses import dataclass
from typing import Union, List


@dataclass(frozen=True)
class InModel:
    model: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str


class InModelFactory:
    @staticmethod
    def from_cli(n: int = 1) -> Union[List["InModel"], "InModel"]:
        """Register arguments, parse CLI, and return immutable InModel."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--input-model-{i}",
                    dest=f"input_model_{i}",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minio_bucket",
                    dest=f"input_model_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minIO_URL",
                    dest=f"input_model_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minIO_ACCESS_KEY",
                    dest=f"input_model_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-model-{i}.minIO_SECRET_KEY",
                    dest=f"input_model_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args, _ = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    InModel(
                        getattr(args, f"input_model_{i}"),
                        getattr(args, f"input_model_{i}_minio_bucket"),
                        getattr(args, f"input_model_{i}_minio_url"),
                        getattr(args, f"input_model_{i}_access_key"),
                        getattr(args, f"input_model_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--input-model", dest="input_model", type=str, required=True
            )
            parser.add_argument(
                "--input-model.minio_bucket",
                dest="input_model_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-model.minIO_URL",
                dest="input_model_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-model.minIO_ACCESS_KEY",
                dest="input_model_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-model.minIO_SECRET_KEY",
                dest="input_model_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return InModel(
                model=args.input_model,
                minio_bucket=args.input_model_minio_bucket,
                minio_url=args.input_model_minio_url,
                access_key=args.input_model_access_key,
                secret_key=args.input_model_secret_key,
            )
