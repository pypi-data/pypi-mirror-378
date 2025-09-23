import concurrent.futures
import copy
from dataclasses import dataclass
from typing import Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from vidrial.jit.compiler import compile, compiler_flags, get_kernel_hash, hash_to_hex, get_nvcc_compiler, DEFAULT_INCLUDE_DIRS
from vidrial.jit.runtime import Runtime
from vidrial.jit.package import register_runtime
from vidrial.jit.settings import settings
from tqdm import tqdm
import os
import logging

logger = logging.getLogger(__name__)
DEFAULT_JIT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.jit_cache')

COMPILATION_JOBS = set()

@dataclass(frozen=True)
class CompilationJob:
    code: str
    include_dirs: tuple[str]
    arch: str
    flags: tuple[str]
    path: str

def build_path(name: str, code: str, root: str, flags: list[str] = []):
    signature = f'{name}$${get_kernel_hash(code)}$${code}$${get_nvcc_compiler()}$${flags}'
    name = f'kernel.{name}.{hash_to_hex(signature)}'
    return f'{root}/{name}'


def render(template: str, template_params: dict[str, Any]) -> str:
    """Format a C++ template string with the given template parameters.
    
    Args:
        template: The template string with {key} placeholders
        template_params: Dictionary of template parameter values
        
    Returns:
        The formatted string with all {key} placeholders replaced
    """
    new_template = copy.deepcopy(template)
    for key, value in template_params.items():
        if hasattr(value, 'to_cpp'):
            value = value.to_cpp()
        elif isinstance(value, bool):
            value = 'true' if value else 'false'
        new_template = new_template.replace(f'{{{key}}}', str(value))
    return new_template


def jit(name: str, code: str, include_dirs: Optional[tuple[str]] = None, arch: Optional[str] = None, root: Optional[str] = None, flags: Optional[list[str]] = None) -> Runtime:
    """ Just-in-time compile a function.

    Args:
        name: The name of the function to compile.
        code: The code of the function to compile.
        include_dirs: The include directories to use for the compilation.
        arch: The architecture to use for the compilation.
        root: The root directory to store the compiled function.
        flags: The flags to use for the compilation.

    Returns:
        A Runtime callable that can be used to call the compiled function.
    """
    if flags is None:
        flags = compiler_flags(arch)
    if include_dirs is None:
        include_dirs = DEFAULT_INCLUDE_DIRS
    if root is None:
        root = DEFAULT_JIT_ROOT
    
    path = build_path(name=name, code=code, root=root, flags=flags)
    logger.info(f'Calling jit funciton: path= {path}')
    register_runtime(name, path)
    if settings.precompile:
        logger.debug(f'Adding Compilation Job with path={path}')
        COMPILATION_JOBS.add(CompilationJob(code=code, include_dirs=include_dirs, arch=arch, flags=tuple(flags), path=path))
        return lambda *args, **kwargs: 0 # return dummy runtime with no errors
    if Runtime.is_path_valid(path):
        logger.info(f'Using cached runtime')
        runtime = Runtime(path)
    else:
        logger.info(f'Compiling runtime')
        runtime = compile(code=code, include_dirs=include_dirs, arch=arch, path=path, flags=flags)
    logger.debug(f'Returning runtime')
    return runtime

def precompile():
    if not COMPILATION_JOBS:
        logger.debug("No compilation jobs to precompile")
        return
    num_workers = min(settings.max_workers, len(COMPILATION_JOBS))
    logger.info(f"Precompiling {len(COMPILATION_JOBS)} jobs with {num_workers} workers")
    def precompile_job(job: CompilationJob):
        if not Runtime.is_path_valid(job.path):
            runtime = compile(code=job.code, include_dirs=job.include_dirs, arch=job.arch, path=job.path, flags=job.flags)
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(precompile_job, job) for job in COMPILATION_JOBS]
        with tqdm(total=len(futures), desc="Precompiling", disable=not settings.verbose) as pbar:
            for future in as_completed(futures):
                pbar.update(1)
                try:
                    future.result()  # This will raise any exceptions that occurred
                except Exception as e:
                    if not settings.allow_failure:
                        raise e
                    if settings.verbose:
                        logger.warning(f"Error during precompilation: {e}")
                    else:
                        logger.debug(f"Error during precompilation: {e}")
    
    logger.info("Precompilation completed")
    COMPILATION_JOBS.clear()  # Clear the jobs after compilation

