"""
OMNITECH OMEGA v3.0 - Multi-GPU Worker for llama.cpp Benchmarking
"""

import os
import sys
import subprocess
import multiprocessing as mp
from typing import Dict, List, Optional
from datetime import datetime


class Worker:
    """Multi-GPU worker for running llama.cpp benchmarks."""
    
    def __init__(self, gpu_ids: Optional[List[int]] = None):
        self.gpu_ids = gpu_ids or self._detect_gpus()
        self.num_workers = len(self.gpu_ids)
        
    def _detect_gpus(self) -> List[int]:
        """Detect available GPUs."""
        gpus = []
        
        # Try to detect NVIDIA GPUs
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=index', '--format=csv,noheader'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                gpus = [int(x.strip()) for x in result.stdout.strip().split('\n') if x.strip()]
        except Exception:
            pass
        
        # If no GPUs detected, use CPU
        if not gpus:
            gpus = [-1]  # -1 indicates CPU
        
        return gpus
    
    def run_benchmark(self, model_path: str, gpu_id: int = -1) -> Dict:
        """
        Run benchmark on a specific GPU.
        
        Args:
            model_path: Path to the GGUF model file
            gpu_id: GPU ID (-1 for CPU)
            
        Returns:
            Dictionary with benchmark results
        """
        env = os.environ.copy()
        
        if gpu_id >= 0:
            env['CUDA_VISIBLE_DEVICES'] = str(gpu_id)
        
        # llama.cpp main binary path
        main_bin = os.environ.get('LLAMA_CPP_MAIN', './llama.cpp/main')
        
        # Benchmark parameters
        n_prompt = int(os.environ.get('BENCHMARK_N_PROMPT', '512'))
        n_gen = int(os.environ.get('BENCHMARK_N_GEN', '256'))
        
        cmd = [
            main_bin,
            '-m', model_path,
            '-n', str(n_gen),
            '--batch-size', '512',
            '--threads', str(mp.cpu_count()),
        ]
        
        try:
            start_time = datetime.now()
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                env=env
            )
            end_time = datetime.now()
            
            # Parse output for tokens/sec
            tps = self._parse_tps(result.stdout)
            
            return {
                'success': result.returncode == 0,
                'tps': tps,
                'gpu_id': gpu_id,
                'model_path': model_path,
                'prompt_tokens': n_prompt,
                'generated_tokens': n_gen,
                'duration': (end_time - start_time).total_seconds(),
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'tps': 0,
                'gpu_id': gpu_id,
                'error': 'Benchmark timed out'
            }
        except Exception as e:
            return {
                'success': False,
                'tps': 0,
                'gpu_id': gpu_id,
                'error': str(e)
            }
    
    def _parse_tps(self, output: str) -> float:
        """Parse tokens per second from llama.cpp output."""
        import re
        
        # Look for patterns like "30.50 tokens/s"
        match = re.search(r'(\d+\.?\d*)\s*tokens/s', output)
        if match:
            return float(match.group(1))
        
        return 0.0
    
    def benchmark_all_gpus(self, model_path: str) -> List[Dict]:
        """Run benchmark on all available GPUs in parallel."""
        results = []
        
        if self.num_workers == 1 and self.gpu_ids[0] == -1:
            # Single CPU worker
            results.append(self.run_benchmark(model_path, gpu_id=-1))
        else:
            # Multiple GPU workers
            with mp.Pool(processes=self.num_workers) as pool:
                results = pool.starmap(
                    self.run_benchmark,
                    [(model_path, gpu_id) for gpu_id in self.gpu_ids]
                )
        
        return results
    
    def get_gpu_info(self) -> List[Dict]:
        """Get information about available GPUs."""
        gpu_info = []
        
        for gpu_id in self.gpu_ids:
            if gpu_id >= 0:
                try:
                    result = subprocess.run(
                        ['nvidia-smi', '-i', str(gpu_id), 
                         '--query-gpu=name,memory.total,memory.free',
                         '--format=csv,noheader,nounits'],
                        capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        parts = result.stdout.strip().split(', ')
                        gpu_info.append({
                            'id': gpu_id,
                            'name': parts[0] if len(parts) > 0 else 'Unknown',
                            'memory_total_gb': int(parts[1]) / 1024 if len(parts) > 1 else 0,
                            'memory_free_gb': int(parts[2]) / 1024 if len(parts) > 2 else 0
                        })
                except Exception:
                    gpu_info.append({'id': gpu_id, 'name': 'Unknown', 'error': 'Could not query'})
            else:
                gpu_info.append({
                    'id': -1,
                    'name': 'CPU',
                    'cores': mp.cpu_count()
                })
        
        return gpu_info


if __name__ == '__main__':
    # Test the worker
    worker = Worker()
    
    print("Available GPUs:")
    for gpu in worker.get_gpu_info():
        print(f"  {gpu}")
    
    print("\nNote: Actual benchmarking requires a valid GGUF model file.")
    print("Set LLAMA_CPP_MAIN environment variable to point to llama.cpp main binary.")
