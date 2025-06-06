from fastapi import HTTPException, Depends, APIRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, date

from app.models import Plan, Subscription, User, Invoice
from app.core.security import get_current_user
from app.db import get_session
from app.utils.enums import PlanEnum, PaymentStatus

from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")  # Indian Standard Time

router = APIRouter()


@router.get("/subscription_invoice")
async def get_subscription_invoice(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        # Fetch active subscription
        subscription_query = select(Subscription).where(
            Subscription.user_id == current_user.id, Subscription.status == "active"
        )
        sub_result = await session.execute(subscription_query)
        subscription = sub_result.scalars().first()

        if not subscription:
            raise HTTPException(status_code=404, detail="No active subscription found.")

        # Fetch related invoice
        invoice_query = select(Invoice).where(
            Invoice.subscription_id == subscription.id
        )
        inv_result = await session.execute(invoice_query)
        invoice = inv_result.scalars().first()

        if not invoice:
            raise HTTPException(
                status_code=404, detail="No invoice found for this subscription."
            )

        return {
            "subscription": {
                "plan_id": subscription.plan_id,
                "start_date": subscription.start_date.isoformat(),
                "end_date": subscription.end_date.isoformat(),
                "status": subscription.status,
            },
            "invoice": {
                "amount": float(invoice.amount),
                "issue_date": (
                    invoice.issue_date.isoformat() if invoice.issue_date else None
                ),
                "due_date": invoice.due_date.isoformat() if invoice.due_date else None,
                "status": invoice.status,
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch invoice: {str(e)}"
        )


@router.post("/subscribe")
async def subscribe(
    plan: PlanEnum,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        existing_subscription_query = select(Subscription).where(
            Subscription.user_id == current_user.id, Subscription.status == "active"
        )
        result = await session.execute(existing_subscription_query)
        existing_subscription = result.scalars().first()

        if existing_subscription:
            return {
                "message": "You already have an active subscription. Do you want to upgrade?"
            }

        selected_plan = await Plan.get_by_name(session=session, name=plan.value)
        if not selected_plan:
            raise HTTPException(status_code=404, detail="Selected plan not found")

        start_date = datetime.now(tz=IST)
        end_date = start_date + timedelta(days=30)

        await Subscription.create(
            session=session,
            user_id=current_user.id,
            plan_id=selected_plan.id,
            start_date=start_date,
            end_date=end_date,
            status="active",
        )
        await session.commit()

        return {"message": "Subscription successful"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to subscribe plan: {str(e)}"
        )


@router.put("/unsubscribe")
async def unsubscribe(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        existing_subscription_query = select(Subscription).where(
            Subscription.user_id == current_user.id, Subscription.status == "active"
        )
        result = await session.execute(existing_subscription_query)
        existing_subscription = result.scalars().first()

        if not existing_subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        existing_subscription.status = "cancelled"
        await session.commit()

        return {"message": "Unsubscribed successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to unsubscribe: {str(e)}")


@router.put("/payment")
async def payment(
    status: PaymentStatus,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        # Get active subscription
        existing_subscription_query = select(Subscription).where(
            Subscription.user_id == current_user.id, Subscription.status == "expired"
        )
        result = await session.execute(existing_subscription_query)
        existing_subscription = result.scalars().first()

        if not existing_subscription:
            raise HTTPException(status_code=404, detail="No active subscription found")

        # Get unpaid invoice for this subscription
        invoice_query = select(Invoice).where(
            Invoice.subscription_id == existing_subscription.id,
            Invoice.status == "unpaid",
        )
        invoice_result = await session.execute(invoice_query)
        invoice = invoice_result.scalars().first()

        # Update invoice status if found
        if invoice:
            if status == PaymentStatus.SUCCESS:
                invoice.status = "paid"
                invoice.issue_date = date.today()
            elif status == PaymentStatus.PENDING:
                invoice.status = "overdue"
            else:
                invoice.status = "upaid"
            invoice.issue_date = date.today()
        existing_subscription.status = "active"
        await session.commit()

        return {"message": "Payment successful"}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process payment: {str(e)}"
        )
