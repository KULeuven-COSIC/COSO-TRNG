"""A module containing data storage functionality for the figure generators."""
from typing import List, Optional
import csv
import os

class StoreData:
    """This class has data storage functionality."""

    def __init__(self, name: str, nb_points: Optional[int]=None):
        self._name = name
        self._nb_points = nb_points

    @property
    def file_path(self) -> str:
        """The file path."""
        if self._nb_points:
            full_file_name = f'{self._name}_{self._nb_points}.csv'
        else:
            full_file_name = f'{self._name}.csv'
        return os.path.join('figures/data', full_file_name)

    @property
    def file_exist(self) -> bool:
        """Does this file exist?"""
        return os.path.isfile(self.file_path)

    def write_data(self, data: List[List[float]], over_write: bool=False) -> bool:
        """Write the given data to the file. Return True if write was successfull.
        Return False if file already exists and over_write is unset."""
        if self.file_exist:
            if not over_write:
                return False
        with open(self.file_path, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for row in data:
                writer.writerow(row)
        return True

    def read_data(self) -> Optional[List[List[float]]]:
        """Read the data from the file. Returns None if the file does not exist."""
        if not self.file_exist:
            return None
        with open(self.file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            result: List[List[float]] = []
            for row in reader:
                result.append([float(r) for r in row])
            return result
