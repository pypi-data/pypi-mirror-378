
from __future__ import annotations
import os, subprocess, shutil
from pathlib import Path
from typing import Optional, Tuple

def log(msg: str) -> None:
    print(msg, flush=True)

def which(cmd: str) -> Optional[str]:
    return shutil.which(cmd)

def detect_asp(explicit_home: Optional[str] = None) -> Tuple[str, str, str]:
    asp_home = explicit_home or os.environ.get("ASP_HOME", "")
    if asp_home:
        pc = Path(asp_home) / "bin" / "pc_align"
        p2 = Path(asp_home) / "bin" / "point2dem"
        if pc.exists() and p2.exists():
            return asp_home, str(pc), str(p2)
    pc = which("pc_align")
    p2 = which("point2dem")
    if pc and p2:
        asp_home = str(Path(pc).resolve().parents[1])
        return asp_home, pc, p2
    raise RuntimeError("ASP not found. Set ASP_HOME or ensure pc_align/point2dem in PATH.")

def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)

def downsample_dem(src: Path, dst: Path, percent: int = 25) -> None:
    if dst.exists():
        return
    run(["gdal_translate", "-r", "average", "-outsize", f"{percent}%", f"{percent}%", str(src), str(dst)])

def run_coreg(
    source_dem: Path,
    reference_dem: Path,
    out_dir: Path,
    epsg: int,
    tr: float,
    downsample_percent: int = 25,
    do_icp: bool = True,
    max_disp_nuth: int = 600,
    max_disp_icp: int = 300,
    nodata: int = -9999,
    asp_home: Optional[str] = None,
    keep_intermediate: bool = False,
    regrid: bool = True,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    asp_home, pc_align, point2dem = detect_asp(asp_home)

    lo_src = out_dir / "SOURCE_lo.tif"
    lo_ref = out_dir / "REF_lo.tif"
    downsample_dem(source_dem, lo_src, downsample_percent)
    downsample_dem(reference_dem, lo_ref, downsample_percent)

    log("== Nuth & Kääb translation ==")
    run([pc_align, "--alignment-method", "nuth", "--compute-translation-only",
         "--max-displacement", str(max_disp_nuth),
         str(lo_src), str(reference_dem), "-o", "nuth"])

    apply_tr = out_dir / "nuth-inverse-transform.txt"
    if do_icp:
        log("== ICP refine (point-to-plane) ==")
        run([pc_align, "--alignment-method", "point-to-plane",
             "--max-displacement", str(max_disp_icp),
             "--initial-transform", str(out_dir / "nuth-transform.txt"),
             str(lo_src), str(reference_dem), "-o", "icp"])
        icp_inv = out_dir / "icp-inverse-transform.txt"
        if icp_inv.exists():
            apply_tr = icp_inv

    log("== Apply final transform to FULL-RES source DEM ==")
    run([pc_align, "--num-iterations", "0", "--max-displacement", "-1",
         "--max-num-source-points", "100000000", "--max-num-reference-points", "200000",
         "--initial-transform", str(apply_tr),
         str(lo_ref), str(source_dem),
         "--save-transformed-source-points", "-o", "full_SOURCE"])

    trans = out_dir / "full_SOURCE-trans_source.tif"
    if not regrid:
        return trans

    log("== Regrid to DEM ==")
    aligned_dem = out_dir / "aligned_dem.tif"
    run([point2dem, str(trans), "--tr", str(tr), "--t_srs", f"EPSG:{epsg}",
         "--nodata-value", str(nodata), "-o", "aligned_dem"])

    if not keep_intermediate:
        for p in [lo_src, lo_ref]:
            try: p.unlink()
            except Exception: pass

    return aligned_dem
