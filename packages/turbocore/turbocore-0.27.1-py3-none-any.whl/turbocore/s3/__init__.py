from botocore.exceptions import ClientError
from typing import Iterator, Optional
from botocore.config import Config
import os
import threading
import boto3
import boto3.s3.transfer
from rich.pretty import pprint as PP
import json
import sys
import os


class SimpleClient:

    def __init__(self, ENV_PREFIX:str = ""):
        self._env_prefix = ENV_PREFIX
        self._s3_user = os.environ.get("%sS3_USER" % self._env_prefix, "")
        self._s3_pass = os.environ.get("%sS3_PASS" % self._env_prefix, "")
        self._s3_endpoint = os.environ.get("%sS3_ENDPOINT" % self._env_prefix, "")
        self._s3 = boto3.client("s3", endpoint_url=self._s3_endpoint, aws_access_key_id=self._s3_user, aws_secret_access_key=self._s3_pass)

    def lsb(self):
        res = [ x['Name'] for x in self._s3.list_buckets()["Buckets"]]
        return res

    def rmb(self, bucket):
        self.rmfr1(bucket)
        self._s3.delete_bucket(Bucket=bucket)

    def mkb(self, bucket, ACL:str='private', exists_ok=False) -> bool:
        try:
            res = self._s3.create_bucket(ACL=ACL, Bucket=bucket)
            return True
        except self._s3.exceptions.BucketAlreadyOwnedByYou as e:
            if exists_ok:
                return True
            else:
                return False
        except ClientError as ce:
            return False
        
    def rmfr1(self, bucket, prefix=""):
        p = self._s3.get_paginator("list_objects_v2")
        for page in p.paginate(Bucket=bucket, Prefix=prefix):
            for o in page.get("Contents", []):
                self._s3.delete_object(Bucket=bucket, Key=o["Key"])

    def write_text(self, bucket:str, k:str, text:str):
        self._s3.put_object(Bucket=bucket, Key=k, Body=text.encode())

    def read_text(self, bucket:str, k:str):
        return self._s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode()

    def write_json(self, bucket:str, k:str, obj):
        self._s3.put_object(Bucket=bucket, Key=k, Body=json.dumps(obj, indent=4).encode())

    def read_json(self, bucket:str, k:str):
        return json.loads(self._s3.get_object(Bucket=bucket, Key=k)["Body"].read().decode())

    def _stream_object(self, bucket, key, chunk_size):
        res = self._s3.get_object(Bucket=bucket, Key=key)
        for chunk in res["Body"].iter_chunks(chunk_size=chunk_size):
            if chunk:
                yield chunk

    def download_full(self, bucket, key, filename, chunk_size=8*1024*1024):
        total=0
        with open(filename, "wb") as f:
            for chunk in self._stream_object(bucket, key, chunk_size=chunk_size):
                f.write(chunk)
                total += len(chunk)
                print(f"\r{total // (1024*1024)} MB", end="", file=sys.stderr)
            print(file=sys.stderr)

    def upload(self, filename, bucket, key):
        txbytes = 0
        lock = threading.Lock()

        def progress(chunk_size):
            nonlocal txbytes
            nonlocal lock
            with lock:
                txbytes+=chunk_size
                print("\r%d MB " % int(txbytes/1024/1024), end="")
        
        config = boto3.s3.transfer.TransferConfig(multipart_threshold=10*1024*1024)
        self._s3.upload_file(Filename=filename, Bucket=bucket, Key=key, ExtraArgs=None, Callback=progress, Config=config)


    def ls(self, bucket, prefix=""):
        keys = []
        paginator = self._s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
        return keys


def main():
    print("export EXAMPLE_S3_USER")
    print("export EXAMPLE_S3_PASS")
    print("export EXAMPLE_S3_ENDPOINT")
    s3 = SimpleClient("EXAMPLE_")

    PP(s3.mkb("first-bucket", exists_ok=True))
    s3.write_text("first-bucket", "aaa/bbb/ccc", "test\nvalue")
    s3.write_json("first-bucket", "aaa/x", {"ok":"yes"})

    PP(s3.ls("first-bucket"))

    # s3.rmfr1("first-bucket", "aaa/")

    print(s3.lsb())
    s3.rmb("first-bucket")
    print(s3.lsb())
    #print(s3.read_text("test02", "testk"))
    # y = s3.read_json("test02", "jdata")
    # PP(y)
    #s3.upload("mopus", "test02", "jbindata")
    #s3.download_full("test02", "jbindata", "mopus-down")
