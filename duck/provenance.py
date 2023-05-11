import os
import uuid
import json
from datetime import datetime
import pathlib

from prov.identifier import Namespace
import prov.model as prov
from prov.dot import prov_to_dot

# prov namespace
PROV_ORGANISATION = prov.PROV["Organization"]
PROV_SOFTWARE_AGENT = prov.PROV["SoftwareAgent"]

# provone namespace
PROVONE = Namespace(
    "provone", uri="http://purl.dataone.org/provone/2015/01/15/ontology#"
)
PROVONE_WORKFLOW = PROVONE["Workflow"]
PROVONE_DATA = PROVONE["Data"]
PROVONE_EXECUTION = PROVONE["Execution"]

# dcterms namespace
DCTERMS = Namespace("dcterms", uri="http://purl.org/dc/terms/")
DCTERMS_SOURCE = DCTERMS["source"]

# clint namespace
CLINT = Namespace("clint", uri="urn:clint:")


class Provenance(object):
    def __init__(self, output_dir):
        if isinstance(output_dir, pathlib.Path):
            self.output_dir = output_dir
        else:
            self.output_dir = pathlib.Path(output_dir)
        self.doc = None
        self._identifier = None
        self._workflow = None

    @property
    def identifier(self):
        return self._identifier

    def start(self, workflow=False):
        # from climatereconstructionai import __version__ as crai_version
        crai_version = "1.0.2"
        from duck import __version__ as duck_version

        self.doc = prov.ProvDocument()
        self._identifier = uuid.uuid4()
        self._workflow = None
        # Declaring namespaces for various prefixes
        self.doc.add_namespace(CLINT)
        self.doc.add_namespace(PROVONE)
        self.doc.add_namespace(DCTERMS)
        # Define entities
        project_clint = self.doc.agent(
            CLINT["CLINT"],
            {
                prov.PROV_TYPE: PROV_ORGANISATION,
                prov.PROV_LABEL: "CLINT - climate intelligence",
                DCTERMS_SOURCE: "https://climateintelligence.eu/",
            },
        )
        self.sw_duck = self.doc.agent(
            CLINT[f"duck_v{duck_version}"],
            {
                prov.PROV_TYPE: PROV_SOFTWARE_AGENT,
                prov.PROV_LABEL: "Duck",
                DCTERMS_SOURCE: f"https://github.com/climateintelligence/duck/releases/tag/v{duck_version}",
            },
        )
        self.doc.wasAttributedTo(self.sw_duck, project_clint)
        self.sw_crai = self.doc.agent(
            CLINT[f"crai_v{crai_version}"],
            {
                prov.PROV_TYPE: PROV_SOFTWARE_AGENT,
                prov.PROV_LABEL: "CRAI",
                DCTERMS_SOURCE: f"https://github.com/FREVA-CLINT/climatereconstructionAI/releases/tag/v{crai_version}",
            },
        )
        # workflow
        if workflow is True:
            self._workflow = self.doc.entity(
                CLINT[f"workflow_{self.identifier}"], {prov.PROV_TYPE: PROVONE_WORKFLOW}
            )
            orchestrate = self._execution_activity(
                identifier=CLINT[f"orchestrate_{self.identifier}"],
                label="orchestrate",
                attributes={
                    prov.PROV_ATTR_STARTTIME: datetime.now().isoformat(
                        timespec="seconds"
                    )
                },
            )
            self.doc.wasAssociatedWith(
                orchestrate, agent=self.sw_duck, plan=self._workflow
            )

    def stop(self):
        if self._workflow:
            self._execution_activity(
                identifier=CLINT[f"orchestrate_{self.identifier}"],
                attributes={
                    prov.PROV_ATTR_ENDTIME: datetime.now().isoformat(timespec="seconds")
                },
            )

    def add_operator(self, operator, parameters, collection, output):
        attributes = {}
        for param in [
            "time",
            "area",
            "level",
            "dims",
            "freq",
            "dataset_name",
            "variable_name",
        ]:
            if param in parameters:
                value = parameters[param]
                if isinstance(value, list):
                    value = ",".join(value)
                attributes[CLINT[param]] = value
        op = self._execution_activity(
            identifier=CLINT[f"{operator}_{uuid.uuid4()}"],
            label=operator,
            attributes=attributes,
        )
        # input data
        ds_in = os.path.basename(collection[0])
        op_input = self._data_entitiy(identifier=CLINT[ds_in], label=ds_in)
        # operator started by crai
        if self._workflow:
            self.doc.wasAssociatedWith(op, agent=self.sw_crai, plan=self._workflow)
        else:
            self.doc.start(op, starter=self.sw_crai, trigger=self.sw_duck)
        # Generated output file
        for out in output:
            ds_out = os.path.basename(out)
            op_output = self._data_entitiy(identifier=CLINT[ds_out], label=ds_out)
            self.doc.wasDerivedFrom(op_output, op_input, activity=op)

    def _data_entitiy(self, identifier, label=None):
        records = self.doc.get_record(identifier)
        if records:
            entity = records[0]
        else:
            entity = self.doc.entity(identifier)
            entity.add_attributes(
                {
                    prov.PROV_TYPE: PROVONE_DATA,
                    prov.PROV_LABEL: label or "data",
                }
            )
        return entity

    def _execution_activity(self, identifier, label=None, attributes=None):
        records = self.doc.get_record(identifier)
        if records:
            activity = records[0]
        else:
            activity = self.doc.activity(identifier)
            activity.add_attributes(
                {
                    prov.PROV_TYPE: PROVONE_EXECUTION,
                    prov.PROV_LABEL: label or "operator",
                }
            )
        if attributes:
            activity.add_attributes(attributes)
        return activity

    def write_json(self):
        outfile = self.output_dir / "provenance.json"
        self.doc.serialize(outfile.as_posix(), format="json")
        return outfile

    def write_png(self):
        outfile = self.output_dir / "provenance.png"
        figure = prov_to_dot(self.doc)
        figure.write_png(outfile.as_posix())
        return outfile

    def get_provn(self):
        return self.doc.get_provn()

    def dump_json(self):
        return self.doc.serialize(indent=2)

    def json(self):
        return json.loads(self.dump_json())
