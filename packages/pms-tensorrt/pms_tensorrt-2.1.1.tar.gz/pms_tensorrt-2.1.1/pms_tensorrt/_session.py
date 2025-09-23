from pms_tensorrt._const import *
from pms_tensorrt._trt_proxy import TRTProxy
from pms_tensorrt._tensor_mode import TensorMode
from pms_tensorrt._tensor_binding import TensorBinding
from pms_tensorrt._utils import synchronize_stream


class TRTSession:

    def __init__(
        self,
        model_path: str,
        device_id: int,
        io_shapes: dict[str, tuple[list[int], np.dtype]],
    ) -> None:
        self.model_path = model_path
        self.io_shapes = io_shapes

        # create proxy
        self._trt_proxy = TRTProxy(model_path=model_path, device_id=device_id)
        # Setup I/O Bindings
        self._input_bindings: list[TensorBinding] = []
        self._output_bindings: list[TensorBinding] = []
        for i in range(self._trt_proxy.engine.num_io_tensors):
            binding = TensorBinding(
                engine=self._trt_proxy.engine,
                context=self._trt_proxy.execution_context,
                binding_index=i,
            )
            binding.bind(*io_shapes[binding.name])
            if binding.mode == TensorMode.INPUT:
                self._input_bindings.append(binding)
                assert -1 not in self._trt_proxy.execution_context.get_tensor_shape(
                    binding.name
                ), f"ERROR, The shape is not fixed."
            elif binding.mode == TensorMode.OUTPUT:
                self._output_bindings.append(binding)
            else:
                raise NotImplementedError(binding.mode)

    def upload(self):
        [binding.upload() for binding in self._input_bindings]

    def inference(self):
        self._trt_proxy.execution_context.execute_async_v3(
            stream_handle=self._trt_proxy.stream,
        )
        synchronize_stream(self._trt_proxy.stream)

    def download(self):
        [binding.download() for binding in self._output_bindings]

    def set_input(
        self,
        input_datas: list[np.ndarray],
    ):
        assert len(input_datas) == len(
            self._input_bindings
        ), f"ERROR, len(input_datas) != len(self.input_bindings)"
        for binding, input_data in zip(self._input_bindings, input_datas):
            input_data_r = input_data.ravel()
            assert (
                binding.host_buffer.shape == input_data_r.shape
            ), f"ERROR, binding.host_array.shape({binding.host_buffer.shape}) =! input_data_r.shape({input_data_r.shape})."
            np.copyto(
                dst=binding.host_buffer,
                src=input_data_r,
            )

    def get_output(
        self,
        output_datas: list[np.ndarray],
    ):
        assert all(
            [o.flags.contiguous for o in output_datas]
        ), "ERROR, ALL Vector must be contiguous."
        assert len(output_datas) == len(
            self._output_bindings
        ), f"ERROR, len(output_datas) != len(self.output_bindings)"
        for binding, output_data in zip(self._output_bindings, output_datas):
            output_data_r = output_data.ravel()
            assert (
                binding.host_buffer.shape == output_data_r.shape
            ), f"ERROR, binding.host_array.shape({binding.host_buffer.shape}) =! output_data_r.shape({output_data_r.shape})."
            np.copyto(
                dst=output_data_r,
                src=binding.host_buffer,
            )

    def run(
        self,
        input_datas: Optional[list[np.ndarray]] = None,
        output_datas: Optional[list[np.ndarray]] = None,
    ) -> None:
        # Set input
        if input_datas is not None:
            self.set_input(input_datas=input_datas)

        # Host to Device
        self.upload()

        # Inference
        self.inference()

        # Device to Host
        self.download()

        # Get output
        if output_datas is not None:
            self.get_output(output_datas=output_datas)

    async def run_async(
        self,
        input_datas: Optional[list[np.ndarray]] = None,
        output_datas: Optional[list[np.ndarray]] = None,
    ) -> None:
        # upload & inference & download
        await asyncio.to_thread(
            self.run,
            input_datas=input_datas,
            output_datas=output_datas,
        )
