
import argparse
from pathlib import Path
from .core import run_coreg

def main() -> None:
    ap = argparse.ArgumentParser(
        prog="demalign",
        description="DEM alignment (Nuth & Kääb + optional ICP refine) with ASP pc_align/point2dem"
    )
    ap.add_argument("--source", required=True, help="Source DEM to align (e.g., SkySat DSM from Metashape)")
    ap.add_argument("--reference", required=True, help="Reference DEM (stable)")
    ap.add_argument("--out", required=True, help="Output directory")
    ap.add_argument("--epsg", type=int, required=True, help="Target EPSG (e.g., 32608)")
    ap.add_argument("--tr", type=float, required=True, help="Output DEM resolution")
    ap.add_argument("--downsample", type=int, default=25, help="Downsample percent for transform estimation")
    ap.add_argument("--no-icp", action="store_true", help="Disable ICP refine")
    ap.add_argument("--max-disp-nuth", type=int, default=600)
    ap.add_argument("--max-disp-icp", type=int, default=300)
    ap.add_argument("--nodata", type=int, default=-9999)
    ap.add_argument("--asp-home", type=str, help="Override ASP_HOME")
    ap.add_argument("--keep-intermediate", action="store_true")
    ap.add_argument("--no-regrid", action="store_true", help="Compute transform only; skip point2dem")
    args = ap.parse_args()

    aligned = run_coreg(
        source_dem=Path(args.source),
        reference_dem=Path(args.reference),
        out_dir=Path(args.out),
        epsg=args.epsg,
        tr=args.tr,
        downsample_percent=args.downsample,
        do_icp=not args.no_icp,
        max_disp_nuth=args.max_disp_nuth,
        max_disp_icp=args.max_disp_icp,
        nodata=args.nodata,
        asp_home=args.asp_home,
        keep_intermediate=args.keep_intermediate,
        regrid=not args.no_regrid,
    )
    print(aligned)
