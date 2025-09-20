__version__ = "1.6.0"
__description__ = "General-Validator is a universal batch data validator with detailed validation results."

# 导入基础类
from .base import BaseValidator
from .engine import ValidationResult, ValidationError, RuleResult, FieldResult


# 导入validate系列校验函数
from .validator import (
    validate,
    validate_not_empty,
    validate_when,
    validate_when_each,
    validate_list_when,
    validate_list,
    validate_nested,
    validator
)

# 导入check系列校验函数
from .checker import (
    check,
    check_not_empty,
    check_when,
    check_when_each,
    check_list_when,
    check_list,
    check_nested,
    checker
)

# 导入inspect系列校验函数
from .inspector import (
    inspect,
    inspect_not_empty,
    inspect_when,
    inspect_when_each,
    inspect_list_when,
    inspect_list,
    inspect_nested,
    inspector
)

__all__ = [
    # 版本信息
    "__version__", 
    "__description__",
    
    # validate系列校验函数（核心数据校验函数，支持极简校验语法，支持通配符，支持嵌套列表校验，支持链式调用，支持阈值模式，支持快速失败，支持多种结果返回模式-断言模式、字典模式、布尔模式）
    "validate",             # 通用校验函数
    "validate_not_empty",   # 非空校验函数
    "validate_when",        # 严格条件校验
    "validate_when_each",   # 逐项条件校验
    "validate_list_when",   # 列表条件校验
    "validate_list",        # validate_list_when的简化版，专门用于列表数据条件校验
    "validate_nested",      # 嵌套校验函数
    "validator",            # 链式校验函数

    # check系列校验函数（validate系列函数的布尔模式别名，校验成功返回True，校验失败返回False，适用于快速校验和判断、条件判断和流程控制、简单的质量控制）
    "check",                # 通用校验函数
    "check_not_empty",      # 非空校验函数
    "check_when",           # 严格条件校验
    "check_when_each",      # 逐项条件校验
    "check_list_when",      # check_when_each的简化版，专门用于列表数据条件校验
    "check_list",           # 列表校验函数
    "check_nested",         # 嵌套校验函数
    "checker",              # 链式校验函数

    # inspect系列校验函数（validate系列函数的字典模式别名， 返回详细的结构化字典信息，适用于API接口响应、可视化数据展示、详细的校验报告、数据分析和统计）
    "inspect",              # 通用校验函数
    "inspect_not_empty",    # 非空校验函数
    "inspect_when",         # 严格条件校验
    "inspect_when_each",    # 逐项条件校验
    "inspect_list_when",    # 列表条件校验
    "inspect_list",         # inspect_list_when的简化版，专门用于列表数据条件校验
    "inspect_nested",       # 嵌套校验函数
    "inspector",            # 链式校验函数

    # 数据结构和异常类
    "BaseValidator",        # 校验器基类
    "ValidationResult",     # 详细校验结果类
    "ValidationError",      # 校验失败异常类
    "RuleResult",           # 单个规则校验结果类
    "FieldResult",          # 单个字段校验结果类
]