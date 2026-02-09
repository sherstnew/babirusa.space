import fnmatch
import os
import re
import shutil
from typing import Optional

from cryptography.fernet import Fernet

from app import SECRET_KEY_USER
from app.data.models import Pupil
from app.data.schemas import FileContent, FileInfo, OperationResult, SearchResult

dir_path = os.path.dirname(os.path.realpath(__file__))
cipher = Fernet(SECRET_KEY_USER) if SECRET_KEY_USER else None

BABIRUSA_HOME = os.path.normpath(os.path.join(dir_path, "..", "..", "..", "babirusa"))


class FileManager:
    def __init__(self, username: str):
        self._username = username
        self._prj_root = os.path.normpath(
            os.path.join(BABIRUSA_HOME, f"user-{username}-prj")
        )

    @staticmethod
    async def authenticate(username: str, password: str) -> "FileManager":
        user = await Pupil.find_one(Pupil.username == username)
        if not user:
            raise PermissionError("Invalid username or password.")

        if cipher is None:
            raise PermissionError("Encryption key is not configured.")

        decrypted = cipher.decrypt(user.hashed_password.encode("utf-8")).decode("utf-8")
        if password != decrypted:
            raise PermissionError("Invalid username or password.")

        prj_root = os.path.normpath(os.path.join(BABIRUSA_HOME, f"user-{username}-prj"))
        if not os.path.isdir(prj_root):
            raise FileNotFoundError(
                f"Project directory for user '{username}' not found."
            )

        return FileManager(username=username)

    def _abs(self, relative_path: str) -> str:
        cleaned = os.path.normpath(relative_path)
        if cleaned.startswith("..") or os.path.isabs(cleaned):
            raise ValueError(f"Invalid path: '{relative_path}'.")
        abs_path = os.path.normpath(os.path.join(self._prj_root, cleaned))
        if not abs_path.startswith(self._prj_root):
            raise ValueError(f"Path traversal detected: '{relative_path}'.")
        return abs_path

    def _rel(self, abs_path: str) -> str:
        return os.path.relpath(abs_path, self._prj_root).replace("\\", "/")

    def _walk_files(self) -> list[str]:
        results: list[str] = []
        for root, _dirs, files in os.walk(self._prj_root):
            for f in files:
                abs_path = os.path.join(root, f)
                results.append(self._rel(abs_path))
        results.sort()
        return results

    def list_all_files(self) -> list[FileInfo]:
        entries: list[FileInfo] = []
        for rel in self._walk_files():
            abs_path = self._abs(rel)
            stat = os.stat(abs_path)
            entries.append(
                FileInfo(
                    name=os.path.basename(rel),
                    relative_path=rel,
                    size=stat.st_size,
                    is_directory=False,
                )
            )
        return entries

    def find_by_name(self, pattern: str) -> list[FileInfo]:
        results: list[FileInfo] = []
        for rel in self._walk_files():
            name = os.path.basename(rel)
            if fnmatch.fnmatch(name, pattern):
                abs_path = self._abs(rel)
                stat = os.stat(abs_path)
                results.append(
                    FileInfo(
                        name=name,
                        relative_path=rel,
                        size=stat.st_size,
                        is_directory=False,
                    )
                )
        return results

    def find_by_path(self, pattern: str) -> list[FileInfo]:
        results: list[FileInfo] = []
        for rel in self._walk_files():
            if fnmatch.fnmatch(rel, pattern):
                abs_path = self._abs(rel)
                stat = os.stat(abs_path)
                results.append(
                    FileInfo(
                        name=os.path.basename(rel),
                        relative_path=rel,
                        size=stat.st_size,
                        is_directory=False,
                    )
                )
        return results

    def read_file(self, relative_path: str, encoding: str = "utf-8") -> FileContent:
        abs_path = self._abs(relative_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: '{relative_path}'")
        if os.path.isdir(abs_path):
            raise IsADirectoryError(
                f"Path is a directory, not a file: '{relative_path}'"
            )

        with open(abs_path, "r", encoding=encoding) as f:
            content = f.read()

        return FileContent(
            relative_path=self._rel(abs_path),
            content=content,
            size=os.path.getsize(abs_path),
        )

    def search_in_files(
        self,
        text: str,
        *,
        is_regex: bool = False,
        case_sensitive: bool = False,
        file_pattern: Optional[str] = None,
    ) -> list[SearchResult]:
        flags = 0 if case_sensitive else re.IGNORECASE
        if is_regex:
            pattern = re.compile(text, flags)
        else:
            pattern = re.compile(re.escape(text), flags)

        results: list[SearchResult] = []
        for rel in self._walk_files():
            if file_pattern and not fnmatch.fnmatch(
                os.path.basename(rel), file_pattern
            ):
                continue
            abs_path = self._abs(rel)
            try:
                with open(abs_path, "r", encoding="utf-8", errors="ignore") as f:
                    for lineno, line in enumerate(f, start=1):
                        if pattern.search(line):
                            results.append(
                                SearchResult(
                                    relative_path=rel,
                                    line_number=lineno,
                                    line_content=line.rstrip("\n\r"),
                                )
                            )
            except (OSError, UnicodeDecodeError):
                continue
        return results

    def create_file(
        self, relative_path: str, content: str = "", encoding: str = "utf-8"
    ) -> OperationResult:
        abs_path = self._abs(relative_path)
        if os.path.exists(abs_path):
            raise FileExistsError(f"File already exists: '{relative_path}'.")

        parent = os.path.dirname(abs_path)
        os.makedirs(parent, exist_ok=True)

        with open(abs_path, "w", encoding=encoding) as f:
            f.write(content)

        return OperationResult(
            success=True,
            message=f"File created: '{relative_path}'",
            relative_path=self._rel(abs_path),
        )

    def edit_file(
        self, relative_path: str, content: str, encoding: str = "utf-8"
    ) -> OperationResult:
        abs_path = self._abs(relative_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: '{relative_path}'.")
        if os.path.isdir(abs_path):
            raise IsADirectoryError(
                f"Path is a directory, not a file: '{relative_path}'"
            )

        with open(abs_path, "w", encoding=encoding) as f:
            f.write(content)

        return OperationResult(
            success=True,
            message=f"File updated: '{relative_path}'",
            relative_path=self._rel(abs_path),
        )

    def delete_file(self, relative_path: str) -> OperationResult:
        abs_path = self._abs(relative_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: '{relative_path}'")
        if os.path.isdir(abs_path):
            raise IsADirectoryError(f"Path is a directory: '{relative_path}'.")

        os.remove(abs_path)

        return OperationResult(
            success=True,
            message=f"File deleted: '{relative_path}'",
            relative_path=relative_path,
        )

    def delete_directory(self, relative_path: str) -> OperationResult:
        abs_path = self._abs(relative_path)
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"Directory not found: '{relative_path}'")
        if not os.path.isdir(abs_path):
            raise NotADirectoryError(f"Path is not a directory: '{relative_path}'")

        shutil.rmtree(abs_path)

        return OperationResult(
            success=True,
            message=f"Directory deleted: '{relative_path}'",
            relative_path=relative_path,
        )

    @property
    def username(self) -> str:
        return self._username

    @property
    def project_root(self) -> str:
        return self._prj_root
