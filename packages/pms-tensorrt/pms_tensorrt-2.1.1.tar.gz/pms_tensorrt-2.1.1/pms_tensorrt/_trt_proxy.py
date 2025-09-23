from pms_tensorrt._const import *
from pms_tensorrt._utils import (
    get_device_count,
    get_device_list,
    select_device,
    create_stream,
    synchronize_stream,
    destroy_stream,
)
from pms_tensorrt._logger import LoguruTRTLogger, SeverityType
import tensorrt as trt


class TRTProxy:

    def __init__(
        self,
        model_path: str,
        device_id: int,
    ) -> None:
        # check gpu
        device_count = get_device_count()
        assert device_count > 0, f"There is no device to alloc."
        assert (
            device_id < device_count
        ), f"num_devices: {device_count}, device_id={device_id} is not available."

        # set env
        # - ray 사용 시 CUDA_VISIBLE_DEVICES를 강제로 변경하는 상황 발생.
        # - 때문에 cuda.init 전에 CUDA_VISIBLE_DEVICES를 초기화한다.
        os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
        os.environ["CUDA_VISIBLE_DEVICES"] = str(
            [i for i in range(device_count)]
        ).replace(" ", "")[1:-1]

        # init cuda
        # cuda.init()

        self._model_path = model_path
        self._device_id = device_id
        self._target_device = get_device_list()[device_id]

        # init
        # import pycuda.autoinit
        # self._device = Device(device_id)
        # self._context = self._device.set_current()
        self._device, self._context = select_device(self._device_id)

        # Create Logger
        self._logger = LoguruTRTLogger()

        # Load TRT runtime and deserialize engine
        with open(model_path, "rb") as f:  # type: ignore
            self._runtime = trt.Runtime(self._logger)
            assert self._runtime
            self._engine = self._runtime.deserialize_cuda_engine(f.read())
            assert self._engine

        # Create exec context
        self._execution_context = self._engine.create_execution_context()
        assert self._execution_context

        # Create Stream
        self._stream = create_stream()

    def __del__(self):
        if self._context is not None:
            self._context.pop()  # destruct context
            self._context = None
        if self._stream is not None:
            destroy_stream(self._stream)
            self._stream = None

    @property
    def logger(self) -> LoguruTRTLogger:
        return self._logger

    @property
    def target_device(self) -> str:
        return self._target_device

    @property
    def engine(self) -> Any:
        return self._engine

    @property
    def execution_context(self) -> Any:
        return self._execution_context

    @property
    def stream(self) -> Any:
        return self._stream

    @property
    def num_devices(self) -> int:
        return get_device_count()
