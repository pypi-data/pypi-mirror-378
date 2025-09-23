import argparse
from dataclasses import dataclass
from typing import Union, List


@dataclass(frozen=True)
class OutDataset:
    dataset: str
    minio_bucket: str
    minio_url: str
    access_key: str
    secret_key: str


class OutDatasetFactory:
    @staticmethod
    def from_cli(n: int = 1) -> Union[List["OutDataset"], "OutDataset"]:
        """Register arguments, parse CLI, and return immutable InDataset."""
        parser = argparse.ArgumentParser()
        if n != 1:
            objs = []
            for i in range(1, n + 1):
                parser.add_argument(
                    f"--output-dataset-{i}",
                    dest=f"output_dataset_{i}_dataset",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minio_bucket",
                    dest=f"output_dataset_{i}_minio_bucket",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minIO_URL",
                    dest=f"output_dataset_{i}_minio_url",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minIO_ACCESS_KEY",
                    dest=f"output_dataset_{i}_access_key",
                    type=str,
                    required=True,
                )
                parser.add_argument(
                    f"--output-dataset-{i}.minIO_SECRET_KEY",
                    dest=f"output_dataset_{i}_secret_key",
                    type=str,
                    required=True,
                )
            args, _ = parser.parse_known_args()
            for i in range(1, n + 1):
                objs.append(
                    OutDataset(
                        getattr(args, f"output_dataset_{i}_dataset"),
                        getattr(args, f"output_dataset_{i}_minio_bucket"),
                        getattr(args, f"output_dataset_{i}_minio_url"),
                        getattr(args, f"output_dataset_{i}_access_key"),
                        getattr(args, f"output_dataset_{i}_secret_key"),
                    )
                )
            return objs
        else:
            parser.add_argument(
                "--output-dataset", dest="output_dataset", type=str, required=True
            )
            parser.add_argument(
                "--output-dataset.minio_bucket",
                dest="output_minio_bucket",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-dataset.minIO_URL",
                dest="output_minio_url",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-dataset.minIO_ACCESS_KEY",
                dest="output_access_key",
                type=str,
                required=True,
            )
            parser.add_argument(
                "--output-dataset.minIO_SECRET_KEY",
                dest="output_secret_key",
                type=str,
                required=True,
            )
            args, _ = parser.parse_known_args()
            return OutDataset(
                dataset=args.output_dataset,
                minio_bucket=args.output_minio_bucket,
                minio_url=args.output_minio_url,
                access_key=args.output_access_key,
                secret_key=args.output_secret_key,
            )
