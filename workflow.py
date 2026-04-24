# workflow.py

import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from activities import scrape_reviews, analyze_sentiment, aggregate_scores


BATCH_SIZE = 10


@workflow.defn
class ReviewSentimentWorkflow:

    @workflow.run
    async def run(self, app_id: str) -> float:

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            maximum_attempts=3,
        )

        # 1. scrape
        reviews = await workflow.execute_activity(
            scrape_reviews,
            app_id,
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy,
        )

        # 2. sentiment — fan out one activity per batch, then fan in
        batches = [reviews[i:i + BATCH_SIZE] for i in range(0, len(reviews), BATCH_SIZE)]
        batch_results = await asyncio.gather(*[
            workflow.execute_activity(
                analyze_sentiment,
                batch,
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )
            for batch in batches
        ])
        scores = [s for batch in batch_results for s in batch]

        # 3. aggregate
        avg_score = await workflow.execute_activity(
            aggregate_scores,
            scores,
            start_to_close_timeout=timedelta(seconds=10),
        )

        return avg_score
