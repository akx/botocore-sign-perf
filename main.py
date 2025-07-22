import os
import sys
import time

import json
import botocore
import botocore.compat
from botocore.config import Config

import boto3

try:
    from awscrt import __version__ as awscrt_version
except ImportError:
    awscrt_version = None

has_crt = getattr(botocore.compat, "HAS_CRT", False)

s3_client = boto3.client(
    "s3",
    aws_access_key_id="AKIAI" * 10,
    aws_secret_access_key="nom" * 10,
    region_name="eu-west-1",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"},
    ),
)

t0 = time.time()
for x in range(10_000):
    s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": "bucket", "Key": str(x)},
        ExpiresIn=120,
    )
t1 = time.time()
sign_time_ms = (t1 - t0) * 1000
record = {
    "sign_time_ms": sign_time_ms,
    "python_version": sys.version_info,
    "boto3_version": boto3.__version__,
    "botocore_version": botocore.__version__,
    "awscrt_version": awscrt_version if has_crt else None,
    "hyperfine_iteration": os.environ.get("HYPERFINE_ITERATION"),
}
print(json.dumps(record))
