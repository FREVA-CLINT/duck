import pytest

from pywps import Service
from pywps.tests import (
    assert_process_exception,
    assert_response_success,
    client_for
)

from tests.common import (
    HADCRUT4_TAS_NC_ZIP,
    HadCRUT5_TAS_MEAN_NC,
)

from duck.processes.wps_clintai import ClintAI
from duck.clintai import (
    HADCRUT5_TAS_MEAN,
    HADCRUT4_TEMPERATURE_ANOMALY,
)


@pytest.mark.skip(reason="don't use tas variable")
def test_wps_clintai_hadcrut4_tas_small():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={HADCRUT4_SMALL_NC}"
    datainputs += f";hadcrut={HADCRUT4_TEMPERATURE_ANOMALY}"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)
    # assert "meta4" in get_output(resp.xml)["output"]
    # assert b"year:2015,2016|month:01,02,03" in resp.data

@pytest.mark.skip(reason="Code has changed")
def test_wps_clintai_hadcrut4_error_wrong_parameter():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={HADCRUT4_SMALL_NC}"
    datainputs += ";hadcrut=HadCRUT3"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.status_code)
    # TODO: should be error code ... fix in pywps!
    # assert resp.status_code == 200
    # print(resp.data)
    # assert b"ExceptionReport" in resp.data
    assert_process_exception(resp, code="InvalidParameterValue")


@pytest.mark.online
def test_wps_clintai_hadcrut4_temperature_anomaly():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={HADCRUT4_TAS_NC_ZIP}"
    # datainputs += f";hadcrut={HADCRUT4_TEMPERATURE_ANOMALY}"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)


@pytest.mark.online
def test_wps_clintai_hadcrut5_tas_mean():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={HadCRUT5_TAS_MEAN_NC}"
    datainputs += f";hadcrut={HADCRUT5_TAS_MEAN}"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)
