import glob
import os


class FileHelper:
    @staticmethod
    def cwd():
        return os.getcwd()

    @staticmethod
    def find_files_by_pattern(patterns):
        matching_files = []

        for pattern in patterns:
            matching_files.extend(glob.glob(os.path.join(FileHelper.cwd(), pattern), recursive=True))

        return matching_files
