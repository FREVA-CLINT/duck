import os
from jinja2 import Template
from pathlib import Path
import shutil

from climatereconstructionai import evaluate

import logging
LOGGER = logging.getLogger("PYWPS")

DUCK_HOME = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(DUCK_HOME, "data")


def write_clintai_cfg(base_dir, name, data_type):
    cfg_templ = """
    --data-root-dir {{ base_dir }}
    --mask-dir {{ base_dir }}/outputs
    --model-dir {{ data_dir }}
    --model-names 20cr_20220114.pth
    --evaluation-dirs {{ base_dir }}/outputs
    --img-names {{ name }}
    --data-types {{ data_type }}
    --device cpu --image-sizes 72
    --out-channels 1
    --lstm-steps 0
    --prev-next-steps 0
    --infill infill
    --eval-names demo
    --dataset-name hadcrut4
    """
    # TODO: --plot-results 0
    # TODO: --dataset-name hadcrut
    cfg = Template(cfg_templ).render(
        base_dir=base_dir,
        data_dir=DATA_DIR,
        name=name,
        data_type=data_type)
    out = Path(base_dir + "/clintai.cfg")
    with open(out, "w") as fp:
        fp.write(cfg)
    return out


def run(dataset, data_type, outdir):
    name = Path(dataset).name
    Path(outdir + "/masks").mkdir()
    Path(outdir + "/outputs/").mkdir()
    Path(outdir + "/images").mkdir()
    input_dir = Path(outdir + "/test_large")
    input_dir.mkdir()
    shutil.move(dataset, input_dir)
    cfg_file = write_clintai_cfg(base_dir=outdir, name=name, data_type=data_type)
    print(f"written cfg {cfg_file}")
    evaluate(cfg_file.as_posix())
    # TODO: remove dummy png files
    Path(f"{outdir}/outputs/demo_masked_gt_0.png").write_text("Sorry. No plot.")
    Path(f"{outdir}/outputs/demo_output_comp_0.png").write_text("Sorry. No plot.")
