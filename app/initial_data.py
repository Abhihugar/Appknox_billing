"""
This script is executed before the application startup.
"""

import asyncio
from app.core import config
from app.db import async_session
from app.models import Plan
from app.utils import PlanEnum


async def main() -> None:

    async with async_session() as session:
        try:
            # Check if the plan already exists
            price_data = {
                PlanEnum.BASIC.value: 100,
                PlanEnum.PRO.value: 199,
                PlanEnum.ENTERPRISE.value: 299,
            }
            for plan in [
                PlanEnum.BASIC.value,
                PlanEnum.PRO.value,
                PlanEnum.ENTERPRISE.value,
            ]:
                existing_plan = await Plan.get_by_name(session=session, name=plan)
                if not existing_plan:
                    # Create the plan
                    new_plan = Plan(
                        name=plan,
                        price=price_data[plan],
                    )
                    session.add(new_plan)
                    await session.commit()
                    print(f"{plan} plan created successfully.")
                else:
                    print(f"{plan} plan already exists.")
        except Exception as e:
            print(f"Exception while adding initial data to the db: {str(e)}")


if __name__ == "__main__":
    # Run the main function asynchronously
    asyncio.run(main())
