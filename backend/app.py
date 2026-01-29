import logging
import os
import time
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from azure.storage.blob import BlobServiceClient
import requests

log_path = os.path.join(os.path.dirname(__file__), 'app.log')
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s %(levelname)s %(name)s %(message)s',
	handlers=[
		logging.FileHandler(log_path),
		logging.StreamHandler()
	]
)
logger = logging.getLogger(__name__)
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
app = Flask(__name__)

@app.route('/')
def index():
	return render_template('index.html')


@app.route('/api/upload-and-translate', methods=['POST'])
def upload_and_translate():
    if 'file' not in request.files:
        logger.error('No file part in request')
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        logger.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    # Accept extra fields for future translation
    source_lang = request.form.get('sourceLang', 'auto')
    target_lang = request.form.get('targetLang', '')

    # Azure Blob Storage config
    conn_str = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')
    target_container = os.environ.get('AZURE_TARGET_CONTAINER', 'translated-docs')
    logger.info(f"[CONFIG] Using target_container: {target_container}")
    try:
        blob_service_client = BlobServiceClient.from_connection_string(conn_str)
        import os as _os
        name, ext = _os.path.splitext(file.filename)
        temp_container = os.environ.get('AZURE_SOURCE_CONTAINER', 'source-docs')
        translated_filename = f"{name}-{target_lang}{ext}"
        # Check if translated file already exists in the target container
        tgt_blob_client = blob_service_client.get_blob_client(container=target_container, blob=translated_filename)
        if tgt_blob_client.exists():
            logger.info(f'[TRANSLATE] Output file {translated_filename} already exists in {target_container}')
            target_sas = os.environ.get('TARGET_SAS_TOKEN')
            tgt_url = f'https://ussampleeastus2storev2.blob.core.windows.net/{target_container}/{translated_filename}?{target_sas}'
            response_json = {
                'result': 'Translation already completed',
                'targetUrl': tgt_url,
                'status': 'OutputFileExists'
            }
            logger.info(f'[TRANSLATE] JSON response to client: {response_json}')
            return jsonify(response_json), 200

        # Upload source file to temp/source container
        source_sas = os.environ.get('SOURCE_SAS_TOKEN')
        src_url = f'https://ussampleeastus2storev2.blob.core.windows.net/{temp_container}/{file.filename}?{source_sas}'
        src_blob_client = blob_service_client.get_blob_client(container=temp_container, blob=file.filename)
        file.stream.seek(0)
        src_blob_client.upload_blob(file.stream.read(), overwrite=True)
        logger.info(f'File {file.filename} uploaded to {temp_container} using SAS')
        # Prepare translation
        target_sas = os.environ.get('TARGET_SAS_TOKEN')
        tgt_url = f'https://ussampleeastus2storev2.blob.core.windows.net/{target_container}/{translated_filename}?{target_sas}'
        logger.info(f'[SAS] Target blob SAS URL: {tgt_url}')
        logger.info(f'[SAS] Target blob SAS string: {target_sas}')
        logger.info(f'[SAS] Target blob name used for SAS: {translated_filename}')
        endpoint = os.environ.get('AZURE_TRANSLATOR_ENDPOINT')
        headers = {
            'Ocp-Apim-Subscription-Key': os.environ.get('AZURE_TRANSLATOR_KEY'),
            'Ocp-Apim-Subscription-Region': os.environ.get('AZURE_TRANSLATOR_REGION'),
            'Content-Type': 'application/json'
        }
        # Build the source object, omitting 'language' if 'auto' is selected
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
        logger.info(f'[TRANSLATE] Sending translation request body: {body}')
        resp = requests.post(endpoint, headers=headers, json=body)
        logger.info(f'[TRANSLATE] Translation API response: {resp.status_code} {resp.text}')
        if resp.status_code not in (200, 202):
            logger.error(f'Translation API error: {resp.status_code} {resp.text}')
            return jsonify({'error': 'Translation API error', 'details': resp.text}), 500
        op_url = resp.headers.get('operation-location') or resp.json().get('operationUrl')
        logger.info(f'Translation started. Operation URL: {op_url}')
        response_json = {
            'result': 'Translation job submitted',
            'operationUrl': op_url,
            'targetUrl': tgt_url,
            'status': 'Submitted'
        }
        logger.info(f'[TRANSLATE] JSON response to client: {response_json}')
        return jsonify(response_json), 200
    except Exception as e:
        logger.exception(f'Azure Blob upload or translation failed: {e}')
        return jsonify({'error': 'Azure Blob upload or translation failed', 'details': str(e)}), 500


# Endpoint to display the error log in the browser
@app.route('/logs')
def logs():
	try:
		with open(log_path, 'r') as f:
			log_content = f.read()
		return f'<pre style="white-space: pre-wrap;">{log_content}</pre>'
	except Exception as e:
		return f'Could not read log file: {e}', 500

if __name__ == '__main__':
	app.run(debug=True)
