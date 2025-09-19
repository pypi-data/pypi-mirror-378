from pms_tensorrt._const import *
import tensorrt as trt
from loguru import logger as _logger_proxy


@unique
class SeverityType(Enum):
    INTERNAL_ERROR = auto()
    ERROR = auto()
    WARNING = auto()
    INFO = auto()
    VERBOSE = auto()


LOG_TYPE_CONVERT_MAP = {
    trt.ILogger.INTERNAL_ERROR: SeverityType.INTERNAL_ERROR,
    trt.ILogger.ERROR: SeverityType.ERROR,
    trt.ILogger.WARNING: SeverityType.WARNING,
    trt.ILogger.INFO: SeverityType.INFO,
    trt.ILogger.VERBOSE: SeverityType.VERBOSE,
}

LOG_CALLER_MAP = {
    SeverityType.INTERNAL_ERROR: _logger_proxy.critical,
    SeverityType.ERROR: _logger_proxy.error,
    SeverityType.WARNING: _logger_proxy.warning,
    SeverityType.INFO: _logger_proxy.info,
    SeverityType.VERBOSE: _logger_proxy.debug,
}


class LoguruTRTLogger(trt.ILogger):

    def __init__(self):
        trt.ILogger.__init__(self)

    def log(self, severity: Union[SeverityType, Any], msg: str):
        if type(severity) is not SeverityType:
            severity = LOG_TYPE_CONVERT_MAP[severity]
        LOG_CALLER_MAP[severity](msg)
