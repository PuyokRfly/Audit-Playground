# n8n Workflow Setup

This directory contains the configuration for the n8n workflow that handles the smart contract analysis.

## Workflow: AuditContract

The main workflow is defined in `AuditWorkflow.json`. It can be imported into your n8n instance.

### Steps

1.  **Webhook Trigger:**
    *   The workflow is triggered by an HTTP POST request to a webhook URL.
    *   The backend sends a JSON body with the `submission_id` and `file_path` of the contract to be analyzed.
    *   **Example Body:** `{"submission_id": "...", "file_path": "..."}`

2.  **Execute Slither Analysis:**
    *   An "Execute Command" node runs the Slither tool on the contract.
    *   **Command:** `slither <file_path> --json -`
    *   The node captures the JSON output for the next step.

3.  **Update Supabase:**
    *   A "Supabase" node connects to your Supabase instance (credentials required).
    *   **Action 1 (Insert):** It inserts the Slither JSON report into the `audit_results` table.
    *   **Action 2 (Update):** It updates the `status` of the submission in the `submissions` table to `completed`.

### Setup Instructions

1.  **Import Workflow:** Import the `AuditWorkflow.json` file into your n8n instance.
2.  **Configure Webhook:** Copy the webhook URL from the "Webhook" node and set it as `N8N_WEBHOOK_URL` in the backend's `.env` file.
3.  **Set Supabase Credentials:** In the "Supabase" node, create a new credential for your Supabase project, providing the project URL and anon key.
4.  **Activate Workflow:** Make sure the workflow is active.
