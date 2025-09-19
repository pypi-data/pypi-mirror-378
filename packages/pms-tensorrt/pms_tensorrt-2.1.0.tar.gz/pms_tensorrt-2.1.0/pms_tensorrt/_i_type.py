from pms_tensorrt._const import *


class IType(Enum):
    Logger = auto()
    Profiler = auto()
    Builder = auto()
    Network = auto()
    Parser = auto()
    IOptimizationProfile = auto()
    IBuilderConfig = auto()
    NetworkDefinitionCreationFlag = auto()
    ICudaEngine = auto()
    IExecutionContext = auto()
    Runtime = auto()
    Refitter = auto()
    IErrorRecorder = auto()
    ITimingCache = auto()
    GPU_Allocator = auto()
    AllocatorFlag = auto()
    IGpuAllocator = auto()
    EngineInspector = auto()
    OnnxParser = auto()
