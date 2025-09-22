from __future__ import annotations
import io
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Iterator, Optional


@dataclass
class FileId:
    dev: int
    ino: int

    @classmethod
    def from_path(cls, path: str) -> Optional["FileId"]:
        try:
            st = os.stat(path)
            return cls(dev=st.st_dev, ino=st.st_ino)
        except FileNotFoundError:
            return None

def _same_file(a: Optional[FileId], b: Optional[FileId]) -> bool:
    return a is not None and b is not None and a.dev == b.dev and a.ino == b.ino



class Tailer:


    def __init__(
            self,
            path,
            callback_newline,
            from_beginning: bool = False,
            poll_interval: float = 0.2,
            encoding: str = "utf-8",
            errors: str = "replace",
            read_chunk: int = 8192,
        ):
        self.path = path
        self.callback_newline = callback_newline
        self.from_beginning = from_beginning
        self.poll_interval = poll_interval
        self.encoding = encoding
        self.errors = errors
        self.read_chunk = read_chunk

        self._file: Optional[io.TextIOWrapper] = None
        self._fid: Optional[FileId] = None
        self._pos: int = 0


    def process(self):
        for line in self.follow_lines():
            if callable(self.callback_newline):
                self.callback_newline(line)


    def follow_lines(self) -> Iterator[str]:
        buf = ""
        while True:
            self._maybe_rotate()

            if not self._file:
                # Datei existiert (noch) nicht: warten und erneut versuchen
                time.sleep(self.poll_interval)
                self._open_if_exists()
                continue

            chunk = self._file.read(self.read_chunk)

            if chunk:
                buf += chunk
                # Gibt komplette Zeilen aus (newline-terminiert)
                while True:
                    nl = buf.find("\n")
                    if nl == -1:
                        break
                    line = buf[: nl + 1]
                    buf = buf[nl + 1 :]
                    yield line
                self._pos = self._file.tell()
            else:
                # Nichts Neues: kleine Pause
                time.sleep(self.poll_interval)

    def _seek(self, pos: int) -> None:
        if self._file is None:
            return
        self._file.seek(pos)
        self._pos = pos


    def _seek_end(self) -> None:
        if self._file is None:
            return
        self._file.seek(0, os.SEEK_END)
        self._pos = self._file.tell()

    def _maybe_rotate(self) -> None:
        """Erkennt logrotate-Fälle und reagiert entsprechend."""
        fid_current = FileId.from_path(self.path)

        # Fall A: Datei existiert nicht -> warten, bis sie wieder da ist
        if fid_current is None:
            if self._file is not None:
                try:
                    self._file.close()
                except Exception:
                    pass
            self._file = None
            self._fid = None
            return

        # Fall B: rename+create -> inode/dev wechseln
        if not _same_file(self._fid, fid_current):
            self._reopen(fid_current)
            return

        # Fall C: copytruncate -> gleiche inode, aber Größe < aktuelle Position
        try:
            size = os.stat(self.path).st_size
        except FileNotFoundError:
            return
        if self._pos > size:
            # Datei wurde gekürzt
            self._seek(0)


    def _reopen(self, fid: FileId) -> None:
        # Bereits offen? Dann schließen, wenn es eine andere Datei ist
        if self._file is not None and _same_file(self._fid, fid):
            return
        if self._file is not None:
            try:
                self._file.close()
            except Exception:
                pass
        # Neu öffnen (immer im Textmodus, gepuffert)
        f = open(self.path, "r", encoding=self.encoding, errors=self.errors)
        self._file = f
        self._fid = fid
        # Nach Reopen standardmäßig ans Ende; aber wenn wir vorherige pos kennen,
        # prüfen wir, ob Truncation vorliegt.
        try:
            size = os.stat(self.path).st_size
        except FileNotFoundError:
            # race: gleich wieder verschwunden
            self._file = None
            self._fid = None
            return
        if self.from_beginning and self._pos == 0:
            self._seek(0)
        else:
            if self._pos <= size:
                self._seek(self._pos)
            else:
                # Truncation (z.B. copytruncate)
                self._seek(0)


    def _open_initial(self) -> None:
        if not self._open_if_exists():
            # Datei fehlt: wir starten im Wartemodus (pos=0)
            self._pos = 0
            return
        # Positionieren
        if self.from_beginning:
            self._seek(0)
        else:
            # ans Ende springen (wie tail -F)
            self._seek_end()

    def _open_if_exists(self) -> bool:
        fid = FileId.from_path(self.path)
        if fid is None:
            return False
        self._reopen(fid)
        return True
