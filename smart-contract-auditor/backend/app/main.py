from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid, subprocess, tempfile, json, os

app = FastAPI()

class AuditRequest(BaseModel):
    user_id: str
    contract_code: str

@app.post("/audit")
def audit(req: AuditRequest):
    submission_id = str(uuid.uuid4())
    tmp_path = f"/tmp/{submission_id}.sol"
    json_path = f"/tmp/{submission_id}_slither.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(req.contract_code)
    try:
        # jalankan slither (pastikan slither terpasang di environment)
        res = subprocess.run(["slither", tmp_path, "--json", json_path], capture_output=True, text=True, timeout=120)
        if res.returncode != 0 and not os.path.exists(json_path):
            raise Exception(res.stderr or res.stdout)
        with open(json_path, "r", encoding="utf-8") as jf:
            raw = json.load(jf)
        return {"submission_id": submission_id, "slither_raw": raw, "status":"done"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass
        try:
            os.remove(json_path)
        except:
            pass
