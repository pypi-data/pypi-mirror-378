# General-Validator

<p align="center">
  <img src="https://img.shields.io/badge/version-1.4.0-brightgreen" alt="Version">
  <img src="https://img.shields.io/badge/python-3.7%2B-blue" alt="Python">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/lang-中文%20%7C%20English-blue" alt="Language">
</p>

一款极简通用数据校验器，专为批量复杂数据校验场景设计，通过极简的校验语法、灵活的阈值机制、强大的联合条件功能，让数据校验变得简单而强大！

> **🌍 [English Documentation](README-EN.md)** | **🇨🇳 [中文完整文档](docs/README.md)**

## ✨ 核心特性

- 🚀 **极简调用**: `check(data, "field > 0")` 一个入口搞定所有校验场景
- 📝 **默认非空**: `check(data, "field1", "field2")` 无需记忆复杂语法
- 🎯 **直观语法**: `"field > 0"` 近乎自然语言表达，简洁好理解
- 🔍 **智能解析**: 自动推断数据类型和校验逻辑
- 🌟 **通配符支持**: `"*.field"` 实现无限深度链式批量校验
- ⚙️ **失败阈值控制**: 严格模式/数量阈值/比率阈值灵活切换
- 🔗 **联合规则校验**: 支持 `&&`（AND）和 `||`（OR）逻辑操作符
- 📊 **详细校验信息**: 新增 validate 系列提供完整校验结果统计分析

## 🚀 快速开始

### 安装

```bash
pip install general-validator
```

### 5分钟上手

```python
from general_validator import check, validate

# 1. 基础校验 - 校验结果返回布尔值
data = {"name": "Alice", "age": 25, "email": "alice@example.com"}
result = check(data, "name", "age > 18", "email *= '@'")  # True

# 2. 详细校验 - 校验结果返回完整分析
try:
    result = validate(data, "name", "age > 18", "email *= '@'")
    print(f"校验详情: {result}")
except ValidationError as e:
    print(f"失败详情: {e}")

# 3. 批量列表校验
users = [
    {"name": "Alice", "age": 25},
    {"name": "Bob", "age": 30},
    {"name": "", "age": 20}  # name为空
]
check(users, "*.name", "*.age > 18", max_fail=1)  # 允许1个失败

# 4. 条件校验
check_when_each(data, "users.*.status == 'active'", "users.*.score > 70")
```

## 📚 文档导航

| 文档 | 描述 |
|------|------|
| [🎯 快速入门](docs/quick-start.md) | 新手友好的入门教程 |
| [📖 API 参考](docs/api-reference/) | 完整的 API 文档 |
| [⚡ 高级特性](docs/advanced-features/) | 阈值控制、条件校验等 |
| [💡 使用示例](docs/examples/) | 实际场景的完整示例 |
| [🏆 最佳实践](docs/best-practices/) | 性能优化和使用建议 |
| [❓ 常见问题](docs/FAQ.md) | 问题排查和解答 |

## 💻 API 预览

### check 系列 - 返回布尔值（经典API）

```python
# 基础校验
check(data, "field1", "field2 > 0", "field3 != null")

# 条件校验
check_when(data, "status == 'active'", "score > 70")
check_when_each(data, "users.*.status == 'active'", "users.*.score > 70")

# 列表校验
check_list(products, "id", "name", "price > 0", max_fail=2)

# 链式调用
checker(data).not_empty("name").greater_than("age", 18).validate()
```

### validate 系列 - 返回详细结果（增强API）

```python
try:
    # 获取详细校验结果
    result = validate(data, "field1", "field2 > 0", output_format="detail")
    print(f"总规则: {result.total_rules}, 成功: {result.passed_rules}")
    
    # 查看具体字段结果
    for rule_result in result.rule_results:
        print(f"规则 '{rule_result.rule}': {rule_result.success}")
        
except ValidationError as e:
    # 快速定位问题
    print(f"失败详情：{e}")
    first_failed = e.get_first_failed_field()
    print(f"首个失败: {first_failed.field_path} - {first_failed.message}")
```

## 🔥 主要优势

| 特性 | General-Validator | 传统方案 |
|------|------------------|---------|
| **学习成本** | ⭐⭐⭐⭐⭐ 零学习成本 | ⭐⭐ 需要学习复杂配置 |
| **代码简洁** | `check(data, "field > 0")` | 需要编写大量判断代码 |
| **批量处理** | `"*.field"` 一次搞定 | 需要循环遍历 |
| **错误定位** | 精确到具体字段路径 | 难以定位问题源头 |
| **阈值控制** | 内置支持严格/宽松模式 | 需要手动实现逻辑 |
| **性能优化** | 内置短路求值优化 | 需要手动优化 |

## 🎯 使用场景

- ✅ **接口测试**: API 响应数据校验
- ✅ **数据质量监控**: 批量数据完整性检查
- ✅ **业务规则验证**: 复杂条件下的数据校验
- ✅ **配置一致性**: 微服务配置校验
- ✅ **数据迁移**: 导入数据格式校验

## 📊 性能表现

- 🚀 单次校验：< 1ms
- 📈 批量校验：1000条数据 < 50ms
- 💾 内存占用：极小（< 10MB）
- 🔄 零依赖：仅使用 Python 标准库

## 🆕 新增特性

### validate 系列 API

新增的 validate 系列函数提供详细的校验分析：

```python
from general_validator import validate, ValidationError

try:
    result = validate(data, "field1", "field2 > 0")
    print(f"校验成功: {result.summary}")
    
    # 查看详细统计
    print(f"规则数: {result.total_rules}")
    print(f"成功率: {result.get_success_rate():.1%}")
    
except ValidationError as e:
    print(f"校验失败: {e.result.summary}")
    
    # 定位具体问题
    for failed_field in e.result.get_failed_fields():
        print(f"失败字段: {failed_field.field_path}")
        print(f"失败原因: {failed_field.message}")
```

### 快速失败模式

控制是否在遇到失败时立即停止：

```python
# 快速失败（默认）- 更快的性能
check(data, "field1", "field2", fast_fail=True)

# 完整执行 - 获取全部错误信息
result = validate(data, "field1", "field2", fast_fail=False)
```

### 输出格式控制

validate 系列支持多种输出格式：

```python
# 简洁摘要（默认）
result = validate(data, rules, output_format="summary")

# 详细信息
result = validate(data, rules, output_format="detail")

# 结构化信息
result = validate(data, rules, output_format="dict")
api_response = {"validation": result}

# 自定义
result = validate(data, rules)
print(result.summary) # 获取摘要信息
print(result.get_detail_message()) # 获取详细信息
print(result.to_dict()) # 获取结构化信息
```

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License - Free for commercial use

---

**让数据校验变得简单而强大！** 🚀