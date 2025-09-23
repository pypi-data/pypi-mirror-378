import ctypes, os
from typing import Any, Generator, TypeVar
import numpy as np
import tensorrt as trt
import cuda.bindings.driver as cu
import cuda.bindings.runtime as rt

T = TypeVar("T")


def is_success(err: tuple[cu.CUresult, object] | cu.CUresult):
    if isinstance(err, tuple):
        err = err[0]
    assert err.real == cu.CUresult.CUDA_SUCCESS, f"CUDA error: {err}"


# --- Device / Context ---


def select_device(device_id: int):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = str(device_id)
    os.environ["CUDA_DEVICE"] = str(device_id)

    is_success(cu.cuInit(0))
    # 마스킹 후 보이는 0번이 곧 요청한 device임
    err, dev = cu.cuDeviceGet(0)
    is_success(err)
    err, ctx = cu.cuDevicePrimaryCtxRetain(dev)
    is_success(err)
    is_success(cu.cuCtxSetCurrent(ctx))
    return dev, ctx


def get_device_count() -> int:
    is_success(cu.cuInit(0))
    err, n = cu.cuDeviceGetCount()
    is_success(err)
    return int(n)


def get_device_list() -> list[str]:
    # 이름은 Runtime API로 조회 (안전)
    err, n = rt.cudaGetDeviceCount()
    assert err == rt.cudaError_t.cudaSuccess, err
    names = []
    for i in range(n):
        err, props = rt.cudaGetDeviceProperties(i)
        assert err == rt.cudaError_t.cudaSuccess, err
        names.append(props.name.decode("utf-8"))
    return names


def mem_alloc_pagelocked(shape: list[int], dtype: np.dtype) -> np.ndarray:
    nelem = trt.volume(shape)
    itemsize = np.dtype(dtype).itemsize
    nbytes = nelem * itemsize
    err, hptr = rt.cudaHostAlloc(nbytes, rt.cudaHostAllocPortable)
    assert err == rt.cudaError_t.cudaSuccess, err
    buf = (ctypes.c_byte * nbytes).from_address(hptr)
    arr = np.frombuffer(buf, dtype=dtype, count=nelem)
    # 필요하면: arr.shape = tuple(shape)
    return arr


def mem_alloc_device(size: int) -> int:
    err, dptr = cu.cuMemAlloc(size)
    is_success(err)
    return int(dptr)  # CUdeviceptr


def set_context_tensor_address(context: Any, name: str, device_ptr: int):
    context.set_tensor_address(name, device_ptr)


def create_stream():
    err, stream = cu.cuStreamCreate(0)
    is_success(err)
    return stream


def synchronize_stream(stream):
    rt.cudaStreamSynchronize(stream)


def destroy_stream(stream):
    rt.cudaStreamDestroy(stream)


def mem_copy_htod(host_memory: np.ndarray, device_ptr: int):
    is_success(cu.cuMemcpyHtoD(device_ptr, host_memory, host_memory.nbytes))


def mem_copy_dtoh(device_ptr: int, host_memory: np.ndarray):
    is_success(cu.cuMemcpyDtoH(host_memory, device_ptr, host_memory.nbytes))


# --- misc ---


def batch(target_list: list[T], batch_size: int) -> Generator[list[T], None, None]:
    l = len(target_list)
    for ndx in range(0, l, batch_size):
        yield target_list[ndx : min(ndx + batch_size, l)]
