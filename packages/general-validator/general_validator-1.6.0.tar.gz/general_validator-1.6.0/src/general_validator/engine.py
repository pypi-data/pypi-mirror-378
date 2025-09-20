# -*- coding:utf-8 -*-
from typing import List, Optional
from .logger import log_debug, log_info, log_warning, log_error, log_critical


class FieldResult:
    """单个字段的校验结果"""

    def __init__(self, field_path, validator, expect_value, actual_value, success, message):
        self.field_path = field_path          # 字段路径，如 "users[1].name"
        self.validator = validator            # 校验器名称，如 "not_empty", "gt"
        self.expect_value = expect_value      # 期望值，如 "> 0", "not empty"
        self.actual_value = actual_value      # 实际值
        self.success = success                # 是否校验成功
        self.message = message                # 详细描述信息

    def to_dict(self):
        """返回字段结果的字典格式"""
        return {
            "field_path": self.field_path,
            "validator": self.validator,
            "expect_value": self.expect_value,
            "actual_value": self.actual_value,
            "success": self.success,
            "message": self.message
        }


class RuleResult:
    """单个规则的校验结果"""

    def __init__(self, rule, total_fields, passed_fields, failed_fields, field_results=None,
                 success=True, failure_rate=0.0, threshold_info=""):
        self.rule = rule                      # 原始规则表达式，如 "users.*.age > 18"
        self.total_fields = total_fields      # 该规则匹配到的字段总数
        self.passed_fields = passed_fields    # 通过校验的字段数
        self.failed_fields = failed_fields    # 失败的字段数
        self.field_results = field_results or []  # 所有字段的详细结果
        self.success = success                # 规则是否整体成功（考虑阈值）
        self.failure_rate = failure_rate      # 失败率
        self.threshold_info = threshold_info  # 阈值信息描述

    def to_dict(self):
        """返回规则结果的字典格式"""
        return {
            "rule": self.rule,
            "total_fields": self.total_fields,
            "passed_fields": self.passed_fields,
            "failed_fields": self.failed_fields,
            "success": self.success,
            "failure_rate": self.failure_rate,
            "threshold_info": self.threshold_info,
            "field_results": [field_result.to_dict() for field_result in self.field_results]
        }


class ValidationResult:
    """整体校验结果"""

    def __init__(self, success, total_rules, passed_rules, failed_rules, rule_results=None,
                 summary="", max_fail_info="", execution_mode="strict", fast_fail=True, output_format="summary"):
        self.success = success                # 整体是否成功
        self.total_rules = total_rules        # 总规则数
        self.passed_rules = passed_rules      # 通过的规则数
        self.failed_rules = failed_rules      # 失败的规则数
        self.rule_results = rule_results or []  # 所有规则的详细结果
        self.summary = summary                # 结果摘要
        self.max_fail_info = max_fail_info    # 失败阈值信息
        self.execution_mode = execution_mode  # 执行模式：strict/threshold
        self.fast_fail = fast_fail            # 快速失败
        self.output_format = output_format    # 输出格式：summary/detail/dict

    def __str__(self):
        """返回校验结果信息"""
        if self.output_format == "summary":
            return self.summary
        elif self.output_format == "detail":
            return self.get_detail_message()
        elif self.output_format == "dict":
            return self.to_dict()
        else:
            log_warning(f"不支持的输出格式: {self.output_format}，自动切换为使用'summary'格式")
            return self.summary

    def get_detail_message(self):
        """返回校验结果详情信息"""
        # 构建详细信息
        detail_message = self.summary

        # 添加所有规则概览
        if self.rule_results:
            detail_message += f"\n\n规则执行概览 ({len(self.rule_results)} 个规则):"
            for rule_result in self.rule_results:
                status_icon = "✓" if rule_result.success else "✗"
                detail_message += f"\n  {status_icon} {rule_result.rule}: {rule_result.passed_fields}/{rule_result.total_fields} 个字段通过"
                if rule_result.failure_rate > 0:
                    detail_message += f" (失败率: {rule_result.failure_rate:.1%})"
                if rule_result.threshold_info and not rule_result.success:
                    detail_message += f" - {rule_result.threshold_info}"

        # 添加具体字段详情
        all_field_results = []
        for rule_result in self.rule_results:
            all_field_results.extend(rule_result.field_results)

        if all_field_results:
            # 分别显示失败和成功的字段
            failed_fields = [f for f in all_field_results if not f.success]
            success_fields = [f for f in all_field_results if f.success]

            # 失败字段详情（最多显示10个）
            if failed_fields:
                detail_message += f"\n\n失败字段详情:"
                display_count = min(len(failed_fields), 10)
                for field_result in failed_fields[:display_count]:
                    detail_message += f"\n  ✗ {field_result.field_path}: {field_result.message}"

                if len(failed_fields) > display_count:
                    detail_message += f"\n  ... 还有 {len(failed_fields) - display_count} 个字段失败"

            # 成功字段概要（如果有失败字段则只显示统计，否则显示前几个成功字段）
            if success_fields:
                if failed_fields:
                    detail_message += f"\n\n成功字段统计: {len(success_fields)} 个字段校验通过"
                else:
                    # 没有失败字段时，显示前几个成功字段作为示例
                    detail_message += f"\n\n成功字段详情:"
                    display_count = min(len(success_fields), 5)
                    for field_result in success_fields[:display_count]:
                        detail_message += f"\n  ✓ {field_result.field_path}: {field_result.message}"

                    if len(success_fields) > display_count:
                        detail_message += f"\n  ... 还有 {len(success_fields) - display_count} 个字段通过"

        # 添加阈值信息
        if self.max_fail_info:
            detail_message += f"\n\n阈值设置: {self.max_fail_info}"

        return detail_message

    def get_error_message(self):
        """返回校验异常消息"""
        # 构建异常消息
        error_message = self.summary

        # 添加失败规则概览
        failed_rules = self.get_failed_rules()
        if failed_rules:
            error_message += f"\n\n失败规则概览 ({len(failed_rules)}/{self.total_rules}):"
            for rule_result in failed_rules:
                error_message += f"\n  ✗ {rule_result.rule}: {rule_result.failed_fields}/{rule_result.total_fields} 个字段失败"
                if rule_result.threshold_info:
                    error_message += f" ({rule_result.threshold_info})"

        # 添加具体失败字段（最多显示10个，避免信息过多）
        failed_fields = self.get_failed_fields()
        if failed_fields:
            error_message += f"\n\n具体失败字段:"
            display_count = min(len(failed_fields), 10)
            for field_result in failed_fields[:display_count]:
                error_message += f"\n  - {field_result.field_path}: {field_result.message}"

            if len(failed_fields) > display_count:
                error_message += f"\n  ... 还有 {len(failed_fields) - display_count} 个字段失败"

        return error_message

    def to_dict(self):
        """
        返回校验结果结构化信息

        包含以下信息：
        - 顶层校验统计信息
        - 详细的规则执行结果  
        - 具体的字段校验详情
        - 阈值和执行模式信息

        :return: dict - 完整的校验结果字典
        """
        return {
            # 整体校验结果
            "success": self.success,
            "summary": self.summary,

            # 统计信息
            "statistics": {
                "total_rules": self.total_rules,
                "passed_rules": self.passed_rules,
                "failed_rules": self.failed_rules,
                "success_rate": self.get_success_rate()
            },

            # 执行配置
            "execution_config": {
                "execution_mode": self.execution_mode,
                "fast_fail": self.fast_fail,
                "max_fail_info": self.max_fail_info
            },

            # 详细规则结果
            "rule_results": [rule_result.to_dict() for rule_result in self.rule_results],

            # 聚合字段信息
            "field_summary": {
                "total_fields": sum(rule.total_fields for rule in self.rule_results),
                "passed_fields": sum(rule.passed_fields for rule in self.rule_results),
                "failed_fields": sum(rule.failed_fields for rule in self.rule_results)
            },

            # 失败详情统计
            "failure_analysis": {
                "failed_rule_count": len(self.get_failed_rules()),
                "failed_field_count": len(self.get_failed_fields()),
                "failed_rules": [rule.rule for rule in self.get_failed_rules()],
                "failed_fields": [field.field_path for field in self.get_failed_fields()]
            }
        }

    def get_failed_rules(self) -> List[RuleResult]:
        """获取所有失败的规则"""
        return [rule for rule in self.rule_results if not rule.success]

    def get_failed_fields(self) -> List[FieldResult]:
        """获取所有失败的字段"""
        failed_fields = []
        for rule_result in self.rule_results:
            failed_fields.extend([field for field in rule_result.field_results if not field.success])
        return failed_fields

    def get_success_rate(self) -> float:
        """获取成功率"""
        return (self.passed_rules / self.total_rules) if self.total_rules > 0 else 1.0


class ValidationError(Exception):
    """校验失败异常，包含详细的失败信息"""

    def __init__(self, result: ValidationResult, output_format="summary"):
        self.result = result
        self.output_format = output_format

        if self.output_format == "summary":
            error_message = result.get_error_message()
        elif self.output_format == "detail":
            error_message = result.get_detail_message()
        elif self.output_format == "dict":
            error_message = result.to_dict()
        else:
            error_message = result.get_error_message()

        super().__init__(error_message)

    def get_failed_rule_count(self) -> int:
        """获取失败规则数量"""
        return len(self.result.get_failed_rules())

    def get_failed_field_count(self) -> int:
        """获取失败字段数量"""
        return len(self.result.get_failed_fields())

    def get_first_failed_rule(self) -> Optional[RuleResult]:
        """获取第一个失败的规则"""
        failed_rules = self.result.get_failed_rules()
        return failed_rules[0] if failed_rules else None

    def get_first_failed_field(self) -> Optional[FieldResult]:
        """获取第一个失败的字段"""
        failed_fields = self.result.get_failed_fields()
        return failed_fields[0] if failed_fields else None


class RuleStats:
    """单个校验规则的统计信息"""

    def __init__(self, rule_name):
        self.rule_name = rule_name
        self.total_count = 0      # 总校验次数
        self.failed_count = 0     # 失败次数
        self.failed_details = []  # 失败详情

    def add_result(self, success, detail=None):
        """添加校验结果"""
        self.total_count += 1
        if not success:
            self.failed_count += 1
            if detail:
                self.failed_details.append(detail)

    def get_failure_rate(self):
        """获取失败率"""
        return self.failed_count / self.total_count if self.total_count > 0 else 0.0

    def exceeds_threshold(self, threshold):
        """检查是否超过阈值"""
        if threshold is None:
            return self.failed_count > 0  # 严格模式
        elif isinstance(threshold, int):
            return self.failed_count > threshold  # 数量阈值
        elif isinstance(threshold, float):
            return self.get_failure_rate() > threshold  # 比率阈值
        else:
            raise ValueError(f"不支持的阈值类型: {type(threshold)}")


class ValidationContext:
    """校验上下文 - 管理所有规则的统计信息和执行控制"""
    
    def __init__(self, max_fail=None, fast_fail=True, output_format="summary"):
        self.max_fail = max_fail
        self.rule_stats = {}  # {rule_name: RuleStats}
        self.is_strict_mode = (max_fail is None)
        self.should_abort = False  # 严格模式快速失败标志
        self.fast_fail = fast_fail
        self.current_rule_name = None  # 当前正在执行的规则名
        self.output_format = output_format    # 输出格式：summary/detail/dict
        
        # 用于兼容原有日志格式的计数器
        self.passed_count = 0
        self.failed_count = 0
        self.total_validations = 0
        
        # 增强：存储详细的字段校验结果（用于构建 ValidationResult）
        self.field_results = []  # List[详细字段结果信息]
    
    def get_or_create_rule_stats(self, rule_name):
        """获取或创建规则统计对象"""
        if rule_name not in self.rule_stats:
            self.rule_stats[rule_name] = RuleStats(rule_name)
        return self.rule_stats[rule_name]
    
    def set_current_rule(self, rule_name):
        """设置当前执行的规则名，用于日志输出"""
        self.current_rule_name = rule_name
    
    def record_field_result(self, success, field_path, validator, expect_value, check_value, detail=None):
        """记录单个字段的校验结果"""
        if self.current_rule_name:
            stats = self.get_or_create_rule_stats(self.current_rule_name)
            stats.add_result(success, detail)
            
            # 增强：保存详细的字段结果信息（用于构建 ValidationResult）
            field_result_info = {
                'rule_name': self.current_rule_name,
                'field_path': field_path,
                'validator': validator,
                'expect_value': expect_value,
                'actual_value': check_value,
                'success': success,
                'detail': detail,
                'message': self._build_field_message(success, field_path, validator, expect_value, check_value)
            }
            self.field_results.append(field_result_info)
            
            # 严格模式下遇到失败立即设置中断标志
            if self.is_strict_mode and not success:
                self.should_abort = True
    
    def record_rule_result(self, success):
        """记录整个规则的执行结果（用于兼容原有日志）"""
        # 更新全局计数器（用于严格模式的规则级别统计）
        if success:
            self.passed_count += 1
        else:
            self.failed_count += 1
            # 严格模式下规则失败时也要设置中断标志
            if self.is_strict_mode:
                self.should_abort = True
        
        self.total_validations += 1
    
    def check_all_thresholds(self):
        """检查是否有规则超过阈值"""
        if self.is_strict_mode:
            return self.failed_count == 0
        
        for rule_name, stats in self.rule_stats.items():
            if stats.exceeds_threshold(self.max_fail):
                log_warning(f"规则 '{rule_name}' 超过阈值: 失败{stats.failed_count}次，失败率{stats.get_failure_rate():.2%}")
                return False
        return True

    def get_threshold_info(self):
        """获取阈值信息"""
        if self.max_fail is None:
            return "严格模式 - 不允许任何失败"
        elif isinstance(self.max_fail, int):
            return f"数量阈值 - 最多允许 {self.max_fail} 个失败"
        elif isinstance(self.max_fail, float):
            return f"比率阈值 - 最多允许 {self.max_fail:.1%} 失败率"
        else:
            return f"阈值 - {self.max_fail}"

    def _build_field_message(self, success, field_path, validator, expect_value, actual_value):
        """构建字段校验的详细消息"""
        if success:
            return f"字段 '{field_path}' 校验成功"
        else:
            if validator == "not_empty":
                return f"字段 '{field_path}' 不能为空，当前值: {repr(actual_value)}"
            elif validator in ["eq", "equals"]:
                return f"字段 '{field_path}' 应该等于 {repr(expect_value)}，当前值: {repr(actual_value)}"
            elif validator == "ne":
                return f"字段 '{field_path}' 不应该等于 {repr(expect_value)}，当前值: {repr(actual_value)}"
            elif validator == "gt":
                return f"字段 '{field_path}' 应该大于 {expect_value}，当前值: {actual_value}"
            elif validator == "ge":
                return f"字段 '{field_path}' 应该大于等于 {expect_value}，当前值: {actual_value}"
            elif validator == "lt":
                return f"字段 '{field_path}' 应该小于 {expect_value}，当前值: {actual_value}"
            elif validator == "le":
                return f"字段 '{field_path}' 应该小于等于 {expect_value}，当前值: {actual_value}"
            elif validator == "contains":
                return f"字段 '{field_path}' 应该包含 {repr(expect_value)}，当前值: {repr(actual_value)}"
            elif validator == "startswith":
                return f"字段 '{field_path}' 应该以 {repr(expect_value)} 开头，当前值: {repr(actual_value)}"
            elif validator == "endswith":
                return f"字段 '{field_path}' 应该以 {repr(expect_value)} 结尾，当前值: {repr(actual_value)}"
            elif validator == "regex":
                return f"字段 '{field_path}' 应该匹配正则表达式 {repr(expect_value)}，当前值: {repr(actual_value)}"
            elif validator == "type_match":
                return f"字段 '{field_path}' 应该是 {expect_value} 类型，当前类型: {type(actual_value).__name__}"
            elif validator.startswith("length_"):
                length_desc = {
                    "length_eq": f"长度等于 {expect_value}",
                    "length_ne": f"长度不等于 {expect_value}",
                    "length_gt": f"长度大于 {expect_value}",
                    "length_ge": f"长度大于等于 {expect_value}",
                    "length_lt": f"长度小于 {expect_value}",
                    "length_le": f"长度小于等于 {expect_value}"
                }.get(validator, f"长度校验 {validator}")
                return f"字段 '{field_path}' {length_desc}，当前长度: {len(actual_value) if hasattr(actual_value, '__len__') else 'N/A'}"
            else:
                return f"字段 '{field_path}' 校验失败: 期望{repr(expect_value)}, 实际{repr(actual_value)} (校验器: {validator})"
                
    def build_detailed_result(self):
        """构建详细的校验结果对象"""

        # 按规则分组字段结果
        rule_results = []
        rule_groups = {}
        
        # 按规则名分组所有字段结果
        for field_info in self.field_results:
            rule_name = field_info['rule_name']
            if rule_name not in rule_groups:
                rule_groups[rule_name] = []
            rule_groups[rule_name].append(field_info)
        
        # 为每个规则构建 RuleResult
        for rule_name, field_infos in rule_groups.items():
            # 构建该规则的所有 FieldResult
            field_results = []
            passed_count = 0
            failed_count = 0
            
            for field_info in field_infos:
                field_result = FieldResult(
                    field_path=field_info['field_path'],
                    validator=field_info['validator'],
                    expect_value=field_info['expect_value'],
                    actual_value=field_info['actual_value'],
                    success=field_info['success'],
                    message=field_info['message']
                )
                field_results.append(field_result)
                
                if field_info['success']:
                    passed_count += 1
                else:
                    failed_count += 1
            
            # 获取规则统计信息
            rule_stats = self.rule_stats.get(rule_name)
            if rule_stats:
                total_fields = rule_stats.total_count
                failure_rate = rule_stats.get_failure_rate()
                rule_success = not rule_stats.exceeds_threshold(self.max_fail)
                threshold_info = self.get_threshold_info()
            else:
                total_fields = len(field_infos)
                failure_rate = failed_count / total_fields if total_fields > 0 else 0.0
                rule_success = failed_count == 0
                threshold_info = "无统计信息" # TODO: 需要优化
            
            # 构建原始规则表达式（去掉 "rule_X: " 前缀）
            original_rule = rule_name.split(": ", 1)[1] if ": " in rule_name else rule_name
            
            rule_result = RuleResult(
                rule=original_rule,
                total_fields=total_fields,
                passed_fields=passed_count,
                failed_fields=failed_count,
                field_results=field_results,
                success=rule_success,
                failure_rate=failure_rate,
                threshold_info=threshold_info
            )
            rule_results.append(rule_result)
        
        # 计算整体结果
        total_rules = len(rule_results)
        passed_rules = len([r for r in rule_results if r.success])
        failed_rules = total_rules - passed_rules
        overall_success = failed_rules == 0
        
        # 构建摘要信息
        if self.is_strict_mode:
            if overall_success:
                summary = f"所有校验通过: {total_rules} 个规则全部成功，共校验了 {len(self.field_results)} 个字段"
            else:
                summary = f"校验失败: {total_rules} 个规则中有 {failed_rules} 个失败，失败率 {failed_rules/total_rules:.1%}{'（快速失败模式）' if self.fast_fail else ''}"
            execution_mode = "strict"
        else:
            if overall_success:
                summary = f"阈值校验通过: {total_rules} 个规则均未超过失败阈值"
            else:
                summary = f"阈值校验失败: {total_rules} 个规则中有 {failed_rules} 个超过失败阈值 {'（快速失败模式）' if self.fast_fail else ''}"
            execution_mode = "threshold"
        
        # 构建最终结果
        result = ValidationResult(
            success=overall_success,
            total_rules=total_rules,
            passed_rules=passed_rules,
            failed_rules=failed_rules,
            rule_results=rule_results,
            summary=summary,
            max_fail_info=self.get_threshold_info(),
            execution_mode=execution_mode,
            fast_fail=self.fast_fail,
            output_format=self.output_format
        )
        
        return result
        
    def is_success(self):
        """判断整体校验是否成功（兼容原有 check() 函数的返回值）"""
        if self.is_strict_mode:
            return not self.should_abort
        else:
            # 阈值模式：检查是否有规则超过阈值
            exceeded_rules = [stats for stats in self.rule_stats.values()
                             if stats.exceeds_threshold(self.max_fail)]
            return len(exceeded_rules) == 0


class ValidationEngine:
    """核心校验引擎 - 被新旧API共同使用"""
    
    def execute(self, data, validations, max_fail=None, fast_fail=True, context=None, output_format="summary"):
        """
        执行校验并返回上下文对象
        
        :param data: 待校验的数据
        :param validations: 校验规则，支持多种简洁格式
        :param max_fail: 失败阈值
        :param fast_fail: 快速失败，默认True
        :param context: 上下文对象，用于累积校验结果（链式调用时使用）
        :param output_format: 校验结果输出格式：summary/detail/dict
        :return: 校验上下文对象
        """
        # 打印任务信息和数据概览
        log_info(f"开始执行数据校验 - 共{len(validations)}个校验规则")
        log_debug(f"待校验数据类型: {type(data).__name__}")
        log_debug(f"校验规则列表: {list(validations)}")
        log_debug(f"失败阈值: {'默认严格模式' if max_fail is None else max_fail}")
        log_debug(f"快速失败: {'是' if fast_fail else '否'}")

        # 参数验证
        if not validations:
            raise ValueError("至少需要提供一个校验规则")
        
        # 如果校验上下文不存在，则创建新校验上下文
        if context is None:
            context = ValidationContext(max_fail, fast_fail, output_format)
        
        # 执行所有校验规则
        for i, validation in enumerate(validations):
            try:
                # 特殊处理：条件校验规则本身不记录到规则统计结果中，直接进行then规则校验，且通过context上下文参数进行校验结果聚合
                if isinstance(validation, dict) and 'conditional' in validation.get('validator', ''):
                    parse_and_validate(data, validation, context)
                    continue

                log_debug(f"[{i+1}/{len(validations)}] 开始校验: {validation}")
                # 设置当前规则名（用于统计）
                rule_name = f"rule_{i+1}: {validation}"
                context.set_current_rule(rule_name)
                # 解析校验规则并执行校验
                result = parse_and_validate(data, validation, context)
                # 记录规则级别校验结果
                if context.is_strict_mode:
                    context.record_rule_result(result) # 在严格模式下，规则的成功与否由parse_and_validate的返回值决定
                    
                    if not result:
                        log_warning(f"[{i+1}/{len(validations)}] 校验失败: {validation} ✗")
                        if context.fast_fail:
                            break # 快速失败
                    else:
                        log_debug(f"[{i+1}/{len(validations)}] 校验通过: {validation} ✓")
                else:
                    rule_stats = context.rule_stats[rule_name]
                    rule_exceeds_threshold = rule_stats.exceeds_threshold(context.max_fail)
                    context.record_rule_result(not rule_exceeds_threshold) # 在阈值模式下，规则的成功与否由是否超过阈值决定：不超过阈值为成功

                    if rule_exceeds_threshold:
                        log_warning(f"[{i+1}/{len(validations)}] 校验失败: {validation} ✗")
                        if context.fast_fail:
                            break # 快速失败
                    else:
                        log_debug(f"[{i+1}/{len(validations)}] 校验通过: {validation} ✓")
            except (KeyError, IndexError, TypeError, ValueError) as e:
                # 数据异常 - 提供更好的上下文信息（使用 from e 保持异常链，便于深度调试）
                error_msg = f"数据结构异常: {validation} - {str(e)}"
                log_error(f"[{i+1}/{len(validations)}] ❌ {error_msg}")
                raise ValueError(error_msg) from e
            except Exception as e:
                # 业务异常：ValidationError 需要直接传播，保持业务语义
                if isinstance(e, ValidationError):
                    raise e
                # 其他系统异常 - 包装为运行时异常
                error_msg = f"校验出现异常: {validation} - '{str(e)}'"
                log_error(f"[{i+1}/{len(validations)}] ❌ {error_msg}")
                raise RuntimeError(error_msg) from e
        
        # 输出最终统计日志
        if context.is_strict_mode:
            # 严格模式：任何失败都返回False
            success_rate = f"{context.passed_count}/{len(validations)}"
            log_info(f"数据校验完成: {success_rate} 通过 (成功率: {context.passed_count/len(validations)*100:.1f}%)")
            
            if context.failed_count > 0:
                log_debug(f"失败统计: 共{context.failed_count}个校验失败")
        else:
            # 阈值模式：检查是否有规则超过阈值
            total_rules = len(context.rule_stats)
            exceeded_rules = [stats for stats in context.rule_stats.values() if stats.exceeds_threshold(context.max_fail)]
            threshold_info = context.get_threshold_info()
            log_info(f"数据校验完成: 总规则{total_rules}个，超过阈值{len(exceeded_rules)}个 | 阈值设置: {threshold_info}")
            
            if exceeded_rules:
                for stats in exceeded_rules:
                    log_warning(f"规则超阈值详情: {stats.rule_name} - 失败{stats.failed_count}/{stats.total_count} (失败率{stats.get_failure_rate():.1%})")
        
        return context


def parse_and_validate(data, rule, context):
    """解析校验规则并执行校验"""
    if isinstance(rule, str):
        return _parse_string_rule(data, rule, context)
    elif isinstance(rule, dict):
        return _parse_dict_rule(data, rule, context)
    else:
        raise ValueError(f"不支持的校验规则格式: {type(rule)}")


def _parse_logical_condition(data, rule, context):
    """解析包含逻辑操作符的联合条件表达式
    
    支持的逻辑操作符：
    - && (AND): 逻辑与，优先级高
    - || (OR): 逻辑或，优先级低
    
    操作符优先级: && > ||
    支持短路求值优化
    
    示例:
    - "status == 'active' && level == 'vip'"
    - "type == 'premium' || level == 'admin'"  
    - "status == 'active' && level == 'vip' || type == 'admin'"
    """
    log_debug(f"解析联合条件: {rule}")
    
    # 第一步: 按 || 分割 (优先级最低)
    or_parts = _split_logical_expression(rule, '||')
    
    if len(or_parts) > 1:
        # 有OR条件，任何一个为True即可 (短路求值)
        for or_part in or_parts:
            or_part = or_part.strip()
            try:
                if _evaluate_and_condition(data, or_part, context):
                    log_debug(f"OR条件命中: {or_part}")
                    return True
            except Exception as e:
                # 如果某个OR分支失败，继续尝试下一个
                log_debug(f"OR条件失败: {or_part} - {str(e)}")
                continue
        # 所有OR条件都失败
        log_debug("所有OR条件都失败")
        return False
    else:
        # 没有OR，只有AND或单一条件
        return _evaluate_and_condition(data, rule, context)


def _evaluate_and_condition(data, rule, context):
    """评估AND条件表达式"""
    # 按 && 分割
    and_parts = _split_logical_expression(rule, '&&')
    
    if len(and_parts) > 1:
        # 有AND条件，所有都必须为True (短路求值)
        for and_part in and_parts:
            and_part = and_part.strip()
            if not _parse_single_condition(data, and_part, context):
                log_debug(f"AND条件失败: {and_part}")
                return False
        log_debug("所有AND条件都通过")
        return True
    else:
        # 单一条件
        return _parse_single_condition(data, rule, context)


def _split_logical_expression(expression, operator):
    """安全分割逻辑表达式，正确处理引号内容"""
    parts = []
    current_part = ""
    in_quotes = False
    quote_char = None
    i = 0
    
    while i < len(expression):
        char = expression[i]
        
        # 处理引号
        if char in ('"', "'") and (i == 0 or expression[i-1] != '\\'):
            if not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char:
                in_quotes = False
                quote_char = None
        
        # 检查操作符
        if not in_quotes and i <= len(expression) - len(operator):
            if expression[i:i+len(operator)] == operator:
                # 找到操作符
                parts.append(current_part)
                current_part = ""
                i += len(operator)
                continue
        
        current_part += char
        i += 1
    
    # 添加最后一部分
    parts.append(current_part)
    return parts


def _parse_single_condition(data, rule, context):
    """解析单一条件（原_parse_string_rule的核心逻辑）"""
    # 支持的操作符映射 (注意：按长度排序，避免匹配冲突)
    operators = [
        ("#<=", "length_le"), ("#>=", "length_ge"), ("#!=", "length_ne"), ("#=", "length_eq"), ("#<", "length_lt"), ("#>", "length_gt"), ("!=", "ne"),
        ("==", "eq"), ("<=", "le"), (">=", "ge"), ("<", "lt"), (">", "gt"),
        ("~=", "regex"), ("^=", "startswith"), ("$=", "endswith"), ("*=", "contains"), ("=*", "contained_by"),
        ("@=", "type_match")
    ]
    
    # 尝试匹配操作符
    for op, validator in operators:
        if op in rule:
            parts = rule.split(op, 1)
            if len(parts) == 2:
                field_path = parts[0].strip()
                expect_value = parts[1].strip()
                
                # 解析期望值
                expect_value = _parse_expect_value(expect_value)
                
                # 执行校验
                return _validate_field_path(data, field_path, validator, expect_value, context)
    
    # 没有操作符，默认为非空校验
    field_path = rule.strip()
    return _validate_field_path(data, field_path, "not_empty", True, context)


def _parse_string_rule(data, rule, context):
    """解析字符串格式的校验规则"""
    # 检查是否包含逻辑操作符
    if '&&' in rule or '||' in rule:
        return _parse_logical_condition(data, rule, context)
    
    # 单一条件，使用原有逻辑
    return _parse_single_condition(data, rule, context)


def _parse_dict_rule(data, rule, context):
    """解析字典格式的校验规则"""
    field_path = rule.get('field')
    validator = rule.get('validator', 'not_empty')
    expect_value = rule.get('expect')
    
    if not field_path:
        raise ValueError("字典格式校验规则必须包含'field'键")
    
    return _validate_field_path(data, field_path, validator, expect_value, context)


def _parse_expect_value(value_str):
    """解析期望值字符串为合适的类型"""
    value_str = value_str.strip()
    
    # 去掉引号
    if (value_str.startswith('"') and value_str.endswith('"')) or \
       (value_str.startswith("'") and value_str.endswith("'")):
        return value_str[1:-1]
    
    # 数字
    if value_str.isdigit():
        return int(value_str)
    
    # 浮点数
    try:
        if '.' in value_str:
            return float(value_str)
    except ValueError:
        pass
    
    # 布尔值
    if value_str.lower() in ['true', 'false']:
        return value_str.lower() == 'true'
    
    # null
    if value_str.lower() in ['null', 'none']:
        return None
    
    # 默认返回字符串
    return value_str


def _validate_field_path(data, field_path, validator, expect_value, context):
    """校验字段路径 - 统一严格模式和阈值模式
    
    :param context: ValidationContext对象，None表示当前是执行条件校验condition条件规则检查，不记录结果到统计中
    :return: True表示校验通过或需要继续执行，False表示严格模式下需要立即停止
    """
    # 特殊处理：条件校验(校验规则为字典格式场景，直接调用对应函数)
    if validator.startswith("conditional"):
        from .validator import validate_when, validate_when_each, validate_list_when
        condition = expect_value['condition']
        then_rules = expect_value['then'] if isinstance(expect_value['then'], list) else [expect_value['then']]
        if validator == "conditional_check":
            return validate_when(data, condition, *then_rules, max_fail=context.max_fail, fast_fail=context.fast_fail, context=context)
        elif validator == "conditional_each_check":
            return validate_when_each(data, condition, *then_rules, max_fail=context.max_fail, fast_fail=context.fast_fail, context=context)
        elif validator == "conditional_list_check":
            return validate_list_when(data, condition, *then_rules, max_fail=context.max_fail, fast_fail=context.fast_fail, context=context)
        else:
            raise ValueError(f"不支持的校验器: {validator}")

    values = _get_values_by_path(data, field_path)
    log_debug(f"字段路径 '{field_path}' 匹配到 {len(values)} 个值")
    if len(values) == 0:
        raise ValueError(f"字段路径 '{field_path}' 匹配到 0 个值，请检查字段路径是否正确")
    
    # 记录所有校验结果，如果有一个失败，则返回False
    rule_result = True
    for value, path in values:
        result = _execute_validator(validator, value, expect_value, path)
        detail = f"校验字段 '{path}': {type(value).__name__} = {repr(value)} | 校验器: {validator} | 期望值: {repr(expect_value)}"
        
        if context is not None:
            # context不为 None，说明当前是执行普通校验规则，记录结果到统计中
            context.record_field_result(result, path, validator, expect_value, value, detail)
            if result:
                log_debug(f"{detail} | 检验结果: ✓")
            else:
                log_warning(f"{detail} | 检验结果: ✗")
                rule_result = False
                # 严格模式下快速失败，立即返回失败（非严格模式则需要执行完规则的所有校验，才能确定是否超过阈值）
                if context.is_strict_mode and context.fast_fail:
                    return False
        else:
            # context为 None，说明当前是执行条件校验condition条件规则检查，不记录结果到统计中
            if result:
                log_debug(f"{detail} | 检验结果: ✓")
            else:
                log_warning(f"{detail} | 检验结果: ✗")
                # 失败立即返回
                return False

    return rule_result



def _get_values_by_path(obj, path):
    """根据路径获取值，支持通配符*"""
    if not path:
        return [(obj, "")]
    
    parts = path.split('.')
    current_objects = [(obj, "")]
    
    for part in parts:
        next_objects = []
        for current_obj, current_path in current_objects:
            new_path = f"{current_path}.{part}" if current_path else part
            
            if part == '*':
                if isinstance(current_obj, list):
                    for i, item in enumerate(current_obj):
                        next_objects.append((item, f"{current_path}[{i}]" if current_path else f"[{i}]"))
                elif isinstance(current_obj, dict):
                    for key, value in current_obj.items():
                        next_objects.append((value, f"{current_path}.{key}" if current_path else key))
                else:
                    raise TypeError(f"通配符'*'只能用于列表或字典，路径: {current_path}, 类型: {type(current_obj)}")
            else:
                if isinstance(current_obj, dict):
                    if part not in current_obj:
                        raise KeyError(f"字段不存在: {new_path}")
                    next_objects.append((current_obj[part], new_path))
                elif isinstance(current_obj, list):
                    if not part.isdigit():
                        raise ValueError(f"列表索引必须是数字: {part}")
                    index = int(part)
                    if index < 0 or index >= len(current_obj):
                        raise IndexError(f"索引超出范围: {new_path}")
                    next_objects.append((current_obj[index], f"{current_path}[{index}]" if current_path else f"[{index}]"))
                else:
                    raise TypeError(f"无法在{type(current_obj)}上访问字段: {part}")
        current_objects = next_objects
    
    return current_objects


def _check_type_match(check_value, expect_value):
    """检查值的类型是否匹配期望类型
    
    :param check_value: 要检查的值
    :param expect_value: 期望的类型，可以是类型对象或类型名称字符串
    :return: True表示类型匹配，False表示类型不匹配
    """
    def get_type(name):
        """根据名称获取类型对象"""
        if isinstance(name, type):
            return name
        elif isinstance(name, str):
            # 支持常见的类型名称
            type_mapping = {
                'int': int,
                'float': float,
                'str': str,
                'string': str,
                'bool': bool,
                'boolean': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'nonetype': type(None),
                'none': type(None),
                'null': type(None)
            }
            
            # 先检查自定义映射
            if name.lower() in type_mapping:
                return type_mapping[name.lower()]
            
            # 尝试从内置类型获取
            try:
                return eval(name)
            except:
                raise ValueError(f"不支持的类型名称: {name}")
        else:
            raise ValueError(f"期望值必须是类型对象或类型名称字符串，当前类型: {type(expect_value)}")
    
    try:
        expected_type = get_type(expect_value)
        return isinstance(check_value, expected_type)
    except Exception as e:
        raise TypeError(f"类型匹配检查失败: {str(e)}")


def _safe_numeric_compare(check_value, expect_value):
    """安全的数值比较，支持字符串数字自动转换
    
    :param check_value: 要检查的值
    :param expect_value: 期望值
    :return: (转换后的check_value, 转换后的expect_value)
    :raises: ValueError: 当值无法转换为数字时
    """
    def to_number(value):
        """将值转换为数字"""
        if isinstance(value, (int, float)):
            return value
        elif isinstance(value, str):
            # 去除首尾空格
            value = value.strip()
            # 尝试转换为整数
            try:
                return int(value)
            except ValueError:
                pass
            # 尝试转换为浮点数
            try:
                return float(value)
            except ValueError:
                pass
        # 无法转换，返回原值
        return value
    
    # 转换两个值
    converted_check = to_number(check_value)
    converted_expect = to_number(expect_value)
    
    # 如果任一值无法转换为数字，回退到原始比较
    if (not isinstance(converted_check, (int, float)) or not isinstance(converted_expect, (int, float))):
        return check_value, expect_value
    
    return converted_check, converted_expect


def _execute_validator(validator, check_value, expect_value, field_path):
    """执行具体的校验
    
    :return: True表示校验通过，False表示校验失败
    :raises: ValueError: 当校验器不支持时
    :raises: TypeError: 当数据类型不匹配时
    """
    try:
        if validator == "not_empty":
            is_empty, _ = is_empty_value(check_value)
            return not is_empty
        
        elif validator == "eq":
            return check_value == expect_value
        
        elif validator == "ne":
            return check_value != expect_value
        
        elif validator == "gt":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val > expect_val
        
        elif validator == "ge":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val >= expect_val
        
        elif validator == "lt":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val < expect_val
        
        elif validator == "le":
            # 数值比较校验器 - 添加智能类型转换
            check_val, expect_val = _safe_numeric_compare(check_value, expect_value)
            return check_val <= expect_val
        
        elif validator == "contains":
            return expect_value in check_value
        
        elif validator == "contained_by":
            return check_value in expect_value
        
        elif validator == "startswith":
            return str(check_value).startswith(str(expect_value))
        
        elif validator == "endswith":
            return str(check_value).endswith(str(expect_value))
        
        elif validator == "regex":
            import re
            try:
                return bool(re.match(str(expect_value), str(check_value)))
            except re.error:
                return False
        
        elif validator == "type_match":
            return _check_type_match(check_value, expect_value)
        
        elif validator == "custom_number_check":
            return isinstance(check_value, (int, float))
        
        elif validator == "in_values":
            return check_value in expect_value
        
        elif validator == "not_in_values":
            return check_value not in expect_value
        
        elif validator == "length_eq":
            return len(check_value) == expect_value
        
        elif validator == "length_ne":
            return len(check_value) != expect_value
        
        elif validator == "length_gt":
            return len(check_value) > expect_value
        
        elif validator == "length_ge":
            return len(check_value) >= expect_value

        elif validator == "length_lt":
            return len(check_value) < expect_value
        
        elif validator == "length_le":
            return len(check_value) <= expect_value

        elif validator == "length_between":
            min_len, max_len = expect_value
            return min_len <= len(check_value) <= max_len
        
        else:
            raise ValueError(f"不支持的校验器: {validator}")
    
    except Exception as e:
        log_error(f"执行校验时出现异常：校验字段 '{field_path}': {type(check_value).__name__} = {repr(check_value)} | 校验器: {validator} | 期望值: {repr(expect_value)} | 异常信息: {str(e)}")
        raise


def _parse_path_expression(expression):
    """
    解析路径表达式，返回路径前缀和相对表达式
    
    支持联合条件和单一条件的路径解析，基于列表通配符*.的位置进行分割(避免与操作符*=冲突)

    例如：
    "users.*.status == 'active'" -> ("users.*", "status == 'active'")
    "users.*.status == 'active' && users.*.level == 'vip'" -> ("users.*", "status == 'active' && level == 'vip'")
    "data.regions.*.cities.*.status == 'active'" -> ("data.regions.*.cities.*", "status == 'active'")
    
    :param expression: 路径表达式字符串，必须包含列表通配符*.以定位列表数据项集合
    :return: (路径前缀, 相对表达式)
    :raises: ValueError: 当表达式格式不正确时
    """
    if not expression or not isinstance(expression, str):
        raise ValueError(f"表达式必须是非空字符串，当前值: {expression}")
    
    expression = expression.strip()
    
    # 验证必须包含列表通配符*.以定位列表数据项集合
    if '*.' not in expression:
        raise ValueError(f"路径表达式必须包含列表通配符*.以定位列表数据项集合: {expression}")
    
    # 检查是否为联合条件
    if '&&' in expression or '||' in expression:
        return _parse_compound_path_expression(expression)
    else:
        return _parse_single_path_expression(expression)


def _parse_single_path_expression(expression):
    """解析单一条件的路径表达式"""
    # 找到最后一个列表通配符*.的位置
    last_wildcard_pos = expression.rfind('*.')
    
    # 向前查找到最近的点号，确定路径前缀的结束位置
    prefix_end = last_wildcard_pos + 1  # 包含*号
    
    # 向后查找到最近的点号，确定相对表达式的开始位置
    remaining_part = expression[prefix_end:]
    if remaining_part.startswith('.'):
        relative_start = prefix_end + 1  # 跳过点号
    else:
        raise ValueError(f"路径表达式中列表通配符*.后必须有具体字段: {expression}")
    
    # 分割路径前缀和相对表达式
    path_prefix = expression[:prefix_end]
    relative_expression = expression[relative_start:]
    
    # 验证相对表达式不为空
    if not relative_expression:
        raise ValueError(f"路径表达式中列表通配符*.后必须有具体字段: {expression}")
    
    return path_prefix, relative_expression


def _parse_compound_path_expression(expression):
    """解析联合条件的路径表达式"""
    # 首先找到所有的路径前缀
    path_prefixes = set()
    
    # 分解联合条件为单个条件
    conditions = _extract_individual_conditions(expression)
    
    for condition in conditions:
        condition = condition.strip()
        if '*.' not in condition:
            continue
            
        # 找到最后一个列表通配符*.的位置
        last_wildcard_pos = condition.rfind('*.')
        prefix_end = last_wildcard_pos + 1  # 包含*号
        
        # 确定路径前缀
        path_prefix = condition[:prefix_end]
        path_prefixes.add(path_prefix)
    
    # 验证所有条件使用相同的路径前缀
    if len(path_prefixes) != 1:
        raise ValueError(f"联合条件中所有子条件必须使用相同的路径前缀: {list(path_prefixes)}")
    
    common_prefix = list(path_prefixes)[0]
    
    # 构建相对表达式：将所有条件的路径前缀替换为空
    relative_expression = _build_relative_expression(expression, common_prefix)
    
    return common_prefix, relative_expression


def _extract_individual_conditions(expression):
    """从联合条件表达式中提取单个条件"""
    # 首先按 || 分割
    or_parts = _split_logical_expression(expression, '||')
    
    conditions = []
    for or_part in or_parts:
        # 再按 && 分割每个 OR 部分
        and_parts = _split_logical_expression(or_part, '&&')
        conditions.extend(and_parts)
    
    return [cond.strip() for cond in conditions if cond.strip()]


def _build_relative_expression(expression, path_prefix):
    """构建相对表达式，去掉路径前缀"""
    # 替换所有路径前缀为空
    prefix_pattern = path_prefix + '.'
    relative_expr = expression.replace(prefix_pattern, '')
    
    # 清理多余的空格
    relative_expr = ' '.join(relative_expr.split())
    
    return relative_expr


def is_empty_value(value):
    """判断值是否为空"""
    if value is None:
        return True, "值为 None"
    if isinstance(value, str):
        if value.strip() == '':
            return True, "值为空字符串"
        if value.strip().lower() == 'null':
            return True, "值为字符串 'null'"
    if isinstance(value, (list, dict)) and len(value) == 0:
        return True, f"值为空{type(value).__name__}"
    return False, None


def get_nested_value(obj, path):
    """根据点分隔的路径获取嵌套值"""
    if not path:
        return obj

    parts = path.split('.')
    current = obj

    for part in parts:
        if not isinstance(current, dict):
            raise TypeError(f"路径 '{path}' 中的 '{part}' 需要字典类型，当前类型: {type(current)}")
        if part not in current:
            raise KeyError(f"路径 '{path}' 中的字段 '{part}' 不存在")
        current = current[part]

    return current


def perform_item_wise_conditional_check(data_or_list, condition, then_rules, max_fail, fast_fail=True, context=None, output_format="summary", mode="bool"):
    """
    逐项条件校验核心逻辑

    支持两种调用方式：
    1. 相对路径模式：data_or_list 为 list，condition/then_rules 为相对路径表达式
    2. 绝对路径模式：data_or_list 为任意数据，condition/then_rules 为绝对路径表达式（包含相同的列表前缀）
       - 内部会解析路径前缀；
       - 提取数据项列表；
       - 并将规则转换为相对表达式后复用列表模式流程；

    :param data_or_list: 校验的数据（任意类型）
    :param condition: 条件表达式
    :param then_rules: then规则列表
    :param max_fail: 失败阈值
    :param fast_fail: 快速失败，默认True
    :param context: 上下文对象，用于累积校验结果（链式调用时使用）
    :param output_format: 校验结果输出格式：summary/detail/dict
    :param mode: 校验结果返回模式
        - "assert": 断言模式，成功返回ValidationResult，失败抛ValidationError
        - "dict": 字典模式，成功/失败都返回结构化字典
        - "bool": 默认布尔模式，成功返回True，失败返回False

    :return: ValidationResult | dict | bool: 根据mode参数返回不同类型
    :raises: ValidationError: 当mode="assert"且校验失败时抛出
    :raises: Exception: 当条件校验异常或数据结构异常时
    """

    # 绝对路径模式，例如 when_each 支持任意数据结构，可以是字典或列表，使用的是绝对路径表达式指向目标列表
    if not isinstance(data_or_list, list) or condition.strip().startswith('*.'):
        data = data_or_list
        # 解析条件表达式，提取路径前缀和相对条件
        condition_path_prefix, relative_condition = _parse_path_expression(condition)
        log_debug(f"条件表达式解析: 路径前缀='{condition_path_prefix}', 相对条件='{relative_condition}'")

        # 验证所有 then 规则与条件的路径前缀一致，并转换为相对规则（前缀一致确保针对同一列表对象，但各个then规则可以嵌套深度不一样）
        relative_then_rules = []
        for i, rule in enumerate(then_rules):
            if not isinstance(rule, str):
                raise ValueError(f"then规则[{i+1}]必须是字符串路径表达式，当前类型: {type(rule)}")
            if not rule.startswith(condition_path_prefix + '.'):
                raise ValueError(f"条件和then规则的路径前缀必须相同: 条件路径前缀='{condition_path_prefix}' vs then[{i+1}]='{rule}'")
            relative_rule = rule.replace(condition_path_prefix + '.', '', 1)
            log_debug(f"then规则[{i+1}]解析: 路径前缀='{condition_path_prefix}', 相对规则='{relative_rule}'")
            relative_then_rules.append(relative_rule)

        # 获取要遍历的数据项列表
        log_debug(f"使用路径前缀获取数据项: {condition_path_prefix}")
        data_items = _get_values_by_path(data, condition_path_prefix)
        data_list = [item_value for item_value, _ in data_items]

        if not data_list:
            msg = f"路径 '{condition_path_prefix}' 没有匹配到任何数据项, 跳过校验"
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

        log_debug(f"路径 '{condition_path_prefix}' 匹配到 {len(data_list)} 个数据项")
        # 进入列表模式
        return perform_item_wise_conditional_check(data_list, relative_condition, relative_then_rules, max_fail, fast_fail, context, output_format, mode)

    # 相对路径模式，例如 list_when 专门用于列表数据，使用的是相对路径表达式指向目标列表
    data_list = data_or_list
    satisfied_items = []

    # 第一轮：筛选满足条件的数据项
    for i, item in enumerate(data_list):
        try:
            condition_result = parse_and_validate(item, condition, context=None)
            if condition_result:
                satisfied_items.append(item)
                log_debug(f"数据项[{i}]满足条件: {condition}")
            else:
                log_debug(f"数据项[{i}]不满足条件: {condition}, 跳过")
        except Exception as e:
            error_msg = f"数据项[{i}]条件校验异常: {condition} - {str(e)}"
            log_error(f"❌ {error_msg}")
            raise Exception(error_msg)

    if not satisfied_items:
        msg = f"没有数据项满足条件: {condition}, 跳过then校验"
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

    log_debug(f"共{len(satisfied_items)}/{len(data_list)}个数据项满足条件，开始then校验")

    # 第二轮：对满足条件的数据项执行then校验
    list_then_rules = [f"*.{rule}" for rule in then_rules]
    from .validator import validate
    return validate(satisfied_items, *list_then_rules, max_fail=max_fail, fast_fail=fast_fail, output_format=output_format, mode=mode, context=context)