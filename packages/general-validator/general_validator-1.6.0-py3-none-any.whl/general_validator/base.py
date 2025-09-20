# -*- coding:utf-8 -*-
"""
数据校验器基类 - 包含所有校验方法的通用实现

此模块提供了校验器的基础实现，包含所有常用的校验方法。
具体的校验器类（如DataChecker、DataValidator）通过继承此基类来获得校验能力。
"""


class BaseValidator:
    """数据校验器基类 - 包含所有校验方法的通用实现"""
    
    def __init__(self, data):
        self.data = data
        self.rules = []
    
    def field(self, path, validator=None, expect=None):
        """添加字段校验"""
        if validator is None:
            # 默认非空
            self.rules.append(path)
        elif expect is None:
            # 字符串表达式
            self.rules.append(f"{path} {validator}")
        else:
            # 分离的校验器和期望值
            self.rules.append(f"{path} {validator} {expect}")
        return self
    
    def not_empty(self, *paths):
        """批量非空校验"""
        self.rules.extend(paths)
        return self
    
    # 等值比较校验
    def equals(self, path, value):
        """等于校验"""
        self.rules.append(f"{path} == {repr(value)}")
        return self
    
    def not_equals(self, path, value):
        """不等于校验"""
        self.rules.append(f"{path} != {repr(value)}")
        return self
    
    # 数值比较校验
    def greater_than(self, path, value):
        """大于校验"""
        self.rules.append(f"{path} > {value}")
        return self
    
    def greater_equal(self, path, value):
        """大于等于校验"""
        self.rules.append(f"{path} >= {value}")
        return self
    
    def less_than(self, path, value):
        """小于校验"""
        self.rules.append(f"{path} < {value}")
        return self
    
    def less_equal(self, path, value):
        """小于等于校验"""
        self.rules.append(f"{path} <= {value}")
        return self
    
    # 数值范围校验
    def between(self, path, min_value, max_value, inclusive=True):
        """数值区间校验"""
        if inclusive:
            self.rules.append(f"{path} >= {min_value}")
            self.rules.append(f"{path} <= {max_value}")
        else:
            self.rules.append(f"{path} > {min_value}")
            self.rules.append(f"{path} < {max_value}")
        return self
    
    # 字符串校验
    def starts_with(self, path, prefix):
        """以指定字符串开头"""
        self.rules.append(f"{path} ^= {repr(prefix)}")
        return self
    
    def ends_with(self, path, suffix):
        """以指定字符串结尾"""
        self.rules.append(f"{path} $= {repr(suffix)}")
        return self
    
    def contains(self, path, substring):
        """包含指定字符串"""
        self.rules.append(f"{path} *= {repr(substring)}")
        return self
    
    def contained_by(self, path, container):
        """被指定字符串包含"""
        self.rules.append(f"{path} =* {repr(container)}")
        return self
    
    def matches_regex(self, path, pattern):
        """正则表达式匹配"""
        self.rules.append(f"{path} ~= {str(pattern)}")
        return self
    
    # 类型校验
    def is_type(self, path, expected_type):
        """类型校验"""
        if isinstance(expected_type, type):
            type_name = expected_type.__name__
        else:
            type_name = str(expected_type)
        self.rules.append(f"{path} @= {repr(type_name)}")
        return self
    
    def is_string(self, path):
        """字符串类型校验"""
        return self.is_type(path, 'str')
    
    def is_number(self, path):
        """数字类型校验（int或float）"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'custom_number_check',
            'expect': None
        })
        return self
    
    def is_integer(self, path):
        """整数类型校验"""
        return self.is_type(path, 'int')
    
    def is_float(self, path):
        """浮点数类型校验"""
        return self.is_type(path, 'float')
    
    def is_boolean(self, path):
        """布尔类型校验"""
        return self.is_type(path, 'bool')
    
    def is_list(self, path):
        """列表类型校验"""
        return self.is_type(path, 'list')
    
    def is_dict(self, path):
        """字典类型校验"""
        return self.is_type(path, 'dict')
    
    def is_none(self, path):
        """None类型校验"""
        return self.is_type(path, 'none')
    
    # 集合校验
    def in_values(self, path, values):
        """值在指定集合中"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'in_values',
            'expect': values
        })
        return self
    
    def not_in_values(self, path, values):
        """值不在指定集合中"""
        # 使用自定义校验逻辑
        self.rules.append({
            'field': path,
            'validator': 'not_in_values',
            'expect': values
        })
        return self
    
    # 长度校验
    def length_equals(self, path, length):
        """长度等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_eq',
            'expect': length
        })
        return self
    
    def length_not_equals(self, path, length):
        """长度不等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_ne',
            'expect': length
        })
        return self
    
    def length_greater_than(self, path, length):
        """长度大于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_gt',
            'expect': length
        })
        return self
    
    def length_less_than(self, path, length):
        """长度小于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_lt',
            'expect': length
        })
        return self

    def length_greater_equal(self, path, length):
        """长度大于等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_ge',
            'expect': length
        })
        return self
    
    def length_less_equal(self, path, length):
        """长度小于等于指定值"""
        self.rules.append({
            'field': path,
            'validator': 'length_le',
            'expect': length
        })
        return self

    def length_between(self, path, min_length, max_length, inclusive=True):
        """长度在指定范围内"""
        if inclusive:
            self.rules.append({
                'field': path,
                'validator': 'length_ge',
                'expect': min_length
            })
            self.rules.append({
                'field': path,
                'validator': 'length_le',
                'expect': max_length
            })
        else:
            self.rules.append({
                'field': path,
                'validator': 'length_gt',
                'expect': min_length
            })
            self.rules.append({
                'field': path,
                'validator': 'length_lt',
                'expect': max_length
            })
        return self
    
    # 特殊校验
    def is_email(self, path):
        """邮箱格式校验"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': email_pattern
        })
        return self
    
    def is_phone(self, path):
        """手机号格式校验（中国大陆）"""
        phone_pattern = r'^1[3-9]\d{9}$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': phone_pattern
        })
        return self
    
    def is_url(self, path):
        """URL格式校验"""
        url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        self.rules.append({
            'field': path,
            'validator': 'regex',
            'expect': url_pattern
        })
        return self
    
    def is_positive(self, path):
        """正数校验"""
        return self.greater_than(path, 0)
    
    def is_negative(self, path):
        """负数校验"""
        return self.less_than(path, 0)
    
    def is_non_negative(self, path):
        """非负数校验"""
        return self.greater_equal(path, 0)
    
    # 批量操作
    def all_fields_not_empty(self, *paths):
        """批量非空校验（别名）"""
        return self.not_empty(*paths)
    
    def all_fields_positive(self, *paths):
        """批量正数校验"""
        for path in paths:
            self.is_positive(path)
        return self
    
    def all_fields_type(self, field_type, *paths):
        """批量类型校验"""
        for path in paths:
            self.is_type(path, field_type)
        return self

    # 条件校验
    def when(self, condition, *then):
        """
        严格条件校验 - 所有匹配项都满足条件时才执行then校验（第一种语义）

        语义说明：
        1. 对所有数据项进行条件校验
        2. 如果所有数据项都满足条件，就执行then规则校验
        3. 如果任一数据项不满足条件，就跳过整个then校验
        4. 每个then规则有独立的统计维度

        :param condition: 条件表达式，支持所有校验器语法
        :param then: then表达式，支持所有校验器语法，可传入多个校验规则
        :return: self（支持链式调用）

        与when_each和list_when方法的区别：
        - when：所有匹配项都满足条件时才执行then校验（严格全部匹配）
        - when_each：每个数据项单独进行条件+then检查（逐项条件检查）
        - list_when：when_each的简化版，专门用于列表数据

        示例：
        # 单个then校验 - 当status为active时，price必须大于0
        .when("status == 'active'", "price > 0")

        # 多个then校验 - 当type为premium时，features字段不能为空且price必须大于100
        .when("type == 'premium'", "features", "price > 100")

        # 批量校验 - 当status为active时，多个字段都必须校验通过
        .when("status == 'active'",
              "price > 0",
              "name",
              "description",
              "category != 'test'")

        # 支持通配符 - 当所有产品状态为active时，价格都必须大于0且名称不能为空
        .when("products.*.status == 'active'",
              "products.*.price > 0",
              "products.*.name")

        # 链式调用示例
        .when("user.level == 'vip'",
            "user.permissions.download == true",
            "user.permissions.upload == true",
            "user.quota > 1000") \
        .when("user.status == 'active'",
            "user.last_login",
            "user.email") \
        .validate()

        注意：
        1. 当条件满足时，所有then校验都必须通过才算成功
        2. 当条件不满足时，跳过所有then校验（返回True）
        3. 支持链式调用，可以添加多个条件校验
        """
        
        # 参数验证
        if not then:
            raise ValueError("至少需要提供一个then校验规则")
        
        # 构建条件校验规则（校验器标识为conditional_check）
        self.rules.append({
            'field': 'conditional',
            'validator': 'conditional_check',
            'expect': {
                'condition': condition,
                'then': list(then)
            }
        })
        return self
    

    def when_each(self, condition, *then):
        """
        逐项条件校验：对指定路径下的每个数据项分别进行条件+then检查（第二种语义）
        
        语义说明：
        1. 通过路径表达式定位要检查的数据项列表
        2. 对每个数据项分别进行条件检查
        3. 对满足条件的数据项执行then规则校验，不满足则跳过
        4. 每个then规则按照满足条件的数据项独立统计失败率
        
        :param condition: 条件表达式，使用路径表达式，如 "users.*.status == 'active'"
        :param then: then规则，使用路径表达式，如 "users.*.score > 70"，可传入多个校验规则
        :return: self（支持链式调用）

        与when和list_when方法的区别：
        - when：所有匹配项都满足条件时才执行then校验（严格全部匹配）
        - when_each：每个数据项单独进行条件+then检查（逐项条件检查）
        - list_when：when_each的简化版，专门用于列表数据

        适用场景：
        - 任意数据结构，不限于列表
        - 需要通过复杂路径表达式定位数据项
        - 希望统计满足条件的数据项中then规则的失败率
        - 避免手动提取数据子集

        示例：
        # 基础用法 - 直接使用路径表达式
        .when_each("users.*.status == 'active'", "users.*.score > 70").validate()

        # 多个then规则 - 活跃用户必须有名字且分数大于80
        .when_each("users.*.status == 'active'",
                               "users.*.name", "users.*.score > 80").validate()

        # 深度嵌套场景
        .when_each("data.regions.*.cities.*.status == 'active'",
                                   "data.regions.*.cities.*.population > 0").validate()

        # 链式调用示例
        .when_each("users.*.status == 'active'", "users.*.score > 70") \
        .when_each("orders.*.status == 'paid'", "orders.*.amount > 0") \
        .validate()

        # 与传统用法的对比：
        # 传统方式（需要预提取）：
        users = data["users"]
        checker(users).list_when("status == 'active'", "score > 70").validate()

        # 新方式（直接路径表达式）：
        checker(data).when_each("users.*.status == 'active'", "users.*.score > 70").validate()

        注意：
        1. 条件和then规则必须使用相同的路径前缀
        2. 路径表达式必须包含通配符*来定位要遍历的数据项
        3. 支持失败阈值设置
        4. 支持链式调用
        """
        
        # 参数验证
        if not then:
            raise ValueError("至少需要提供一个then校验规则")
        
        # 构建路径条件校验规则（校验器标识为conditional_each_check）
        self.rules.append({
            'field': 'conditional',
            'validator': 'conditional_each_check',
            'expect': {
                'condition': condition,
                'then': list(then)
            }
        })
        return self
    
    def list_when(self, condition, *then):
        """
        逐项条件校验：when_each的简化版，专门用于列表数据
        
        :param condition: 条件表达式，支持所有校验器语法
        :param then: then表达式，支持所有校验器语法，可传入多个校验规则
        :return: self（支持链式调用）

        与when和when_each方法的区别：
        - when：所有匹配项都满足条件时才执行then校验（严格全部匹配）
        - when_each：每个数据项单独进行条件+then检查（逐项条件检查）
        - list_when：when_each的简化版，专门用于列表数据
        
        适用场景：
        - 当前数据是列表格式
        - 需要对列表中符合条件的数据项进行个别校验
        - 希望统计满足条件的数据项中then规则的失败率

        示例：
        # 对用户列表，活跃用户的分数必须大于70
        checker(users).list_when("status == 'active'", "score > 70").validate()

        # 多个then规则 - 活跃用户必须有名字且分数大于80
        checker(users).list_when("status == 'active'", "name", "score > 80").validate()

        注意：
        1. 当前数据必须是列表格式，否则校验时会抛出异常
        2. 每个数据项单独进行条件+then检查
        3. 支持失败阈值设置
        4. 支持链式调用
        """
        
        # 参数验证
        if not then:
            raise ValueError("至少需要提供一个then校验规则")
        
        # 构建条件校验规则（校验器标识为conditional_list_check）
        self.rules.append({
            'field': 'conditional',
            'validator': 'conditional_list_check',
            'expect': {
                'condition': condition,
                'then': list(then)
            }
        })
        return self