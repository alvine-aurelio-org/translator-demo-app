
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

## Architecture
- **Frontend:** HTML/JS (Flask template)
- **Backend:** Python Flask
- **Azure Services:**
  - Azure Storage (blob containers for source and translated docs)
  - Azure Translator (Document Translation API)
  - Managed Identity (for Azure deployment)

## Local Development
1. Clone the repo.
2. Set `AZURE_STORAGE_CONNECTION_STRING` in your environment.
3. Install dependencies:
	```
	pip install -r backend/requirements.txt
	pip install azure-identity azure-storage-blob azure-ai-translation-document
	```
4. Run the Flask app:
	```
	$env:FLASK_APP='backend/app.py'; flask run --host=0.0.0.0 --port=5000
	```
5. Open the app in your browser and upload a document.

## Azure Deployment
1. Deploy backend to Azure App Service, VM, or container.
2. Enable managed identity for the resource.
3. Assign "Storage Blob Data Contributor" role to the managed identity for your storage account.
4. Remove the connection string from environment variables.
5. The app will use managed identity for authentication.

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
