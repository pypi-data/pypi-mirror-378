from pms_tensorrt._const import *
import tensorrt as trt

# import pycuda.driver as cuda  # ref : https://documen.tician.de/pycuda/install.html
from cuda.core.experimental import Device, LaunchConfig, Program, ProgramOptions, launch


def select_device(device_id: int):
    os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
    os.environ["CUDA_VISIBLE_DEVICES"] = f"{device_id}"
    os.environ["CUDA_DEVICE"] = f"{device_id}"


def mem_alloc_pagelocked(shape: List[int], dtype: np.dtype) -> np.ndarray:
    return cuda.pagelocked_empty(trt.volume(shape), dtype=dtype)


def mem_alloc_device(size: int) -> int:
    return cuda.mem_alloc(size)


def set_context_tensor_address(context: Any, name: str, device_ptr: int):
    context.set_tensor_address(name, device_ptr)


def mem_copy_htod(
    host_memory: np.ndarray,
    device_ptr: int,
):
    cuda.memcpy_htod(device_ptr, host_memory)


def mem_copy_dtoh(
    device_ptr: int,
    host_memory: np.ndarray,
):
    cuda.memcpy_dtoh(host_memory, device_ptr)


def get_device_list() -> List[str]:
    stdout = subprocess.check_output("nvidia-smi --list-gpus", shell=True)
    stdout_str = stdout.decode("utf-8")
    device_list = stdout_str.split("\n")[:-1]
    return device_list


def get_device_count() -> int:
    return len(get_device_list())


def batch(target_list: List[T], batch_size: int) -> Generator[List[T], None, None]:
    l = len(target_list)
    for ndx in range(0, l, batch_size):  # iterable 데이터를 배치 단위로 확인
        yield target_list[
            ndx : min(ndx + batch_size, l)
        ]  # batch 단위 만큼의 데이터를 반환
