#include "../copy/copy_kernels.cuh"
using namespace cute;
using namespace vidrial;

template<typename T, int thread_num, typename SlabShape, typename TileShape, typename GSlab>
void launch_add_one_inplace(T* ptr) {
    auto cfg = make_tiling_cfg<T, thread_num>(SlabShape{}, TileShape{}, GSlab{});
    auto gA = make_tensor(ptr, GSlab{});
    int blocks = size<1>(cfg.TileBlock);
    tensor_scalar_add_kernel<<<blocks, int(cfg.thread_num)>>>(cfg, gA.data(), gA.data(), 1.f);
}

template<typename T, int thread_num, typename SlabShape, typename TileShape, typename GSlab>
void launch_add_one(T* in, T* out) {
    auto cfg = make_tiling_cfg<T, thread_num>(SlabShape{}, TileShape{}, GSlab{});
    auto gA = make_tensor(in, GSlab{});
    auto gB = make_tensor(out, GSlab{});
    int blocks = size<1>(cfg.TileBlock);
    tensor_scalar_add_kernel<<<blocks, int(cfg.thread_num)>>>(cfg, gA.data(), gB.data(), 1.f);
}
