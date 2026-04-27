# Project Overview

**2D2P Statistical Analysis Pipeline** — a reproducible port of the legacy
`2D2P` code (Zilong Ji et al.) for processing 2-dimensional virtual-reality
two-photon calcium imaging data. Raw data are rotating-stage 2P recordings
of hippocampal CA1 pyramidal neurons expressing GCaMP6f, paired with a rotary
encoder and VR behavioural logs. The new layer under `io_core/` + `pipeline/`
handles three different session-folder variants, unrotates frames to a
common wall-clock reference, runs Suite2p with a pinned CA1-pyramidal /
GCaMP6f config, and emits ΔF/F, place-cell classification, place fields,
cross-day ROI matching, and QC reports.

A parallel workstream under `Behavioural_analysis/_v2_pipeline/` walks the
cleaned `MiceVRlogs/` tree (Phases 1/2/3 across Practical and Imaging rigs)
and produces per-session metrics, cross-day learning curves, MixedLM fits,
per-mouse trajectory PDFs, and a combined results report for thesis
Results chapters.

# Active sprint (as of 2026-04-27)

- Thesis submission deadline: **30 April 2026**.
- Behavioural results chapter: complete in v4 draft
  (`Behavioural_analysis/_v2_pipeline/results/`).
- Imaging results chapter: pending. Tier 1 batch (17 sessions) runs via
  `scripts/run_tier1_batch.sh`, ~25 h sequential.
- VRlog audit **IN PROGRESS** — some imaging sessions missing VRlogs,
  `MiceVRlogs/` at project root may contain the missing files. Audit
  must complete before kicking off batch.
- Discussion chapter: drafting concurrent with batch.
- Active thesis file: `Thesis_FullDraft_Revised_v4.docx` → next save-as
  v5 once Results lands.

# Tech Stack

- **Python only.** This project does not use R in any capacity. All
  analysis, pipeline code, manuscripts, and build steps are Python
  (edited in Visual Studio 2022) or Jupyter notebooks in an Anaconda
  environment. Never introduce R, Rmd, papaja, bookdown, officedown, or
  any R-flavoured tool. Use `jupyter-academic-builder` (not
  `rmd-academic-builder`) for academic documents.
- Python 3.8+. Active conda env on AHNB-ANATOMY is **`suite2p`** (not
  `2D2P`); the historical `2D2P` env name still appears in some legacy
  setup notes but is no longer the live environment.
- Suite2p (lazy-imported; pipeline degrades gracefully when absent)
- Cellpose 2.2.1 (installed in the `suite2p` env; powers
  `pipeline/figures.py` `detect_cell_bodies` Cellpose-first path)
- ScanImage TIFFs via `ScanImageTiffIO` / SITiffIO
- NumPy, SciPy (ndimage, optimize), scikit-image, matplotlib, pandas
- tifffile, OASIS (via Suite2p) for deconvolution
- Legacy GUI: tkinter (`2D2P.py`, `centerdetector.py`)
- Shell on AHNB-ANATOMY is **Anaconda Prompt (cmd), not PowerShell**.
  Argparse docstrings and CLI help strings must be **ASCII-only** —
  the cmd-prompt console codepage will raise `UnicodeEncodeError` on
  smart quotes, en/em dashes, or arrows when argparse renders `--help`.

# Project Structure

```
Statistical Analysis Pipeline/
├── io_core/                # Unified I/O: variants, manifest (scan_session),
│                           # tiff_metadata, rotary_log, vrlog, frame_sync
├── pipeline/               # Processing layers built on io_core:
│                           #   centre, centre_auto (experimental),
│                           #   unrotate, suite2p_config, run_suite2p,
│                           #   qc_report, fluorescence, place_cells,
│                           #   place_fields, cross_day, cell_registry,
│                           #   session_analysis, population_decoding,
│                           #   pmt_compare, dp_compare, figures
├── scripts/                # CLI entry points:
│                           #   batch_run_session.py   (main runner)
│                           #   end_to_end_183.py      (pilot 183 driver)
│                           #   pmt_compare_cli.py     (PMT-swap report)
│                           #   cross_day_registry_cli.py
│                           #   scan_pilot_sessions.py
│                           #   smoke_test_io.py, smoke_test_unrotate.py
│                           #   test_fluorescence_vs_legacy.py
│                           #   test_decoding.py, test_pmt_stats.py
│                           #   validate_centre_auto.py
│                           #   task_stats_pilot.py        (single-session
│                           #     driver for task_metrics — writes per-lap /
│                           #     per-trial / per-bin CSVs + 4-page PDF)
│                           #   run_task_stats_dataset.py  (walks MiceVRlogs
│                           #     and emits task_metrics_session.csv)
│                           #   regenerate_qc.py           (re-emit per-trial
│                           #     QC HTML from existing Suite2p outputs
│                           #     without re-running registration)
│                           #   SETUP_from_scratch.md  (env bootstrap;
│                           #     prequel to RUNBOOK_full_pilots.md)
│                           #   RUNBOOK_full_pilots.md + Step2_runbook.pdf
├── pilot_session/          # 183/183_03082023 + 183/183_04082023 (Variant B),
│                           # 724/724_11112024 (Variant B with _NNNNN
│                           #   separator + combined VRlog + kind-tagged
│                           #   baseline/stack REdata),
│                           # 724/724_12112024 (Variant C — no NNNNN
│                           #   suffixes; paired via time-window containment),
│                           # 935/20260320 (Variant A; incomplete pilot —
│                           #   no VRlog, sparse data_* numbering)
├── MiceVRlogs/             # Canonical behavioural-log tree: one folder per
│                           #   mouse, each containing Phase 1/, Phase 2/,
│                           #   Phase 3/{Imaging Rig, Practical Rig}/.
│                           #   Quarantine folders at the root:
│                           #   CavelogsPracticalRig/ (raw unsorted logs),
│                           #   _misattributed/, _sanity_check/,
│                           #   recordingsImagingRig/, recordingsPracticalRig/,
│                           #   ConvertedTimestampsPracticalRig/, ImagingPC/,
│                           #   VRtracker/, Training notes/
├── Behavioural_analysis/   # Behavioural workstream:
│                           #   _v2_pipeline/  (parse_log, metrics,
│                           #                   task_metrics, aggregate,
│                           #                   inferential, plots,
│                           #                   progression_plots, outliers,
│                           #                   results_report, run_dataset
│                           #                   + README.md + results/)
│                           #   Behavioural_analyses.py + .pdf  (legacy script
│                           #                                    and rendered
│                           #                                    report)
│                           #   Single trial analysis/, Trajectory plots/,
│                           #   Tortuosity analysis/, Linear_track_plots/,
│                           #   Square_plots/, Improvement Ratio/,
│                           #   Linear_trajectory_analysis/,
│                           #   Animated_plot_VR_input/, Live_plot_mouse_input.py,
│                           #   view_video.ipynb, PythonApplication1/
├── analysis_notebook/      # Original analysis notebooks (reference, being ported)
├── paper_notebook/         # Figure-generation notebooks for the 2D2P paper
├── notebook/               # Earliest exploratory notebooks
├── manuscript/             # Methods writeup: build_methods.py → methods.ipynb
│                           # + methods.md + methods.docx, references.bib,
│                           # pmt_compare.csv + pmt_compare_report.html
├── annotated_chapters_revisions/  # Thesis chapter drafts + annotated
│                           #   revisions + suggested revisions (docx/pdf)
├── thesis-supervisor-skill/       # Custom skill for PhD-thesis review
│                           #   (SKILL.md + qmul_guidelines.md +
│                           #    reference_theses_summary.md +
│                           #    field_conventions.md + viva_checklist.md)
├── Thesis_FullDraft_Revised_v*.docx    # Rolling thesis full-draft revisions
│                                       # (current: v4, 2026-04-24)
├── Thesis_v4_next_steps.md             # Punch list to take v4 → submission
├── Thesis_Improvements_Suggestions.docx # Running list of thesis improvements
├── thesis_supervision_report_*.docx    # Dr. Constructive / Dr. Adversarial
│                                       # supervisor-style chapter reviews
├── thesis_methods_snippets.docx        # Methods §2.7 source paragraphs
├── outlier_criteria_appendix.docx      # Appendix on robust-z outlier flags
├── task_metrics_report.docx            # Standalone write-up of task_metrics
│                                       # results (per-lap / per-trial / per-bin)
├── imaging_audit_report.html           # Phase 1A imaging-dataset audit
│                                       # (D:\data + E:\Data + E:\ImagingPC)
├── imaging_consolidation_plan.md       # DRAFT plan to consolidate the
│                                       # imaging dataset into D:\imaging_clean\
├── Figures/                # Paper figure outputs
├── 2D2P.py                 # Legacy tkinter GUI entry point (preserved)
├── twoDtwoP.py             # Renamed GUI variant using NewZdriftProcessor
│                           #   (automated, watch-folder Z-drift)
├── newzdriftprocessor.py   # Continuous Z-drift class used by twoDtwoP.py
├── centerdetector.py,      # Legacy circlecenter.txt GUI (still authoritative
│   stackprocessor.py,      #   for centre detection — auto-centre is experimental)
│   zdriftprocessor.py,
│   fovfinder.py, …         # Other legacy standalone modules
├── Single_trial_analysis.py,   # Legacy behavioural / trajectory analysis
│   Tortuosity_analysis.py,     #   scripts (matplotlib Agg backend, operate
│   Trajectory_plots.py         #   on pilot_session outputs — being ported)
├── utils_*.py              # Legacy utility modules (io, image, fluorescence,
│                           # analysis) — the new pipeline vectorises these
├── README.md, LICENSE, .gitignore
└── SETUP_from_scratch.pdf  # Rendered copy of scripts/SETUP_from_scratch.md
```

# Development Commands

Install (existing lab recipe — historical `2D2P` env name; the live env
on AHNB-ANATOMY is `suite2p`):
```
conda create -n suite2p python=3.8
conda activate suite2p
# Install ScanImageTiffIO (https://github.com/rhayman/ScanImageTiffIO)
# then pip-install remaining deps as needed (Suite2p, Cellpose==2.2.1, ...)
```
For a from-scratch machine setup (env, VS 2022 interpreter, smoke tests
before the runbook takes over) see `scripts/SETUP_from_scratch.md` —
the batch pipeline itself no longer needs ScanImageTiffIO; only the
legacy tkinter GUIs do, and every pilot already has `circlecenter.txt`
on disk.

Run the batch pipeline on a session:
```
python scripts/batch_run_session.py pilot_session/183/183_03082023
python scripts/batch_run_session.py <path> --only 00004,00005
python scripts/batch_run_session.py <path> --exclude 00003     # skip aborted trials
python scripts/batch_run_session.py <path> --skip-unrotate --skip-suite2p
python scripts/batch_run_session.py <path> --skip-analysis --skip-decoding
python scripts/batch_run_session.py <path> --aggregate-only    # rebuild session HTML
python scripts/batch_run_session.py <path> --batch-size 50 --n-shuffles 500
python scripts/batch_run_session.py <path> --concat            # concatenated
                                                               # Suite2p mode
                                                               # (see below)
```
See `scripts/RUNBOOK_full_pilots.md` for the canonical per-pilot recipes
(183, 724, 935) — including which trials to exclude and expected runtimes
on the AHNB-ANATOMY box.

`--concat` switches the runner into the colleague-style architecture:
cross-trial DC harmonisation in unrotation (`compute_session_dc_offsets`,
`pipeline/unrotate.py`) followed by **one** Suite2p run on the folder of
unrotated TIFFs (`run_suite2p_concatenated`, `pipeline/run_suite2p.py`).
Outputs land at `<session>/processed/suite2p_concat/` and per-trial
Suite2p, QC, and `analyse_trial` are skipped — `analyse_trial` is not
yet adapted to concat outputs.

Other CLIs:
```
python scripts/end_to_end_183.py                # pilot 183 driver
python scripts/pmt_compare_cli.py               # PMT-swap comparison report
python scripts/cross_day_registry_cli.py        # cross-day ROI registry
python scripts/scan_pilot_sessions.py           # quick variant/flag audit
python scripts/validate_centre_auto.py          # auto-centre vs. manual
python scripts/regenerate_qc.py <session>       # refresh QC HTML only
                                                # (no Suite2p re-run)
```

Smoke tests:
```
python scripts/smoke_test_io.py        # io_core scanner on pilots
python scripts/smoke_test_unrotate.py  # unrotation sanity check
python scripts/test_fluorescence_vs_legacy.py  # ΔF/F parity vs. legacy loop
python scripts/test_decoding.py        # Bayesian decoder sanity checks
python scripts/test_pmt_stats.py       # PMT signal-stats parity
```

Behavioural pipeline (run from `Behavioural_analysis/`):
```
python -m _v2_pipeline.run_dataset          # per-session metrics (long-form CSV)
python -m _v2_pipeline.aggregate            # cross-day + MixedLM aggregation
python -m _v2_pipeline.plots                # per-mouse trajectory PDFs
python -m _v2_pipeline.progression_plots    # Phase 3 Practical → Imaging cross-rig
python -m _v2_pipeline.outliers             # robust-z outlier flags
python -m _v2_pipeline.inferential          # publication stats (BH-FDR,
                                            #   bootstrap CIs, speed-control)
python -m _v2_pipeline.results_report       # combined results PDF (356 pp)
```
Task-conditioned scalars (per-lap / per-trial / per-bin) sit alongside the
session-level metrics:
```
python scripts/task_stats_pilot.py          # one-session driver + 4-page PDF
python scripts/run_task_stats_dataset.py    # full dataset → task_metrics_session.csv
```
Outputs land under `Behavioural_analysis/_v2_pipeline/results/`:
`behavioural_session_metrics.csv`, `task_metrics_session.csv`,
`mixed_effects_fits*.csv`, `inferential_v2/` (publication-grade fits +
markdown summary + report PDF), per-mouse trajectory PDFs, and the
`_results_front_v*.pdf` front-matter snapshots.

# Coding Conventions

- Public API is surfaced through `io_core/__init__.py` and
  `pipeline/__init__.py` — add to `__all__` when you add public objects.
- Suite2p is **lazy-imported** inside wrappers so the repo is usable without
  Suite2p installed (wrappers return `success=False` with a clear error).
- Filename regexes live in one place: `io_core.variants.RegexCatalog`. Don't
  scatter parsing rules.
- Three session variants (A/B/C) are dispatched by `classify_variant`; new
  readers must handle all three or fail loudly.
- ΔF/F and place-cell code is vectorised; any reimplementation of legacy
  notebook logic must be cross-checked against the legacy loop within
  documented tolerances (≤ 8% on boundary artefacts, float precision in
  interior — see `scripts/test_fluorescence_vs_legacy.py`).
- Provenance: `run_suite2p_*` writes a `params.json` beside every Suite2p
  output containing recipe name, applied deltas, full ops, and diff vs. the
  lab-legacy deltas. Keep this up to date when you change
  `ca1_gcamp6f_ops()`.
- QC reports are single-file, self-contained HTML (base64-inline PNGs) so
  they are portable and emailable.

# Code review workflow

- Claude Code installed locally with Codex CLI as a second-opinion
  subagent.
- Subagent definitions live at `.claude/agents/codex-reviewer.md` in each
  project root that wants the loop. Canonical copy at
  `D:/Statistical Analysis Pipeline/Imaging_data_analysis/.claude/agents/codex-reviewer.md`.
- Memory rule when invoking: statistical/inferential suggestions
  (effect-size definitions, denominators, hypothesis-test variants,
  preprocessing parameters, signal-processing choices) are **ADVISORY**,
  not authoritative. Bugs (off-by-one, NaN handling, type errors) can be
  auto-fixed.
- Codex calls run ~$0.03 – $0.10 per script review; subagent invokes
  Codex once per call, do not loop.

# Important Context

- **Three session variants** (see `io_core/variants.py`):
  - **A** — new pipeline (ScanImage 2023, session-wide `rotary_stream_*.txt`,
    e.g. mouse 935).
  - **B** — legacy, per-trial `REdata_*.NNNNN.txt` *or* `REdata_*_NNNNN.txt`
    (both `.NNNNN` and `_NNNNN` separators are accepted; 183 uses the dot,
    724_11112024 uses the underscore).
  - **C** — legacy, per-trial `REdata_*.txt` without any NNNNN suffix;
    paired to TIFFs via time-window containment (e.g. `724/724_12112024`).
- **Clock-sync anchor**: ScanImage per-page `epoch` + `frameTimestamps_sec`
  is the canonical frame → wall-clock anchor for *both* eras. The raw TIFF
  (not the unrotated one) carries this — pass the **raw** TIFF to
  `analyse_trial`; `unrotate_trial` strips the metadata.
- **183 rename (2026-04-20)**: Riccardo renamed the 183 session TIFFs to
  `DDMMYYYY_{baseline,session,stack}_NNNNN.tif`. Trial `00001` is therefore
  now `kind=baseline`, not a regular session trial. The batch runner
  defaults to `--only` over `session/*` kind; use `--only 00001` to run
  the baseline trial explicitly. 183_04082023 still uses the original
  unadorned `DDMMYYYY_NNNNN.tif` naming.
- **724 quirks** (see `scripts/RUNBOOK_full_pilots.md`):
  - 724_11112024 has a **combined VRlog** `..._00006 TO_00008.txt`
    covering trials 6–8; manifest expansion maps all three indices to
    the same file.
  - Kind-tagged REdata (`REdata_..._{baseline,stack}.txt`) wins for
    baseline/stack TIFFs so `baseline_00003` cannot steal
    `session_00003`'s per-trial REdata.
  - `baseline_00003` was **aborted mid-acquisition**; run with
    `--exclude 00003`.
  - 724_12112024 exercises Variant C (per-trial logs without NNNNN —
    `read_tiff_headers=True` is mandatory so the time-window pairing
    runs in the scan path).
- **Pilot session gaps**: `935/20260320` is an incomplete pilot with no
  VRlog and sparse `data_*` numbering — the pipeline runs but VR-derived
  place-cell metrics will be degenerate. `183/183_03082023` is the
  primary validation target (complete, has colleague's DP/DP_exp
  reference output for cross-checking).
- **DP reference comparison**: `pipeline/dp_compare.py` diffs the new
  pipeline against the colleague's legacy DP/DP_exp outputs (circle
  centres, 200-frame averaged TIFFs, side-by-side previews). Used to
  flag centre-selection, polar-angle convention, and PMT 0.5 V fallback
  discrepancies on pilot 183 (2026-04-19).
- **Auto-centre detector is EXPERIMENTAL** (`pipeline/centre_auto.py`).
  Validated 2026-04-18: ±10–30 px off manual ground truth — not
  production-ready. The legacy Tk `CenterDetector` GUI producing
  `circlecenter.txt` remains authoritative.
- **Default imaging channel** is channel 2 (anatomical); falls back to
  channel 1 if ch2 is absent. Set via `preferred_channel_for_variant`.
- **Suite2p deviations from default** are listed with justifications in
  `pipeline/suite2p_config.py` (fs=30, block_size=[64,64], maxregshift=0.15,
  batch_size=200, tau=0.7 for GCaMP6f).
- **Population decoding convention**: `pipeline/population_decoding.py`
  uses a **rate-per-frame** (not rate-per-second) convention for Bayesian
  position decoding. This matters when comparing MSE across datasets
  sampled at different frame rates — don't quietly rescale.
- **Publication figures** live in `pipeline/figures.py`: ROI-category
  maps, tuning-map grids, example calcium traces, and the Cellpose-first
  anatomical `detect_cell_bodies` (LoG + radial high-pass fallback to
  catch corner cells). The Cellpose path is opt-in so the module stays
  importable without Cellpose installed.
- **Hardware context**: development machine is Windows x64, i9-12900K,
  16 GB RAM. Default Suite2p settings fit comfortably; a full 2000-frame
  recording needs ≥ 8 GB RAM (Suite2p binary ~1 GB + torch/scipy overhead).
- **Timezone**: all logs come from the same PC, so naive local-time
  timestamps are compared against each other throughout. This is
  intentional and documented; deferred as a defensive-posture item.
- **Unrotation output convention**: `<session>/processed/unrot/<stem>_unrot.tif`.
  Suite2p output: `<session>/processed/suite2p/<stem>/plane0/`.
  QC: `<session>/processed/qc/<stem>/index.html`.
- **MiceVRlogs layout**: canonical tree is one folder per mouse →
  `Phase 1/`, `Phase 2/`, `Phase 3/{Imaging Rig, Practical Rig}/`. Rig
  assignment within Phase 3 is detected by the `RealTimeGainX=` token on
  trajectory lines of the VR log; Imaging Rig logs carry it, Practical
  Rig logs do not. Folders to skip when walking the tree:
  `recordingsImagingRig/`, `recordingsPracticalRig/`,
  `ConvertedTimestampsPracticalRig/`, `Training notes/`, `ImagingPC/`,
  `VRtracker/`, `CavelogsPracticalRig/`, `_misattributed/`,
  `_sanity_check/`. Four sessions were reclassified P2 → P1 on 2026-04-23.
- **CavelogsPracticalRig triage (2026-04-23)**: 834 orphan Practical-Rig
  logs triaged into five quarantine subfolders plus 19 rescued and moved
  into per-mouse folders. Subfolders: `_aborted_or_stub/` (656),
  `_already_in_mouse_folder/` (38), `_pre_traininglog_unattributed/` (76),
  `_colleague_mice/` (37), `_needs_manual_attribution/` (8). Do not
  reabsorb these without re-triaging.
- **Arena dimensions in rig coordinates** (used by teleport detection and
  path-length normalisation):
  - Square arena (Phase 1, Phase 3 square sessions):
    X ∈ [−19.51, −5.86], Z ∈ [36.72, 50.37], normalised to 0–60 cm.
  - Linear track, Phase 1: X ∈ (50, 60), Z ∈ (−70, 70).
  - Linear track, Phase 2: X ∈ (40, 70), Z ∈ (−100, 100).
  - Teleport rule: |dZ| > 30% of session Z range.
- **Training Log Excel date-storage quirk**: Italian-format DD/MM entries
  were reinterpreted by Excel as US MM/DD when stored as datetimes. For
  any datetime-typed cell with day ≤ 12, assume day and month are swapped
  and correct on load. Text-typed cells are untouched.
- **Behavioural pipeline conventions** (`Behavioural_analysis/_v2_pipeline/`):
  teleport-aware path-length and speed for linear-track Phase 2/3;
  V9-style square-arena stats for Phase 1 and Phase 3 square sessions;
  cross-day aggregation adds `session_index`/`day_index`; group stats use
  a MixedLM per phase × rig (`metric ~ session_index + (1 | mouse)`).
  `task_metrics.py` adds per-lap / per-trial / per-bin breakdowns
  (lap-time distribution, motion-bias profile, tortuosity, target-beacon).
  `inferential.py` produces the publication-grade fits: bootstrap 95% CIs,
  BH-FDR-adjusted p-values, optional log-transform for skewed metrics,
  and a parallel speed-controlled re-fit. Headline finding
  (2026-04-24, inferential_v2): 27-cell MixedLM grid → 7 survive
  BH-FDR, 4 ★★ after speed-control. P3 Practical `reward_per_min`
  β = 0.168, p_FDR < 0.001 (highly significant learning curve);
  P3 Imaging is at a plateau (flat `reward_per_min`), and Imaging-rig
  session counts remain too small for group MixedLM in most mice.
- **Two-machine workflow**: the home `Claude.app` install receives
  `manuscript/`, `pipeline/`, `io_core/`, `scripts/`, `Behavioural_analysis/`,
  `Figures/`, `paper_notebook/`, `analysis_notebook/`, and the thesis
  drafts. `pilot_session/` (~237 GB of raw imaging data) stays on
  AHNB-ANATOMY and is not synced.
- **Thesis state** (current draft: `Thesis_FullDraft_Revised_v4.docx`,
  2026-04-24): Methods chapter is drafted in `manuscript/` (auto-built
  from pipeline + io_core docstrings via `manuscript/build_methods.py`)
  and v4 adds a red-marked §2.7 covering the behavioural / inferential
  stack. Results Ch 3 §3.2 is fully populated in v4 (incl. new §3.2.7
  MixedLM grid, §3.2.8 per-mouse atlas, §3.2.9 outlier narrative);
  Ch 4 / Ch 5 imaging-results chapters are still placeholder-heavy and
  Ch 6 Discussion is short (≈ 2 551 words) and not yet reconciled with
  the behavioural findings. Submission punch list lives in
  `Thesis_v4_next_steps.md`. Full-draft revisions are tracked as
  `Thesis_FullDraft_Revised_v*.docx` at the repo root; annotated
  per-chapter revisions live under `annotated_chapters_revisions/`;
  source material for the imaging results lives in `paper_notebook/`
  and `analysis_notebook/`.
- **Imaging-results next priorities** (set 2026-04-24): three-step
  sequence before drafting Ch 4 / Ch 5 — (1) sort the imaging dataset
  and produce a canonical session manifest, (2) run the full imaging
  pipeline + stats on it, (3) integrate into the v5 thesis draft.
  Do not skip steps.
- **Imaging data drive locations** (AHNB-ANATOMY):
  - `D:\data\` — ~833 GB messy IPC copy (working scratch).
  - `E:\Data\` — ~1.2 TB canonical organised tree (source of truth).
  - `E:\ImagingPC\` — ~207 GB orphan-TIFF + protocol snapshot, includes
    the colleague's pipeline source at `E:\ImagingPC\SM2PCode\2D2P\`
    (concatenated Suite2p via the manual GUI + DC harmonisation; the
    colleague's ΔF/F handles negative F0 from the PMT 0.5 V floor).
- **Imaging audit Phase 1A (2026-04-24)**: read-only audit across the
  three drives produced `imaging_audit_report.html` and a draft
  `imaging_consolidation_plan.md` at the repo root. Headline numbers:
  57 sessions detected, 17 `ok` and 40 `incomplete`; 8 D-vs-E duplicate
  pairs (3 exact, 5 differ); 16 orphan TIFFs at root level; 29 sessions
  missing a co-located VRlog. **No files have been moved yet** — the
  consolidation plan is awaiting per-category approval before Phase 1B.
- **Concat pipeline (2026-04-24)**: `--concat` flag added to
  `batch_run_session.py`; new public entrypoints `run_suite2p_concatenated`
  (`pipeline/run_suite2p.py`) and `compute_session_dc_offsets`
  (`pipeline/unrotate.py`), both surfaced in `pipeline/__init__.py`.
  Built to fix the 7-PC depletion problem on per-trial Suite2p runs and
  to match the colleague's pipeline architecture. `analyse_trial` is
  not yet adapted to concat outputs — downstream stats currently still
  expect the per-trial layout.
- **Thesis-supervisor skill**: `thesis-supervisor-skill/` at the repo
  root provides a custom skill for PhD-thesis review (Dr. Constructive
  + Dr. Adversarial personas, four modes: structural, content-gap,
  conceptual-tutor, stats). Grounded in QMUL submission guidelines,
  four reference passed-viva theses, field conventions for hippocampal
  2P calcium imaging in VR, and a viva checklist. Reports it produces
  are written to `thesis_supervision_report_*.docx` at the repo root.

# Architecture notes

## Three parallel copies of `utils_io.py`

The project carries **three actively-used copies** of `utils_io.py` —
none is "the canonical" in the dead-code sense. Each tree's importers
pull from their sibling copy via bare `from utils_io import ...` (no
package form); there is no `__init__.py` in any of these directories,
so resolution happens through `sys.path[0]` (the script's parent
directory) or via explicit `sys.path.append("..")` /
`sys.path.insert(0, str(Path.cwd().parent))` in the notebooks.

- `D:/Statistical Analysis Pipeline/utils_io.py` — root copy. Contains
  only `get_imaging_files` + `get_rotary_center`. Used by the root
  `utils_image.py` / `utils_analysis.py` and the notebooks under
  `analysis_notebook/` and `notebook/`.
- `D:/Statistical Analysis Pipeline/2D2P_main/utils_io.py` — full
  legacy-pipeline surface, **missing** `_is_legacy_rotary_log` and
  `read_rotary_log_legacy`; its `get_frame_angles_from_rotary` lacks
  the legacy-format branch. Used by `2D2P_main/utils_*.py`,
  `2D2P_main/qt_*.py`, and the notebooks under
  `2D2P_main/{paper_,}notebook/`.
- `D:/Statistical Analysis Pipeline/Imaging_data_analysis/2D2P/utils_io.py`
  — most complete copy (full set including the legacy-format rotary
  branch). Used by everything under `Imaging_data_analysis/2D2P/`.

**Propagation rule.** Any fix to `utils_io.py` (e.g. the 2026-04-27
batch — exact-trial-match pairing in `get_imaging_files`,
duplicate-namelist rejection, `_epoch_list_to_datetime` rewrite, and
the `get_scanimage_frame_times` substitution) must be applied to **all
three copies** to take effect everywhere. Importers do not share state
across trees.

## Pending: x/y convention drift in `2D2P/utils_image.py`

`utils_image.py` carries an unresolved x/y axis convention drift.
Surfaced 2026-04-27; **not fixed in that session** because the bug is
latent on the square FOVs this lab actually records, and a correct fix
is module-wide rather than one-line.

**The disagreement.** Five sites in/around `Imaging_data_analysis/2D2P/`
disagree about whether centre coordinates are stored as `[x, y]` or
`[y, x]`:

- `utils_io.py::get_rotary_center` — returns `[x, y]` (column 0 of
  `circlecenter.txt` is named `rotx`, column 1 `roty`, packed as
  `[rotx, roty]`). This is the centre source-of-truth.
- `utils_image.py::_cv2_crop_bounds` body — does `cx = rotCenter[1]`,
  `cy = rotCenter[0]`, i.e. **expects input as `[y, x]`**. Comment
  `# OpenCV expects center = (x, y) = (col, row)` describes the output
  tuple, not the input, and is misleading.
- Caller #3 `get_unrotate_crop_cv2` — docstring says
  `rotCenter (list): rotation center [row, col]` → asserts `[y, x]`,
  matches helper body.
- Caller #2 `get_meanframe_from_Zstacks_cv2_reg_then_unrotcrop` —
  parameter named `rot_center_xy` with explicit comment
  `# IMPORTANT: (x, y), keep xy consistent everywhere` → asserts
  `[x, y]`, contradicts helper body.
- Caller #1 `get_meanframe_from_Zstacks_cv2` — undocumented; convention
  not stated.

**Why it has been latent.** `_cv2_crop_bounds` computes
`min(cx, w0 - cx, cy, h0 - cy)`. For a square FOV (`w0 == h0`) the
inscribed-rectangle math is symmetric in cx/cy, so the swap produces
the same crop bounds either way. ScanImage frames in this lab are
square (256x256, 332x332, 346x346), so the bug does not manifest in
current data. It would surface on non-square FOVs or whenever the
centre is far enough off-axis that `cx vs w0` and `cy vs h0` select
different limits.

**Proper fix scope (do not attempt as a one-liner).**

1. Pick the canonical convention. Recommended: `[x, y]`, matching
   `get_rotary_center` (the source) and caller #2's documented
   interface.
2. Fix `_cv2_crop_bounds` body: `cx = rotCenter[0]`, `cy = rotCenter[1]`,
   and rewrite the misleading comment.
3. Fix caller #3 `get_unrotate_crop_cv2`'s docstring (currently asserts
   `[row, col]` — opposite of the new convention).
4. Add an explicit docstring to caller #1
   `get_meanframe_from_Zstacks_cv2`.
5. Audit every external caller — notably
   `Imaging_data_analysis/2D2P/notebook/AligningTiffandRotatryAngle_newpipeline.ipynb`,
   which passes `Rotcenter = [248, 236]` to multiple of these functions
   and must use the same convention at every call site.

**Validation requirement.** This change touches the unrotation geometry
that `diagnose_meanReg.py` was specifically built to validate. Before
committing any fix, run `diagnose_meanReg.py` on the 183_03082023 pilot
and compare panel C (RegFrame on colleague's unrotated frames) against
panel D (`DP_exp/meanReg.png` reference). The patched code must produce
output indistinguishable from the colleague's pre-existing reference,
not just "look reasonable".

# Decisions log

| Date | Decision |
|---|---|
| 2026-04-27 | Set up Claude Code + Codex CLI dual-agent review loop. Rationale: catches errors single-model self-review misses; first run on `utils_io.py` found 14 issues including 2 silent-corruption bugs. |
| 2026-04-27 | Fixed `utils_io.py` latent bugs (anchored trial-id matching, dedup namelist, `_epoch_list_to_datetime` timedelta rewrite). Verified no historical analyses affected — all 7 callers passed 5-digit padded literals. Commits `89e21da`, `fae6eb2`. |
| 2026-04-27 | Propagated patches to all three copies of `utils_io.py` (project-root, `2D2P_main/`, `Imaging_data_analysis/2D2P/`). Function bodies AST-identical post-patch. Commit `1397dc1`. |
| 2026-04-27 | Deferred x/y convention drift in `2D2P/utils_image.py` — latent on square FOVs, fix needs validation against `DP_exp/meanReg.png` via `diagnose_meanReg.py`. Documented in Architecture, deferred post-thesis. Commit `a05b7a7`. |
| 2026-04-27 | Codex review of `utils_image.py`: 20 findings, none actioned in this session. Most are defensive hardening or methodological-advisory. Top safety bug (#19 `rmtree` without containment) is in dead `UnrotateTiff` (#17 `NameError`) → zero current exposure. Defer post-thesis. |

# Known issues

- `2D2P/utils_image.py`: 20 Codex findings deferred. Top three: x/y
  convention drift in `_cv2_crop_bounds` (latent on square FOVs);
  `RegFrame` int16 wraparound for uint16 > 32767; `UnrotateTiff` dead
  due to commented-out `SITiffIO` import. None block current analysis
  path.
- VRlog audit incomplete — some sessions in `E:\Data\` may have VRlogs
  in `MiceVRlogs\` at project root. Pairing must be verified before
  file moves (substring-matching risk class).
- Three parallel copies of `utils_io.py` exist by design (see
  Architecture notes). Any future fix must propagate to all three.
