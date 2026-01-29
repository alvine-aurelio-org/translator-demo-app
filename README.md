
# Azure Translator Document Demo

## Overview
This app demonstrates secure document translation using Azure Translator and Azure Storage. It supports DOCX, PDF, TXT, and other Office formats, with a modern frontend and Flask backend. Authentication uses connection string locally and managed identity in Azure.

## Features
- Drag-and-drop document upload
- Language selection for translation
- Progress bar and upload status
- Preview and download translated files
- Secure Azure Storage integration
- Azure Translator Document API
- Detailed error handling and logging


## Azure Services Architecture

This solution uses the following Azure services:

- **Azure Storage (Blob Storage):**
	- Stores uploaded source documents and translated files securely in separate containers (e.g., `source-docs`, `translated-docs`).
	- Accessed via SAS tokens for secure, time-limited access.

- **Azure AI Translator (Document Translation API):**
	- Performs asynchronous, large-scale document translation between supported languages and formats.
	- Accessed securely from the backend using a key (local) or managed identity (Azure).

- **Azure Managed Identity:**
	- Provides secure, passwordless authentication for the backend when deployed to Azure.
	- Used to access Azure Storage and Translator without storing secrets in code or environment variables.

- **Azure Role-Based Access Control (RBAC):**
	- Controls access to storage resources by assigning the appropriate roles (e.g., Storage Blob Data Contributor) to the managed identity.

The backend (Flask) acts as a secure bridge between the frontend and Azure services, handling authentication, SAS generation, and translation orchestration.

## Prerequisites
- Python 3.8+
- pip (Python package manager)
- Azure account with:
  - Azure Storage Account (Blob Storage)
  - Azure AI Translator resource (Document Translation API)

## Local Development
1. **Clone the repo:**
	```sh
	git clone <your-fork-or-this-repo-url>
	cd translator-demo
	```
2. **Set up environment variables:**
	- Create a file named `.env` in the `backend/` directory with your own Azure values. Example:
	  ```ini
	  # backend/.env (DO NOT COMMIT REAL SECRETS)
	  SOURCE_SAS_TOKEN=your_source_container_sas_token
	  TARGET_SAS_TOKEN=your_target_container_sas_token
	  AZURE_STORAGE_ACCOUNT_NAME=your_storage_account_name
	  AZURE_STORAGE_ACCOUNT_KEY=your_storage_account_key
	  AZURE_STORAGE_CONNECTION_STRING=your_storage_connection_string
	  AZURE_SOURCE_CONTAINER=source-docs
	  AZURE_TARGET_CONTAINER=translated-docs
	  AZURE_TRANSLATOR_KEY=your_translator_key
	  AZURE_TRANSLATOR_REGION=your_translator_region
	  AZURE_TRANSLATOR_ENDPOINT=https://<your-translator-resource>.cognitiveservices.azure.com/translator/document/batches?api-version=2025-12-01-preview
	  ```
	- **How to get these values:**
	  - SAS tokens: Azure Portal > Storage Account > Containers > Shared Access Signature.
	  - Storage connection string: Azure Portal > Storage Account > Access Keys.
	  - Translator key/region/endpoint: Azure Portal > AI Translator resource > Keys & Endpoint.
	- **To update values:** Edit `backend/.env` and restart the app.

3. **Install dependencies:**
	```sh
	pip install -r backend/requirements.txt
	pip install azure-identity azure-storage-blob azure-ai-translation-document python-dotenv
	```
4. **Run the Flask app:**
	```sh
	python backend/app.py
	```
	Or, using Flask CLI:
	```sh
	cd backend
	$env:FLASK_APP='app.py'; flask run --host=0.0.0.0 --port=5000
	```
5. **Open the app:**
	Go to [http://localhost:5000](http://localhost:5000) in your browser.

## Security Notes
- Never expose Azure credentials in client-side code.
- Use managed identity for production deployments.
- Restrict storage account access with RBAC.

## File Structure
```
translator-demo/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   └── templates/
│       └── index.html
├── translator-demo.html
└── README.md
```

## License
MIT

---
Built for Azure Translator and secure document workflows.
