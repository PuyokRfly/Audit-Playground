import os
import httpx
from backend.supabase_client import get_supabase_client

# It's better to load the prompt from a file to keep the code clean.
try:
    with open('prompt_template.txt', 'r') as f:
        PROMPT_TEMPLATE = f.read()
except FileNotFoundError:
    # Fallback to a default prompt if the file is not found
    PROMPT_TEMPLATE = """
You are a smart contract security auditor. Your task is to analyze the provided Slither JSON output, which contains findings from a security analysis of a smart contract.

Based on the findings, you must perform the following actions:
1.  **Assess the Severity**: Aggregate the findings by their severity level (e.g., high, medium, low, informational).
2.  **Calculate a Risk Score**: Compute a single, overall risk score for the contract on a scale of 0 to 100, where 0 represents no risk and 100 represents the highest possible risk. The score should reflect the number and severity of the vulnerabilities found.
3.  **Generate a Summary Report**: Write a concise summary of the audit in Bahasa Indonesia. The summary should be easy for a non-technical person to understand.
4.  **Provide Top 3 Recommendations**: List the top 3 most critical issues and suggest concrete code-level recommendations for fixing them. Present this in Bahasa Indonesia.

Your final output must be a JSON object with the following structure:
{
  "risk_score": <integer>,
  "summary_report": "<string in Bahasa Indonesia>"
}

Here is the Slither JSON data:
{slither_json}
"""

async def analyze_and_report(submission_id: str):
    """
    Fetches Slither results, sends them to an AI for analysis, and updates the database.
    """
    supabase = get_supabase_client()
    dart_ai_url = os.environ.get("DART_AI_URL")
    dart_ai_api_key = os.environ.get("DART_AI_API_KEY")

    if not dart_ai_url or not dart_ai_api_key:
        raise ValueError("DART_AI_URL and DART_AI_API_KEY must be set.")

    # 1. Fetch raw_slither_json from Supabase
    try:
        response = supabase.table('audit_results').select('raw_slither_json').eq('submission_id', submission_id).single().execute()
        if not response.data or 'raw_slither_json' not in response.data:
            raise Exception(f"No Slither results found for submission_id: {submission_id}")

        slither_json = response.data['raw_slither_json']

    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        # Optionally, update the submission status to 'failed'
        supabase.table('audit_submissions').update({"status": "failed"}).eq("id", submission_id).execute()
        raise

    # 2. Prepare the prompt and call the AI
    prompt = PROMPT_TEMPLATE.format(slither_json=slither_json)
    headers = {
        "Authorization": f"Bearer {dart_ai_api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "dart-ai-model-name", # Or whatever the model name is
        "prompt": prompt,
        "response_format": "json"
    }

    ai_response_data = None
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            ai_response = await client.post(dart_ai_url, json=payload, headers=headers)
            ai_response.raise_for_status()
            ai_response_data = ai_response.json()

            if "risk_score" not in ai_response_data or "summary_report" not in ai_response_data:
                raise Exception("AI response is missing required fields 'risk_score' or 'summary_report'")

    except httpx.RequestError as e:
        print(f"Error calling AI service: {e}")
        supabase.table('audit_submissions').update({"status": "failed"}).eq("id", submission_id).execute()
        raise
    except Exception as e:
        print(f"Error processing AI response: {e}")
        print(f"AI Response Content: {ai_response.text if 'ai_response' in locals() else 'No response'}")
        supabase.table('audit_submissions').update({"status": "failed"}).eq("id", submission_id).execute()
        raise

    # 3. Update the audit_results table in Supabase
    try:
        risk_score = ai_response_data['risk_score']
        summary_report = ai_response_data['summary_report']

        supabase.table('audit_results').update({
            'risk_score': risk_score,
            'summary_report': summary_report
        }).eq('submission_id', submission_id).execute()

        # Also update the submission status to 'done'
        supabase.table('audit_submissions').update({"status": "done"}).eq("id", submission_id).execute()

        print(f"Successfully updated audit results for submission_id: {submission_id}")

    except Exception as e:
        print(f"Error updating Supabase with AI results: {e}")
        supabase.table('audit_submissions').update({"status": "failed"}).eq("id", submission_id).execute()
        raise

    return {
        "submission_id": submission_id,
        "risk_score": risk_score,
        "summary_report": summary_report
    }
