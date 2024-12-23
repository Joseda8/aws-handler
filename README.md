# AWS-Handler
## _A toolkit to work with AWS on Python_

## What AWS-Handler does

This package provides out-of-the-box util functions to work with AWS in a more automatic way. For now it only contains a module to read files from S3.


## How to install

This package is not available in the Python Package Index so it must be installed manually by running:

```sh
# Install build package
python3 -m pip install --upgrade build

# Build package
python3 -m build

# Install package
pip3 install dist/aws_handler-<version>-py3-none-any.whl
```


## Get started

An example of how to use the reader module.

```python
from aws_handler import S3Reader

test_bucket = "my_bucket"
test_keyword = "filename_*.xlsx"
s3_reader = S3Reader(bucket=test_bucket)
s3_files = s3_reader.retrieve_files(path="my_excel_files", keywords=[test_keyword])
for file in s3_files[test_keyword]:
    df_data = s3_reader.read_file(file_object=file)
    print(df_data)
```

### Get started - For development

Install the dependencies in the requirements files.


This package is not available in the Python Package Index so it must be installed manually by running:

```sh
pip3 install -r requirements.txt
pip3 install -r requirements-dev.txt
```
