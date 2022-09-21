#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

"""
import abc
import logging
import os
import shutil
import sys
from pathlib import Path
from typing import Final

from locate import locate_english_subs_by_size
from locate import locate_english_subs_vtx


class _EventHandler(abc.ABC):
    def __init__(self, log: logging.Logger):
        self._log = log

    def handle(self, event_type: str):
        self._log.info(f"Handling {event_type}")


class TestEventHandler(_EventHandler):
    def __init__(self, log: logging.Logger):
        super().__init__(log)

    def handle(self, event_type: str):
        self._log.info(f"Handling {event_type}")


class _SubtitleCopier(object):
    def __init__(
        self,
        log: logging.Logger,
        src_folder: Path,
        dest_folder: Path,
        srt_locater,
    ):
        self._log = log
        self.src_folder = src_folder
        self.dest_folder = dest_folder
        self.srt_locater = srt_locater

    def copy(self):
        if self.src_folder.exists() and self.src_folder.is_dir():
            self._log.info(f"{self.src_folder} exists")

            english_srts = self.srt_locater(self._log, self.src_folder)

            for srt_file, suffix in [
                (english_srts.full_subtitle, ".en.srt"),
                (english_srts.sdh_subtitle, ".en.sdh.srt"),
                (english_srts.forced_subtitle, ".en.forced.srt"),
            ]:
                if srt_file is not None:
                    new_srt_path = self.dest_folder.with_suffix(suffix)
                    self._log.info(f"Copying {srt_file.name} to {new_srt_path.name}")

                    shutil.copy(srt_file, new_srt_path)

        else:
            self._log.info(f"No {self.src_folder} found, nothing to do")


class RadarrDownloadEventHandler(_EventHandler):
    def __init__(self, log: logging.Logger):
        super().__init__(log)
        self.download_file_src_folder: Path = Path(
            os.environ.get("radarr_moviefile_sourcefolder"),
        )

        # This is the destination folder Radarr will copy the movie file to
        media_destination_path = Path(os.environ.get("radarr_moviefile_path"))

        # The expected subtitle path is a simple Subs folder at the root level
        expected_subs_folder = self.download_file_src_folder / Path("Subs")

        copier = None

        if "rarbg" in self.download_file_src_folder.name.lower():

            copier = _SubtitleCopier(
                self._log,
                expected_subs_folder,
                media_destination_path,
                locate_english_subs_by_size,
            )
        elif "vxt" in self.download_file_src_folder.name.lower():
            copier = _SubtitleCopier(
                self._log,
                expected_subs_folder,
                media_destination_path,
                locate_english_subs_vtx,
            )

        if copier is not None:
            copier.copy()


class SonarrDownloadEventHandler(_EventHandler):
    def __init__(self, log: logging.Logger):
        super().__init__(log)
        self.episode_file_path = Path(os.environ["sonarr_episodefile_path"])
        self.episode_file_src_path = Path(os.environ["sonarr_episodefile_sourcepath"])
        self.episode_file_src_folder = Path(
            os.environ["sonarr_episodefile_sourcefolder"],
        )

        media_destination_path = self.episode_file_path

        copier = None

        if "rarbg" in self.episode_file_src_folder.name.lower():

            # The expected subtitle folder is Subs at the root level, with individual
            # episode's subtitles in folders under that, named by the episode file name
            expected_subs_folder = (
                self.episode_file_src_folder
                / Path("Subs")
                / Path(self.episode_file_src_path.with_suffix("").name)
            )

            copier = _SubtitleCopier(
                self._log,
                expected_subs_folder,
                media_destination_path,
                locate_english_subs_by_size,
            )

        if copier is not None:
            copier.copy()


if __name__ == "__main__":

    version: Final[str] = "0.0.1"

    main_log = logging.getLogger("custom-sub-import")

    log_fmt = logging.Formatter(
        fmt="%(asctime)s %(name)-20s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    info_handler = logging.StreamHandler(sys.stderr)
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(log_fmt)

    debug_handler = logging.StreamHandler(sys.stdout)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(log_fmt)

    main_log.addHandler(info_handler)
    main_log.addHandler(debug_handler)
    main_log.setLevel(logging.INFO)

    main_log.info(f"Starting subtitle importer {version}")

    radarr_events_to_handlers = {
        "Download": RadarrDownloadEventHandler,
        "Test": TestEventHandler,
    }

    sonarr_events_to_handlers = {
        "Download": SonarrDownloadEventHandler,
        "Test": TestEventHandler,
    }

    handler_mapping = None

    if "radarr_eventtype" in os.environ:

        env_event_type = os.environ["radarr_eventtype"]

        handler_mapping = radarr_events_to_handlers

    elif "sonarr_eventtype" in os.environ:
        env_event_type = os.environ["sonarr_eventtype"]

        handler_mapping = sonarr_events_to_handlers

    if env_event_type in handler_mapping:
        handler_mapping[env_event_type](main_log).handle(env_event_type)
    else:
        main_log.warning(f"Unhandled event: {env_event_type}")
