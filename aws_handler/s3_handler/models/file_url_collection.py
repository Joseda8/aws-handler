from typing import Iterator, List, Union

from .file_url import UrlFile


class UrlFileCollection:
    def __init__(self, url_file_objects: List[UrlFile] = None):
        """
        Initialize a UrlFileCollection object.

        :param url_file_objects: A list of UrlFile objects.
        """
        if url_file_objects is None:
            url_file_objects = []
        self._number_of_files: int = len(url_file_objects)
        self._url_file_objects = url_file_objects

    @property
    def number_of_files(self) -> int:
        """
        Get the number of files in the UrlFileCollection.

        :return: The number of files in the UrlFileCollection.
        """
        return self._number_of_files

    @property
    def url_file_objects(self) -> List[UrlFile]:
        """
        Get files.

        :return: The UrlFile stored.
        """
        return self._url_file_objects

    def add_url_file_object(self, url_file_obj: UrlFile):
        """
        Add a UrlFile to the list.

        :param url_file_obj: The UrlFile to be added to the list.
        """
        self._url_file_objects.append(url_file_obj)
        self._number_of_files += 1

    def order_files_by_last_modified_or_name(self):
        """
        Order the list of UrlFile instances for each keyword based on
        last_modified or name if last_modified is the same.
        """
        self._url_file_objects = sorted(
            self._url_file_objects,
            key=lambda file_info: (file_info.last_modified, file_info.s3_url),
            reverse=False,
        )

    def order_files_by_name(self):
        """
        Order the list of UrlFile instances for each keyword based on name.
        """
        self._url_file_objects = sorted(
            self._url_file_objects,
            key=lambda file_info: (file_info.s3_url),
            reverse=False,
        )

    def get_latest_file(self) -> "UrlFileCollection":
        """
        Get a UrlFileCollection with the UrlFile with latest last_modified
        property.

        :return: The UrlFileCollection with the latest last_modified property.
        :raises: ValueError if the list is empty (length is 0).
        """
        if not self._url_file_objects:
            raise ValueError(
                "The list of UrlFiles is empty. Cannot find the latest file."
            )

        latest_file = max(
            self._url_file_objects,
            key=lambda file_info: file_info.last_modified,
        )
        latest_file_list = UrlFileCollection(url_file_objects=[latest_file])
        return latest_file_list

    def get_file_by_name_keyword(self, keyword: str) -> List[UrlFile]:
        """
        Get a list of UrlFile instances that have the given keyword in their
        file names.

        :param keyword: The keyword to search for in the file names.
        :return: A list of UrlFile instances matching the keyword.
        """
        matching_files = [
            file_obj
            for file_obj in self._url_file_objects
            if keyword in file_obj.file_name
        ]
        return matching_files

    def extend(self, url_file_objects: "UrlFileCollection"):
        """
        Extend the UrlFileCollection by appending UrlFile instances from
        another list.

        :param url_file_objects: List of UrlFile instances to append.
        """
        self._url_file_objects.extend(url_file_objects)
        self._number_of_files += url_file_objects.number_of_files

    def to_dict_list(self) -> List[dict]:
        """
        Convert the UrlFileCollection to a list of dictionaries, where each
        dictionary represents a UrlFile object.

        :return: A list of dictionaries representing UrlFile objects.
        """
        return [file_obj.to_dict() for file_obj in self._url_file_objects]

    def __iter__(self) -> Iterator[UrlFile]:
        """
        Returns an iterator object for the list of UrlFile instances.
        """
        return iter(self._url_file_objects)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union[UrlFile, List[UrlFile]]:
        """
        Get the UrlFile instance or a list of UrlFile instances from the
        UrlFileCollection.

        :param index: The index (or slice) to access the UrlFile(s).

        :return: If an int is passed, returns the UrlFile at the given index.
                 If a slice is passed, returns a new UrlFileCollection
                 containing the sliced UrlFiles.
        :raises: IndexError if the index is out of range.
        """
        return self._url_file_objects[index]

    def __add__(self, other: "UrlFileCollection") -> "UrlFileCollection":
        """
        Merge two UrlFileCollection instances.

        :param other: Another UrlFileCollection instance to merge with.

        :return: A new UrlFileCollection instance containing the merged
                 UrlFiles.
        """
        merged_url_file_objects = (
            self._url_file_objects + other._url_file_objects
        )
        return UrlFileCollection(merged_url_file_objects)

    def __repr__(self) -> str:
        """
        Return a string representation of the UrlFileCollection in a list
        format.

        :return: A string representing the UrlFileCollection as a list of
                 dictionaries.
        """
        return str(self.to_dict_list())
