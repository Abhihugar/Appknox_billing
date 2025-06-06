from app.models import Subscription, Invoice
from app.sync_db import get_sync_db
from datetime import date, timedelta
from celery import shared_task


@shared_task
def check_active_sub_and_generate_invoice():
    """
    Cron job: Check active subscriptions that end today,
    generate an invoice, and store it in the invoice table.
    """
    today = date.today()

    with get_sync_db() as db:
        # Get subscriptions that are active and end today
        subscriptions = (
            db.query(Subscription)
            .filter(Subscription.status == "active", Subscription.end_date == today)
            .all()
        )

        for sub in subscriptions:
            # Generate invoice
            invoice = Invoice(
                user_id=sub.user_id,
                subscription_id=sub.id,
                amount=sub.plan.price,
                issue_date=today,
                due_date=today + timedelta(days=7),  # e.g., due in 7 days
                status="unpaid",
            )

            db.add(invoice)

            # Optionally, update subscription status to expired
            sub.status = "expired"

        db.commit()
