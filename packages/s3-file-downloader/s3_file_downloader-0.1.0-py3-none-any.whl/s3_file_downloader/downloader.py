import os
from .utils import safe_filename

class S3Downloader:
    def __init__(self, s3_client):
        self.s3 = s3_client

    def list_objects(self, bucket: str, prefix: str = "", limit: int | None = 10):
        """
        List object KEYS under a prefix (files only; skip 'folder' placeholders).
        - If limit is None: return ALL files (paginate fully).
        - If limit is an int: keep paginating until we collect that many files (or exhaust).
        """
        def _filter(contents):
            # keep only real objects (not keys ending with '/')
            return [
                it["Key"]
                for it in contents
                if not it["Key"].endswith("/")
            ]

        paginator = self.s3.get_paginator("list_objects_v2")

        if limit is None:
            keys = []
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
                keys.extend(_filter(page.get("Contents", [])))
            return keys
        else:
            keys = []
            for page in paginator.paginate(Bucket=bucket, Prefix=prefix, PaginationConfig={"PageSize": 1000}):
                for k in _filter(page.get("Contents", [])):
                    keys.append(k)
                    if len(keys) >= limit:
                        return keys
            return keys  # fewer than limit available

    def download_one(self, bucket: str, key: str, dest_dir: str, overwrite: bool = False):
        """
        Download ONE S3 object into dest_dir with a safe local name.
        If overwrite=False and the file already exists, skip it.
        """
        if key.endswith("/"):
            raise ValueError(f"'{key}' looks like a folder marker (ends with '/'). Pick a real file key.")

        os.makedirs(dest_dir, exist_ok=True)
        local_path = os.path.join(dest_dir, safe_filename(key))

        if not overwrite and os.path.exists(local_path):
            print(f"Already exists, skipping: {local_path}")
            return local_path

        self.s3.download_file(bucket, key, local_path)
        print(f"Downloaded: {key} -> {local_path}")
        return local_path

    def download_many(self, bucket: str, keys: list, dest_dir: str, overwrite: bool = False):
        """
        Download MULTIPLE objects sequentially (one-by-one).
        Returns a list of local file paths.
        """
        downloaded = []
        total = len(keys)
        for i, key in enumerate(keys, start=1):
            print(f"[{i}/{total}] {key}")
            local_path = self.download_one(bucket=bucket, key=key, dest_dir=dest_dir, overwrite=overwrite)
            downloaded.append(local_path)
        return downloaded

    def download_all_by_prefix(self, bucket: str, prefix: str, dest_dir: str, limit: int | None = None, overwrite: bool = False):
        """
        List objects under a prefix and download them sequentially.
        - If limit is None: download ALL under the prefix (can be large!)
        - If limit is an int: download up to that many.
        Returns a list of local file paths.
        """
        keys = self.list_objects(bucket=bucket, prefix=prefix, limit=limit)
        return self.download_many(bucket=bucket, keys=keys, dest_dir=dest_dir, overwrite=overwrite)
