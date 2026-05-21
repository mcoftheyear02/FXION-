
/*
 * FXION PCIe ENGINE — CUDA Q8 Augmented Quantization Kernel
 * GTX 970 optimized: SM 5.2, 4GB GDDR5, 1664 CUDA cores
 *
 * Build:
 *   nvcc -arch=sm_52 -O2 -o bin/fxion_gpu.exe gpu/fxion_pcie_engine.cu
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <cuda_runtime.h>

#define QUANT_LEVELS  6
#define BLOCK_SIZE    256
#define Q8_SCALE      127.0f
#define Q4_SCALE      7.0f

// ────────────────────────────────────────────────────────
// Q8 Quantization Kernel
// Quantizes float32 weights to INT8 (Q8_0)
// ────────────────────────────────────────────────────────
__global__ void q8_quantize_kernel(
    const float* __restrict__ input,
    int8_t*      __restrict__ output,
    float*       __restrict__ scales,
    int N, int block_size)
{
    int block_id = blockIdx.x;
    int tid      = threadIdx.x;
    int base     = block_id * block_size;
    int idx      = base + tid;

    __shared__ float smax[BLOCK_SIZE];

    // Load and find abs max in block
    float val = (idx < N) ? fabsf(input[idx]) : 0.0f;
    smax[tid] = val;
    __syncthreads();

    // Parallel reduction for max
    for (int s = BLOCK_SIZE/2; s > 0; s >>= 1) {
        if (tid < s) smax[tid] = fmaxf(smax[tid], smax[tid+s]);
        __syncthreads();
    }

    float scale = smax[0] / Q8_SCALE;
    if (tid == 0) scales[block_id] = scale;
    __syncthreads();

    // Quantize
    if (idx < N) {
        output[idx] = (int8_t)roundf(input[idx] / fmaxf(scale, 1e-8f));
    }
}

// ────────────────────────────────────────────────────────
// Q8 Dequantization Kernel
// ────────────────────────────────────────────────────────
__global__ void q8_dequantize_kernel(
    const int8_t* __restrict__ input,
    float*        __restrict__ output,
    const float*  __restrict__ scales,
    int N, int block_size)
{
    int block_id = blockIdx.x;
    int idx      = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < N) {
        output[idx] = (float)input[idx] * scales[block_id];
    }
}

// ────────────────────────────────────────────────────────
// Matrix-Vector Product (Q8 weight × FP32 activation)
// ────────────────────────────────────────────────────────
__global__ void q8_matvec_kernel(
    const int8_t* __restrict__ W,    // [M x K] quantized
    const float*  __restrict__ x,    // [K]
    const float*  __restrict__ scales,
    float*        __restrict__ y,    // [M]
    int M, int K, int block_size)
{
    int row = blockIdx.x * blockDim.x + threadIdx.x;
    if (row >= M) return;

    float acc = 0.0f;
    for (int k = 0; k < K; k++) {
        int   block_id = (row * K + k) / block_size;
        float w_fp     = (float)W[row * K + k] * scales[block_id];
        acc += w_fp * x[k];
    }
    y[row] = acc;
}

// ────────────────────────────────────────────────────────
// UCB1 Reward Kernel (parallel evaluation across quant levels)
// ────────────────────────────────────────────────────────
__global__ void ucb1_reward_kernel(
    float* __restrict__ rewards,
    int*   __restrict__ counts,
    float* __restrict__ ucb_scores,
    int t, int n_quants, float q8_boost)
{
    int i = threadIdx.x;
    if (i >= n_quants) return;

    float exploit = (counts[i] > 0) ? rewards[i] / (float)counts[i] : 0.0f;
    float explore = (counts[i] > 0) ? sqrtf(2.0f * logf((float)t) / (float)counts[i]) : 1e9f;
    float boost   = (i == 5) ? q8_boost : 0.0f;   // Q8_0 is index 5

    ucb_scores[i] = exploit + explore + boost;
}

// ────────────────────────────────────────────────────────
// GPU Benchmark (tokens/sec simulation on device)
// ────────────────────────────────────────────────────────
__global__ void bench_kernel(float* __restrict__ result, int iterations)
{
    float acc = 0.0f;
    for (int i = 0; i < iterations; i++) {
        acc += sinf((float)i * 0.001f) * cosf((float)i * 0.002f);
    }
    if (threadIdx.x == 0 && blockIdx.x == 0) result[0] = acc;
}

// ────────────────────────────────────────────────────────
// Host Utilities
// ────────────────────────────────────────────────────────
void check_cuda(cudaError_t e, const char* msg) {
    if (e != cudaSuccess) {
        fprintf(stderr, "[CUDA ERROR] %s: %s\n", msg, cudaGetErrorString(e));
        exit(1);
    }
}

void print_gpu_info() {
    int dev; cudaGetDevice(&dev);
    cudaDeviceProp p; cudaGetDeviceProperties(&p, dev);
    printf("[GPU] %s | SM %d.%d | VRAM %.0f MB | Clock %d MHz\n",
        p.name, p.major, p.minor,
        p.totalGlobalMem / (1024.0*1024.0),
        p.clockRate / 1000);
}

// ────────────────────────────────────────────────────────
// MAIN
// ────────────────────────────────────────────────────────
int main(int argc, char** argv) {
    printf("=== FXION PCIe ENGINE — Q8 AUGMENTED ===\n");
    print_gpu_info();

    // 1. Benchmark
    float *d_res, h_res;
    check_cuda(cudaMalloc(&d_res, sizeof(float)), "bench alloc");
    bench_kernel<<<1, 1>>>(d_res, 10000);
    cudaDeviceSynchronize();
    cudaMemcpy(&h_res, d_res, sizeof(float), cudaMemcpyDeviceToHost);
    printf("[BENCH] Kernel warmup: %.4f\n", h_res);
    cudaFree(d_res);

    // 2. Q8 quantization test
    int N = 4096, BS = 256;
    int n_blocks = (N + BS - 1) / BS;

    float  *h_in  = (float*)malloc(N*sizeof(float));
    int8_t *h_q8  = (int8_t*)malloc(N*sizeof(int8_t));
    float  *h_deq = (float*)malloc(N*sizeof(float));
    float  *h_scl = (float*)malloc(n_blocks*sizeof(float));

    for (int i = 0; i < N; i++) h_in[i] = sinf(i * 0.01f) * 2.5f;

    float  *d_in; int8_t *d_q8; float *d_deq, *d_scl;
    check_cuda(cudaMalloc(&d_in,  N*sizeof(float)),  "alloc d_in");
    check_cuda(cudaMalloc(&d_q8,  N*sizeof(int8_t)), "alloc d_q8");
    check_cuda(cudaMalloc(&d_deq, N*sizeof(float)),  "alloc d_deq");
    check_cuda(cudaMalloc(&d_scl, n_blocks*sizeof(float)), "alloc d_scl");

    cudaMemcpy(d_in, h_in, N*sizeof(float), cudaMemcpyHostToDevice);

    q8_quantize_kernel<<<n_blocks, BS>>>(d_in, d_q8, d_scl, N, BS);
    q8_dequantize_kernel<<<n_blocks, BS>>>(d_q8, d_deq, d_scl, N, BS);
    cudaDeviceSynchronize();

    cudaMemcpy(h_q8,  d_q8,  N*sizeof(int8_t), cudaMemcpyDeviceToHost);
    cudaMemcpy(h_deq, d_deq, N*sizeof(float),  cudaMemcpyDeviceToHost);
    cudaMemcpy(h_scl, d_scl, n_blocks*sizeof(float), cudaMemcpyDeviceToHost);

    // Compute reconstruction error
    float err = 0.0f;
    for (int i = 0; i < N; i++) err += fabsf(h_in[i] - h_deq[i]);
    printf("[Q8] Quant→Deq MAE: %.6f (N=%d, blocks=%d)\n", err/N, N, n_blocks);
    printf("[Q8] Scale[0]=%.6f  Q8[0]=%d\n", h_scl[0], (int)h_q8[0]);

    // 3. UCB1 reward kernel
    float h_rew[6] = {3.1f,4.2f,6.0f,7.5f,8.1f,9.4f};
    int   h_cnt[6] = {12,  15,  20,  22,  18,  25};
    float h_ucb[6] = {0};
    float *d_rew; int *d_cnt; float *d_ucb;
    cudaMalloc(&d_rew, 6*sizeof(float)); cudaMemcpy(d_rew, h_rew, 6*sizeof(float), cudaMemcpyHostToDevice);
    cudaMalloc(&d_cnt, 6*sizeof(int));   cudaMemcpy(d_cnt, h_cnt, 6*sizeof(int),   cudaMemcpyHostToDevice);
    cudaMalloc(&d_ucb, 6*sizeof(float));

    ucb1_reward_kernel<<<1, 6>>>(d_rew, d_cnt, d_ucb, 112, 6, 0.15f);
    cudaDeviceSynchronize();
    cudaMemcpy(h_ucb, d_ucb, 6*sizeof(float), cudaMemcpyDeviceToHost);

    const char* names[6] = {"Q2_K","Q3_K","Q4_K_M","Q5_K_M","Q6_K","Q8_0"};
    int best = 0;
    printf("[UCB1] Scores:\n");
    for (int i = 0; i < 6; i++) {
        printf("  %-10s %.4f%s\n", names[i], h_ucb[i], i==5?" ← Q8 BOOST":"");
        if (h_ucb[i] > h_ucb[best]) best = i;
    }
    printf("[UCB1] Best quant: %s\n", names[best]);

    // Cleanup
    free(h_in); free(h_q8); free(h_deq); free(h_scl);
    cudaFree(d_in); cudaFree(d_q8); cudaFree(d_deq); cudaFree(d_scl);
    cudaFree(d_rew); cudaFree(d_cnt); cudaFree(d_ucb);

    printf("=== FXION GPU ENGINE COMPLETE ===\n");
    return 0;
}
