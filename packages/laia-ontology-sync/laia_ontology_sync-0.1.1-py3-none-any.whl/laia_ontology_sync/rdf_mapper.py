
from typing import Any, Dict
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import XSD
from bson import ObjectId

def to_literal(value: Any):
    if isinstance(value, bool):
        return Literal(value, datatype=XSD.boolean)
    if isinstance(value, int):
        return Literal(value, datatype=XSD.integer)
    if isinstance(value, float):
        return Literal(value, datatype=XSD.decimal)
    if isinstance(value, ObjectId):
        return Literal(str(value))
    return Literal(str(value))

def build_resource_uri(base_uri_prefix: str, collection_name: str, _id: Any) -> str:
    return f"{base_uri_prefix.rstrip('/')}/{collection_name}/{_id}"

def doc_to_rdf(doc: Dict[str, Any], context: Dict[str, str], base_uri: str) -> Graph:
    """
    doc: documento Mongo ya con _id
    context: mapeo {"campo": "https://schema.org/..."}
    base_uri: p.e. "http://example.org/theme/" (debe terminar con '/')
    """
    g = Graph()
    subject = URIRef(f"{base_uri}{doc['_id']}")

    for field, iri in context.items():
        if field not in doc:
            continue
        predicate = URIRef(iri)
        value = doc[field]

        if isinstance(value, list):
            for v in value:
                g.add((subject, predicate, to_literal(v)))
        else:
            g.add((subject, predicate, to_literal(value)))

    return g
