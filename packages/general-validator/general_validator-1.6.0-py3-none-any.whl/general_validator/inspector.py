# -*- coding:utf-8 -*-
from .validator import validate, validate_not_empty, validate_when, validate_when_each, validate_list_when, validate_list, validate_nested, DataValidator

"""
General-Validator inspect系列数据校验函数 - validate系列函数的字典模式别名，方便调用，同时保持完全向后兼容

inspect系列函数始终返回详细的结构化字典信息，适用于：
- API接口响应
- 可视化数据展示  
- 详细的校验报告
- 数据分析和统计
"""

def inspect(data, *validations, max_fail=None, fast_fail=True, context=None):
    """
    极简数据校验入口函数 - validate函数的字典模式别名
    
    :param data: 要校验的数据
    :param validations: 校验规则，支持多种简洁格式
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认，保持完全兼容性）
        - int: 每个规则最多允许N个失败 (如 max_fail=3)
        - float: 每个规则最多允许N%失败率 (如 max_fail=0.1 表示10%)

    :param context: 上下文对象，用于累积校验结果（链式调用时使用）
    :return: dict: 详细的结构化字典信息
    
    示例用法：
    1. 默认非空校验 - 最简形式
    inspect(response, "data.product.id", "data.product.name")
    
    2. 带校验器的形式
    inspect(response, "data.product.id > 0", "data.product.price >= 10.5")
    
    3. 混合校验
    inspect(response, 
          "data.product.id",           # 默认非空
          "data.product.price > 0",    # 大于0
          "status_code == 200")        # 等于200
    
    4. 列表批量校验 - 通配符
    inspect(response, "data.productList.*.id", "data.productList.*.name")
    
    5. 嵌套列表校验
    inspect(response, "data.productList.*.purchasePlan.*.id > 0")
    """
    return validate(data, *validations, max_fail=max_fail, fast_fail=fast_fail, mode="dict", context=context)


def inspect_not_empty(data, *validations, max_fail=None, fast_fail=True):
    """
    专门的非空校验 - validate_not_empty函数的字典模式别名

    :param data: 待校验的数据
    :param validations: 校验规则，支持多种简洁格式
    :param max_fail: 失败阈值
    :param fast_fail: 快速失败，默认True
    :return: dict: 详细的结构化字典信息
    """
    return validate_not_empty(data, *validations, max_fail=max_fail, fast_fail=fast_fail, mode="dict")


def inspect_when(data, condition, *then, max_fail=None, fast_fail=True, context=None):
    """
    严格条件校验 - validate_when函数的字典模式别名

    语义说明：
    1. 对所有数据项进行条件校验
    2. 如果所有数据项都满足条件，就执行then规则校验
    3. 如果任一数据项不满足条件，就跳过整个then校验
    4. 每个then规则有独立的统计维度
    
    :param data: 要校验的数据
    :param condition: 条件表达式，支持所有校验器语法
    :param then: then表达式，支持所有校验器语法，可传入多个校验规则
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）
    :return: dict: 详细的结构化字典信息
    
    示例：
    1. 单个then校验 - 当status为active时，price必须大于0
    inspect_when(data, "status == 'active'", "price > 0")
    
    2. 多个then校验 - 当type为premium时，features字段不能为空且price必须大于100
    inspect_when(data, "type == 'premium'", "features", "price > 100")
    
    3. 批量校验 - 当status为active时，多个字段都必须校验通过
    inspect_when(data, "status == 'active'",
               "price > 0",
               "name",
               "description",
               "category != 'test'")
    
    4. 支持通配符 - 当所有产品状态为active时，价格都必须大于0且名称不能为空
    inspect_when(data, "products.*.status == 'active'",
               "products.*.price > 0",
               "products.*.name")
    
    5. 混合条件校验 - 当用户为VIP时，多个权限字段都必须校验
    inspect_when(data, "user.level == 'vip'",
               "user.permissions.download == true",
               "user.permissions.upload == true",
               "user.quota > 1000")

    注意：
    1. 当条件满足时，所有then校验都必须通过才算成功
    2. 当条件不满足时，跳过所有then校验（返回True）
    """
    return validate_when(data, condition, *then, max_fail=max_fail, fast_fail=fast_fail, mode="dict", context=context)


def inspect_when_each(data, condition, *then, max_fail=None, fast_fail=True, context=None):
    """
    逐项条件校验 - validate_when_each函数的字典模式别名
    
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
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）
    :return: dict: 详细的结构化字典信息

    示例用法：
    1. 基础用法 - 直接使用路径表达式，无需预提取列表
    inspect_when_each(data, "users.*.status == 'active'", "users.*.score > 70")
    
    2. 多个then规则 - 活跃VIP用户必须有名字且分数大于80
    inspect_when_each(data, "users.*.status == 'active'", "users.*.name", "users.*.score > 80")
    
    3. 深度嵌套场景 - 支持复杂路径表达式
    inspect_when_each(response, "data.regions.*.cities.*.status == 'active'", "data.regions.*.cities.*.population > 0")
    
    4. 阈值模式 - 允许30%的活跃用户分数不达标
    inspect_when_each(data, "users.*.status == 'active'", "users.*.score > 70", max_fail=0.3)
    """
    return validate_when_each(data, condition, *then, max_fail=max_fail, fast_fail=fast_fail, mode="dict", context=context)


def inspect_list_when(data_list, condition, *then, max_fail=None, fast_fail=True, context=None):
    """
    列表逐项条件校验 - validate_list_when函数的字典模式别名

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
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）
    :return: dict: 详细的结构化字典信息

    示例用法：
    1. 基础用法 - 对用户列表，活跃用户的分数必须大于70
    users = [
        {"name": "张三", "status": "active", "score": 85},
        {"name": "李四", "status": "active", "score": 65},  # 条件满足但then失败
        {"name": "王五", "status": "inactive", "score": 70}  # 条件不满足，跳过
    ]
    inspect_list_when(users, "status == 'active'", "score > 70")

    2. 多个then规则 - 活跃用户必须有名字且分数大于80
    inspect_list_when(users, "status == 'active'", "name", "score > 80")

    3. 阈值模式 - 允许30%的活跃用户分数不达标
    inspect_list_when(users, "status == 'active'", "score > 70", max_fail=0.3)
    """
    return validate_list_when(data_list, condition, *then, max_fail=max_fail, fast_fail=fast_fail, mode="dict", context=context)


def inspect_list(data_list, *validations, max_fail=None, fast_fail=True, **named_validations):
    """
    列表数据批量校验 - validate_list函数的字典模式别名
    
    :param data_list: 数据列表
    :param validations: 字段校验规则（默认非空校验，同时支持符号表达式校验和字典格式参数校验）
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :param named_validations: 具名字段校验规则 field_name="validator expression"}
    :return: dict: 详细的结构化字典信息
    
    示例：
    1. 默认非空校验
    inspect_list(productList, "id", "name", "price")
    
    2. 带校验器
    inspect_list(productList, "name", id="> 0", price=">= 0")
    或
    inspect_list(productList, "name", "id > 0", "price >= 0")
    
    3. 混合使用
    inspect_list(productList, "name", "description", id="> 0", status="== 'active'")
    或
    inspect_list(productList, "name", "description", "id > 0", "status == 'active'")
    """
    return validate_list(data_list, *validations, max_fail=max_fail, fast_fail=fast_fail, mode="dict", **named_validations)


def inspect_nested(data, list_field, nested_field, *validations, max_fail=None, fast_fail=True):
    """
    嵌套列表数据批量校验 - validate_nested函数的字典模式别名
    
    :param data: 要校验的数据
    :param list_field: 列表路径
    :param nested_field: 嵌套对象字段名，支持列表或字典对象
    :param validations: 字段校验规则
    :param max_fail: 失败阈值
        - None: 严格模式，一个失败全部失败（默认）
        - int: 每个规则最多允许N个失败
        - float: 每个规则最多允许N%失败率

    :param fast_fail: 快速失败，默认True
    :return: dict: 详细的结构化字典信息
    
    示例：
    1. 默认非空校验
    inspect_nested(response, "data.productList", "purchasePlan", "id", "name")
    
    2. 带校验器
    inspect_nested(response, "data.productList", "purchasePlan", "id > 0", "amount >= 100")
    """
    return validate_nested(data, list_field, nested_field, *validations, max_fail=max_fail, fast_fail=fast_fail, mode="dict")


class DataInspector(DataValidator):
    """数据校验器 - 继承DataValidator链式调用类，返回字典结果"""
    
    def validate(self, max_fail=None, fast_fail=True):
        """重写DataValidator.validate方法，执行校验并返回字典结果
        :param max_fail: 失败阈值
            - None: 严格模式，一个失败全部失败（默认）
            - int: 每个规则最多允许N个失败
            - float: 每个规则最多允许N%失败率

        :param fast_fail: 快速失败，默认True
        :return: dict: 详细的结构化字典信息
        
        示例：
        result = inspector(data)\
                .not_empty("field1", "field2")\
                .greater_than("field3", 0)\
                .validate(max_fail=0.1)
        print(f"链式校验结果概要: { result.success }")
        print(f"链式校验结果详情: { json.dumps(result, indent=2, ensure_ascii=False) }")
        """
        return super().validate(max_fail=max_fail, fast_fail=fast_fail, mode="dict")


def inspector(data):
    """创建数据校验器 - validator链式调用函数的别名"""
    return DataInspector(data)