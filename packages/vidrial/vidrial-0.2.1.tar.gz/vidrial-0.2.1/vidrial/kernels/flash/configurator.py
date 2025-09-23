import torch
import logging
import pandas as pd
from functools import lru_cache, partial
import random
from dataclasses import dataclass
from typing import List, Iterable, Any
from itertools import product
from math import prod
from copy import copy
from vidrial.kernels.mma_configurator import SMEM_LIMIT, MAX_THREADS_PER_BLOCK, evenly_divides, reasonable_atom_placements, dtype_to_bytes, static_shape, MMAAtom, safe_filter, REG_PER_SM, get_largest_atoms, SM_NUMBER, torch_dtype_to_c, MMAAtom_registry

logger = logging.getLogger(__name__)

@dataclass
class FlashConfig:
    Atom1: MMAAtom
    Atom2: MMAAtom
    MNKTileShape1: tuple[int, ...]
    NTile2: int
    MNKAtomPlacement1: tuple[int, ...]
    dtype: torch.dtype
    acc_dtype: torch.dtype
    MNDEP: tuple[int, ...] # (seq_q, seq_k, d, e, batch_size)
    smempipe1: int = 1
    smempipe2: int = 1
    regpipe1: int = 1
    regpipe2: int = 1
    use_ldsm1: bool = True
    use_ldsm2: bool = True
    swizzle1: int = 1
    swizzle2: int = 1
    q_in_reg: bool = True
    max_smem: int = SMEM_LIMIT
    max_threads: int = MAX_THREADS_PER_BLOCK

    @property
    def thread_count(self):
        return self.Atom1.thread_count * prod(self.MNKAtomPlacement1) # type: ignore

    @property
    def MNKAtomPlacement2(self):
        """Use second MMA's atom placement for filters like register estimate"""
        m_placement_1, n_placement_1, k_placement_1 = self.MNKAtomPlacement1
        total_atoms = self.thread_count // self.Atom1.thread_count
        atom1_shape = self.Atom1.MNK
        atom2_shape = self.Atom2.MNK
        m_placement_2 = m_placement_1 * atom1_shape[0] // atom2_shape[0]
        k_placement_2 = n_placement_1 * atom1_shape[1] // atom2_shape[1]
        n_placement_2 = total_atoms // (m_placement_2 * k_placement_2)
        assert n_placement_2 >= 1, "N_placement_2 must be at least 1"
        return (m_placement_2, n_placement_2, k_placement_2)
    
    @property
    def MNKP(self):
        """The MNKP of the second mma"""
        return (self.MNDEP[0], self.MNDEP[-2], self.MNDEP[1], self.MNDEP[-1])
    
    @property
    def MNKTileShape2(self):
        return (self.MNKTileShape1[0], self.NTile2, self.MNKTileShape1[1])
    
    @property
    def smem_estimate(self):
        M_tile_1, N_tile_1, d_tile_1 = self.MNKTileShape1
        Q_smem = M_tile_1 * self.MNDEP[2] * dtype_to_bytes(self.dtype)
        K_smem = N_tile_1 * d_tile_1 * dtype_to_bytes(self.dtype) * self.smempipe1
        V_smem = N_tile_1 * d_tile_1 * dtype_to_bytes(self.dtype) * self.smempipe2
        O_smem = M_tile_1 * N_tile_1 * dtype_to_bytes(self.dtype)
        l_smem = M_tile_1 * dtype_to_bytes(self.acc_dtype)
        if self.q_in_reg:
            return max(Q_smem, K_smem + V_smem, O_smem + l_smem)
        else:
            return max(Q_smem + K_smem + V_smem, O_smem + l_smem)

    @property
    def register_estimate(self):
        M_tile_1, N_tile_1, K_tile_1 = self.MNKTileShape1
        M_tile_2, N_tile_2, K_tile_2 = M_tile_1, self.NTile2, N_tile_1
        Q_reg = M_tile_1 * K_tile_1 // self.regpipe1 if not self.q_in_reg else M_tile_1 * self.MNDEP[2]
        K_reg = N_tile_1 * K_tile_1 // self.regpipe1
        S_reg = M_tile_2 * N_tile_1
        V_reg = N_tile_2 * K_tile_2 // self.regpipe2
        O_reg = M_tile_2 * N_tile_2
        if self.q_in_reg:
            return max(Q_reg + K_reg + S_reg, Q_reg + S_reg + V_reg + O_reg)
        else:
            return max(Q_reg + K_reg + S_reg, S_reg + V_reg + O_reg)
        
    @property
    def rest_m_1(self):
        return self.MNKTileShape1[0] // (self.Atom1.MNK[0] * self.MNKAtomPlacement1[0])
    
    @property
    def rest_n_1(self):
        return self.MNKTileShape1[1] // (self.Atom1.MNK[1] * self.MNKAtomPlacement1[1])
    
    @property
    def rest_k_1(self):
        return self.MNKTileShape1[2] // (self.Atom1.MNK[2] * self.MNKAtomPlacement1[2])
    
    @property
    def rest_m_2(self):
        return self.MNKTileShape2[0] // (self.Atom2.MNK[0] * self.MNKAtomPlacement2[0])
    
    @property
    def rest_n_2(self):
        return self.MNKTileShape2[1] // (self.Atom2.MNK[1] * self.MNKAtomPlacement2[1])
    
    @property
    def rest_k_2(self):
        return self.MNKTileShape2[2] // (self.Atom2.MNK[2] * self.MNKAtomPlacement2[2])

    @property
    def register_per_thread_estimate(self):
        rest_k_q = self.rest_k_1 // self.regpipe1 if not self.q_in_reg else self.MNDEP[2] // (self.Atom1.MNK[2] * self.MNKAtomPlacement1[2])
        Q_reg = self.Atom1.MNK[0] * self.Atom1.MNK[2] * self.rest_m_1 * rest_k_q // self.Atom1.thread_count
        K_reg = self.Atom1.MNK[1] * self.Atom1.MNK[2] * self.rest_n_1 * self.rest_k_1 // self.regpipe1 // self.Atom1.thread_count
        S_reg = self.Atom1.MNK[0] * self.Atom1.MNK[1] * self.rest_m_1 * self.rest_n_1 // self.Atom1.thread_count
        V_reg = self.Atom2.MNK[1] * self.Atom2.MNK[2] * self.rest_n_2 * self.rest_k_2 // self.regpipe2 // self.Atom2.thread_count
        O_reg = self.Atom2.MNK[0] * self.Atom2.MNK[1] * self.rest_m_2 * self.rest_n_2 // self.Atom2.thread_count
        if self.q_in_reg:
            return max(Q_reg + K_reg + S_reg, Q_reg + S_reg + V_reg + O_reg)
        else:
            return max(Q_reg + K_reg + S_reg, S_reg + V_reg + O_reg)

def get_valid_atoms(MNKTileShape, dtype, acc_dtype):
    """Returns all the atoms that evenly divide the tile shape and which have compatible types
    """
    Dtype = torch_dtype_to_c(dtype)
    AccDtype = torch_dtype_to_c(acc_dtype)
    valid_atoms = []
    for atom in [a for a in MMAAtom_registry.values() if not a.name.startswith('UniversalFMA')]:
        divides = evenly_divides(MNKTileShape, atom.MNK)
        valid_types = atom.A_type.value == Dtype and atom.B_type.value == Dtype and atom.C_type.value == AccDtype and atom.D_type.value == AccDtype
        if divides and valid_types:
            valid_atoms.append(atom)
    return valid_atoms

def reasonable_MNK_tile_shapes(M=None, N=None, K=None, MNK=None):
    """Generate a list of reasonable tile shapes for the MMA problem.
    """
    default_sizes = {1, 2, 4, 8, 16, 32, 64, 128}
    K_default_sizes = {1, 2, 4, 8, 16, 32, 64, 96, 128}
    M_sizes = default_sizes if M is None else {M,}
    N_sizes = default_sizes if N is None else {N,}
    K_sizes = K_default_sizes if K is None else {K,}
    for M in list(M_sizes):
        for N in list(N_sizes):
            for K in list(K_sizes):
                yield (M, N, K)

def second_mma_atom(atom, MNKTileShape, N_tile, dtype, acc_dtype):
    M_tile_1, N_tile_1, _ = MNKTileShape
    Tile = (M_tile_1, N_tile, N_tile_1)
    return get_valid_atoms(Tile, dtype, acc_dtype)

def initial_config_sweep(MNDEP, dtype, acc_dtype, M_tile=None, N_tile=None, K_tile=None, max_smem=SMEM_LIMIT, max_threads=MAX_THREADS_PER_BLOCK) -> list[FlashConfig]:
    configs = []
    MNK = MNDEP[:-2]
    E = MNDEP[-2]
    # Generate an initial large list of reasonable configs
    for MNKTileShape in reasonable_MNK_tile_shapes(M_tile, N_tile, K_tile, MNK):
        if not evenly_divides(MNK, MNKTileShape):
            continue
        for atom in get_valid_atoms(MNKTileShape, dtype, acc_dtype):
            for MNKAtomPlacement in reasonable_atom_placements(MNKTileShape, atom, max_threads):
                for NTile2 in {32, 64, 128}:
                    if E % NTile2 != 0:
                        continue
                    for atom2 in second_mma_atom(atom, MNKTileShape, NTile2, dtype, acc_dtype):
                        configs.append(FlashConfig(
                            Atom1=atom,
                            Atom2=atom2,
                            MNKTileShape1=MNKTileShape,
                            NTile2=NTile2,
                            MNKAtomPlacement1=MNKAtomPlacement,
                            dtype=dtype,
                            acc_dtype=acc_dtype,
                            MNDEP=MNDEP,
                        ))
    logger.info(f"Generated {len(configs)} initial mma configs")
    return configs


@safe_filter
def register_spillage_filter(spillage, configs):
    # We want to avoid register spillage both on per thread level and on per SM level
    configs = [c for c in configs if c.register_estimate <= REG_PER_SM and c.register_per_thread_estimate <= (255 + (spillage if c.q_in_reg else 0))]
    logger.info(f"Filtered to {len(configs)} flash configs for register spillage")
    return configs

@safe_filter
def register_underutil_filter(level, configs):
    # We want to avoid underutilizing the registers, if we are using < x% of
    # max registers, we filter out the configs that are underutilized
    top_usage = sorted([c.register_estimate for c in configs], reverse=True)[0]
    configs = [c for c in configs if c.register_estimate >= top_usage * level]
    logger.info(f"Filtered to {len(configs)} flash configs for register underutilization")
    return configs

@safe_filter
def smem_underutil_filter(level, configs):
    # We want to avoid underutilizing the smem, if we are using < x% of
    # max smem, we filter out the configs that are underutilized
    top_usage = sorted([c.smem_estimate for c in configs], reverse=True)[0]
    configs = [c for c in configs if c.smem_estimate >= top_usage * level]
    logger.info(f"Filtered to {len(configs)} flash configs for smem underutilization")
    return configs

@safe_filter
def regpipe_filter(regpipes, configs):
    # Filter out configs that use regpipe other than the ones we want to use
    configs = [c for c in configs if c.regpipe1 in regpipes and c.regpipe2 in regpipes]
    logger.info(f"Filtered to {len(configs)} flash configs for regpipe")
    return configs

@safe_filter
def smempipe_filter(smempipes, configs):
    # Filter out configs that use smempipe other than the ones we want to use
    configs = [c for c in configs if c.smempipe1 in smempipes and c.smempipe2 in smempipes]
    logger.info(f"Filtered to {len(configs)} flash configs for smempipe")
    return configs

@safe_filter
def warp_filter(num_warps, configs):
    # Filter out configs that use more warps than the number of warps we want to use
    configs = [c for c in configs if prod(c.MNKAtomPlacement1) <= num_warps]
    logger.info(f"Filtered to {len(configs)} flash configs for warp size")
    return configs

@safe_filter
def top_mtile_filter(top_k, configs):
    top_m_tiles = sorted([c.MNKTileShape1[0] for c in configs], reverse=True)[:top_k]
    configs = [c for c in configs if c.MNKTileShape1[0] in top_m_tiles]
    logger.info(f"Filtered to {len(configs)} flash configs for top mtile")
    return configs

@safe_filter
def thread_count_filter(configs):
    # If the candiate configs don't even use a full warp, pick the largerst one (relevant for small problems)
    thread_counts = [c.thread_count for c in configs]
    max_thread_count = max(thread_counts)
    if max_thread_count <= 32:
        configs = [c for c, t in zip(configs, thread_counts) if t == max_thread_count]

    # If there are configs that use multiples of 32 threads filter out the rest
    if any([t % 32 == 0 for t in thread_counts]):
        configs = [c for c, t in zip(configs, thread_counts) if t % 32 == 0]
    logger.info(f"Filtered to {len(configs)} flash configs due to thread count")
    return configs

@safe_filter
def atom_size_filter(configs):
    # Use the largest possible atom. Avoid benchmarking smaller instructions. TODO: verify this is a good idea
    largest_atom2s = get_largest_atoms([c.Atom2 for c in configs])
    configs = [c for c in configs if c.Atom2 in largest_atom2s]
    largest_atom1s = get_largest_atoms([c.Atom1 for c in configs])
    configs = [c for c in configs if c.Atom1 in largest_atom1s]
    logger.info(f"Filtered to {len(configs)} flash configs for largest atoms")
    return configs

@safe_filter
def saturation_filter(configs):
    MNKP = configs[0].MNKP
    # If the problem does not saturate the GPU, pick the config with the largest number of C tiles
    batch_size = MNKP[3] if isinstance(MNKP[3], int) else prod(MNKP[3])
    C_tile_nums = [ (MNKP[0]//c.MNKTileShape2[0]) * (MNKP[1]//c.MNKTileShape2[1]) * batch_size for c in configs]
    max_C_tile_num = max(C_tile_nums)
    if max_C_tile_num < SM_NUMBER:
        configs = [c for c, C_tile_num in zip(configs, C_tile_nums) if C_tile_num == max_C_tile_num]
    logger.info(f"Filtered to {len(configs)} flash configs for C tile count")
    return configs

@safe_filter
def arithmetic_intensity_filter(min_MN_tile_size, configs):
    # We want to pick as large a MNTile as possible to imporove arithmetic intensity
    MN_tile_sizes = [c.MNKTileShape2[0] * c.MNKTileShape2[1] for c in configs]
    if any([MN_tile_size > min_MN_tile_size for MN_tile_size in MN_tile_sizes]):
        configs = [c for c, MN_tile_size in zip(configs, MN_tile_sizes) if MN_tile_size >= min_MN_tile_size]
    logger.info(f"Filtered to {len(configs)} flash configs for large MN tile size")
    return configs

@safe_filter
def atom_placement_filter(configs):
    # we only pick atom placement that has k placement = 1
    configs = [c for c in configs if c.MNKAtomPlacement1[2] == 1 and c.MNKAtomPlacement2[2] == 1 and c.MNKAtomPlacement1[0] >= 1 and c.MNKAtomPlacement2[1] >= 1]
    logger.info(f"Filtered to {len(configs)} flash configs for atom placement")
    return configs

@safe_filter
def max_k_tile_filter(max_k_tile_num, configs):
    # we don't want there to be too many k tiles for the first mma
    configs = [c for c in configs if c.MNDEP[2] // c.MNKTileShape1[2] <= max_k_tile_num]
    logger.info(f"Filtered to {len(configs)} flash configs for max k tile number")
    return configs


def adjust_config(config: FlashConfig):
    """There're parameters that are being min/maxed inside the kernel, so we can prune them here"""
    config.smempipe2 = min(config.smempipe2, config.MNDEP[1] // config.MNKTileShape2[2])
    config.smempipe1 = config.smempipe2 * (config.MNDEP[2] // config.MNKTileShape1[2])
    config.regpipe1 = min(config.regpipe1, config.rest_k_1)
    config.regpipe2 = min(config.regpipe2, config.rest_k_2)
    return config


def deduplicate(configs: List[FlashConfig]) -> List[FlashConfig]:
    """Deduplicate configs using hash of the entire config."""
    seen = set()
    unique = []
    for config in configs:
        key = hash(str(config))
        if key not in seen:
            seen.add(key)
            unique.append(config)
    logger.info(f"Deduplicated {len(configs)} configs to {len(unique)} unique configs")
    return unique


def performance_expansion(configs: List[FlashConfig], smempipe=None, regpipe=None, use_ldsm=None, swizzle=None, q_in_reg=None):
    smempipes = [1, 2] if smempipe is None else (smempipe,) if not isinstance(smempipe, Iterable) else smempipe
    regpipes = [1] if regpipe is None else (regpipe,) if not isinstance(regpipe, Iterable) else regpipe
    use_ldsms = [True] if use_ldsm is None else (use_ldsm,) if not isinstance(use_ldsm, Iterable) else use_ldsm
    swizzles = [1] if swizzle is None else (swizzle,) if not isinstance(swizzle, Iterable) else swizzle
    q_in_regs = [True, False] if q_in_reg is None else (q_in_reg,) if not isinstance(q_in_reg, Iterable) else q_in_reg
    new_configs = []
    for config in configs:
        for smempipe, regpipe1, regpipe2, use_ldsm1, use_ldsm2, swizzle1, swizzle2, q_in_reg in product(smempipes, regpipes, regpipes, use_ldsms, use_ldsms, swizzles, swizzles, q_in_regs):
            c = copy(config)
            if (c.MNDEP[1] // c.MNKTileShape2[2]) < smempipe:
                continue
            c.smempipe1 = smempipe * (c.MNDEP[2] // c.MNKTileShape1[2])
            c.regpipe1 = regpipe1
            c.use_ldsm1 = use_ldsm1
            c.swizzle1 = swizzle1
            c.smempipe2 = smempipe
            c.regpipe2 = regpipe2
            c.use_ldsm2 = use_ldsm2
            c.swizzle2 = swizzle2
            c.q_in_reg = q_in_reg
            if c.smem_estimate > SMEM_LIMIT:
                continue
            new_configs.append(c)
    new_configs = [adjust_config(c) for c in new_configs]
    new_configs = deduplicate(new_configs)
    logger.info(f"Expanded to {len(new_configs)} configs with smempipe, regpipe, use_ldsm, swizzle for mma")
    return new_configs

def print_configs_table(configs: List[FlashConfig], max_rows: int = 50):
    """Print FlashConfig objects in a nicely formatted table."""
    if not configs:
        print("No configs to display.")
        return
    
    # Prepare the data for the table
    headers = [
        "ID", "Smem(KB)", "Reg/SM", "Reg/Th", "Th", "Atom1", "Atom2", "MNKTile1", "MNKPlace1", "NTile2", 
        "SMPipe1", "SMPipe2",
        "RegPipe1", "RegPipe2", "LDSM1", "LDSM2", "Swiz1", "Swiz2", "QinReg", 
    ]
    
    table_data = []
    for idx, c in enumerate(configs[:max_rows]):
        row = [
            idx,
            f"{c.smem_estimate / 1024:.1f}",
            c.register_estimate,
            c.register_per_thread_estimate,
            c.thread_count,
            c.Atom1.name,
            c.Atom2.name,
            f"{c.MNKTileShape1[0]}x{c.MNKTileShape1[1]}x{c.MNKTileShape1[2]}",
            f"{c.MNKAtomPlacement1[0]}x{c.MNKAtomPlacement1[1]}x{c.MNKAtomPlacement1[2]}",
            c.NTile2,
            c.smempipe1,
            c.smempipe2,
            c.regpipe1,
            c.regpipe2,
            "Y" if c.use_ldsm1 else "N",
            "Y" if c.use_ldsm2 else "N", 
            c.swizzle1,
            c.swizzle2,
            "Y" if c.q_in_reg else "N"
        ]
        table_data.append(row)
    
    # Print the table
    df = pd.DataFrame(table_data, columns=headers)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    logger.debug(f"\nFlash Attention Configurations ({len(configs)} total, showing first {min(len(configs), max_rows)}):")
    logger.debug(f"\n{df}")
    
    # Print summary statistics
    logger.debug("\nSummary Statistics:")
    logger.debug(f"  Total configs: {len(configs)}")
    logger.debug(f"  Thread counts: {min(c.thread_count for c in configs)} - {max(c.thread_count for c in configs)}")
    logger.debug(f"  SMEM usage (KB): {min(c.smem_estimate / 1024 for c in configs):.1f} - {max(c.smem_estimate / 1024 for c in configs):.1f}")
    logger.debug(f"  Register/SM: {min(c.register_estimate for c in configs)} - {max(c.register_estimate for c in configs)}")
    logger.debug(f"  Register/Thread: {min(c.register_per_thread_estimate for c in configs)} - {max(c.register_per_thread_estimate for c in configs)}")

def render_configs(configs: List[FlashConfig]):
    new_configs = [
        {
            'Atom1': c.Atom1.name,
            'Atom2': c.Atom2.name,
            'MNKTileShape1': static_shape(c.MNKTileShape1),
            'MNKAtomPlacement1': static_shape(c.MNKAtomPlacement1),
            'NTile2': c.NTile2,
            **{k: v for k, v in c.__dict__.items() if k in ['smempipe1', 'regpipe1', 'use_ldsm1', 'swizzle1', 'smempipe2', 'regpipe2', 'use_ldsm2', 'swizzle2', 'q_in_reg']}
        }
        for c in configs
    ]
    logger.info(f"Filtered to {len(new_configs)} flash configs for kernel compatibility")
    return new_configs

def make_configurator(filter_funcs):
    @lru_cache(maxsize=None)
    def configurator(MNDEP, dtype, acc_dtype, M_tile=None, N_tile=None, K_tile=None, max_smem=SMEM_LIMIT, max_threads=MAX_THREADS_PER_BLOCK, smempipe=None, regpipe=None, use_ldsm=None, swizzle=None, q_in_reg=None, random_seed=None) -> list[dict[str, Any]]:
        configs = initial_config_sweep(MNDEP, dtype, acc_dtype, M_tile, N_tile, K_tile, max_smem, max_threads)
        configs = performance_expansion(configs, smempipe=smempipe, regpipe=regpipe, use_ldsm=use_ldsm, swizzle=swizzle, q_in_reg=q_in_reg)
        for filter_func in filter_funcs:
            configs = filter_func(configs)
        if random_seed is not None:
            random.seed(random_seed)
            random.shuffle(configs)
        
        # Print configs in a nice table format
        print_configs_table(configs)
        
        configs = render_configs(configs)
        return configs

    return configurator

no_filter_configurator = make_configurator([])

BASE_FILTERS = [
    atom_placement_filter,
    thread_count_filter, # For small problems, we want to use the maximum number of threads
    atom_size_filter, # Use the largest possible atom. Avoid benchmarking smaller instructions. TODO: verify this is a good idea
    partial(register_spillage_filter, 0), # Avoid register spillage
    saturation_filter, # If the problem does not saturate the GPU, pick the config with the largest number of C tiles
    partial(arithmetic_intensity_filter, 2048), # We want to pick as large a MNTile as possible to imporove arithmetic intensity
]

base_configurator = make_configurator(BASE_FILTERS)

ADVANCED_FILTERS = [
    atom_placement_filter,
    thread_count_filter,
    atom_size_filter,
    # partial(top_mtile_filter, 2), # We want to pick the top 2 mtiles
    partial(register_spillage_filter, 20), # Avoid register spillage
    saturation_filter,
    # partial(max_k_tile_filter, 2), # we don't want there to be too many k tiles for the first mma
    partial(arithmetic_intensity_filter, 2048),
    partial(smem_underutil_filter, 0.3), # Avoid underutilizing the smem relative to maximum smem usage
    partial(register_underutil_filter, 0.3), # Avoid underutilizing the registers relative to maximum register usage
    partial(warp_filter, 4), # Avoid using more warps than the number of warps we want to use
    partial(smempipe_filter, [1, 2, 3, 4]), # Smempipe 1 and 2 and 3 and 4 are the only ones we want to use
    partial(regpipe_filter, [1, 2]), # Regpipe 1 is probably good enough
]

advanced_configurator = make_configurator(ADVANCED_FILTERS)