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
from typing import List
from typing import Optional


class _LocatedSubtitles(object):
    def __init__(
        self,
        full_subtitle,
        sdh_subtitle,
        forced_subtitle,
    ) -> None:
        self.full_subtitle: Optional[Path] = full_subtitle
        self.sdh_subtitle: Optional[Path] = sdh_subtitle
        self.forced_subtitle: Optional[Path] = forced_subtitle


class _EventHandler(abc.ABC):
    def __init__(self, log: logging.Logger):
        self._log = log
        self._handle_hooks = []

    def handle(self, event_type: str):
        self._log.info(f"Handling {event_type}")
        for hook in self._handle_hooks:
            hook()


class TestEventHandler(_EventHandler):
    def __init__(self, log: logging.Logger):
        super().__init__(log)

    def handle(self, event_type: str):
        self._log.info(f"Handling {event_type}")


class _RarbgSubtitleCopier(_EventHandler):
    def __init__(self, log: logging.Logger):
        super().__init__(log)
        self._handle_hooks.append(self._handle_subs_check)

        # A handler wanting to use the RARBG copier should set these three fields correctly
        # Where is source folder of the download?
        self.download_src_folder = None
        # What is the expected folder containing subtitles for this download?
        self.expected_subs_folder = None
        # What is the path to the file which was created from this download?
        self.media_destination_path = None

    def _handle_subs_check(self):
        if "RARBG" in self.download_src_folder.name:
            self._handle_rarbg_subs()

    def _handle_rarbg_subs(self):
        if self.expected_subs_folder.exists() and self.expected_subs_folder.is_dir():
            self._log.info(f"{self.expected_subs_folder} exists")

            english_srts = self._locate_english_subs_by_size(self.expected_subs_folder)

            for srt_file, suffix in [
                (english_srts.full_subtitle, ".en.srt"),
                (english_srts.sdh_subtitle, ".en.sdh.srt"),
                (english_srts.forced_subtitle, ".en.forced.srt"),
            ]:
                if srt_file is not None:
                    new_srt_path = self.media_destination_path.with_suffix(suffix)
                    self._log.info(f"Copying {srt_file.name} to {new_srt_path.name}")

                    shutil.copy(srt_file, new_srt_path)

        else:
            self._log.info(f"No {self.expected_subs_folder} found, nothing to do")

    def _locate_english_subs(self, expected_subs_folder: Path) -> _LocatedSubtitles:
        """
        Given a folder, will attempt to locate the properly named English subtitle files within the folder.
        If a subtitle is not found, it will be None
        """
        full_subtitle: Path = expected_subs_folder / Path("2_English.srt")
        sdh_subtitle: Path = expected_subs_folder / Path("3_English.srt")
        forced_subtitle: Path = expected_subs_folder / Path("4_English.srt")

        if not full_subtitle.exists() or not full_subtitle.is_file():
            self._log.info(f"{full_subtitle} not found")
            full_subtitle = None
        else:
            self._log.info(f"{full_subtitle} exists")

        if not sdh_subtitle.exists() or not sdh_subtitle.is_file():
            self._log.info(f"{sdh_subtitle} not found")
            sdh_subtitle = None
        else:
            self._log.info(f"{sdh_subtitle} exists")

        if not forced_subtitle.exists() or not forced_subtitle.is_file():
            self._log.info(f"{forced_subtitle} not found")
            forced_subtitle = None
        else:
            self._log.info(f"{forced_subtitle} exists")

        if full_subtitle is None and sdh_subtitle is None:
            self._log.warning(
                "Falling back to size based English SRT location, if possible",
            )
            full_subtitle = self._locate_english_subs_by_size(expected_subs_folder)

        return _LocatedSubtitles(full_subtitle, sdh_subtitle, forced_subtitle)

    def _locate_english_subs_by_size(
        self,
        expected_subs_folder: Path,
    ) -> _LocatedSubtitles:
        """
        Given a folder, this will locate the largest English language subtitle within it.
        If no English subtitles are found, it will return None, otherwise it will return the path
        """

        full_subtitle = None
        sdh_subtitle = None
        forced_subtitle = None

        srt_files: List[Path] = sorted(list(expected_subs_folder.glob("*.srt")))
        if len(srt_files):
            self._log.info("Filtering to English subs")
            english_files = []
            for eng_check_srt_file in srt_files:
                if "english" in eng_check_srt_file.name.lower():
                    english_files.append(eng_check_srt_file)

            srt_files = sorted(
                english_files,
                key=lambda x: x.stat().st_size,
            )

        if len(srt_files) == 0:
            self._log.info("No English subs found")
        elif len(srt_files) == 1:
            full_subtitle = srt_files[0]
        elif len(srt_files) == 2:
            smaller_srt = srt_files[0]
            larger_srt = srt_files[1]

            # If the smaller size is lt 10kb, assume it is a forced subtitle
            # and the larger size is the full subtitle
            # Otherwise, assume the smaller size is the full subtitle and the larger size
            # is the SDH subtitle
            if smaller_srt.stat().st_size < 10240:
                self._log.warning(
                    f"Assuming {smaller_srt.name} of size {smaller_srt.stat().st_size} is a forced subtitle",
                )
                forced_subtitle = smaller_srt
                full_subtitle = larger_srt
            else:
                full_subtitle = smaller_srt
                sdh_subtitle = larger_srt
        else:
            if len(srt_files) > 3:
                self._log.warning(
                    f"Found {len(srt_files)} English subs, only considering 3",
                )
            srt_files = srt_files[0:3]

            # Smallest file is forced
            # Medium file is full
            # Largest file is SDH
            forced_subtitle = srt_files[0]
            full_subtitle = srt_files[1]
            sdh_subtitle = srt_files[2]

        return _LocatedSubtitles(full_subtitle, sdh_subtitle, forced_subtitle)


class RadarrDownloadEventHandler(_RarbgSubtitleCopier):
    def __init__(self, log: logging.Logger):
        super().__init__(log)
        self.download_file_src_folder: Path = Path(
            os.environ.get("radarr_moviefile_sourcefolder"),
        )
        self.movie_file_path: Path = Path(os.environ.get("radarr_moviefile_path"))

        self.download_src_folder = self.download_file_src_folder
        self.expected_subs_folder = self.download_file_src_folder / Path("Subs")
        self.media_destination_path = self.movie_file_path


class SonarrDownloadEventHandler(_RarbgSubtitleCopier):
    def __init__(self, log: logging.Logger):
        super().__init__(log)
        self.episode_file_path = Path(os.environ["sonarr_episodefile_path"])
        self.episode_file_src_path = Path(os.environ["sonarr_episodefile_sourcepath"])
        self.episode_file_src_folder = Path(
            os.environ["sonarr_episodefile_sourcefolder"],
        )

        self.download_src_folder = self.episode_file_src_folder
        # For TV, subtitles are found in Subs/filename without suffix
        self.expected_subs_folder = (
            self.episode_file_src_folder
            / Path("Subs")
            / Path(self.episode_file_src_path.with_suffix("").name)
        )
        self.media_destination_path = self.episode_file_path


if __name__ == "__main__":

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
