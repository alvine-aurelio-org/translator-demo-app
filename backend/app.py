import os
from flask import Flask, request, jsonify, render_template, url_for
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from azure.ai.translation.document import DocumentTranslationClient, DocumentTranslationInput, TranslationTarget
import time

app = Flask(__name__)

STORAGE_ACCOUNT_NAME = "translatorstoragelxqk42"
SOURCE_CONTAINER = "source-docs"
TARGET_CONTAINER = "translated-docs"
TRANSLATOR_ENDPOINT = "https://tl-001.cognitiveservices.azure.com/"
TRANSLATOR_REGION = "eastus"

@app.route('/')
def homepage():
    return render_template('index.html')

import os
TRANSLATOR_KEY = os.getenv("AZURE_TRANSLATOR_KEY", "YOUR_TRANSLATOR_KEY")

@app.route('/api/translate', methods=['POST'])
def translate_file():
    file = request.files.get('file')
    lang = request.form.get('lang')
    if not file or not lang:
        return jsonify({'error': 'Missing file or lang'}), 400


    import logging
    ext = os.path.splitext(file.filename)[1].lower()
    import logging
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    use_managed_identity = not conn_str
    logging.warning(f"AZURE_STORAGE_CONNECTION_STRING at runtime: {conn_str}")
    try:
        if use_managed_identity:
            logging.warning("Using DefaultAzureCredential for BlobServiceClient (Managed Identity)")
            credential = DefaultAzureCredential()
            blob_service_client = BlobServiceClient(account_url=f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/", credential=credential)
        else:
            logging.warning(f"Using connection string for BlobServiceClient: {conn_str[:40]}...")
            blob_service_client = BlobServiceClient.from_connection_string(conn_str)
            credential = None
        source_blob_client = blob_service_client.get_blob_client(container=SOURCE_CONTAINER, blob=file.filename)
        file.stream.seek(0)
        source_blob_client.upload_blob(file.stream.read(), overwrite=True)
    except Exception as e:
        logging.error(f"Blob upload error: {e}")
        error_code = getattr(e, 'error_code', None)
        error_message = str(e)
        # Try to extract error code from the exception content if available
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            import re
            response_text = e.response.text
            if callable(response_text):
                response_text = response_text()
            if isinstance(response_text, (str, bytes)):
                match = re.search(r'<Code>(.*?)</Code>', response_text)
                if match:
                    error_code = match.group(1)
        return jsonify({'error': error_message}), 500
    source_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{SOURCE_CONTAINER}/{file.filename}"
    target_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{TARGET_CONTAINER}/"

    # Start Document Translation job
    if use_managed_identity:
        doc_client = DocumentTranslationClient(endpoint=TRANSLATOR_ENDPOINT, credential=credential)
    else:
        doc_client = DocumentTranslationClient(endpoint=TRANSLATOR_ENDPOINT, credential=DefaultAzureCredential())
    inputs = [
        DocumentTranslationInput(
            source_url=source_url,
            targets=[TranslationTarget(target_url=target_url, language_code=lang)]
        )
    ]
    poller = doc_client.begin_translation(inputs)
    # Poll for completion
    while not poller.done():
        time.sleep(2)
    result = poller.result()
    logging.warning("Document Translation Results:")
    # Find translated file name
    translated_file_name = None
    for doc in result:
        logging.warning(f"Status: {doc.status}, Source: {doc.source_document_url}, Translated: {getattr(doc, 'translated_document_url', None)}, Error: {getattr(doc, 'error', None)}")
        if doc.status == "Succeeded":
            translated_file_name = os.path.basename(doc.translated_document_url)
            logging.warning(f"Translated file found: {translated_file_name}")
            break
    if not translated_file_name:
        error_details = [f"Status: {doc.status}, Error: {getattr(doc, 'error', None)}" for doc in result]
        logging.error(f"Translation failed. Details: {error_details}")
        return jsonify({'error': 'Translation failed.', 'details': error_details}), 500
    translated_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{TARGET_CONTAINER}/{translated_file_name}"

    is_image = ext in ['.jpg', '.jpeg', '.png']
    if is_image:
        return jsonify({'error': 'Unsupported file type. Only DOCX, PDF, TXT, XLSX, PPTX, and other Office documents are supported for translation. Images are not supported.'}), 400

    return jsonify({
        'result': 'Translation complete.',
        'translatedFileUrl': translated_url,
        'isImage': is_image
    })

if __name__ == '__main__':
    app.run(debug=True)
