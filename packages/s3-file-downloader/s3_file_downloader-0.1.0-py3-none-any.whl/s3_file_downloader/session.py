import boto3
from botocore.client import Config
from botocore import UNSIGNED

def make_s3_client(region="us-east-1", unsigned=False):
    """
    Create an S3 client.
    - unsigned=True  -> public buckets (no credentials needed)
    - unsigned=False -> uses your AWS credentials if configured
    """
    cfg = Config()
    if unsigned:
        cfg.signature_version = UNSIGNED
    return boto3.client("s3", region_name=region, config=cfg)
