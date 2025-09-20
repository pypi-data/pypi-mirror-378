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

    def list_buckets(self):
        res = [ x['Name'] for x in self._s3.list_buckets()["Buckets"]]
        return res

    def mkb(self, bucket, ACL:str='private'):
        res = self._s3.create_bucket(ACL=ACL, Bucket=bucket)
        return res

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




def main():
    s3 = SimpleClient("EXAMPLE_")
    # s3.mkb("test02")
    # s3.write_text("test02", "testk", "test\nvalue")
    #print(s3.list_buckets())
    #print(s3.read_text("test02", "testk"))
    #s3.write_json("test02", "jdata", {"ok":"yes"})
    # y = s3.read_json("test02", "jdata")
    # PP(y)
    #s3.upload("mopus", "test02", "jbindata")
    #s3.download_full("test02", "jbindata", "mopus-down")
