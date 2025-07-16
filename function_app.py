import azure.functions as func
import logging
import json
import os
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="get_case_comments", methods=["POST"])
def get_case_comments(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Function get_case_comments triggered.")

    try:
        data = req.get_json()
        case_id = data.get("case_id")
        if not case_id:
            return func.HttpResponse("Missing 'case_id'", status_code=400)

        # Get Salesforce credentials from environment
        ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
        INSTANCE_URL = os.environ.get("INSTANCE_URL")

        if not ACCESS_TOKEN or not INSTANCE_URL:
            return func.HttpResponse("Missing Salesforce credentials", status_code=500)

        query = f"SELECT CommentBody FROM CaseComment WHERE ParentId = '{case_id}'"
        url = f"{INSTANCE_URL}/services/data/v58.0/query?q={query}"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        records = response.json().get("records", [])
        comments = [r["CommentBody"] for r in records]

        return func.HttpResponse(json.dumps({"comments": comments}), mimetype="application/json")

    except Exception as e:
        logging.error(str(e))
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)
