/*
 * FXION CUDA GPU AI-Assisted Mining Kernel
 * This kernel generates candidate nonces using a lightweight AI-inspired heuristic,
 * performs GPU mining work, and reports the first found candidate nonce.
 *
 * Build command:
 *   nvcc -O3 -arch=sm_52 -o bin/fxion_gpu_ai_miner.exe fxion_gpu_ai_miner.cu
 */

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <cuda_runtime.h>

void check_cuda(cudaError_t result, const char* msg) {
    if (result != cudaSuccess) {
        fprintf(stderr, "[CUDA ERROR] %s: %s\n", msg, cudaGetErrorString(result));
        exit(1);
    }
}

__device__ inline uint32_t rotate_left(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

__device__ inline uint32_t ai_hash_mix(uint32_t nonce, uint32_t seed) {
    uint32_t value = nonce ^ seed;
    value = rotate_left(value, 13) ^ 0xA5A5A5A5u;
    value += (seed ^ 0x3C6EF372u);
    value ^= (value >> 16);
    value = rotate_left(value, 7) + (value & 0xFF00FF00u);
    return value;
}

__global__ void ai_nonce_generator(uint32_t* nonces, uint32_t base, uint32_t pattern, int N) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= N) return;
    uint32_t candidate = base + (uint32_t)idx * 0x9E3779B1u;
    candidate ^= pattern * ((uint32_t)idx + 1u);
    candidate = rotate_left(candidate, (idx & 7));
    nonces[idx] = candidate;
}

__global__ void stratum_mining_kernel(const uint32_t* nonces, uint32_t* results, uint32_t seed, uint32_t target, int N) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= N) return;
    uint32_t hash = ai_hash_mix(nonces[idx], seed);
    if (hash < target) {
        results[idx] = nonces[idx];
    } else {
        results[idx] = 0xFFFFFFFFu;
    }
}

static uint32_t djb2_hash(const char* str) {
    uint32_t hash = 5381u;
    while (*str) {
        hash = ((hash << 5) + hash) + (uint8_t)(*str++);
    }
    return hash;
}

static uint32_t compact_to_target32(const char* nbits) {
    if (!nbits) return 0x00FFFFFFu;
    size_t len = strlen(nbits);
    const char* s = nbits;
    if (len > 8) s = nbits + (len - 8);
    uint32_t value = 0;
    for (int i = 0; i < 8 && s[i]; ++i) {
        char c = s[i];
        uint32_t v = 0;
        if (c >= '0' && c <= '9') v = c - '0';
        else if (c >= 'a' && c <= 'f') v = 10 + (c - 'a');
        else if (c >= 'A' && c <= 'F') v = 10 + (c - 'A');
        value = (value << 4) | v;
    }
    if (value == 0) value = 0x00FFFFFFu;
    return value;
}

int main(int argc, char** argv) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <job_id> <nbits_hex> <duration_seconds>\n", argv[0]);
        return 1;
    }

    const char* job_id = argv[1];
    const char* nbits = argv[2];
    int duration = atoi(argv[3]);
    if (duration < 1) duration = 1;

    uint32_t seed = djb2_hash(job_id);
    uint32_t target = compact_to_target32(nbits);
    uint32_t pattern = seed ^ 0x5A5A5A5Au;

    const int N = 1 << 20;
    const int BLOCK_SIZE = 256;
    const int blocks = (N + BLOCK_SIZE - 1) / BLOCK_SIZE;

    uint32_t* d_nonces = nullptr;
    uint32_t* d_results = nullptr;
    check_cuda(cudaMalloc(&d_nonces, N * sizeof(uint32_t)), "alloc nonces");
    check_cuda(cudaMalloc(&d_results, N * sizeof(uint32_t)), "alloc results");

    ai_nonce_generator<<<blocks, BLOCK_SIZE>>>(d_nonces, seed, pattern, N);
    check_cuda(cudaDeviceSynchronize(), "initialize nonces");

    stratum_mining_kernel<<<blocks, BLOCK_SIZE>>>(d_nonces, d_results, seed, target, N);
    check_cuda(cudaDeviceSynchronize(), "run mining kernel");

    uint32_t* h_results = (uint32_t*)malloc(N * sizeof(uint32_t));
    if (!h_results) {
        fprintf(stderr, "Memory allocation failed on host.\n");
        return 1;
    }

    check_cuda(cudaMemcpy(h_results, d_results, N * sizeof(uint32_t), cudaMemcpyDeviceToHost), "copy results");

    uint32_t found = 0xFFFFFFFFu;
    for (int i = 0; i < N; ++i) {
        if (h_results[i] != 0xFFFFFFFFu) {
            found = h_results[i];
            break;
        }
    }

    if (found != 0xFFFFFFFFu) {
        printf("FOUND %u\n", found);
    } else {
        printf("NONE\n");
    }

    free(h_results);
    cudaFree(d_nonces);
    cudaFree(d_results);
    return 0;
}
