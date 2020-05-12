from tableschema import Table
from tabulator.loaders.aws import AWSLoader
from datapackage.exceptions import CastError
import re
import openpyxl
import os
import boto3
from tempfile import TemporaryFile
import shutil

from .constants import BUCKET, FILES_PREFIX, BCODMO_METADATA_KEY


def clean_resource_name(name):
    name = name.casefold()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^-a-z0-9._/]", "", name)
    return name


def infer_schema(submission_title, filename, options):
    print("OPTIONS", options)
    # TODO if xlsx/xls, infer a schema for each sheet
    object_key = f"{submission_title}/{FILES_PREFIX}/{filename}"
    object_name = f"s3://{BUCKET}/{object_key}"
    lat_col = options.pop("latitudeCol", None)
    lon_col = options.pop("longitudeCol", None)

    if filename.endswith(".xls") or filename.endswith(".xlsx"):
        if "sheet" in options:
            resources = [
                {
                    "object_name": object_name,
                    "options": options,
                    "resource_name": clean_resource_name(options["sheet"]),
                }
            ]
        else:
            loader = AWSLoader()
            b = loader.load(object_name, mode="b")

            # Create copy for remote source
            # For remote stream we need local copy (will be deleted on close by Python)
            new_bytes = TemporaryFile()
            shutil.copyfileobj(b, new_bytes)
            b.close()
            b = new_bytes
            b.seek(0)
            wb = openpyxl.load_workbook(b)
            # TODO decide if this is too slow for larger excel sheets

            resources = []
            for sheet_name in wb.sheetnames:
                resources.append(
                    {
                        "object_name": object_name,
                        "options": {"sheet": sheet_name},
                        "resource_name": clean_resource_name(sheet_name),
                    }
                )

    else:
        resources = [
            {
                "object_name": object_name,
                "options": options,
                "resource_name": clean_resource_name(filename),
            }
        ]

    res = []
    for resource in resources:
        table = Table(resource["object_name"], **options)
        missing_values = options.get("missingValues", None)
        if missing_values:
            table.infer(confidence=1, missing_values=missing_values)
        else:
            table.infer(confidence=1)

        # Update the schema to desired human input for testing?
        # table.schema.update_field('col1', { "name": "col1", "type": "number", "format": "default" })
        # table.schema.commit(strict=True)

        schema = table.schema.descriptor

        if missing_values:
            schema.update({"missingValues": missing_values})
        if "temporalFields" in options:
            temporalFieldsDict = dict(
                [(tf.get("field"), tf) for tf in options.get("temporalFields")]
            )
            for f in schema.get("fields", []):
                name = f.get("name")
                if name and name in temporalFieldsDict:
                    tf = temporalFieldsDict[name]
                    f.update(
                        {
                            "type": tf.get("type", "string"),
                            "format": tf.get("format", ""),
                        }
                    )

        # Create BCODMO_METADATA_KEY and add sample_rows
        sample_rows = table.read(cast=False, limit=5)

        schema[BCODMO_METADATA_KEY] = {}
        for i in range(len(schema["fields"])):
            field = schema["fields"][i]
            field[BCODMO_METADATA_KEY] = {
                "sample_rows": [r[i] for r in sample_rows],
            }

        # Add the options to the resource schema so they can be persisted later
        if "headers" in options:
            schema[BCODMO_METADATA_KEY]["headers"] = options["headers"]
        for field in schema["fields"]:
            if lat_col and field["name"] == lat_col:
                field[BCODMO_METADATA_KEY]["definition"] = "latitude"
            if lon_col and field["name"] == lon_col:
                field[BCODMO_METADATA_KEY]["definition"] = "longitude"

        resObj = {
            "resource_name": resource["resource_name"],
            "schema": schema,
            "error": None,
        }
        if "sheet" in options:
            resObj["sheet"] = options["sheet"]
        res.append(resObj)
    return res
