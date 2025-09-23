import argparse
from dataclasses import dataclass
from typing import Union, List


@dataclass(frozen=True)
class InDataset:
    dataset: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str


class InDatasetFactory:
    """Factory for creating InDataset objects from CLI arguments."""

    @staticmethod
    def from_cli(n: int = 1) -> Union[List["InDataset"], "InDataset"]:
        """Register arguments, parse CLI, and return immutable InDataset."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--input-dataset-{i}",
                    dest=f"input_dataset_{i}",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minio_bucket",
                    dest=f"input_dataset_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minIO_URL",
                    dest=f"input_dataset_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minIO_ACCESS_KEY",
                    dest=f"input_dataset_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--input-dataset-{i}.minIO_SECRET_KEY",
                    dest=f"input_dataset_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args, _ = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    InDataset(
                        getattr(args, f"input_dataset_{i}"),
                        getattr(args, f"input_dataset_{i}_minio_bucket"),
                        getattr(args, f"input_dataset_{i}_minio_url"),
                        getattr(args, f"input_dataset_{i}_access_key"),
                        getattr(args, f"input_dataset_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--input-dataset", dest="input_dataset", type=str, required=True
            )
            parser.add_argument(
                "--input-dataset.minio_bucket",
                dest="input_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-dataset.minIO_URL",
                dest="input_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-dataset.minIO_ACCESS_KEY",
                dest="input_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--input-dataset.minIO_SECRET_KEY",
                dest="input_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return InDataset(
                dataset=args.input_dataset,
                minio_bucket=args.input_minio_bucket,
                minio_url=args.input_minio_url,
                access_key=args.input_access_key,
                secret_key=args.input_secret_key,
            )
