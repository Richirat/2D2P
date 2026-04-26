import os
import glob
import tifffile as tiff
import numpy as np
import re
import datetime as dt
from pathlib import Path


def get_imaging_files(datafolder, namelist, readVRlogs=True):
    '''
    Get the (TIFF, RElog[, VRlog]) triples for each requested trial in a session
    folder, paired by exact trial-id match.

    Args:
        datafolder: the folder containing the data files.
        namelist: list of 5-digit zero-padded trial-id strings,
                  e.g. ['00003', '00004', '00005'].
        readVRlogs: when True, also include the VRlog file for each trial.

    Returns:
        A list of [tiff, RElog] (readVRlogs=False) or [tiff, RElog, VRlog]
        (readVRlogs=True) entries, one per requested trial, sorted by trial id.

    Raises:
        ValueError: if any namelist entry is not a 5-digit zero-padded string,
                    if multiple files of the same kind match a trial, or if any
                    requested trial cannot be paired with all required files.
    '''
    # (a) Every namelist entry must be a 5-digit zero-padded string.
    bad = [x for x in namelist
           if not (isinstance(x, str) and re.fullmatch(r"\d{5}", x))]
    if bad:
        raise ValueError(
            "namelist entries must be 5-digit zero-padded strings "
            f"(e.g. '00005'); got invalid entries: {bad!r}"
        )
    dupes = sorted({x for x in namelist if namelist.count(x) > 1})
    if dupes:
        raise ValueError(f"namelist contains duplicate entries: {dupes!r}")
    requested = sorted(namelist)            # 5-digit padded -> string sort == numeric sort
    requested_set = set(requested)

    # Trial token = trailing 5-digit group in the file stem, anchored to a
    # non-digit boundary so a 6-digit suffix can't masquerade as a 5-digit trial.
    trial_re = re.compile(r"(?<!\d)(\d{5})$")

    def trial_of(path):
        m = trial_re.search(Path(path).stem)
        return m.group(1) if m else None

    folder = Path(datafolder)

    def build_map(paths, kind):
        m = {}
        for p in paths:
            if "stack" in Path(p).name:     # basename-only stack exclusion
                continue
            t = trial_of(p)
            if t is None or t not in requested_set:
                continue
            if t in m:
                raise ValueError(
                    f"Multiple {kind} files matched trial {t} in {datafolder}: "
                    f"{m[t]!r} and {str(p)!r}"
                )
            m[t] = str(p)
        return m

    tif_by_trial = build_map(glob.glob(str(folder / "*.tif")), "TIFF")
    re_by_trial  = build_map(glob.glob(str(folder / "RE*.txt")), "RElog")
    vr_by_trial  = (build_map(glob.glob(str(folder / "[0-9]*.txt")), "VRlog")
                    if readVRlogs else {})

    # (b) Every requested trial must produce a complete pairing.
    allfiles = []
    missing = []
    for trial in requested:
        tif = tif_by_trial.get(trial)
        rel = re_by_trial.get(trial)
        vrl = vr_by_trial.get(trial) if readVRlogs else None
        miss = []
        if tif is None: miss.append("TIFF")
        if rel is None: miss.append("RElog")
        if readVRlogs and vrl is None: miss.append("VRlog")
        if miss:
            missing.append(f"trial {trial} (missing: {', '.join(miss)})")
            continue
        allfiles.append([tif, rel, vrl] if readVRlogs else [tif, rel])

    if len(allfiles) != len(namelist):
        raise ValueError(
            f"get_imaging_files could not pair every requested trial in {datafolder}: "
            + "; ".join(missing)
        )

    return allfiles

def get_rotary_center(centerfile):
    '''
    get the rotary center from the centerfile
    Args:
        centerfile: the file containing the rotary center
    Returns:
        the rotary center 
    '''
    
    with open(centerfile, "r") as f:
        # read the last row
        last_line = f.readlines()[-1]
        # assign the x and y coordinates to self.rotx and self.roty
        rotx = float(last_line.split()[0])
        roty = float(last_line.split()[1])
    
    rotCenter = [rotx, roty]
    
    return rotCenter



_num_re = re.compile(r"^[+-]?\d+(\.\d+)?([eE][+-]?\d+)?$")


def _parse_value(v: str):
    v = v.strip()

    if v == "[]":
        return []
    if v == "{}":
        return {}

    # Bracket array like: [2023  7 27 16  9 18.354]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if inner == "":
            return []
        parts = re.split(r"[\s,]+", inner)
        out = []
        for p in parts:
            if not p:
                continue
            if _num_re.match(p):
                out.append(int(p) if re.match(r"^[+-]?\d+$", p) else float(p))
            else:
                out.append(p)
        return out

    if _num_re.match(v):
        return int(v) if re.match(r"^[+-]?\d+$", v) else float(v)

    return v


def parse_scanimage_description(desc: str) -> dict:
    """
    Parse ScanImage per-frame ImageDescription text into a dict.
    Only parses the first block before '---'.
    """
    d = {}
    block = desc.split('---', 1)[0]
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith('%') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        d[k.strip()] = _parse_value(v)
    return d


def _epoch_list_to_datetime(epoch_list):
    """
    epoch_list format: [Y, M, D, h, m, s.sss]
    """
    if not isinstance(epoch_list, (list, tuple)) or len(epoch_list) < 6:
        raise ValueError(f"Invalid epoch format: {epoch_list}")

    Y, M, D, h, m, sec = epoch_list[:6]
    sec_float = float(sec)
    base = dt.datetime(int(Y), int(M), int(D), int(h), int(m), 0)
    return base + dt.timedelta(seconds=sec_float)


def get_scanimage_frame_times(path_tif: str):
    """
    Read a ScanImage TIFF and return per-frame START and ACQUIRE times.

    Returns
    -------
    frame_start_rel_sec : (N,) float64
        Frame START times relative to acquisition start (frameTimestamps_sec)

    frame_start_wallclock : (N,) datetime64[ns]
        Wall-clock frame START times (epoch + frameTimestamps_sec)

    frame_acquire_rel_sec : (N,) float64
        Frame ACQUIRE times approximated as next frame's START time

    frame_acquire_wallclock : (N,) datetime64[ns]
        Wall-clock frame ACQUIRE times
    """

    ts = []
    epoch_list = None

    with tiff.TiffFile(path_tif) as tf:
        for i, page in enumerate(tf.pages):
            desc = page.description

            if isinstance(desc, dict):
                dd = desc.get("Description", desc)
            elif isinstance(desc, str):
                dd = parse_scanimage_description(desc)
            else:
                raise TypeError(f"Page {i}: unexpected description type: {type(desc)}")

            if epoch_list is None:
                if "epoch" not in dd:
                    raise KeyError(f"Page {i}: missing epoch")
                epoch_list = dd["epoch"]

            if "frameTimestamps_sec" not in dd:
                raise KeyError(f"Page {i}: missing frameTimestamps_sec")

            ts.append(float(dd["frameTimestamps_sec"]))

    frame_start_rel_sec = np.asarray(ts, dtype=np.float64)

    # ---- wall-clock START times ----
    epoch_dt = _epoch_list_to_datetime(epoch_list)
    epoch64 = np.datetime64(epoch_dt, "ns")

    frame_start_wallclock = epoch64 + (frame_start_rel_sec * 1e9).astype("timedelta64[ns]")

    # ---- ACQUIRE times: shift by one frame ----
    frame_acquire_rel_sec = np.empty_like(frame_start_rel_sec)
    frame_acquire_rel_sec[:-1] = frame_start_rel_sec[1:]

    if frame_start_rel_sec.size >= 2:
        dt_last = frame_start_rel_sec[-1] - frame_start_rel_sec[-2]
    else:
        dt_last = 0.0

    frame_acquire_rel_sec[-1] = frame_start_rel_sec[-1] + dt_last

    frame_acquire_wallclock = epoch64 + (frame_acquire_rel_sec * 1e9).astype("timedelta64[ns]")

    # return (
    #     frame_start_rel_sec,
    #     frame_start_wallclock,
    #     frame_acquire_rel_sec,
    #     frame_acquire_wallclock,
    # )

    return (
        frame_acquire_rel_sec,
        frame_acquire_wallclock,
    )

def read_rotary_log(path_txt, tA_wall=None, window_sec=1.0):
    """
    Read rotary log with columns:
    DateTime  MonotonicSec  AngleDeg
    Returns: (dt_list, mono_list, angle_list)
    """
    dt_list = []
    mono_list = []
    angle_list = []

    # optional time window filter
    t_min = None
    t_max = None
    if tA_wall is not None:
        tA_wall_arr = np.asarray(tA_wall)
        if tA_wall_arr.size > 0:
            if np.issubdtype(tA_wall_arr.dtype, np.datetime64):
                # convert numpy datetime64 -> python datetime
                def _dt64_to_dt(x):
                    ns = x.astype("datetime64[ns]").astype("int64")
                    return dt.datetime(1970, 1, 1) + dt.timedelta(microseconds=ns / 1000.0)

                t_min = _dt64_to_dt(tA_wall_arr.min())
                t_max = _dt64_to_dt(tA_wall_arr.max())
            else:
                # assume list of datetime objects
                t_min = min(tA_wall)
                t_max = max(tA_wall)

            if window_sec is None:
                window_sec = 0.0

            t_min = t_min - dt.timedelta(seconds=float(window_sec))
            t_max = t_max + dt.timedelta(seconds=float(window_sec))

    with open(path_txt, "r", encoding="utf-8") as f:
        header = f.readline()
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue

            dt_str = parts[0] + " " + parts[1]
            mono_str = parts[2]
            angle_str = parts[3] if len(parts) > 3 else ""

            try:
                t = dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
            except ValueError:
                try:
                    t = dt.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue

            if t_min is not None and (t < t_min or t > t_max):
                continue

            try:
                mono = float(mono_str)
            except ValueError:
                continue

            if angle_str == "" or angle_str.lower() == "nan":
                angle = np.nan
            else:
                try:
                    angle = float(angle_str)
                except ValueError:
                    angle = np.nan

            dt_list.append(t)
            mono_list.append(mono)
            angle_list.append(angle)

    return dt_list, mono_list, angle_list


def get_frame_angles_from_rotary(tif_path, rotary_log_path, window_sec=1.0):
    """
    For each frame in tif_path, return nearest rotary angle from rotary_log_path.

    Returns
    -------
    angle_at_tA : (N,) float64
        Angle per frame, nearest neighbor matched by wall-clock time.
    tA_rel : (N,) float64
        Frame acquire times relative to acquisition start (seconds).
    tA_wall : (N,) datetime64[ns]
        Frame acquire wall-clock timestamps.
    """
    tA_rel, tA_wall = get_scanimage_frame_times(tif_path)
    dt_list, _, angle_list = read_rotary_log(rotary_log_path, tA_wall=tA_wall, window_sec=window_sec)

    angle_arr = np.asarray(angle_list, dtype=float)
    dt_arr = np.array(dt_list, dtype="datetime64[ns]")

    if len(tA_wall) == 0:
        angle_at_tA = np.array([], dtype=float)
    else:
        idx = np.searchsorted(dt_arr, tA_wall, side="left")
        idx = np.clip(idx, 0, len(dt_arr) - 1)

        prev_idx = np.clip(idx - 1, 0, len(dt_arr) - 1)
        use_prev = (idx > 0) & (
            np.abs(tA_wall - dt_arr[prev_idx]) <= np.abs(tA_wall - dt_arr[idx])
        )
        idx[use_prev] = prev_idx[use_prev]
        angle_at_tA = angle_arr[idx]

    return angle_at_tA, tA_rel, tA_wall



def load_tiff_and_time(tif_path, txt_path):
    """
    Read tiff and its paired time.txt

    Returns
    -------
    img : ndarray
        Tiff image data
    frame_indices : list[int]
        FrameIndex values
    monotonic_secs : list[float]
        MonotonicSec values
    """
    tif_path = Path(tif_path)
    txt_path = Path(txt_path)

    frame_indices = []
    monotonic_secs = []

    with txt_path.open("r", encoding="utf-8") as f:
        _ = f.readline()  # skip header
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 3:
                continue
            try:
                mono = float(parts[1])
                frame = int(parts[2])
            except ValueError:
                continue
            monotonic_secs.append(mono)
            frame_indices.append(frame)

    img = tiff.imread(str(tif_path))
    return img, frame_indices, monotonic_secs


def get_angles_from_monotonic(monotonic_secs, rotary_log_path, window_sec=1.0):
    """
    For each monotonic timestamp, return nearest rotary angle from rotary_log_path.

    Returns
    -------
    angle_at_mono : (N,) float64
        Angle per monotonic timestamp (nearest neighbor)
    mono_arr : (N,) float64
        Monotonic timestamps as float array
    """
    mono_arr = np.asarray(monotonic_secs, dtype=float)
    if mono_arr.size == 0:
        return np.array([], dtype=float), mono_arr

    mono_min = float(mono_arr.min()) - float(window_sec)
    mono_max = float(mono_arr.max()) + float(window_sec)

    mono_list = []
    angle_list = []

    with open(rotary_log_path, "r", encoding="utf-8") as f:
        _ = f.readline()  # skip header
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 4:
                continue

            mono_str = parts[2]
            angle_str = parts[3]

            try:
                mono = float(mono_str)
            except ValueError:
                continue

            if mono < mono_min or mono > mono_max:
                continue

            if angle_str == "" or angle_str.lower() == "nan":
                angle = np.nan
            else:
                try:
                    angle = float(angle_str)
                except ValueError:
                    angle = np.nan

            mono_list.append(mono)
            angle_list.append(angle)

    mono_log = np.asarray(mono_list, dtype=float)
    angle_arr = np.asarray(angle_list, dtype=float)

    if mono_log.size == 0:
        return np.full_like(mono_arr, np.nan, dtype=float), mono_arr

    # Nearest-neighbor matching
    idx = np.searchsorted(mono_log, mono_arr, side="left")
    idx = np.clip(idx, 0, len(mono_log) - 1)

    prev_idx = np.clip(idx - 1, 0, len(mono_log) - 1)
    use_prev = (idx > 0) & (np.abs(mono_arr - mono_log[prev_idx]) <= np.abs(mono_arr - mono_log[idx]))
    idx[use_prev] = prev_idx[use_prev]

    angle_at_mono = angle_arr[idx]
    return angle_at_mono, mono_arr


def load_buffer_frames_and_angles(tif_path, txt_path, rotary_log_path, window_sec=1.0):
    """
    Read tiff + time.txt + rotary_log, output:
      frames: tiff image data
      angles: angle per frame (matched by MonotonicSec)
    """
    frames, _, monotonic_secs = load_tiff_and_time(tif_path, txt_path)
    angles, _ = get_angles_from_monotonic(monotonic_secs, rotary_log_path, window_sec=window_sec)
    return frames, angles




    
    
    
