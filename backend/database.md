# Database Schema

This document defines the database schema for the Audit Playground application.

## Tables

### `submissions`

This table stores information about each smart contract submission.

| Column Name     | Data Type | Constraints                | Description                               |
|-----------------|-----------|----------------------------|-------------------------------------------|
| `id`            | `uuid`    | Primary Key, Default: `gen_random_uuid()` | Unique identifier for the submission.     |
| `created_at`    | `timestamptz` | Not Null, Default: `now()` | Timestamp of when the submission was created. |
| `file_name`     | `text`    | Not Null                   | The original name of the uploaded file.   |
| `status`        | `text`    | Not Null, Default: `'pending'` | The current status of the audit (e.g., 'pending', 'processing', 'completed', 'failed'). |
| `storage_path`  | `text`    | Not Null                   | The path to the contract file in object storage. |

### `audit_results`

This table stores the results of the Slither audit for each submission.

| Column Name     | Data Type | Constraints                | Description                               |
|-----------------|-----------|----------------------------|-------------------------------------------|
| `id`            | `uuid`    | Primary Key, Default: `gen_random_uuid()` | Unique identifier for the audit result.   |
| `submission_id` | `uuid`    | Not Null, Foreign Key to `submissions.id` | The submission this audit result belongs to. |
| `report_json`   | `jsonb`   | Not Null                   | The raw JSON output from the Slither analysis. |
| `summary`       | `text`    |                            | A brief, human-readable summary of the findings. |
| `created_at`    | `timestamptz` | Not Null, Default: `now()` | Timestamp of when the audit was completed. |
