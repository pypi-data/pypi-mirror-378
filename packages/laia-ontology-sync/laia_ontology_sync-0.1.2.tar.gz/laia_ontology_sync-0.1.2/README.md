# laia-ontology-sync

Librería en Python para **sincronizar MongoDB con Apache Jena Fuseki** utilizando **RDF y SPARQL**.

Permite escuchar cambios en MongoDB (inserciones, actualizaciones y eliminaciones) y mantener un dataset en Fuseki sincronizado en tiempo real, generando triples RDF a partir de documentos Mongo.

---

## ✨ Características

- 🔄 Sincronización automática entre MongoDB y Fuseki.
- 🗄️ Escucha en tiempo real (`change streams`) de MongoDB.
- 🧩 Conversión de documentos Mongo a grafos RDF con [rdflib](https://rdflib.readthedocs.io/).
- 📝 Inserción, actualización y eliminación de triples en Fuseki.
- 🔧 Funciones utilitarias para construir URIs y literales RDF.
- 🛠️ Logging con formato de colores para debug.

---

## 📦 Instalación

```bash
pip install laia-ontology-sync
```

---

## 🚀 Uso

```python
from laia_ontology_sync.sync import start_background_watcher
from my_models import Theme

models = {"theme": Theme}

thread = start_background_watcher(
    mongo_url="mongodb://localhost:27017",
    db_name="mi_basedatos",
    models=models,
    fuseki_base="http://localhost:3030",
    user="admin",
    pwd="admin",
    base_uri_prefix="http://example.org/"
)
```

---

## ⚙️ Requisitos

- Python 3.9 o superior

- MongoDB >= 4.0 (con soporte para change streams)

- Apache Jena Fuseki