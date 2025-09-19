# demalign

**Authors:** Aram Fathian; Dan Shugar  
**Affiliation:** Department of Earth, Energy, and Environment; Water, Sediment, Hazards, and Earth-surface Dynamics (waterSHED) Lab; University of Calgary  
**License:** MIT

`demalign` aligns a **source DEM** (e.g., a DSM from SkySatPrep + Metashape) to a **stable reference DEM** (e.g., COP30) using
**NASA Ames Stereo Pipeline (ASP)** tools: it estimates the horizontal/vertical translation using **Nuth & Kääb**, optionally refines
with **ICP (point-to-plane)**, applies the inverse transform to the source, and re-grids to a DEM with `point2dem`.

- Fast downsampled transform estimation (Nuth & Kääb)
- Optional ICP refine, then apply transform at full resolution
- Re-grid the transformed source cloud into a DEM in your target CRS/resolution
- Outputs suitable for **DEM of Difference (DoD)** workflows

> demalign is a Python CLI wrapper around the proven ASP workflow (`pc_align` + `point2dem`).

## Installation

### Quick install (recommended)

> Use a fresh Conda environment so GDAL CLI and Python bindings (if used) won’t conflict.

```bash
# 1) Create & activate env (Linux/macOS/WSL)
conda create -n demalign -c conda-forge -y python=3.10 gdal numpy
conda activate demalign

# 2) Install the package (from source for now)
# pip install demalign        # (once on PyPI)
pip install -e .              # if you're in the repo folder
```

### External dependencies (required)

- **NASA Ames Stereo Pipeline (ASP)** ≥ 3.3 (provides `pc_align`, `point2dem`)  
  Download & install: https://github.com/NeoGeographyToolkit/StereoPipeline

  Then set on every shell:
  ```bash
  export ASP_HOME="$HOME/StereoPipeline"
  export PATH="$ASP_HOME/bin:$PATH"
  export LD_LIBRARY_PATH="$ASP_HOME/lib:${LD_LIBRARY_PATH:-}"
  export CSM_PLUGIN_PATH="$ASP_HOME/lib/csmplugins"

  # verify
  pc_align --help | head -n 3
  point2dem --help | head -n 3
  ```

- **GDAL** (CLI) for `gdal_translate` downsampling used internally
  ```bash
  gdalinfo --version
  ```

### Alternative install options

**A) From GitHub (specific tag):**
```bash
pip install "git+https://github.com/aramfathian/demalign.git@v0.1.0"
```

**B) From source (editable dev install):**
```bash
# inside the repo folder
pip install -e .[dev]
```

### Notes on dependencies

- ASP is an **external** dependency; `demalign` shells out to `pc_align` and `point2dem`.
- `gdal_translate` is used for quick downsampling; GDAL itself is not a Python dependency here.

## Usage (examples)

**Basic: align a source DEM to a reference DEM and write an aligned DEM.**
```bash
demalign   --source /path/to/source_dem.tif   --reference /path/to/reference_dem.tif   --epsg 32608   --tr 5   --out /path/to/out_dir
```

**Common options**
- `--downsample 25`          Downsample percent for fast transform estimation (default: 25)
- `--no-icp`                 Disable ICP refine (Nuth & Kääb only)
- `--max-disp-nuth 600`      Max displacement for Nuth stage (m)
- `--max-disp-icp 300`       Max displacement for ICP stage (m)
- `--nodata -9999`           Nodata value for outputs (default: -9999)
- `--keep-intermediate`      Keep intermediate clouds/downsized DEMs
- `--asp-home`               Override `ASP_HOME` detection
- `--no-regrid`              Compute transform only; do not run `point2dem`

### Outputs
- `nuth-transform.txt`, `nuth-inverse-transform.txt` (and, if used, `icp-*.txt`)
- `full_SOURCE-trans_source.tif` (transformed source point cloud from `pc_align`)
- `aligned_dem.tif` (DEM from `point2dem`), unless `--no-regrid`

## Workflow tips

- Use a **stable reference DEM** (e.g., COP30) that matches the **height datum** of your source DEM (ellipsoidal vs orthometric).  
- Work in a **consistent projected CRS** (e.g., the scene’s UTM zone) and pass it via `--epsg`.
- Start with the default `--downsample 25` for robust, fast estimation; increase for very noisy DEMs.
- If terrain is complex or initial offsets are large, enable ICP (`--no-icp` *not* set) for refinement.

## Troubleshooting

- **`ASP not found`** → Set `ASP_HOME` and/or make sure `pc_align` and `point2dem` are on your `PATH`.
- **`gdal_translate: not found`** → Install GDAL CLI (`conda install -c conda-forge gdal`).
- **Huge datasets** → Increase `--downsample` to speed transform estimation; keep `--keep-intermediate` for QA.
- **CRS issues** → Always pass the correct `--epsg`; the output DEM will be gridded in that CRS.

## How to cite
```
Fathian, A., Shugar, D. (2025). demalign (v0.2.0) [Software]. Zenodo. https://doi.org/10.5281/zenodo.17157750
```

## License
MIT (see `LICENSE`).

## Acknowledgements
Built around the **NASA Ames Stereo Pipeline** tools (`pc_align`, `point2dem`) and a production-tested shell workflow adapted to a reusable Python CLI. See: https://stereopipeline.readthedocs.io/en/latest/index.html
