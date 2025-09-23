
from typing import Dict, Type, Optional
from pymongo import MongoClient
from bson import ObjectId
import threading
from .logger import _logger

from .rdf_mapper import doc_to_rdf, build_resource_uri
from .fuseki_client import (
    ensure_dataset_exists,
    upload_graph,
    delete_resource_triples,
)

def _get_model_context(model: Type) -> Dict[str, str]:
    try:
        extra = getattr(model, "model_config", {}).get("json_schema_extra", {}) 
        return extra.get("@context", {}) or {}
    except Exception:
        return {}

def watch_mongo_and_sync(
    mongo_url: str,
    db_name: str,
    models: Dict[str, Type],  # {"theme": Theme, ...} keys = nombre colección
    fuseki_base: str = "http://localhost:3030",
    user: str = "admin",
    pwd: str = "admin",
    base_uri_prefix: str = "http://example.org/",
    watch_whole_db: bool = True,
):
    """
    Inicia el loop (bloqueante) de escucha y sincronización.
    - models: diccionario colección -> clase Pydantic
    - watch_whole_db: si True usa db.watch(); si False, un watch por colección listada en models
    """
    client = MongoClient(mongo_url)
    db = client[db_name]

    def process_change(change: dict):
        ns = change.get("ns", {})
        coll = ns.get("coll")
        op = change.get("operationType")

        if not coll:
            return

        model = models.get(coll)
        if not model:
            return

        dataset = coll.lower()
        ensure_dataset_exists(dataset, fuseki_base, user, pwd)

        context = _get_model_context(model)
        base_uri = f"{base_uri_prefix.rstrip('/')}/{coll}/"  # .../theme/

        _logger.info(f"Recieved petition: {op}")

        if op == "insert":
            doc = change["fullDocument"]
            _logger.info(f"Inserting doc: {doc}")
            graph = doc_to_rdf(doc, context, base_uri)
            upload_graph(graph, dataset, fuseki_base, user, pwd)

        elif op == "update":
            _id = change["documentKey"]["_id"]
            _logger.info(f"Updating doc with id: {_id}")
            resource_uri = build_resource_uri(base_uri_prefix, coll, _id)
            delete_resource_triples(resource_uri, dataset, fuseki_base, user, pwd)
            doc = change.get("fullDocument")
            if doc:
                graph = doc_to_rdf(doc, context, base_uri)
                upload_graph(graph, dataset, fuseki_base, user, pwd)

        elif op == "delete":
            _id = change["documentKey"]["_id"]
            _logger.info(f"Deleting doc with id: {_id}")
            resource_uri = build_resource_uri(base_uri_prefix, coll, _id)
            delete_resource_triples(resource_uri, dataset, fuseki_base, user, pwd)

    if watch_whole_db:
        with db.watch(full_document="updateLookup") as stream:
            for change in stream:
                process_change(change)
    else:
        watches = []
        for coll_name in models.keys():
            coll = db[coll_name]
            watches.append(coll.watch(full_document="updateLookup"))
        try:
            while True:
                for stream in watches:
                    try:
                        change = stream.try_next()
                        if change is not None:
                            process_change(change)
                    except StopIteration:
                        pass
        finally:
            for s in watches:
                s.close()

def start_background_watcher(
    mongo_url: str,
    db_name: str,
    models: Dict[str, Type],
    fuseki_base: str = "http://localhost:3030",
    user: str = "admin",
    pwd: str = "admin",
    base_uri_prefix: str = "http://example.org/",
    watch_whole_db: bool = True,
) -> threading.Thread:
    """
    Lanza watch_mongo_and_sync en un thread daemon y lo devuelve.
    """
    _logger.info('Starting background watcher mongo')
    args = (mongo_url, db_name, models, fuseki_base, user, pwd, base_uri_prefix, watch_whole_db)
    t = threading.Thread(target=watch_mongo_and_sync, args=args, daemon=True)
    t.start()
    return t
