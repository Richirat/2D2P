import os
import glob
import re
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
    
    
    
