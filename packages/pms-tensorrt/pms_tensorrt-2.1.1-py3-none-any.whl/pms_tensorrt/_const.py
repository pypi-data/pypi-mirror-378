import os
import asyncio
import numpy as np
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, List, Generator, Iterable, Union, Optional, Tuple, TypeVar
from enum import Enum, auto, unique

T = TypeVar("T")  # T 대신 다른 문자/단어를 써도 되지만 일반적으로 T를 사용합니다.
