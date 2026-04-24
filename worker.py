# worker.py

import asyncio
from concurrent.futures import ThreadPoolExecutor

from temporalio.client import Client
from temporalio.worker import Worker

from workflow import ReviewSentimentWorkflow
from activities import scrape_reviews, analyze_sentiment, aggregate_scores


async def main():
    client = await Client.connect("localhost:7233")

    with ThreadPoolExecutor(max_workers=10) as activity_executor:
        worker = Worker(
            client,
            task_queue="review-task-queue",
            workflows=[ReviewSentimentWorkflow],
            activities=[scrape_reviews, analyze_sentiment, aggregate_scores],
            activity_executor=activity_executor,
        )

        await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
