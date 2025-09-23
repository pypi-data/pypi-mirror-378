# s3-file-downloader

A simple Python library to **list and download files from Amazon S3**.  
Supports both **public (unsigned)** and **private (AWS credentials)** buckets.

---

##  Features
- List objects in an S3 bucket under a prefix
- Download:
  - One file
  - Many files
  - All files under a prefix
- Safe local filenames (handles weird S3 keys)
- Works with **public access** or with **your AWS credentials**

---

## Installation

From PyPI (after publishing):

```bash
pip install s3-file-downloader
````

For development (local install):

```bash
git clone https://github.com/<your-username>/s3-file-downloader.git
cd s3-file-downloader
pip install -e .
```

---

##  Usage Example

```python
from s3_file_downloader import make_s3_client, S3Downloader

# Public access (no AWS credentials needed)
s3 = make_s3_client(region="us-east-1", unsigned=True)
dl = S3Downloader(s3)

bucket = "aws-bigdata-blog"
prefix = "artifacts/flink-refarch/data/nyc-tlc-trips.snz/"

# 1) List objects
keys = dl.list_objects(bucket=bucket, prefix=prefix, limit=5)
print("Found keys:", keys)

# 2) Download one file
if keys:
    dl.download_one(bucket, keys[0], "./downloads_one")

# 3) Download many files
dl.download_many(bucket, keys, "./downloads_many")

# 4) Download all files under prefix
dl.download_all_by_prefix(bucket, prefix, "./downloads_all", limit=None)
```

---

##  Requirements

* Python 3.8+
* boto3 (`pip install boto3`)
* AWS credentials if accessing private buckets

  * Run `aws configure` or set environment variables:

    * `AWS_ACCESS_KEY_ID`
    * `AWS_SECRET_ACCESS_KEY`
    * `AWS_SESSION_TOKEN` (if required)

---

##  Authors

* **Your Name** ([@Divya-Idupulapati](https://github.com/Divya-Idupulapati))
* **Friend’s Name** ([@PavanMarella10](https://github.com/PavanMarella10))

---

##  License

MIT License — free to use, copy, modify, and share.

```

