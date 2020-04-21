# nexp.clients.blobs

from typing import Any, Union
from os import path

import boto3

from nexp.aliases import OptionalString
from nexp.config import config
from nexp import utils


class Blobs:
    def __init__(
        self,
        resource: Union[Any, None] = None,
        bucket: OptionalString = None,
        prefix: OptionalString = None,
        url_expiry_seconds: Union[int, None] = None,
    ) -> None:
        self.__resource = resource or boto3.resource("s3")
        self.__bucket = str(bucket or config.s3_bucket)
        self.__prefix = str(prefix or config.s3_prefix)
        self.url_expiry_seconds = url_expiry_seconds or config.s3_url_expiry_seconds

    def upload_file_and_presign(
        self,
        source_filepath: str,
        destination_dirname: str,
        destination_filename: str,
        content_type: str,
    ) -> str:
        """Given a source_filepath, a destination dirname, and a destination
        filepath, upload the file at the source filepath to S3 and generate
        a presigned URL that will allow folks to download it."""
        key = path.join(
            self.__prefix,
            destination_dirname,
            utils.date_string(),
            destination_filename,
        )

        response = self.__resource.meta.client.upload_file(
            source_filepath,
            self.__bucket,
            key,
            ExtraArgs={"Metadata": {"Content-Type": content_type, "ACL": "private"}},
        )

        response = self.__resource.meta.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.__bucket, "Key": key,},
            ExpiresIn=self.url_expiry_seconds,
        )

        return response
