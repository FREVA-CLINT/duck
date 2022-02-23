from pathlib import Path

from pywps import Process
from pywps import LiteralInput
from pywps import ComplexInput, ComplexOutput
from pywps import FORMATS
from pywps.app.Common import Metadata
# from pywps.app.exceptions import ProcessError

from duck import clintai

import logging
LOGGER = logging.getLogger("PYWPS")

# FORMAT_PNG = Format("image/png", extension=".png", encoding="base64")


class ClintAI(Process):
    def __init__(self):
        inputs = [
            ComplexInput('dataset', 'Upload your NetCDF file here',
                         abstract='Enter a URL pointing to a NetCDF file.',
                         min_occurs=1,
                         max_occurs=1,
                         supported_formats=[FORMATS.NETCDF]),
            LiteralInput('data_type', "Data Type",
                         abstract="Choose data type.",
                         min_occurs=1,
                         max_occurs=1,
                         default='tas',
                         allowed_values=['tas']),
        ]
        outputs = [
            ComplexOutput('output', 'NetCDF Output',
                          abstract='NetCDF Output produced by ClintAI.',
                          as_reference=True,
                          supported_formats=[FORMATS.NETCDF]),
            # ComplexOutput('plot_output_comp', 'plot output comp',
            #               abstract='plot output comp.',
            #               as_reference=True,
            #               supported_formats=[FORMAT_PNG]),
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
            abstract="Fills the gaps in your uploaded dataset.",
            metadata=[
                Metadata('Clint AI', 'https://github.com/FREVA-CLINT/climatereconstructionAI'),
                Metadata('Clint Project', 'https://climateintelligence.eu/'),
            ],
            inputs=inputs,
            outputs=outputs,
            status_supported=True,
            store_supported=True,
        )

    def _handler(self, request, response):
        dataset = request.inputs['dataset'][0].file
        data_type = request.inputs['data_type'][0].data

        response.update_status('starting ...', 0)

        clintai.run(dataset, data_type, outdir=self.workdir)

        response.outputs["output"].file = Path(self.workdir + "/outputs/demo_output_comp.nc")
        # response.outputs["log"].file = Path(self.workdir + "/logs/demo.log")
        # response.outputs["plot_output_comp"].file = Path(self.workdir + "/images/demo_output_comp.png")

        response.update_status('done.', 100)
        return response
