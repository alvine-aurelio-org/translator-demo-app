

# Azure Translator Document Demo (Azure Deployment)

## Overview
This branch is optimized for direct deployment to Azure using Azure Static Web Apps (frontend) and Azure Functions (backend). It demonstrates secure document translation using Azure AI Translator and Azure Blob Storage.

---

## Prerequisites
- Azure Subscription
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) (az)
- [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local) (func)
- [Node.js](https://nodejs.org/) (for Static Web Apps CLI, if needed)
- Python 3.8+ (for backend)

---

## Azure Resources to Deploy
- Azure Storage Account (Blob Storage)
- Azure AI Translator Resource
- Azure Static Web App (for frontend)
- Azure Function App (for backend)

---

## Deployment Steps

### 1. Clone the Repository
```sh
git clone <your-fork-or-this-repo-url>
cd translator-demo-app
```

### 2. Set Required Environment Variables
Create a file named `local.settings.json` in the `azure-function-backend/` directory (for local dev) or set these as Application Settings in Azure Function App:

```json
{
	"IsEncrypted": false,
	"Values": {
		"AzureWebJobsStorage": "<your-storage-connection-string>",
		"SOURCE_SAS_TOKEN": "<source-container-sas>",
		"TARGET_SAS_TOKEN": "<target-container-sas>",
		"AZURE_STORAGE_ACCOUNT_NAME": "<storage-account-name>",
		"AZURE_SOURCE_CONTAINER": "source-docs",
		"AZURE_TARGET_CONTAINER": "translated-docs",
		"AZURE_TRANSLATOR_KEY": "<translator-key>",
		"AZURE_TRANSLATOR_REGION": "<translator-region>",
		"AZURE_TRANSLATOR_ENDPOINT": "https://<your-translator-resource>.cognitiveservices.azure.com/translator/document/batches?api-version=2025-12-01-preview"
	}
}
```

**Parameters to change:**
- `<your-storage-connection-string>`: Azure Storage Account > Access Keys > Connection string
- `<source-container-sas>`: SAS token for source-docs container (read access)
- `<target-container-sas>`: SAS token for translated-docs container (write access)
- `<storage-account-name>`: Your storage account name
- `<translator-key>`: Azure AI Translator key
- `<translator-region>`: Azure AI Translator region (e.g., eastus2)
- `<your-translator-resource>`: Name of your Translator resource

> **Tip:** Set these as Application Settings in the Azure Portal for production.

---

### 3. Deploy Azure Resources (CLI)

#### a. Create Resource Group
```sh
az group create --name <resource-group> --location <location>
```

#### b. Create Storage Account
```sh
az storage account create --name <storage-account-name> --resource-group <resource-group> --location <location> --sku Standard_LRS
az storage container create --account-name <storage-account-name> --name source-docs
az storage container create --account-name <storage-account-name> --name translated-docs
```

#### c. Create Translator Resource
```sh
az cognitiveservices account create --name <translator-resource> --resource-group <resource-group> --kind TextTranslation --sku S1 --location <location> --yes
```

#### d. Deploy Azure Function App
```sh
cd azure-function-backend
func azure functionapp publish <your-function-app-name>
```

#### e. Deploy Static Web App (Frontend)
```sh
# If using Azure Static Web Apps CLI
npm install -g @azure/static-web-apps-cli
swa deploy ./frontend --app-name <your-static-web-app-name> --env production
```

---

## Running the App
- **Frontend:** Deployed as Azure Static Web App (or serve locally for dev)
- **Backend:** Deployed as Azure Function App
- **Blob Storage:** Holds source and translated files
- **Translator:** Handles document translation jobs

---

## Environment Variables (Summary)
| Variable                   | Description                                 |
|----------------------------|---------------------------------------------|
| AzureWebJobsStorage        | Azure Storage connection string              |
| SOURCE_SAS_TOKEN           | SAS token for source-docs container          |
| TARGET_SAS_TOKEN           | SAS token for translated-docs container      |
| AZURE_STORAGE_ACCOUNT_NAME | Storage account name                         |
| AZURE_SOURCE_CONTAINER     | Source container name (default: source-docs) |
| AZURE_TARGET_CONTAINER     | Target container name (default: translated-docs) |
| AZURE_TRANSLATOR_KEY       | Azure Translator API key                     |
| AZURE_TRANSLATOR_REGION    | Azure Translator region                      |
| AZURE_TRANSLATOR_ENDPOINT  | Translator endpoint URL                      |

---

## Notes
- Use Managed Identity for production if possible (update code and assign roles).
- Never expose secrets in client-side code or public repos.
- For troubleshooting, check Azure Function logs and Storage account monitoring.

---

## References
- [Azure Translator Documentation](https://learn.microsoft.com/azure/ai-services/translator/document-translation/overview)
- [Azure Functions Documentation](https://learn.microsoft.com/azure/azure-functions/)
- [Azure Static Web Apps Documentation](https://learn.microsoft.com/azure/static-web-apps/)
- [Azure Storage Documentation](https://learn.microsoft.com/azure/storage/blobs/)

---
MIT License
