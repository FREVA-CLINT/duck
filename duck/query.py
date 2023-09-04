from duck.db import GraphDB
import pandas as pd


def query():
    query_str = """
        SELECT ?process ?dataset ?variable ?startTime ?endTime ?input ?output ?min ?max ?mean ?stddev ?info
        WHERE {
            ?exec rdf:type provone:Execution ;
                rdfs:label ?process ;
                clint:dataset_name ?dataset ;
                clint:variable_name ?variable ;
                prov:startedAtTime ?startTime ;
                prov:endedAtTime ?endTime ;
                clint:min ?min ;
                clint:max ?max ;
                clint:mean ?mean ;
                clint:stddev ?stddev ;
                clint:info ?info .

            ?input rdf:type prov:Entity .
        
            ?output rdf:type prov:Entity ;
                prov:qualifiedDerivation [ prov:entity ?input; prov:hadActivity ?exec ] .
    }
    """
    graph_db = GraphDB()
    results = graph_db.query(query_str)

    data = []
    for row in results:
        # print(row)
        process = row.process.split("/")[-1]
        dataset = row.dataset.value
        variable = row.variable.value
        start_time = row.startTime.value
        end_time = row.endTime.value
        input = row.input.split("/")[-1]
        input = input.split("urn:clint:")[-1]
        output = row.output.split("/")[-1]
        output = output.split("urn:clint:")[-1]
        min = row.min.value
        max = row.max.value
        mean = row.mean.value
        stddev = row.stddev.value
        info = row.info.value
        data.append({
            "Process": process, 
            "Dataset": dataset,
            "Variable": variable, 
            "Start Time": start_time, 
            "End Time": end_time,
            "Input": input,
            "Output": output,
            "Min": min,
            "Max": max,
            "Mean": mean,
            "StdDev": stddev,
            "Info": info,
        })
    df = pd.DataFrame(data)
    return df
