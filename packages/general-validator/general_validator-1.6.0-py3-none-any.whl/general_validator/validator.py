# -*- coding:utf-8 -*-
from .logger import log_debug, log_info, log_warning, log_error
from .base import BaseValidator
from .engine import ValidationEngine, ValidationResult, ValidationError, perform_item_wise_conditional_check, get_nested_value, parse_and_validate


"""
General-Validator 核心数据校验函数
"""


def validate(data, *validations, max_fail=None, fast_fail=True, output_format="summary", mode="assert", context=None) -> ValidationResult:
    """
    极简通用数据校验函数
    
    :param data: 要校验的数据
    :param validations: 校验规则，支持多种简洁格式
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）

    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 校验失败时抛出（mode="assert"时）
    :raises ValueError: 当mode参数不支持、校验规则格式错误、数据结构异常时抛出
    :raises RuntimeError: 当校验过程中出现系统异常时抛出
    
    示例：
    
    1. 成功场景 - 获取详细校验结果
    try:
        result = validate(data, "field1", "field2 > 0", "field3")
        print(f"校验成功: {result.summary}")
        print(f"共校验了 {result.total_rules} 个规则，全部通过")
        
        # 查看每个规则的执行详情
        for rule_result in result.rule_results:
            print(f"规则 '{rule_result.rule}': {rule_result.passed_fields}/{rule_result.total_fields} 字段通过")
    
    2. 失败场景 - 快速定位问题根源
    except ValidationError as e:
        print(f"校验失败: {str(e)}")
        
        # 快速定位：第一个失败的规则和字段
        first_failed_rule = e.get_first_failed_rule()
        first_failed_field = e.get_first_failed_field()
        if first_failed_field:
            print(f"首个失败: {first_failed_field.field_path} -> {first_failed_field.message}")
        
        # 详细分析：遍历所有失败项
        for rule_result in e.result.get_failed_rules():
            print(f"失败规则: {rule_result.rule}")
            for field_result in [f for f in rule_result.field_results if not f.success]:
                print(f"  - {field_result.field_path}: 期望{field_result.expect_value}, 实际{field_result.actual_value}")
    
    3. 阈值模式 - 灵活的质量控制
    try:
        result = validate(data, "users.*.id > 0", "users.*.name", max_fail=0.1)  # 允许10%失败
        print(f"校验通过: {result.summary}")
        if result.execution_mode == "threshold":
            print("在可接受的质量范围内")
    except ValidationError as e:
        print(f"质量不达标: {e}")
        print(f"失败率超过了设定的阈值 ({e.result.max_fail_info})")
    """
    # 使用核心引擎执行校验
    engine = ValidationEngine()
    context = engine.execute(data, validations, max_fail, fast_fail, context=context, output_format=output_format)
    
    # 构建详细结果
    result = context.build_detailed_result()
    
    # 根据 mode 参数决定返回类型
    if mode == "assert":
        # 断言模式：成功返回ValidationResult，失败抛ValidationError（默认）
        if result.success:
            return result
        else:
            raise ValidationError(result, output_format=output_format)
    elif mode == "dict":
        # 字典模式：成功/失败都返回结构化数据
        return result.to_dict()
    elif mode == "bool":
        # 布尔模式：只返回成功/失败状态
        return result.success
    else:
        raise ValueError(f"不支持的mode值: {mode}，支持的值: 'assert', 'dict', 'bool'")


def validate_not_empty(data, *validations, max_fail=None, fast_fail=True, output_format="summary", mode="assert") -> ValidationResult:
    """
    专门的非空校验
    
    :param data: 要校验的数据
    :param validations: 校验规则，支持多种简洁格式
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False

    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 当mode="assert"且校验失败时抛出
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    try:
        result = validate_not_empty(data, "field1", "field2")
        print(f"非空校验成功: {result}")
    except ValidationError as e:
        print(f"非空校验失败: {e}")
    """
    return validate(data, *validations, max_fail=max_fail, fast_fail=fast_fail, output_format=output_format, mode=mode)


def validate_when(data, condition, *then, max_fail=None, fast_fail=True, output_format="summary", mode="assert", context=None) -> ValidationResult:
    """
    严格条件校验 - 所有匹配项都满足条件时才执行then校验（第一种语义）
    
    语义说明：
    1. 对所有数据项进行条件校验
    2. 如果所有数据项都满足条件，就执行then规则校验
    3. 如果任一数据项不满足条件，就跳过整个then校验（返回成功）
    4. 每个then规则有独立的统计维度
    
    :param data: 要校验的数据
    :param condition: 条件表达式，支持所有校验器语法
    :param then: then表达式，支持所有校验器语法，可传入多个校验规则
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）

    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 当mode="assert"且校验失败时抛出
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    try:
        result = validate_when(data, "products.*.status == 'active'", "products.*.price > 0")
        print(f"条件校验成功: {result}")
    except ValidationError as e:
        print(f"条件校验失败: {e}")
    """
    # 参数验证
    if not then:
        raise ValueError("至少需要提供一个then校验规则")
    
    log_info(f"开始严格条件校验 - 数据长度: {len(data)}, then规则数: {len(then)}")
    log_debug(f"校验规则: validate_when({condition}) then({', '.join(str(rule) for rule in then)})")
    log_debug(f"失败阈值: {'默认严格模式' if max_fail is None else max_fail}")
    
    try:
        # 检查条件是否满足（条件检查不计入统计）
        condition_result = parse_and_validate(data, condition, context=None)
        
        # 条件不成立，跳过then校验
        if not condition_result:
            msg = f"条件不成立: validate_when({condition}), 跳过then校验"
            log_warning(msg)
            result = ValidationResult(success=True, total_rules=0, passed_rules=0, failed_rules=0, summary=msg, fast_fail=fast_fail, output_format=output_format)
            if mode == "assert":
                return result
            elif mode == "dict":
                return result.to_dict()
            elif mode == "bool":
                return True
            else:
                raise ValueError(f"不支持的mode值: {mode}，支持的值: 'assert', 'dict', 'bool'")

        # 条件成立，直接调用validate()函数校验then规则。这样每个then规则自然成为独立的统计维度
        log_debug(f"条件成立: validate_when({condition}), 执行then校验")
        return validate(data, *then, max_fail=max_fail, fast_fail=fast_fail, output_format=output_format, mode=mode, context=context)
    except ValidationError as e:
        log_error(f"❌ 严格条件校验失败: validate_when({condition}) - '{str(e)}'")
        raise
    except Exception as e:
        log_error(f"❌ 严格条件校验出现异常: validate_when({condition}) - '{str(e)}'")
        raise


def validate_when_each(data, condition, *then, max_fail=None, fast_fail=True, output_format="summary", mode="assert", context=None) -> ValidationResult:
    """
    逐项条件校验 - 对指定路径下的每个数据项分别进行条件+then检查（第二种语义）
    
    语义说明：
    1. 通过路径表达式定位要检查的数据项列表
    2. 对每个数据项分别进行条件检查
    3. 对满足条件的数据项执行then规则校验，不满足则跳过
    4. 每个then规则按照满足条件的数据项独立统计失败率
    
    :param data: 要校验的数据（任意类型）
    :param condition: 条件表达式，使用路径表达式，如 "users.*.status == 'active'"
    :param then: then规则，使用路径表达式，如 "users.*.score > 70"，可传入多个校验规则
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）

    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 当mode="assert"且校验失败时抛出
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    try:
        result = validate_when_each(data, "users.*.status == 'active'", "users.*.score > 70")
        print(f"逐项校验成功: {result}")
    except ValidationError as e:
        print(f"逐项校验失败: {e}")
    """
    # 参数验证
    if not then:
        raise ValueError("至少需要提供一个then校验规则")
    
    log_info(f"开始逐项条件校验 - 数据长度: {len(data)}, then规则数: {len(then)}")
    log_debug(f"校验规则: validate_when_each({condition}) then({', '.join(str(rule) for rule in then)})")
    log_debug(f"失败阈值: {'默认严格模式' if max_fail is None else max_fail}")
    
    try:
        return perform_item_wise_conditional_check(data, condition, then, max_fail, fast_fail, context=context, output_format=output_format, mode=mode)
    except ValidationError as e:
        log_error(f"❌ 逐项条件校验失败: validate_when_each({condition}) - '{str(e)}'")
        raise
    except Exception as e:
        log_error(f"❌ 逐项条件校验出现异常: validate_when_each({condition}) - '{str(e)}'")
        raise



def validate_list_when(data_list, condition, *then, max_fail=None, fast_fail=True, output_format="summary", mode="assert", context=None) -> ValidationResult:
    """
    列表逐项条件校验 - validate_when_each函数的简化版，专门用于列表数据

    语义说明：
    1. 针对数据项列表，对每个数据项分别进行条件检查
    2. 对满足条件的数据项执行then规则校验，不满足则跳过
    3. 每个then规则按照满足条件的数据项独立统计失败率
    4. 每个then规则的失败率 = (满足条件但then失败的数据项数) / (满足条件的数据项总数)

    :param data_list: 要校验的数据列表
    :param condition: 条件表达式，支持所有校验器语法
    :param then: then表达式，支持所有校验器语法，可传入多个校验规则
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）

    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 当mode="assert"且校验失败时抛出
    :raises: Exception: 当参数错误或数据结构异常时抛出异常
    
    示例：
    try:
        users = [{"name": "张三", "status": "active", "score": 85}, ...]
        result = validate_list_when(users, "status == 'active'", "score > 70")
        print(f"列表条件校验成功: {result}")
    except ValidationError as e:
        print(f"列表条件校验失败: {e}")
    """
    # 参数验证
    if not isinstance(data_list, list):
        raise TypeError(f"data_list必须是列表，当前类型: {type(data_list)}")

    if not then:
        raise ValueError("至少需要提供一个then校验规则")

    log_info(f"开始列表逐项条件校验 - 列表长度: {len(data_list)}, then规则数: {len(then)}")
    log_debug(f"校验规则: validate_list_when({condition}) then({', '.join(str(rule) for rule in then)})")
    log_debug(f"失败阈值: {'默认严格模式' if max_fail is None else max_fail}")

    try:
        return perform_item_wise_conditional_check(data_list, condition, then, max_fail, fast_fail, context=context, output_format=output_format, mode=mode)
    except ValidationError as e:
        log_error(f"❌ 列表逐项条件校验失败: validate_list_when({condition}) - '{str(e)}'")
        raise
    except Exception as e:
        log_error(f"❌ 列表逐项条件校验出现异常: validate_list_when({condition}) - '{str(e)}'")
        raise


def validate_list(data_list, *validations, max_fail=None, fast_fail=True, output_format="summary", mode="assert", **named_validations) -> ValidationResult:
    """
    列表数据批量校验

    :param data_list: 数据列表
    :param validations: 字段校验规则（默认非空校验，同时支持符号表达式校验和字典格式参数校验）
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False

    :param named_validations: 具名字段校验规则 field_name="validator expression"}
    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 当mode="assert"且校验失败时抛出
    :raises: TypeError: 当data_list不是列表时抛出
    
    示例：
    try:
        result = validate_list(products, "id", "name", "price > 0", max_fail=2)
        print(f"列表校验成功: {result}")
    except ValidationError as e:
        print(f"列表校验失败: {e}")
    """
    total_fields = len(validations) + len(named_validations)
    log_info(f"列表数据批量校验 - 列表长度: {len(data_list) if isinstance(data_list, list) else '未知'}, 字段数: {total_fields}")
    log_debug(f"非空校验字段: {list(validations)}")
    log_debug(f"带校验器字段: {dict(named_validations)}")
    
    if not isinstance(data_list, list):
        raise TypeError(f"data_list必须是列表，当前类型: {type(data_list)}")
    
    # 构建校验规则
    rules = []
    # 默认非空校验的字段
    for field in validations:
        rules.append(f"*.{field}")
    # 带校验器的字段
    for field, validator_expr in named_validations.items():
        rules.append(f"*.{field} {validator_expr}")
    
    # 调用核心 validate 函数
    return validate(data_list, *rules, max_fail=max_fail, fast_fail=fast_fail, output_format=output_format, mode=mode)


def validate_nested(data, list_field, nested_field, *validations, max_fail=None, fast_fail=True, output_format="summary", mode="assert") -> ValidationResult:
    """
    嵌套列表数据批量校验

    :param data: 要校验的数据
    :param list_field: 列表路径
    :param nested_field: 嵌套对象字段名，支持列表或字典对象
    :param validations: 字段校验规则
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False

    :param named_validations: 具名字段校验规则 field_name="validator expression"}
    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 当mode="assert"且校验失败时抛出
    :raises: ValueError: 当列表路径不存在、嵌套对象不存在或为空时抛出
    
    示例：
    try:
        result = validate_nested(response, "data.productList", "purchasePlan", "id > 0", "amount >= 100")
        print(f"嵌套列表校验成功: {result}")
    except ValidationError as e:
        print(f"嵌套列表校验失败: {e}")
    """
    log_info(f"嵌套列表数据批量校验 - 路径: {list_field}.*.{nested_field}, 字段数: {len(validations)}")
    log_debug(f"列表路径: {list_field}")
    log_debug(f"嵌套对象路径: {nested_field}")
    log_debug(f"字段校验规则: {list(validations)}")
    
    main_list = get_nested_value(data, list_field)
    if isinstance(main_list, list) and len(main_list) > 0:
        nested_obj = main_list[0].get(nested_field)
        if not nested_obj:
            raise ValueError(f"validate_nested校验时嵌套对象 {nested_field} 不存在或为空")
    else:
        raise ValueError(f"validate_nested校验时列表路径 {list_field} 的值不是列表或为空列表")

    # 构建校验规则
    rules = []
    for validation in validations:
        if isinstance(nested_obj, list):
            rules.append(f"{list_field}.*.{nested_field}.*.{validation}")
        elif isinstance(nested_obj, dict):
            rules.append(f"{list_field}.*.{nested_field}.{validation}")
        else:
            raise ValueError(f"validate_nested校验时嵌套对象 {nested_field} 不是列表或字典")

    return validate(data, *rules, max_fail=max_fail, fast_fail=fast_fail, output_format=output_format, mode=mode)


class DataValidator(BaseValidator):
    """数据校验器 - 链式调用并返回详细结果"""
    
    def validate(self, max_fail=None, fast_fail=True, output_format="summary", mode="assert") -> ValidationResult:
        """
        执行校验并返回详细结果
        
        :param max_fail: 失败阈值
            - None: 严格模式，一个失败全部失败（默认）
            - int: 每个规则最多允许N个失败
            - float: 每个规则最多允许N%失败率

        :param fast_fail: 快速失败，默认True
        :param output_format: 校验结果输出格式：summary/detail/dict
        :param mode: 校验结果返回模式
        - "assert": 默认断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 布尔模式，成功返回True，失败返回False

        :param named_validations: 具名字段校验规则 field_name="validator expression"}
        :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
        :raises: ValidationError: 当mode="assert"且校验失败时抛出
        
        示例：
        try:
            result = validator(data)\
                .not_empty("field1", "field2")\
                .greater_than("field3", 0)\
                .validate(max_fail=0.1)
            print(f"链式校验成功: {result.summary}")
        except ValidationError as e:
            print(f"链式校验失败: {e}")
        """
        return validate(self.data, *self.rules, max_fail=max_fail, fast_fail=fast_fail, output_format=output_format, mode=mode)


def validator(data):
    """创建数据校验器 - 增强版，支持详细结果返回"""
    return DataValidator(data)