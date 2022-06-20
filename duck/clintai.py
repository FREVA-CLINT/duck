import os
from jinja2 import Template
import shutil
import collections

from climatereconstructionai import evaluate
import multiprocessing
import time
import logging
LOGGER = logging.getLogger("PYWPS")

DUCK_HOME = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(DUCK_HOME, "data")

HADCRUT5_TAS_MEAN = "HadCRUT5"
HADCRUT4_TEMPERATURE_ANOMALY = "HadCRUT4"
# HADCRUT4_TAS = "HadCRUT"

HADCRUT = collections.OrderedDict({
    HADCRUT5_TAS_MEAN: {
        "variable": "tas_mean",
        "name": "hadcrut",
    },
    HADCRUT4_TEMPERATURE_ANOMALY: {
        "variable": "temperature_anomaly",
        "name": "hadcrut",
    },
    # HADCRUT4_TAS: {
    #     "variable": "tas",
    #     "name": "hadcrut",
    # },
})


HADCRUT_VALUES = list(HADCRUT.keys())


def prog_func(base_dir, response):
    ilimit = 2000
    perc_start = 10
    perc_end = 100 - perc_start
    prog_file = str(base_dir) + "/progfwd.info"
    response.update_status('Infilling ...', perc_start)
    for i in range(ilimit):
        try:
            prog_fwd = open(prog_file).readline().strip()
            if prog_fwd != "":
                val = int(perc_start + perc_end * int(prog_fwd) / 100)
                response.update_status('Infilling ...', val)
                if prog_fwd == "100":
                    break
        except IOError:
            pass
        time.sleep(0.1)


def write_clintai_cfg(base_dir, name, evalname, data_type, dataset_name):
    cfg_templ = """
    --data-root-dir {{ base_dir }}
    --log-dir {{ base_dir }}
    --mask-dir {{ base_dir }}/outputs
    --model-dir {{ data_dir }}
    --model-names 20crtasgn72.pth
    --evaluation-dirs {{ base_dir }}/outputs
    --img-names {{ name }}
    --data-types {{ data_type }}
    --device cpu --image-sizes 72
    --n-filters 18
    --out-channels 1
    --lstm-steps 0
    --prev-next-steps 0
    --eval-names {{ evalname }}
    --plot-results 0
    --dataset-name {{ dataset_name }}
    --progress-fwd
    """
    cfg = Template(cfg_templ).render(
        base_dir=base_dir,
        data_dir=DATA_DIR,
        name=name,
        evalname=evalname,
        data_type=data_type,
        dataset_name=dataset_name)
    out = base_dir / "clintai.cfg"
    with open(out, "w") as fp:
        fp.write(cfg)
    return out


def run(dataset, hadcrut, outdir, response):
    data_type = HADCRUT[hadcrut]["variable"]
    dataset_name = HADCRUT[hadcrut]["name"]
    (outdir / "masks").mkdir()
    (outdir / "outputs").mkdir()
    input_dir = outdir / "test_large"
    input_dir.mkdir()
    shutil.move(dataset.as_posix(), input_dir.as_posix())
    # print(f"dataset={dataset}")
    cfg_file = write_clintai_cfg(
        base_dir=outdir,
        name=dataset.name,
        evalname=dataset.stem,
        data_type=data_type,
        dataset_name=dataset_name)
    # print(f"written cfg {cfg_file}")
    try:
        prog_thread = multiprocessing.Process(target=prog_func, args=(outdir, response))
        prog_thread.start()
        eval_thread = multiprocessing.Process(target=evaluate, args=(cfg_file.as_posix(),))
        eval_thread.start()
        eval_thread.join()
        prog_thread.terminate()

    except SystemExit:
        raise Exception("CRAI exited with an error.")
