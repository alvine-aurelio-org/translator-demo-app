
import logging
import azure.functions as func
import json
import os
from azure.storage.blob import BlobServiceClient
import requests

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    if req.method != 'POST':
        return func.HttpResponse(
            json.dumps({'error': 'Only POST allowed'}),
            status_code=405,
            mimetype='application/json'
        )

    try:
        # Parse multipart form data
        form = req.form
        files = req.files
        file = files.get('file') if files else None
        if not file:
            return func.HttpResponse(json.dumps({'error': 'No file uploaded'}), status_code=400, mimetype='application/json')
        source_lang = form.get('sourceLang', 'auto')
        target_lang = form.get('targetLang', '')

        # Azure Blob Storage config
        conn_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
        target_container = os.environ.get('AZURE_TARGET_CONTAINER', 'translated-docs')
        temp_container = os.environ.get('AZURE_SOURCE_CONTAINER', 'source-docs')
        name, ext = os.path.splitext(file.filename)
        translated_filename = f"{name}-{target_lang}{ext}"

        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        tgt_blob_client = blob_service_client.get_blob_client(container=target_container, blob=translated_filename)
        if tgt_blob_client.exists():
            target_sas = os.environ.get('TARGET_SAS_TOKEN')
            tgt_url = f'https://ussampleeastus2storev2.blob.core.windows.net/{target_container}/{translated_filename}?{target_sas}'
            response_json = {
                'result': 'Translation already completed',
                'targetUrl': tgt_url,
                'status': 'OutputFileExists'
            }
            return func.HttpResponse(json.dumps(response_json), status_code=200, mimetype='application/json')

        # Upload source file to temp/source container
        source_sas = os.environ.get('SOURCE_SAS_TOKEN')
        src_url = f'https://ussampleeastus2storev2.blob.core.windows.net/{temp_container}/{file.filename}?{source_sas}'
        src_blob_client = blob_service_client.get_blob_client(container=temp_container, blob=file.filename)
        file.stream.seek(0)
        src_blob_client.upload_blob(file.stream.read(), overwrite=True)

        # Prepare translation
        target_sas = os.environ.get('TARGET_SAS_TOKEN')
        tgt_url = f'https://ussampleeastus2storev2.blob.core.windows.net/{target_container}/{translated_filename}?{target_sas}'
        endpoint = os.environ.get('AZURE_TRANSLATOR_ENDPOINT')
        headers = {
            'Ocp-Apim-Subscription-Key': os.environ.get('AZURE_TRANSLATOR_KEY'),
            'Ocp-Apim-Subscription-Region': os.environ.get('AZURE_TRANSLATOR_REGION'),
            'Content-Type': 'application/json'
        }
        source_obj = {
            "sourceUrl": src_url
        }
        if source_lang and source_lang.lower() != "auto":
            source_obj["language"] = source_lang
        body = {
            "inputs": [
                {
                    "storageType": "File",
                    "source": source_obj,
                    "targets": [
                        {
                            "targetUrl": tgt_url,
                            "language": target_lang
                        }
                    ]
                }
            ]
        }
        logging.info(f"Submitting translation job to {endpoint}")
        logging.info(f"Request headers: {json.dumps(headers)}")
        logging.info(f"Request body: {json.dumps(body)}")
        resp = requests.post(endpoint, headers=headers, json=body)
        logging.info(f"Translator API response: {resp.status_code} {resp.text}")
        if resp.status_code not in (200, 202):
            return func.HttpResponse(json.dumps({'error': 'Translation API error', 'details': resp.text}), status_code=500, mimetype='application/json')
        op_url = resp.headers.get('operation-location') or resp.json().get('operationUrl')
        response_json = {
            'result': 'Translation job submitted',
            'operationUrl': op_url,
            'targetUrl': tgt_url,
            'status': 'Submitted'
        }
        return func.HttpResponse(json.dumps(response_json), status_code=200, mimetype='application/json')
    except Exception as e:
        logging.exception(f'Azure Blob upload or translation failed: {e}')
        return func.HttpResponse(json.dumps({'error': 'Azure Blob upload or translation failed', 'details': str(e)}), status_code=500, mimetype='application/json')
