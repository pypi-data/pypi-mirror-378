"""
Worker runner for NetIntel-OCR
"""

import multiprocessing
import threading
import time
import signal
import sys
from typing import Dict, Any


def run_workers(worker_count: int = 4,
                queue_backend: str = 'redis',
                concurrency: int = 1,
                embedded: bool = False,
                debug: bool = False,
                **kwargs) -> None:
    """
    Start worker processes for PDF processing

    Args:
        worker_count: Number of worker processes
        queue_backend: Queue backend (redis, rabbitmq, sqlite)
        concurrency: Concurrent tasks per worker
        embedded: Run workers in embedded mode (same process)
        debug: Enable debug mode
        **kwargs: Additional configuration
    """

    print(f"Starting {worker_count} workers with {queue_backend} backend")

    if embedded:
        # Run workers in threads within the same process
        print("Running in embedded mode")
        workers = []

        for i in range(worker_count):
            worker = threading.Thread(
                target=worker_loop,
                args=(i, queue_backend, concurrency, debug),
                daemon=True
            )
            worker.start()
            workers.append(worker)

        # Wait for all workers
        try:
            for worker in workers:
                worker.join()
        except KeyboardInterrupt:
            print("\nStopping workers...")
            sys.exit(0)
    else:
        # Run workers in separate processes
        print("Running in separate processes")
        processes = []

        for i in range(worker_count):
            process = multiprocessing.Process(
                target=worker_loop,
                args=(i, queue_backend, concurrency, debug)
            )
            process.start()
            processes.append(process)

        # Wait for all processes
        try:
            for process in processes:
                process.join()
        except KeyboardInterrupt:
            print("\nStopping workers...")
            for process in processes:
                process.terminate()
            for process in processes:
                process.join(timeout=5)
            sys.exit(0)


def worker_loop(worker_id: int,
                queue_backend: str,
                concurrency: int,
                debug: bool) -> None:
    """
    Main worker loop for processing tasks

    Args:
        worker_id: Worker identifier
        queue_backend: Queue backend type
        concurrency: Number of concurrent tasks
        debug: Enable debug logging
    """

    print(f"Worker {worker_id} started (queue: {queue_backend}, concurrency: {concurrency})")

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    signal.signal(signal.SIGTERM, lambda *args: sys.exit(0))

    # Main processing loop
    while True:
        try:
            # TODO: Implement actual queue processing
            # This is a placeholder that simulates work
            if debug:
                print(f"Worker {worker_id}: Checking for tasks...")

            # Simulate processing
            time.sleep(5)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Worker {worker_id} error: {e}")
            if debug:
                import traceback
                traceback.print_exc()
            time.sleep(1)

    print(f"Worker {worker_id} stopped")


def stop_all_workers() -> None:
    """Stop all running workers"""
    # Send termination signal to all worker processes
    import os
    import subprocess

    try:
        subprocess.run(['pkill', '-f', 'netintel.*worker'], check=False)
        print("All workers stopped")
    except Exception as e:
        print(f"Error stopping workers: {e}")