
import os
from dataclasses import dataclass

@dataclass
class OntologySyncConfig:
    mongo_url: str = os.getenv("MONGO_CLIENT_URL", "mongodb://localhost:27017/?replicaSet=rs0")
    mongo_db: str = os.getenv("MONGO_DATABASE_NAME", "test")
    fuseki_base: str = os.getenv("FUSEKI_BASE_URL", "http://localhost:3030")
    fuseki_user: str = os.getenv("FUSEKI_USER", "admin")
    fuseki_password: str = os.getenv("FUSEKI_PASSWORD", "admin")
    base_uri_prefix: str = os.getenv("ONTOLOGY_BASE_URI", "http://example.org/")
    # Si True, el watcher escucha toda la DB; si False, solo colecciones listadas en `models`
    watch_whole_db: bool = True