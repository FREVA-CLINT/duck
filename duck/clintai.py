import os
from jinja2 import Template
import shutil

from climatereconstructionai import evaluate

import logging
LOGGER = logging.getLogger("PYWPS")

DUCK_HOME = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(DUCK_HOME, "data")


def write_clintai_cfg(base_dir, name, data_type, dataset_name):
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
    --plot-results 0
    --dataset-name {{ dataset_name }}
    """
    cfg = Template(cfg_templ).render(
        base_dir=base_dir,
        data_dir=DATA_DIR,
        name=name,
        data_type=data_type,
        dataset_name=dataset_name)
    out = base_dir / "clintai.cfg"
    with open(out, "w") as fp:
        fp.write(cfg)
    return out


def run(dataset, data_type, dataset_name, outdir):
    (outdir / "masks").mkdir()
    (outdir / "outputs").mkdir()
    input_dir = outdir / "test_large"
    input_dir.mkdir()
    shutil.move(dataset.as_posix(), input_dir.as_posix())
    # print(f"dataset={dataset}")
    cfg_file = write_clintai_cfg(
        base_dir=outdir,
        name=dataset.name,
        data_type=data_type,
        dataset_name=dataset_name)
    # print(f"written cfg {cfg_file}")
    try:
        evaluate(cfg_file.as_posix())
    except SystemExit:
        raise Exception("clintai exited with an error.")
