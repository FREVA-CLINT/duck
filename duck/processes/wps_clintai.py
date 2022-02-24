from pathlib import Path

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

DATA_TYPES_MAP = {
    "Near Surface Air Temperature": "tas",
    "Temperature Anomaly": "temperature_anomaly",
}


class ClintAI(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Upload your HadCRUT file here',
                         abstract="Enter a URL pointing to a NetCDF file."
                                  "Use HadCRUT4 files https://www.metoffice.gov.uk/hadobs/hadcrut4/",
                         min_occurs=1,
                         max_occurs=1,
                         supported_formats=[FORMATS.NETCDF]),
            LiteralInput('data_type', "Data Type",
                         abstract="Choose data type.",
                         min_occurs=1,
                         max_occurs=1,
                         # default='tas',
                         allowed_values=[
                            "Near Surface Air Temperature",
                            "Temperature Anomaly"
                         ]),
        ]
        outputs = [
            ComplexOutput('output', 'NetCDF Output',
                          abstract='NetCDF Output produced by ClintAI.',
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]),
            ComplexOutput('plot_original', 'Plot: before',
                          abstract='Plot of original input file.',
                          as_reference=True,
                          supported_formats=[FORMAT_PNG]),
            ComplexOutput('plot_infilled', 'Plot: after',
                          abstract='Plot of infilled output file.',
                          as_reference=True,
                          supported_formats=[FORMAT_PNG]),
            # ComplexOutput('log', 'logfile',
            #               abstract='logfile of ClintAI execution.',
            #               as_reference=True,
            #               supported_formats=[FORMATS.TEXT]),
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
        data_type = DATA_TYPES_MAP[request.inputs['data_type'][0].data]

        response.update_status('infilling ...', 10)

        try:
            clintai.run(dataset, data_type, outdir=self.workdir)
        except Exception:
            raise ProcessError("infilling failed!.")

        response.outputs["output"].file = Path(self.workdir + "/outputs/demo_output_comp.nc")
        # response.outputs["log"].file = Path(self.workdir + "/logs/demo.log")
        response.outputs["plot_original"].file = Path(self.workdir + "/outputs/demo_masked_gt_0.png")
        response.outputs["plot_infilled"].file = Path(self.workdir + "/outputs/demo_output_comp_0.png")

        response.update_status('done.', 100)
        return response
