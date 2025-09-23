#pragma once

#include <type_traits>
#include <utility>

namespace vidrial {

template<int smempipe_=2, int regpipe_=1, bool use_ldsm_=true, int swizzle_=0>
struct PerfCfg {
    static constexpr int smempipe = smempipe_;
    static constexpr int regpipe = regpipe_;
    static constexpr bool use_ldsm = use_ldsm_;
    static constexpr int swizzle = swizzle_;
};

template<int smempipe_=2, int regpipe_=1, bool use_ldsm_=true, int swizzle_=0, bool q_in_reg_=true>
struct FlashPerfCfg {
    static constexpr int smempipe = smempipe_;
    static constexpr int regpipe = regpipe_;
    static constexpr bool use_ldsm = use_ldsm_;
    static constexpr int swizzle = swizzle_;
    static constexpr bool q_in_reg = q_in_reg_;
};

using DefaultPerfCfg = PerfCfg<2, 1, true, 0>;

template<int smempipe_, int regpipe_, bool use_ldsm_, int swizzle_, bool q_in_reg_>
void print_cfg(FlashPerfCfg<smempipe_, regpipe_, use_ldsm_, swizzle_, q_in_reg_> const& cfg, std::string prefix = "") {
    std::cout << "FlashPerfCfg:\n";
    std::cout << prefix << "  smempipe: " << cfg.smempipe << "\n";
    std::cout << prefix << "  regpipe: " << cfg.regpipe << "\n";
    std::cout << prefix << "  use_ldsm: " << cfg.use_ldsm << "\n";
    std::cout << prefix << "  swizzle: " << cfg.swizzle << "\n";
    std::cout << prefix << "  q_in_reg: " << cfg.q_in_reg << "\n";
}

template<int smempipe_, int regpipe_, bool use_ldsm_, int swizzle_>
void print_cfg(PerfCfg<smempipe_, regpipe_, use_ldsm_, swizzle_> const& cfg, std::string prefix = "") {
    std::cout << "PerfCfg:\n";
    std::cout << prefix << "  smempipe: " << cfg.smempipe << "\n";
    std::cout << prefix << "  regpipe: " << cfg.regpipe << "\n";
    std::cout << prefix << "  use_ldsm: " << cfg.use_ldsm << "\n";
    std::cout << prefix << "  swizzle: " << cfg.swizzle << "\n";
}

} // namespace vidrial

