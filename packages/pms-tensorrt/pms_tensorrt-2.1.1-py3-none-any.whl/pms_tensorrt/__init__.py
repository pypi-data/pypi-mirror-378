__TARGET_TRT_VERSION = "10.13"
try:
    import tensorrt as __trt

    for __v1, __v2 in zip(
        __TARGET_TRT_VERSION.split("."), __trt.__version__.split(".")
    ):
        assert (
            __v1 == __v2
        ), f"ERROR, TensorRT version is mismatch. Current version is {__trt.__version__}. But, the library need tensorrt=={__TARGET_TRT_VERSION}"
    from ._logger import LoguruTRTLogger
    from ._session import TRTSession
    from ._tensor_binding import TensorBinding
    from ._tensor_mode import TensorMode
    from ._trt_proxy import TRTProxy
    from ._utils import get_device_count, get_device_list, batch
    from ._i_type import IType
    from ._trt_builder_flag import TRTBuilderFlag
    from ._shape_profile import ShapeProfile
    from ._engine_builder import EngineBuilder
except Exception as ex:
    from loguru import logger as __logger

    __logger.critical(
        f"You CAN NOT import this package. Exception = {ex}\nNote: Since tensorrt does not support pep517, this package will not automatically install tensorrt."
    )

__version__ = "2.1.1"
