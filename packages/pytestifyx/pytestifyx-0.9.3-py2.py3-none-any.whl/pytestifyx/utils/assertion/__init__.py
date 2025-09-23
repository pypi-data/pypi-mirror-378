"""
PyTestifyx 断言工具包

提供灵活且强大的断言方法，支持不同粒度的数据比较和验证。

主要功能：
- 基础断言（相等、不等、包含等）
- JSON/字典深度比较with精细化控制
- 响应断言（状态码、头部、响应体）
- 数组/列表断言
- 字符串断言（正则、长度等）
- 数值断言（范围、精度等）
- 部分匹配和忽略字段
- 自定义断言条件

使用示例：
    # 基础断言
    assert_that(response.status_code).equals(200)
    assert_that(data).is_not_none()
    
    # JSON深度比较
    assert_that(actual_data).deep_equals(expected_data)
    
    # 忽略字段
    assert_that(actual_data).ignore_fields_config(['timestamp']).deep_equals(expected_data)
    
    # 部分匹配
    assert_that(actual_data).partial_match_config().deep_equals(expected_data)
    
    # 响应断言
    assert_that(response).status_code(200).is_json().json_contains({"code": 200})
    
    # 专业化比较器
    json_comp = JsonComparator(data)
    result = json_comp.deep_compare(expected, ignore_fields=['id'], partial_match=True)
    
    # 数组断言
    array_comp = ArrayComparator(items)
    assert array_comp.contains_all(['item1', 'item2'])
    
    # 字符串断言
    str_comp = StringComparator(text)
    assert str_comp.matches_pattern(r'\\d{4}-\\d{2}-\\d{2}')
    
    # 数值断言
    num_comp = NumberComparator(value)
    assert num_comp.is_between(1, 100)
"""

from .core import AssertionManager, AssertionError
from .comparator import (
    BaseComparator, JsonComparator, ArrayComparator, 
    StringComparator, NumberComparator
)
from .validator import ResponseValidator, SchemaValidator
from .utils import (
    IgnoreFields, PartialMatch, DataTransformer, 
    ComparisonConfig, PathMatcher, DataMasker
)

# 创建全局断言管理器实例
assert_that = AssertionManager()

# 便捷函数
def assert_response(response):
    """创建响应验证器的便捷函数"""
    return ResponseValidator(response)

def assert_schema(data):
    """创建模式验证器的便捷函数"""
    return SchemaValidator(data)

def assert_json(data):
    """创建JSON比较器的便捷函数"""
    return JsonComparator(data)

def assert_array(data):
    """创建数组比较器的便捷函数"""
    return ArrayComparator(data)

def assert_string(data):
    """创建字符串比较器的便捷函数"""
    return StringComparator(data)

def assert_number(data):
    """创建数值比较器的便捷函数"""
    return NumberComparator(data)

# 导出主要接口
__all__ = [
    # 核心断言
    'assert_that',
    'AssertionManager', 
    'AssertionError',
    
    # 比较器
    'BaseComparator',
    'JsonComparator',
    'ArrayComparator', 
    'StringComparator',
    'NumberComparator',
    
    # 验证器
    'ResponseValidator',
    'SchemaValidator',
    
    # 工具类
    'IgnoreFields',
    'PartialMatch',
    'DataTransformer',
    'ComparisonConfig',
    'PathMatcher',
    'DataMasker',
    
    # 便捷函数
    'assert_response',
    'assert_schema',
    'assert_json',
    'assert_array',
    'assert_string',
    'assert_number'
]
