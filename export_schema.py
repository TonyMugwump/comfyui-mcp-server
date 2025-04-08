from fastapi.openapi.utils import get_openapi
import json
from openapi_server import app

with open("openapi_schema.json", "w") as f:
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    json.dump(schema, f, indent=2)