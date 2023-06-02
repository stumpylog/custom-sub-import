"""
Defines the various ways to locate a set of subtitles
"""
from pathlib import Path
from typing import List
from typing import Optional


class LocatedSubtitles:
    def __init__(
        self,
        full_subtitle,
        sdh_subtitle,
        forced_subtitle,
    ) -> None:
        self.full_subtitle: Optional[Path] = full_subtitle
        self.sdh_subtitle: Optional[Path] = sdh_subtitle
        self.forced_subtitle: Optional[Path] = forced_subtitle


def locate_english_subs_by_name(
    log,
    expected_subs_folder: Path,
) -> LocatedSubtitles:
    """
    Given a folder, will attempt to locate the properly named English subtitle files within the folder.
    If a subtitle is not found, it will be None.

    If RARBG naming was consistent, this would be the quickest and best solution.  But
    the names of files vary, so it isn't used.
    """
    full_subtitle: Path = expected_subs_folder / Path("2_English.srt")
    sdh_subtitle: Path = expected_subs_folder / Path("3_English.srt")
    forced_subtitle: Path = expected_subs_folder / Path("4_English.srt")

    if not full_subtitle.exists() or not full_subtitle.is_file():
        log.info(f"{full_subtitle} not found")
        full_subtitle = None
    else:
        log.info(f"{full_subtitle} exists")

    if not sdh_subtitle.exists() or not sdh_subtitle.is_file():
        log.info(f"{sdh_subtitle} not found")
        sdh_subtitle = None
    else:
        log.info(f"{sdh_subtitle} exists")

    if not forced_subtitle.exists() or not forced_subtitle.is_file():
        log.info(f"{forced_subtitle} not found")
        forced_subtitle = None
    else:
        log.info(f"{forced_subtitle} exists")

    return LocatedSubtitles(full_subtitle, sdh_subtitle, forced_subtitle)


def locate_english_subs_by_size(
    log,
    expected_subs_folder: Path,
) -> LocatedSubtitles:
    """
    Given a folder, this will locate the largest English language subtitle within it.
    If no English subtitles are found, it will return None, otherwise it will return the path.

    The type of subtitle is chosen based on size.

    If only 1 subtitle is found, it is assumed to be a normal subtitle. It may actually be SDH, but that
    is a minor thing.

    If two subtitles are found, a subtitle under 10Kb is assumed to be a forced subtitle, with the other
    being a full subtitle.  If no subtitle is under 10Kb, the larger file is assumed as SDH, with
    the smaller being the full subtitle.

    Finally, if three subtitle files are found, they are ordered by size and assumed to be
    forced, full and SDH in order.

    """

    full_subtitle = None
    sdh_subtitle = None
    forced_subtitle = None

    srt_files: List[Path] = sorted(list(expected_subs_folder.glob("*.srt")))
    if len(srt_files):
        log.info("Filtering to English subs")
        english_files = []
        for eng_check_srt_file in srt_files:
            if "english" in eng_check_srt_file.name.lower():
                english_files.append(eng_check_srt_file)

        srt_files = sorted(
            english_files,
            key=lambda x: x.stat().st_size,
        )

    if len(srt_files) == 0:
        log.info("No English subs found")
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
            log.warning(
                f"Assuming {smaller_srt.name} of size {smaller_srt.stat().st_size} is a forced subtitle",
            )
            forced_subtitle = smaller_srt
            full_subtitle = larger_srt
        else:
            full_subtitle = smaller_srt
            sdh_subtitle = larger_srt
    else:
        if len(srt_files) > 3:
            log.warning(
                f"Found {len(srt_files)} English subs, only considering 3",
            )
        srt_files = srt_files[0:3]

        # Smallest file is forced
        # Medium file is full
        # Largest file is SDH
        forced_subtitle = srt_files[0]
        full_subtitle = srt_files[1]
        sdh_subtitle = srt_files[2]

    return LocatedSubtitles(full_subtitle, sdh_subtitle, forced_subtitle)


def locate_english_subs_vtx(
    log,
    expected_subs_folder: Path,
) -> LocatedSubtitles:
    full_subtitle = None
    sdh_subtitle = None
    forced_subtitle = None

    srt_files: List[Path] = sorted(list(expected_subs_folder.glob("*.srt")))
    if len(srt_files):
        log.info("Filtering to English subs")
        english_files = []
        for eng_check_srt_file in srt_files:
            if "english" in eng_check_srt_file.name.lower():
                english_files.append(eng_check_srt_file)

        srt_files = sorted(
            english_files,
            key=lambda x: x.stat().st_size,
        )

    if len(srt_files) == 0:
        log.info("No English subs found")
    elif len(srt_files) == 1:
        forced_subtitle = srt_files[0]
    elif len(srt_files) == 2:
        smaller_srt = srt_files[0]
        larger_srt = srt_files[1]

        if smaller_srt.stat().st_size < 10240:
            log.warning(
                f"Assuming {smaller_srt.name} of size {smaller_srt.stat().st_size} is a forced subtitle",
            )
            full_subtitle = smaller_srt
            sdh_subtitle = larger_srt
        else:
            forced_subtitle = smaller_srt
            sdh_subtitle = larger_srt
    else:
        if len(srt_files) > 3:
            log.warning(
                f"Found {len(srt_files)} English subs, only considering 3",
            )
        srt_files = srt_files[0:3]

        # Smallest file is full
        # Medium file is forced
        # Largest file is SDH
        full_subtitle = srt_files[0]
        forced_subtitle = srt_files[1]
        sdh_subtitle = srt_files[2]

    return LocatedSubtitles(full_subtitle, sdh_subtitle, forced_subtitle)
