from typing import List, Optional, Tuple

import boto3
from botocore.client import BaseClient as BotoClient
from botocore.exceptions import ClientError

from bracelet_lib.models.storage import BlobOpType


class BlobStorageCtrl:
    s3_access_key_id     : str
    s3_secret_access_key : str
    s3_region            : str
    s3_bucket            : str
    s3_ttl               : int
    s3_client            : BotoClient

    # noinspection PyTypeChecker
    def __init__(self):
        super().__init__()

    def init(
            self,
            s3_access_key_id     : str,
            s3_secret_access_key : str,
            s3_region            : str,
            s3_bucket            : str,
            s3_ttl               : int = 3600
    ):
        self.s3_access_key_id     = s3_access_key_id
        self.s3_secret_access_key = s3_secret_access_key
        self.s3_region            = s3_region
        self.s3_bucket            = s3_bucket
        self.s3_ttl               = s3_ttl
        self.s3_client            = boto3.client(
            's3',
            aws_access_key_id     = s3_access_key_id,
            aws_secret_access_key = s3_secret_access_key,
            region_name           = s3_region
        )

    def get_signed_url(self, path: str) -> Optional[str ]:
        """
        Generate a signed url for a GET request
        :param path: file location at BlobStorage
        :return: Signed url for fetch the GET request
        """
        method_parameters = {
            'Bucket': self.s3_bucket,
            'Key'   : path
        }

        try:
            response = self.s3_client.generate_presigned_url(
                ClientMethod = 'get_object',
                Params       = method_parameters,
                ExpiresIn    = self.s3_ttl,
                HttpMethod   = 'GET'
            )

        except ClientError:
            # print("--> Couldn't get a pre-signed GET URL ", e)
            return None

        return response

    def get_delete_signed_url(self, path: str) -> Optional[str ]:
        """
        Generate a signed url for a DELETE request
        :param path: file location at BlobStorage
        :return: Signed url for fetch the DELETE request
        """
        method_parameters = {
            'Bucket': self.s3_bucket,
            'Key'   : path
        }

        try:
            response = self.s3_client.generate_presigned_url(
                ClientMethod = 'delete_object',
                Params       = method_parameters,
                ExpiresIn    = self.s3_ttl,
                HttpMethod   = 'DELETE'
            )

        except ClientError:
            # print("--> Couldn't get a pre-signed DELETE URL ", e)
            return None

        return response

    def get_upload_signed_url(self, path: str) -> Optional[str ]:
        """
        Generate a signed url for a POST or PUT operation request
        :param path: file location at BlobStorage
        :return: Signed url for fetch the operation
        """
        method_parameters = {
            'Bucket': self.s3_bucket,
            'Key'   : path
        }

        try:
            response = self.s3_client.generate_presigned_url(
                ClientMethod = 'put_object',
                Params       = method_parameters,
                ExpiresIn    = self.s3_ttl,
                HttpMethod   = 'PUT'
            )

        except ClientError:
            # print("--> Couldn't get a pre-signed POST/PUT URL ", e)
            return None

        return response

    def get_multipart_data(self, path: str) -> Optional[Tuple[str, str, str ] ]:
        """
        Create a multipart upload request to BlobStorage
        :param path: file location at BlobStorage
        :return: Multipart operation ID and URLs to complete and abort operation
        """

        try:
            upload = self.s3_client.create_multipart_upload(
                Bucket  = self.s3_bucket,
                Key     = path,
                Expires = self.s3_ttl
            )

            upload_id = upload['UploadId']
            method_parameters = {
                'Bucket'     : self.s3_bucket,
                'Key'        : path,
                'UploadId'   : upload_id
            }

            complete_url = self.s3_client.generate_presigned_url(
                ClientMethod = 'complete_multipart_upload',
                Params       = method_parameters,
                ExpiresIn    = self.s3_ttl,
                HttpMethod   = 'POST'
            )

            abort_url = self.s3_client.generate_presigned_url(
                ClientMethod = 'abort_multipart_upload',
                Params       = method_parameters,
                ExpiresIn    = self.s3_ttl,
                HttpMethod   = 'POST'
            )

            return upload_id, complete_url, abort_url

        except ClientError:
            # print("--> Couldn't get a pre-signed {http_method} URL ", e)
            return None

    def generate_parts_signed_url(
            self,
            upload_id  : str,
            num_parts  : int,
            path       : str
    ) -> Optional[List[str]]:
        """
        Generate signed url for all parts of the multipart upload operation
        :param upload_id: ID of the multipart upload operation
        :param num_parts: Number of parts which must be generated
        :param path: file location at BlobStorage
        :return: List of signed urls for all parts of the multipart upload operation
        """
        signed_urls: [str] = []

        method_parameters = {
            'Bucket'     : self.s3_bucket,
            'Key'        : path,
            'UploadId'   : upload_id,
            'PartNumber' : None
        }

        for i in range(1, num_parts + 1):
            method_parameters['PartNumber'] = i

            try:
                part_signed_url = self.s3_client.generate_presigned_url(
                    ClientMethod = 'upload_part',
                    Params       = method_parameters,
                    ExpiresIn    = self.s3_ttl,
                    HttpMethod   = 'PUT'
                )

            except ClientError:
                # print("--> Couldn't get a pre-signed {http_method} URL ", e)
                return None

            signed_urls.append(part_signed_url)

        return signed_urls


# singleton
blob_storage_ctrl = BlobStorageCtrl()
