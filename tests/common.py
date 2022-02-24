import os
from pathlib import Path

from pywps import get_ElementMakerForVersion
from pywps.app.basic import get_xpath_ns
from pywps.tests import WpsClient, WpsTestResponse

VERSION = "1.0.0"
WPS, OWS = get_ElementMakerForVersion(VERSION)
xpath_ns = get_xpath_ns(VERSION)


TEST_DATA_CACHE_DIR = Path.home() / ".duck" / "cache" / "testdata"
TESTS_HOME = os.path.abspath(os.path.dirname(__file__))

HADCRUT4_URL = "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/"
HADCRUT4_NC_ZIP = "HadCRUT.4.6.0.0.anomalies.1_to_10_netcdf.zip"


def resource_file(filepath):
    p = Path(f"{TESTS_HOME}/testdata/{filepath}")
    print("test file", p.as_uri())
    return p.as_uri()


HADCRUT4_SMALL_NC = resource_file(
    "tas_hadcrut4/tas_hadcrut4_187709_189308.nc")
HADCRUT4_SMALL_NC_ZIP = resource_file(
    "tas_hadcrut4.zip")
HADCRUT4_ANOMALIES_1_NC = (TEST_DATA_CACHE_DIR / HADCRUT4_NC_ZIP).as_uri()
HADCRUT4_TAS_NC_ZIP = "https://www.metoffice.gov.uk/hadobs/hadcrut4/data/current/gridded_fields/HadCRUT.4.6.0.0.median_netcdf.zip"  # noqa
HadCRUT5_TAS_MEAN_NC = "https://www.metoffice.gov.uk/hadobs/hadcrut5/data/current/non-infilled/HadCRUT.5.0.1.0.anomalies.ensemble_mean.nc"  # noqa


class WpsTestClient(WpsClient):

    def get(self, *args, **kwargs):
        query = "?"
        for key, value in kwargs.items():
            query += "{0}={1}&".format(key, value)
        return super(WpsTestClient, self).get(query)


def client_for(service):
    return WpsTestClient(service, WpsTestResponse)


def get_output(doc):
    """Copied from pywps/tests/test_execute.py.
    TODO: make this helper method public in pywps."""
    output = {}
    for output_el in xpath_ns(doc, '/wps:ExecuteResponse'
                                   '/wps:ProcessOutputs/wps:Output'):
        [identifier_el] = xpath_ns(output_el, './ows:Identifier')

        lit_el = xpath_ns(output_el, './wps:Data/wps:LiteralData')
        if lit_el != []:
            output[identifier_el.text] = lit_el[0].text

        ref_el = xpath_ns(output_el, './wps:Reference')
        if ref_el != []:
            output[identifier_el.text] = ref_el[0].attrib['href']

        data_el = xpath_ns(output_el, './wps:Data/wps:ComplexData')
        if data_el != []:
            output[identifier_el.text] = data_el[0].text

    return output
