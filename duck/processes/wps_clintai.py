from pathlib import Path
from zipfile import ZipFile

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import FORMATS, Format
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from duck import clintai

import logging
LOGGER = logging.getLogger("PYWPS")

FORMAT_PNG = Format("image/png", extension=".png", encoding="base64")


class ClintAI(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Add your HadCRUT file here',
                         abstract="Enter a URL pointing to a HadCRUT NetCDF file."
                                  "Example: "
                                  "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc",  # noqa
                         min_occurs=1,
                         max_occurs=1,
                         supported_formats=[FORMATS.NETCDF, FORMATS.ZIP]),
            LiteralInput('hadcrut', "HadCRUT variant",
                         abstract="Choose HadCRUT variant of your dataset.",
                         min_occurs=1,
                         max_occurs=1,
                         allowed_values=clintai.HADCRUT_VALUES),
        ]
        outputs = [
            ComplexOutput('output', 'Infilled HadCRUT output',
                          abstract='NetCDF output produced by ClintAI.',
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]),
            ComplexOutput('plot_original', 'Plot: before',
                          abstract='Plot of original input file. First timestep.',
                          as_reference=True,
                          supported_formats=[FORMAT_PNG]),
            ComplexOutput('plot_infilled', 'Plot: after',
                          abstract='Plot of infilled output file. First timestep.',
                          as_reference=True,
                          supported_formats=[FORMAT_PNG]),
        ]

        super(ClintAI, self).__init__(
            self._handler,
            identifier="clintai",
            title="ClintAI",
            version="0.1.0",
            abstract="Fills the gaps in your uploaded climate dataset (HadCRUT).",
            metadata=[
                Metadata('Clint AI', 'https://github.com/FREVA-CLINT/climatereconstructionAI'),
                Metadata('Clint Project', 'https://climateintelligence.eu/'),
                Metadata('HadCRUT on Wikipedia', 'https://en.wikipedia.org/wiki/HadCRUT'),
                Metadata('HadCRUT4', 'https://www.metoffice.gov.uk/hadobs/hadcrut4/'),
                Metadata('HadCRUT5', 'https://www.metoffice.gov.uk/hadobs/hadcrut5/'),
                Metadata('Near Surface Air Temperature',
                         'https://www.atlas.impact2c.eu/en/climate/temperature/?parent_id=22'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        dataset = request.inputs['dataset'][0].file
        hadcrut = request.inputs['hadcrut'][0].data

        response.update_status('Prepare dataset ...', 10)
        workdir = Path(self.workdir)

        if Path(dataset).suffix == ".zip":
            with ZipFile(dataset, 'r') as zip:
                print("extraction zip file", workdir)
                zip.extractall(workdir.as_posix())

        # only one dataset file
        try:
            dataset_0 = list(workdir.rglob('*.nc'))[0]
            # print(dataset_0)
        except Exception:
            raise ProcessError("Could not extract netcdf file.")

        response.update_status('Infilling ...', 20)

        try:
            clintai.run(
                dataset_0,
                hadcrut=hadcrut,
                outdir=workdir)
        except Exception:
            raise ProcessError("Infilling failed.")

        response.outputs["output"].file = workdir / "outputs" / "demo_output_comp.nc"
        response.outputs["plot_original"].file = workdir / "outputs" / "demo_masked_gt_0.png"
        response.outputs["plot_infilled"].file = workdir / "outputs" / "demo_output_comp_0.png"

        response.update_status('done.', 100)
        return response
