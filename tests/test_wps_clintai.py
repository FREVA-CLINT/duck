import pytest

from pywps import Service
from pywps.tests import (
    assert_process_exception,
    assert_response_success,
    client_for
)

from tests.common import (
    HADCRUT4_SMALL_NC,
    HADCRUT4_SMALL_NC_ZIP,
    HADCRUT4_TAS_NC_ZIP,
    HadCRUT5_TAS_MEAN_NC,
)

from duck.processes.wps_clintai import ClintAI


def test_wps_clintai_hadcrut4_small():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={HADCRUT4_SMALL_NC}"
    datainputs += ";hadcrut=HadCRUT4"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)
    # assert "meta4" in get_output(resp.xml)["output"]
    # assert b"year:2015,2016|month:01,02,03" in resp.data


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


def test_wps_clintai_hadcrut4_small_zip():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={HADCRUT4_SMALL_NC_ZIP}"
    datainputs += ";hadcrut=HadCRUT4"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)


@pytest.mark.xfail(reason="not working")
# @pytest.mark.skip(reason="not working")
def test_wps_clintai_hadcrut4_tas():
    client = client_for(Service(processes=[ClintAI()]))
    # datainputs = f"dataset=@xlink:href={HADCRUT4_ANOMALIES_1_NC}"
    datainputs = f"dataset=@xlink:href={HADCRUT4_TAS_NC_ZIP}"
    datainputs += ";hadcrut=HadCRUT4"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)


def test_wps_clintai_hadcrut5_tas_mean():
    client = client_for(Service(processes=[ClintAI()]))
    datainputs = f"dataset=@xlink:href={HadCRUT5_TAS_MEAN_NC}"
    datainputs += ";hadcrut=HadCRUT5"
    resp = client.get(
        f"?service=WPS&request=Execute&version=1.0.0&identifier=clintai&datainputs={datainputs}"
    )
    # print(resp.data)
    assert_response_success(resp)
