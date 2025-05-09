import os, logging, json
import azure.functions as func
from azure.cosmos import CosmosClient, PartitionKey

app = func.FunctionApp()          # already present

# --- Cosmos setup ---
COSMOS_URL = os.environ["COSMOS_URL"]
COSMOS_KEY = os.environ["COSMOS_KEY"]

client = CosmosClient(COSMOS_URL, COSMOS_KEY)
db  = client.create_database_if_not_exists("alertdb")
ctr = db.create_container_if_not_exists("logs", PartitionKey(path="/source"))
# ---------------------

@app.function_name(name="ingest_logs")
@app.route(route="ingest_logs", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def ingest_logs(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Ingest request received")
    try:
        body = req.get_json()
        ctr.upsert_item(body)          # store log entry
        return func.HttpResponse("OK", status_code=200)
    except Exception as e:
        logging.exception(e)
        return func.HttpResponse("Bad request", status_code=400)
