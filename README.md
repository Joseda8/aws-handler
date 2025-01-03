# AWS-Handler
## _A toolkit to work with AWS on Python_

## What AWS-Handler does

This package provides out-of-the-box util functions to work with AWS in a more automatic way. For now it only contains a module to read files from S3.


## How to install

This package is not available in the Python Package Index but in the test environment. It can be installed with:

```sh
pip3 install -i https://test.pypi.org/simple/ aws-handler
```

Or manually from the root of this repo with:

```sh
# Install build package
python3 -m pip install --upgrade build

# Build package
python3 -m build

# Install package
pip3 install dist/aws_handler-<version>-py3-none-any.whl
```


## Get started

Some examples on how to use the library.

### Reader module

An example of how to use the reader module.

```python
from aws_handler import S3Handler

test_bucket = "my_bucket"
test_keyword = "filename_*.xlsx"
s3_handler = S3Handler(bucket=test_bucket)
s3_files = s3_handler.retrieve_files(path="my_excel_files", keywords=[test_keyword])
for file in s3_files[test_keyword]:
    df_data = s3_handler.read_file(file_object=file)
    print(df_data)
```

### Writer module

An example of how to use the writer module.

```python
from aws_handler import S3Handler

test_bucket = "my_bucket"
test_data = {"hello": "world"}
s3_handler = S3Handler(bucket=test_bucket)
s3_handler.write_json_to_s3(data=test_data, file_name="test.json", file_path="path/path")
```

### Boto3 Connector

The AWS-Handler currently utilizes a Boto3 connection to interact with AWS services. To set up AWS credentials please refer to the official Boto3 documentation:  
[Quickstart Guide for Boto3 Configuration](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration).

> **Note:** The method using a `~/.aws/credentials` file was selected for the development of this library.


### Get started - For development

Install the dependencies in the requirements files.

```sh
pip3 install -r project_settings/python/requirements.txt
pip3 install -r project_settings/python/requirements-dev.txt
```

Install the Git hooks:

```sh
pre-commit install --config project_settings/git/.pre-commit-config.yaml
```

The tests can be run with:

```sh
python3 -m pytest -s
```
