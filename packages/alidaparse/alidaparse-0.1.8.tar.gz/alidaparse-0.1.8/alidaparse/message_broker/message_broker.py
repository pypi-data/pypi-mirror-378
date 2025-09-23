import argparse
from dataclasses import dataclass
import os
import uuid
from datetime import datetime
from kafka import KafkaProducer
from .utils import upload_file_to_minio
import json


@dataclass(frozen=True)
class MessageBroker:
    go_manager_brokers: str
    go_manager_topic: str
    go_minio_path: str
    go_minio_bucket: str
    go_minio_url: str
    go_access_key: str
    go_secret_key: str
    go_use_ssl: bool

    @staticmethod
    def _prepare_metadata_json(
        name, messageType, title=None, description=None, var=None, show=True
    ):
        result = {
            "name": name,
            "key": name.lower().replace(" ", "-"),
            "uuid": str(uuid.uuid4()),
            "messageType": messageType,
            "title": title,
            "description": description,
            "var": var,
            "created": str(datetime.now()),
            "modified": str(datetime.now()),
            "show": show,
        }
        if "BDA_ID" in os.environ:
            result["bdaId"] = os.environ.get("BDA_ID")

        if "SERVICE_ID" in os.environ:
            result["serviceId"] = os.environ.get("SERVICE_ID")

        if "ORGANIZATION_ID" in os.environ:
            result["organizationId"] = os.environ.get("ORGANIZATION_ID")

        if "OWNER_ID" in os.environ:
            result["ownerId"] = os.environ.get("OWNER_ID")

        if "EXECUTION_ID" in os.environ:
            result["executionId"] = os.environ.get("EXECUTION_ID")

        if "ACCESS_LEVEL" in os.environ:
            result["accessLevel"] = os.environ.get("ACCESS_LEVEL")

        if "EXECUTOR_ID" in os.environ:
            result["executorId"] = os.environ.get("EXECUTOR_ID")

        if "EXECUTOR_NAME" in os.environ:
            result["executorName"] = os.environ.get("EXECUTOR_NAME")

        if "EXECUTOR_ORG_ID" in os.environ:
            result["executorOrgId"] = os.environ.get("EXECUTOR_ORG_ID")

        if "EXECUTOR_ORG_NAME" in os.environ:
            result["executorOrgName"] = os.environ.get("EXECUTOR_ORG_NAME")
        return result

    @staticmethod
    def _prepare_file_metadata(
        name, messageType, localPath, path, extension, filename, **kwargs
    ):
        metadata = MessageBroker._prepare_metadata_json(
            name=name, messageType=messageType, **kwargs
        )
        metadata["localPath"] = localPath
        metadata["path"] = path
        metadata["extension"] = extension
        metadata["filename"] = filename
        return metadata

    def send_application_media(self, file_to_send, file_name, file_type, **kwargs):
        metadata = self._prepare_file_metadata(
            file_name,
            file_type,
            file_to_send,
            self.go_minio_path + file_name,
            "." + file_to_send.split(".")[-1],
            file_name,
            **kwargs,
        )

        upload_file_to_minio(
            self.go_minio_url,
            self.go_access_key,
            self.go_secret_key,
            self.go_minio_bucket,
            self.go_minio_path + file_name,
            file_to_send,
            secure=self.go_use_ssl,
        )
        print(
            f"[MEDIA] type={file_type} local={file_to_send} remote_object={self.go_minio_url} uploadto={self.go_minio_path + file_name}"
        )

        self._send_message(metadata, self.go_manager_brokers, self.go_manager_topic)

    @staticmethod
    def _send_message(data, go_manager_brokers, go_manager_topic):
        producer = KafkaProducer(bootstrap_servers=go_manager_brokers.split(","))
        producer.send(go_manager_topic, json.dumps(data).encode("utf-8"))
        producer.flush()


class MessageBrokerFactory:
    @staticmethod
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ("yes", "true", "t", "y", "1"):
            return True
        elif v.lower() in ("no", "false", "f", "n", "0", ""):
            return False

    @staticmethod
    def from_cli() -> "MessageBroker":
        parser = argparse.ArgumentParser(add_help=False)
        parser.add_argument(
            "--go_manager.brokers", dest="go_manager_brokers", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.topic", dest="go_manager_topic", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.base_path", dest="go_minio_path", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.minio_bucket", dest="go_minio_bucket", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.minIO_URL", dest="go_minio_url", type=str, required=True
        )
        parser.add_argument(
            "--go_manager.minIO_ACCESS_KEY",
            dest="go_access_key",
            type=str,
            required=True,
        )
        parser.add_argument(
            "--go_manager.minIO_SECRET_KEY",
            dest="go_secret_key",
            type=str,
            required=True,
        )
        parser.add_argument(
            "--go_manager.use_ssl",
            dest="go_use_ssl",
            type=MessageBrokerFactory.str2bool,
            required=True,
        )
        args, _ = parser.parse_known_args()
        return MessageBroker(
            go_manager_brokers=args.go_manager_brokers,
            go_manager_topic=args.go_manager_topic,
            go_minio_path=args.go_minio_path,
            go_minio_bucket=args.go_minio_bucket,
            go_minio_url=args.go_minio_url,
            go_access_key=args.go_access_key,
            go_secret_key=args.go_secret_key,
            go_use_ssl=args.go_use_ssl,
        )
