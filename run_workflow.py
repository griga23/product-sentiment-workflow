# run_workflow.py

import asyncio
from temporalio.client import Client


async def main():
    client = await Client.connect("localhost:7233")

    app_id = "728880"  # Overcooked 2 game,my kids love it

    result = await client.execute_workflow(
        "ReviewSentimentWorkflow",
        app_id,
        id=f"game-review-workflow-{app_id}",
        task_queue="review-task-queue",
    )

    print(f"Final sentiment score for app {app_id}: -1 worst <--- {result} ---> 1 best)")


if __name__ == "__main__":
    asyncio.run(main())
