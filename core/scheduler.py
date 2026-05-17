"""
OMNITECH OMEGA v3.0 - Redis Scheduler / Job Queue Gate
"""

import os
import json
import time
import redis
from typing import Dict, Optional, List
from datetime import datetime


class Scheduler:
    """Redis-based job queue scheduler with rate limiting."""
    
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis = None
        self.queue_key = 'omnitech:jobs'
        self.rate_limit_key = 'omnitech:rate_limit'
        
        # Try to connect to Redis
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            self.redis = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True
            )
            self.redis.ping()
            print(f"Connected to Redis at {self.redis_host}:{self.redis_port}")
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}")
            print("Running in mock mode without Redis")
            self.redis = None
            self.mock_queue = []
    
    def enqueue_job(self, job_data: Dict) -> str:
        """
        Add a job to the queue.
        
        Args:
            job_data: Dictionary containing job information
            
        Returns:
            Job ID
        """
        job_id = f"job_{int(time.time() * 1000)}"
        job = {
            'id': job_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            **job_data
        }
        
        if self.redis:
            self.redis.lpush(self.queue_key, json.dumps(job))
        else:
            self.mock_queue.insert(0, job)
        
        print(f"Enqueued job: {job_id}")
        return job_id
    
    def dequeue_job(self) -> Optional[Dict]:
        """
        Get the next job from the queue.
        
        Returns:
            Job data or None if queue is empty
        """
        if self.redis:
            job_str = self.redis.rpop(self.queue_key)
            if job_str:
                return json.loads(job_str)
        elif self.mock_queue:
            return self.mock_queue.pop()
        
        return None
    
    def check_rate_limit(self, client_id: str, limit: int = 100, window: int = 60) -> bool:
        """
        Check if client has exceeded rate limit.
        
        Args:
            client_id: Client identifier
            limit: Maximum requests per window
            window: Time window in seconds
            
        Returns:
            True if request is allowed, False if rate limited
        """
        if not self.redis:
            return True  # No rate limiting in mock mode
        
        current_time = int(time.time())
        window_start = current_time - window
        
        key = f"{self.rate_limit_key}:{client_id}"
        
        # Remove old entries
        self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count requests in current window
        request_count = self.redis.zcard(key)
        
        if request_count >= limit:
            return False
        
        # Add current request
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, window)
        
        return True
    
    def get_queue_length(self) -> int:
        """Get current queue length."""
        if self.redis:
            return self.redis.llen(self.queue_key)
        return len(self.mock_queue) if hasattr(self, 'mock_queue') else 0
    
    def get_job_status(self, job_id: str) -> Optional[str]:
        """Get status of a specific job."""
        if not self.redis:
            for job in getattr(self, 'mock_queue', []):
                if job.get('id') == job_id:
                    return job.get('status')
            return None
        
        # Scan queue for job
        jobs = self.redis.lrange(self.queue_key, 0, -1)
        for job_str in jobs:
            job = json.loads(job_str)
            if job.get('id') == job_id:
                return job.get('status')
        
        return None
    
    def update_job_status(self, job_id: str, status: str):
        """Update job status."""
        if not self.redis:
            for job in getattr(self, 'mock_queue', []):
                if job.get('id') == job_id:
                    job['status'] = status
                    break
            return
        
        # In real implementation, would use a separate status store
        print(f"Job {job_id} status updated to: {status}")
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics."""
        return {
            'queue_length': self.get_queue_length(),
            'redis_connected': self.redis is not None,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_queue(self):
        """Clear all jobs from the queue."""
        if self.redis:
            self.redis.delete(self.queue_key)
        else:
            self.mock_queue = []
        print("Queue cleared")


if __name__ == '__main__':
    # Test the scheduler
    scheduler = Scheduler()
    
    print("\nTesting job queue...")
    
    # Enqueue some jobs
    for i in range(5):
        scheduler.enqueue_job({
            'type': 'quantize',
            'model': f'model_{i}.gguf',
            'quant_level': 'Q4_K_M'
        })
    
    print(f"Queue length: {scheduler.get_queue_length()}")
    
    # Dequeue jobs
    print("\nDequeuing jobs:")
    while True:
        job = scheduler.dequeue_job()
        if not job:
            break
        print(f"  Processed: {job['id']} - {job['model']}")
    
    print(f"Queue length after dequeue: {scheduler.get_queue_length()}")
    
    # Test rate limiting
    print("\nTesting rate limiting:")
    for i in range(5):
        allowed = scheduler.check_rate_limit('test_client', limit=3, window=60)
        print(f"  Request {i+1}: {'Allowed' if allowed else 'Rate Limited'}")
    
    # Get stats
    print("\nScheduler Stats:")
    print(json.dumps(scheduler.get_stats(), indent=2))
