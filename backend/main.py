import os
import shutil
import httpx
import stripe
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from pydantic import BaseModel
from backend.supabase_client import get_supabase_client
from backend.ai_reporter import analyze_and_report


# Load environment variables
from dotenv import load_dotenv
load_dotenv()

stripe.api_key = os.getenv("STRIPE_API_KEY")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

app = FastAPI()

# Create the uploads directory if it doesn't exist
UPLOADS_DIR = "backend/uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Audit Playground Backend"}

async def trigger_n8n_workflow(task_id: str, contract_code: str):
    """
    Triggers the n8n workflow by sending a POST request to the webhook.
    """
    if not N8N_WEBHOOK_URL:
        print("N8N_WEBHOOK_URL not set. Skipping workflow trigger.")
        return

    payload = {"taskId": task_id, "contractCode": contract_code}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(N8N_WEBHOOK_URL, json=payload)
            response.raise_for_status()
            print(f"Successfully triggered n8n workflow for task {task_id}")
    except httpx.RequestError as e:
        print(f"Error triggering n8n workflow: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger analysis workflow: {e}")


@app.post("/upload/")
async def upload_contract(file: UploadFile = File(...)):
    """
    Receives a smart contract file, saves it, creates a submission record,
    and triggers the n8n analysis workflow.
    """
    supabase = get_supabase_client()

    # Define the path where the file will be saved
    file_path = os.path.join(UPLOADS_DIR, file.filename)

    # Save the uploaded file
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not save file: {e}")

    submission_id = None
    # Create a record in the 'submissions' table
    try:
        data, count = supabase.table('submissions').insert({
            "file_name": file.filename,
            "storage_path": file_path,
            "status": "pending"
        }).execute()

        submission_data = data[1][0] if data[1] else None

        if not submission_data:
            raise HTTPException(status_code=500, detail="Failed to create submission record in database.")

        submission_id = submission_data['id']

        # Read the contract code to send to the webhook
        with open(file_path, "r") as f:
            contract_code = f.read()

        # Trigger the n8n workflow
        await trigger_n8n_workflow(task_id=submission_id, contract_code=contract_code)

        return {"message": "File uploaded successfully and analysis started.", "submission_id": submission_id}

    except Exception as e:
        # If any step fails, clean up the saved file
        if os.path.exists(file_path):
            os.remove(file_path)

        # If submission was created but workflow failed, maybe update status to 'failed'
        if submission_id:
            supabase.table('submissions').update({"status": "failed"}).eq("id", submission_id).execute()

        # Re-raise the exception
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

# Pydantic model for the request body of the analysis endpoint
class AuditAnalysisRequest(BaseModel):
    submission_id: str

class CreateCheckoutSessionRequest(BaseModel):
    submission_id: str

@app.post("/create-checkout-session")
async def create_checkout_session(request: CreateCheckoutSessionRequest):
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Premium Audit',
                        },
                        'unit_amount': 2000,
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url='http://localhost:3000/results/{CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:3000/pricing',
            client_reference_id=request.submission_id
        )
        return {"id": checkout_session.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=str(e))
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=str(e))

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        submission_id = session.get('client_reference_id')
        if submission_id:
            supabase = get_supabase_client()
            try:
                supabase.table('submissions').update({'status': 'paid'}).eq('id', submission_id).execute()
            except Exception as e:
                # Log the error
                print(f"Failed to update submission status for {submission_id}: {e}")
                raise HTTPException(status_code=500, detail="Failed to update submission status.")


    return {"status": "success"}

@app.post("/analyze-audit/")
async def analyze_audit_endpoint(request: AuditAnalysisRequest):
    """
    Endpoint to trigger the AI analysis of an audit result.
    This is expected to be called by the n8n workflow.
    """
    try:
        result = await analyze_and_report(request.submission_id)
        return {"message": "Analysis completed successfully.", "data": result}
    except Exception as e:
        # The error is already logged in the analyze_and_report function.
        # We can also log it here if needed.
        # The submission status should have been updated to 'failed' in the function.
        raise HTTPException(status_code=500, detail=f"An error occurred during analysis: {e}")
