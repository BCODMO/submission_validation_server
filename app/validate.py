import os
import traceback
from goodtables import validate
import requests
from .constants import BCODMO_METADATA_KEY, BUCKET
from .checks import latitude, longitude, header_name_invalid
import logging

ROW_LIMIT = 200000

VALIDATION_RESULT_URL = os.environ.get("SUBMISSION_VALIDATION_RESULT_URL")
SUBMISSION_API_KEY = os.environ.get("SUBMISSION_API_KEY")


def validate_resource(resource):
    try:
        print(f"Starting the validation of a resource")
        object_key = resource[BCODMO_METADATA_KEY]["objectKey"]
        object_name = f"s3://{BUCKET}/{object_key}"
        options = {}
        checks = [
            "structure",
            "schema",
            # Custom checks
            {"header-name-invalid": {}},
        ]
        schema = None
        if "sheet" in resource:
            options["sheet"] = resource["sheet"]
        if "schema" in resource:
            schema = resource["schema"]
            if "headers" in resource["schema"][BCODMO_METADATA_KEY]:
                options["headers"] = resource["schema"][BCODMO_METADATA_KEY]["headers"]
            for field in resource["schema"]["fields"]:
                definition = field[BCODMO_METADATA_KEY].get("definition", None)
                if definition == "latitude":
                    checks.append(
                        {"latitude-bounds": {"constraint": field["name"],},}
                    )
                if definition == "longitude":
                    checks.append(
                        {"longitude-bounds": {"constraint": field["name"],},}
                    )
        if not schema:
            report = validate(
                object_name,
                infer_schema=True,
                checks=checks,
                row_limit=ROW_LIMIT,
                **options,
            )
        else:
            report = validate(
                object_name,
                schema=schema,
                checks=checks,
                row_limit=ROW_LIMIT,
                **options,
            )
        status = "validate-success"
        if not report["valid"]:
            status = "validate-error"
    except Exception as e:
        tb = traceback.format_exc()
        logging.error(f"Error while validating {str(e)}")
        logging.error(tb)

        status = "validate-error"
        report = {
            "valid": False,
            "tables": [],
            "warnings": [],
            "error": str(e),
        }
    submissionTitle = resource.get(BCODMO_METADATA_KEY, {}).get("submissionTitle", None)
    if not submissionTitle:
        raise Exception(f"No submission title passed to this task: {resource}")
    warnings = report["warnings"]
    new_warnings = []
    for warning in warnings:
        if warning.endswith(f"has reached {ROW_LIMIT} row(s) limit"):
            new_warning = f"Validation was limited to {ROW_LIMIT} rows"
        else:
            new_warning = warning
        new_warnings.append(new_warning)
    report["warnings"] = new_warnings

    # Make sure the error is not an exception type
    for table in report.get("tables", []):
        for error in table.get("errors", []):
            md = error.get("message-data")
            if md and type(md) != str:
                error["message-data"] = str(md)
    data = {
        "submissionTitle": submissionTitle,
        "resourceName": resource.get("name", ""),
        "status": status,
        "report": report,
        # The API key in order to authenticate with the other server
        "submissionApiKey": SUBMISSION_API_KEY,
    }
    r = requests.post(url=VALIDATION_RESULT_URL, json=data,)
