import os
import tempfile

from django.core.files.uploadedfile import UploadedFile
from django.core.files.uploadhandler import FileUploadHandler

from . import settings


# copied from TemporaryFileUploadHandler
class CustomFileUploadHandler(FileUploadHandler):
    def new_file(self, *args, **kwargs):
        """
        Create the file object to append to as data is coming in.
        """
        super().new_file(*args, **kwargs)
        self.file = CustomUploadedFile(
            self.file_name, self.content_type, 0, self.charset, self.content_type_extra
        )

    def receive_data_chunk(self, raw_data, start):
        self.file.write(raw_data)

    def file_complete(self, file_size):
        self.file.seek(0)
        self.file.size = file_size
        return self.file

    def upload_interrupted(self):
        if hasattr(self, "file"):
            location = self.file.temporary_file_path()
            try:
                self.file.close()
                os.remove(location)
            except FileNotFoundError:
                pass


# copied from TemporaryUploadedFile
class CustomUploadedFile(UploadedFile):
    """
    A file uploaded to a temporary location (i.e. stream-to-disk).
    """

    def __init__(self, name, content_type, size, charset, content_type_extra=None):
        start, ext = os.path.splitext(name)
        file = tempfile.NamedTemporaryFile(
            suffix=ext, prefix=start + "_", dir=settings.FILE_UPLOAD_TEMP_DIR
        )
        super().__init__(file, name, content_type, size, charset, content_type_extra)

    def temporary_file_path(self):
        """Return the full path of this file."""
        return self.file.name

    def close(self):
        try:
            return self.file.close()
        except FileNotFoundError:
            # The file was moved or deleted before the tempfile could unlink
            # it. Still sets self.file.close_called and calls
            # self.file.file.close() before the exception.
            pass
