from pywps import Service
from pywps.tests import assert_response_success, client_for

from .common import TESTDATA

from duck.processes.wps_clintai import ClintAI


def test_wps_clintai():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={TESTDATA['tas_hadcrut_small']}"
    datainputs += ";data_type=tas"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)
    # assert "meta4" in get_output(resp.xml)["output"]
    # assert b"year:2015,2016|month:01,02,03" in resp.data
