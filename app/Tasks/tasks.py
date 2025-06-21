# tasks.py
from ..celery_worker import celery_app
from datetime import datetime, timezone
from ..Utils.models import Claim
import os, csv
from ..Utils.database import SessionLocal

@celery_app.task(name="generate_claims_report_task")
def generate_claims_report_task(task_id: str, username: str, webhook_url: str = None):
    db = SessionLocal()
    try:
        claims = db.query(Claim).all()
        status_groups = {}
        for claim in claims:
            status = claim.status.value
            if status not in status_groups:
                status_groups[status] = {"claims": [], "total_amount": 0}
            status_groups[status]["claims"].append(claim)
            status_groups[status]["total_amount"] += float(claim.claim_amount)

        os.makedirs("reports", exist_ok=True)
        csv_filename = f"reports/claims_report_{task_id}.csv"

        with open(csv_filename, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Status', 'Claim ID', 'Patient Name', 'Diagnosis Code', 
                             'Procedure Code', 'Claim Amount', 'Submitted At', 'Status Total'])

            for status, group in status_groups.items():
                total = group["total_amount"]
                for i, claim in enumerate(group["claims"]):
                    writer.writerow([
                        status,
                        claim.id,
                        claim.patient_name,
                        claim.diagnosis_code,
                        claim.procedure_code,
                        f"${float(claim.claim_amount):.2f}",
                        claim.submitted_at.strftime("%Y-%m-%d %H:%M:%S"),
                        f"${total:.2f}" if i == 0 else ""
                    ])
        # Store metadata in Redis or DB if needed
        # Optionally send webhook here if webhook_url is not None

        return {
            "status": "COMPLETED",
            "file_path": csv_filename,
            "completed_at": datetime.now(timezone.utc).isoformat()
        }

    except Exception as e:
        return {
            "status": "FAILED",
            "error": str(e),
            "completed_at": datetime.now(timezone.utc).isoformat()
        }
    finally:
        db.close()
