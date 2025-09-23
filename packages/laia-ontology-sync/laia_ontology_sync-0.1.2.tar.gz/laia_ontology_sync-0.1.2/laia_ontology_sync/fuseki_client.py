
from typing import Optional
import requests
from rdflib import Graph
from .logger import _logger

def _dataset_root(base: str, dataset: str) -> str:
    return f"{base.rstrip('/')}/{dataset}"

def _update_url(base: str, dataset: str) -> str:
    return f"{_dataset_root(base, dataset)}/update"

def _admin_datasets_url(base: str) -> str:
    return f"{base.rstrip('/')}/$/datasets"

def dataset_exists(dataset: str, fuseki_base: str, user: str, pwd: str) -> bool:
    resp = requests.get(_dataset_root(fuseki_base, dataset), auth=(user, pwd))
    return resp.status_code == 200

def ensure_dataset_exists(dataset: str, fuseki_base: str, user: str, pwd: str) -> None:
    if dataset_exists(dataset, fuseki_base, user, pwd):
        return
    resp = requests.post(
        _admin_datasets_url(fuseki_base),
        data={"dbName": dataset, "dbType": "tdb2"},
        auth=(user, pwd),
    )
    if resp.status_code not in (200, 201):
        raise RuntimeError(f"Fuseki dataset create failed [{resp.status_code}]: {resp.text}")

def sparql_update(dataset: str, update_query: str, fuseki_base: str, user: str, pwd: str) -> None:
    url = _update_url(fuseki_base, dataset)
    resp = requests.post(
        url,
        data=update_query.encode("utf-8"),
        headers={"Content-Type": "application/sparql-update"},
        auth=(user, pwd),
    )
    if not (200 <= resp.status_code < 300):
        _logger.error(f"Fuseki SPARQL update failed [{resp.status_code}]: {resp.text}")
        raise RuntimeError(f"Fuseki SPARQL update failed [{resp.status_code}]: {resp.text}")
    else:
        _logger.info(f"Fuseki SPARQL success [{resp.status_code}]")

def upload_graph(graph: Graph, dataset: str, fuseki_base: str, user: str, pwd: str) -> None:
    triples = graph.serialize(format="nt")
    update = f"INSERT DATA {{ {triples} }}"
    sparql_update(dataset, update, fuseki_base, user, pwd)

def delete_resource_triples(resource_uri: str, dataset: str, fuseki_base: str, user: str, pwd: str) -> None:
    update = f"DELETE WHERE {{ <{resource_uri}> ?p ?o }}"
    sparql_update(dataset, update, fuseki_base, user, pwd)
