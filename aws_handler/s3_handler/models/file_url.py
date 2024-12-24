class UrlFile:
    def __init__(self, last_modified: str, s3_url: str):
        """
        Initialize a UrlFile object object.

        :param last_modified: The last_modified of the UrlFile object.
        :param s3_url: The s3_url of the UrlFile object.
        """
        self._file_extension = s3_url.split(".")[-1]
        self._last_modified = last_modified
        self._s3_url = s3_url
        self._file_name = self._extract_file_name(s3_url)

    @property
    def file_extension(self) -> str:
        """
        Get the file_extension of the UrlFile object.

        :return: The file_extension of the UrlFile object.
        """
        return self._file_extension

    @property
    def last_modified(self) -> str:
        """
        Get the last_modified of the UrlFile object.

        :return: The last_modified of the UrlFile object.
        """
        return self._last_modified

    @property
    def s3_url(self) -> str:
        """
        Get the s3_url of the UrlFile object.

        :return: The s3_url of the UrlFile object.
        """
        return self._s3_url

    @property
    def file_name(self) -> str:
        """
        Get the file_name of the UrlFile object.

        :return: The file_name of the UrlFile object.
        """
        return self._file_name

    def to_dict(self) -> dict:
        """
        Convert the UrlFile object to a dictionary representation.

        :return: A dictionary with keys: 'file_extension', 'last_modified', 's3_url', and 'file_name'.
        """
        return {
            "file_extension": self._file_extension,
            "last_modified": self._last_modified,
            "s3_url": self._s3_url,
            "file_name": self._file_name,
        }

    def _extract_file_name(self, s3_url: str) -> str:
        """
        Extracts the file name from the s3_url and returns it.

        :param s3_url: The s3_url from which to extract the file name.
        :return: The extracted file name.
        """
        # Split on the last "/" to get the file name
        parts = s3_url.rsplit("/", 1)
        file_name = parts[-1]
        return file_name

    def __str__(self) -> str:
        """
        Get a string representation of the UrlFile object.

        :return: A string containing the s3_url, last_modified, file_name,
                 and file_extension of the UrlFile object.
        """
        return (
            f"s3_url: {self._s3_url}, last_modified: {self._last_modified}, "
            f"file_name: {self._file_name}, file_extension: {self._file_extension}"
        )
