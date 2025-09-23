from pms_tensorrt._const import *
from pms_tensorrt._logger import LoguruTRTLogger, SeverityType
from pms_tensorrt._i_type import IType
from pms_tensorrt._shape_profile import ShapeProfile
from pms_tensorrt._trt_builder_flag import TRTBuilderFlag
import tensorrt as trt


class EngineBuilder:
    # ref: https://docs.nvidia.com/deeplearning/tensorrt/api/python_api/index.html

    def __init__(self) -> None:
        self._logger = LoguruTRTLogger()
        self._trt_contexts = {}
        # create builder
        self[IType.Builder] = trt.Builder(self._logger)  # type: ignore
        # create network(empty)
        self[IType.Network] = self[IType.Builder].create_network(
            flags=1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)  # type: ignore
        )
        # create config(empty)
        self[IType.IBuilderConfig] = self[IType.Builder].create_builder_config()
        # create paser
        self[IType.OnnxParser] = trt.OnnxParser(  # type: ignore
            network=self[IType.Network],
            logger=self._logger,
        )
        self[IType.IOptimizationProfile] = self[
            IType.Builder
        ].create_optimization_profile()

    def __getitem__(self, key: IType) -> Any:
        return self._trt_contexts[key]

    def __setitem__(self, key: IType, value: Any):
        assert key not in self._trt_contexts, f"ERROR, The key '{key}' is alreay exist."
        self._trt_contexts[key] = value

    def build_from_onnx(
        self,
        onnx_path: str,
        plan_path: str,
        config_flags: List[TRTBuilderFlag] = [],
        shape_profiles: List[ShapeProfile] = [],
    ):
        assert os.path.exists(onnx_path), f"ERROR, The onnx_path is not exist."
        assert not os.path.exists(plan_path), f"ERROR, The plan_path is alreay exist."

        # parse onnx
        _onnx_parsing_result = self[IType.OnnxParser].parse_from_file(onnx_path)
        assert _onnx_parsing_result, f"ERROR, Fail to parsing onnx file at {onnx_path}."

        # set flags
        for flag in config_flags:
            self[IType.IBuilderConfig].set_flag(trt.BuilderFlag(flag.value))  # type: ignore

        # set profile
        for profile in shape_profiles:
            self[IType.IOptimizationProfile].set_shape(
                input=profile.name,
                min=profile.min_shape,
                opt=profile.opt_shape,
                max=profile.max_shape,
            )

        # apply the profile to config
        self[IType.IBuilderConfig].add_optimization_profile(
            self[IType.IOptimizationProfile]
        )

        # serializing
        serialized_network = self[IType.Builder].build_serialized_network(
            network=self[IType.Network],
            config=self[IType.IBuilderConfig],
        )

        # save engine file
        with open(plan_path, "wb") as f:
            f.write(serialized_network)
