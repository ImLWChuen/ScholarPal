"""
Scheduler background runner for ScholarPal.
Periodically triggers freshness audits and crawler coordination jobs.
Writes a heartbeat timestamp file for Docker healthcheck monitoring.
"""

import asyncio
import logging
import os
import signal
import time

from app.core.config import settings
from app.jobs.scheduler import audit_freshness_job, trigger_crawler_sync_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] (scheduler) %(message)s",
)
logger = logging.getLogger("scheduler")

HEARTBEAT_FILE = os.getenv("SCHEDULER_HEARTBEAT_FILE", "/tmp/scheduler_heartbeat")


class SchedulerRunner:
    def __init__(self, interval_seconds: int = 60):
        self.interval = interval_seconds
        self.running = True

    def touch_heartbeat(self) -> None:
        try:
            with open(HEARTBEAT_FILE, "w") as f:
                f.write(str(time.time()))
        except Exception as e:
            logger.warning(f"Could not touch heartbeat file: {e}")

    async def run(self) -> None:
        logger.info(f"ScholarPal Scheduler daemon started. Interval: {self.interval} seconds.")
        self.touch_heartbeat()

        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop.add_signal_handler(sig, self.stop)
            except (NotImplementedError, RuntimeError):
                # Signals might not be fully hookable on Windows event loops
                pass

        iteration = 0
        while self.running:
            iteration += 1
            logger.info(f"--- Scheduler iteration #{iteration} started ---")
            try:
                # 1. Audit freshness of known scholarships (Rule 4)
                await audit_freshness_job()

                # 2. Trigger crawler sync
                await trigger_crawler_sync_job()

                self.touch_heartbeat()
                logger.info(f"--- Scheduler iteration #{iteration} completed ---")
            except Exception as e:
                logger.error(f"Error in scheduler iteration #{iteration}: {e}", exc_info=True)

            # Sleep until next execution cycle
            for _ in range(self.interval):
                if not self.running:
                    break
                await asyncio.sleep(1)

        logger.info("Scheduler daemon shut down cleanly.")

    def stop(self) -> None:
        logger.info("Received shutdown signal. Stopping scheduler loop...")
        self.running = False


if __name__ == "__main__":
    runner = SchedulerRunner(interval_seconds=settings.SCHEDULER_INTERVAL_SECONDS)
    asyncio.run(runner.run())
