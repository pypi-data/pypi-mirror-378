# Vidrial

A mixed CUDA/Python package that enalbes:
* writing non-spaghetti CUDA kernels for deep learning
* calling the custom kernels form python with pytorch tensors

Often, cuda code sucks. There is little code reuse, 

Rely extensively on Cute layouts.

# CUDA Framework Overview

Abstract away common logic (like pointer arithmetic) and construct infinitely configurable 

## Separation of Static and Dynamic Code
Separation of 


## Compute Hierarchy

GPU, CTA, Warp, thread

Compute hierarchy. Systematic names for tensors
* **Slab** Data relating to a GPU.
* **Tile** Data belonging to a CTA
* **Fragment** Data belonging to a thread.




| Component  | Description          |
|------------|----------------------|
| TileCopy   |                      |
| TileMMA   |                      |
| tprod   |                      |
| SmartReduce |                      |


Curently, we have used vidrial to write the following kernels

| Component  | Description          |
|------------|----------------------|
| copy       |                     |
| mma        |                      |
| sympow        |                      |
| sympow_bwd        |                      |
| sympow_mma        |                      |
| mma_sympow_bwd        |                      |
| flash_attn        |                      |


## Example Kernel 

```c++
template <typename Cfg, typename T>
__global__ void tiled_mma_kernel(Cfg cfg, T* A_ptr, T* B_ptr, T* C_ptr) {
    int tid = threadIdx.x;
    int bid_M = blockIdx.x; int bid_N = blockIdx.y; int bid_P = blockIdx.z;
    auto tile_coords = MmaMNKCoords(cfg.MNK_tile_shape);
    tile_coords.step_M(blockIdx.x); tile_coords.step_N(blockIdx.y); tile_coords.step_P(blockIdx.z);
    // ----- Global memory slabs -----
    auto gA_slab = make_tensor(make_gmem_ptr(A_ptr), cfg.A.gSlab);
    auto gB_slab = make_tensor(make_gmem_ptr(B_ptr), cfg.B.gSlab);
    auto gC_slab = make_tensor(make_gmem_ptr(C_ptr), cfg.C.gSlab);
    // ----- Shared memory tiles -----
    extern __shared__ char smem[cfg.smem_size];
    auto sA_tile = make_tensor<T>(make_smem_ptr(smem), cfg.A.sTile);
    auto sB_tile = make_tensor<T>(make_smem_ptr(smem+cosize(cfg.A.sTile)), cfg.C.sTile);
    auto rC_frg_mma = cfg.C.make_mma_frg();
    clear(rC_frg_mma);
    // ----- Main loop -----
    for (int k_tile = 0; k_tile < cfg.K_tile_num; k_tile++) {
        auto gA_tile = tile_coords.slice_A_tile(gA_slab);
        auto gB_tile = tile_coords.slice_B_tile(gB_slab);
        CTA_copy(cfg.A.tile_copy, gA_tile, sA_tile);
        CTA_copy(cfg.B.tile_copy, gB_tile, sB_tile);
        __syncthreads();
        smem_mma(sA, sB, rC);
    }
    // ----- Write C_tile to global memory -----
    auto sC_tile = make_tensor(make_smem_ptr(smem), cfg.C.sTile);
    copy(rC_frg_mma, slice_rest(sC_tile, cfg.C.mma_FrgThr, tid));
    __syncthreads();
    auto gC_tile = tile_coords.slice_C_tile(gC_slab);
    CTA_copy_tile(cfg.C.tile_copy, sC_tile, gC_tile);
}
```

To learn more about the how vidrial kernels work see this page.


## JIT System

### Settings
The JIT system can be
* `PickAny` finds 
* `PickBest`
```python
import torch as th
import vidrial as vid
from vidrial.jit.settings import settings
from vidrial.ops import mm

n = 1024

A = th.randn([n,n])
B = th.randn([n,n])

# Will run a 
with settings.set(vid.PickBest, num_workers=8):
    C = mm(A,B)
```

# Installation

# Build for release
```bash
uv sync --group dev
uv run python build_kernels.py
uv build
```


