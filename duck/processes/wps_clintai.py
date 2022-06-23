from pathlib import Path
from zipfile import ZipFile

from pywps import Process
from pywps import ComplexInput, ComplexOutput
from pywps import FORMATS, Format
from pywps.app.Common import Metadata
from pywps.app.exceptions import ProcessError

from duck import clintai
import xarray as xr

import logging
LOGGER = logging.getLogger("PYWPS")

FORMAT_PNG = Format("image/png", extension=".png", encoding="base64")

MEDIA_ROLE = "http://www.opengis.net/spec/wps/2.0/def/process/description/media"


class ClintAI(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Add your HadCRUT file here',
                         abstract="Enter a URL pointing to a HadCRUT NetCDF file with missing values.",
                                  # "Example: "
                                  # "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc",  # noqa
                         min_occurs=1,
                         max_occurs=1,
                         supported_formats=[FORMATS.NETCDF, FORMATS.ZIP]),
        ]
        outputs = [
            ComplexOutput('output', 'Reconstructed dataset',
                          abstract='NetCDF output produced by CRAI.',
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]),
            ComplexOutput('plot', 'Preview of the first time step',
                          # abstract='Plot of original input file. First timestep.',
                          as_reference=True,
                          supported_formats=[FORMAT_PNG]),
        ]

        super(ClintAI, self).__init__(
            self._handler,
            identifier="crai",
            title="CRAI",
            version="0.1.0",
            abstract="AI-enhanced climate service to infill missing values in climate datasets.",
            metadata=[
                Metadata(
                    title="CRAI Logo",
                    href="https://github.com/FREVA-CLINT/duck/raw/main/docs/source/_static/crai_logo.png",
                    role=MEDIA_ROLE),
                Metadata('CRAI', 'https://github.com/FREVA-CLINT/climatereconstructionAI'),
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

        response.update_status('Prepare dataset ...', 0)
        workdir = Path(self.workdir)

        if Path(dataset).suffix == ".zip":
            with ZipFile(dataset, 'r') as zip:
                print("extraction zip file", workdir)
                zip.extractall(workdir.as_posix())

        # only one dataset file
        try:
            dataset_0 = list(workdir.rglob('*.nc'))[0]
        except Exception:
            raise ProcessError("Could not extract netcdf file.")

        ds = xr.open_dataset(dataset_0)

        vars = list(ds.keys())
        if "temperature_anomaly" in vars:
            hadcrut = "HadCRUT4"
        elif "tas_mean" in vars:
            hadcrut = "HadCRUT5"
        else:
            raise ProcessError("File could not been identified as HadCRUT4/HadCRUT5")

        # response.update_status('Infilling ...', 20)
        try:
            clintai.run(
                dataset_0,
                hadcrut=hadcrut,
                outdir=workdir,
                update_status=response.update_status)
        except Exception as e:
            raise ProcessError(str(e))

        response.outputs["output"].file = workdir / "outputs" / str(dataset_0.stem+"_infilled.nc")
        response.outputs["plot"].file = workdir / "outputs" / str(dataset_0.stem+"_combined_0.png")

        response.update_status('done.', 100)
        return response
