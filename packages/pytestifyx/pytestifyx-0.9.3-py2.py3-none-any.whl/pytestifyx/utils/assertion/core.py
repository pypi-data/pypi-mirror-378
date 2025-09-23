"""
断言核心模块

提供主要的断言管理器和基础断言方法。
"""

import json
import re
from typing import Any, Union, Optional, Dict, List, Callable
from deepdiff import DeepDiff

from pytestifyx.utils.logs.core import log
from .utils import IgnoreFields, PartialMatch


class AssertionError(Exception):
    """自定义断言异常"""
    pass


class AssertionManager:
    """
    断言管理器 - 提供链式调用的断言接口
    
    Usage:
        assert_that(actual).equals(expected)
        assert_that(response).status_code(200).contains_json({"code": 200})
        assert_that(data).ignore_fields(["timestamp"]).deep_equals(expected)
    """
    
    def __init__(self, actual: Any = None):
        self.actual = actual
        self.ignore_fields = []
        self.partial_match = False
        self.strict_order = True
        self.precision = None
        self.case_sensitive = True
        
    def __call__(self, actual: Any) -> 'AssertionManager':
        """允许函数式调用: assert_that(value)"""
        return AssertionManager(actual)
    
    def _log_comparison(self, expected: Any, result: bool, message: str = ""):
        """记录比较日志"""
        log.info(f'实际值: {json.dumps(self.actual, ensure_ascii=False, default=str)}')
        log.info(f'期望值: {json.dumps(expected, ensure_ascii=False, default=str)}')
        if result:
            log.info(f'断言成功: {message}')
        else:
            log.error(f'断言失败: {message}')
    
    def _raise_if_failed(self, condition: bool, message: str):
        """条件失败时抛出异常"""
        if not condition:
            raise AssertionError(message)
    
    # 配置方法 - 支持链式调用
    def ignore_fields_config(self, fields: Union[str, List[str]]) -> 'AssertionManager':
        """配置忽略的字段"""
        if isinstance(fields, str):
            fields = [fields]
        self.ignore_fields = fields
        return self
    
    def partial_match_config(self, enabled: bool = True) -> 'AssertionManager':
        """配置部分匹配模式"""
        self.partial_match = enabled
        return self
    
    def strict_order_config(self, enabled: bool = True) -> 'AssertionManager':
        """配置严格顺序模式"""
        self.strict_order = enabled
        return self
    
    def precision_config(self, precision: int) -> 'AssertionManager':
        """配置数值精度"""
        self.precision = precision
        return self
    
    def case_sensitive_config(self, enabled: bool = True) -> 'AssertionManager':
        """配置大小写敏感"""
        self.case_sensitive = enabled
        return self
    
    # 基础断言方法
    def equals(self, expected: Any, message: str = "") -> 'AssertionManager':
        """相等断言"""
        result = self.actual == expected
        self._log_comparison(expected, result, message or "相等性检查")
        self._raise_if_failed(result, f"期望值相等，但实际值 {self.actual} != {expected}")
        return self
    
    def not_equals(self, expected: Any, message: str = "") -> 'AssertionManager':
        """不相等断言"""
        result = self.actual != expected
        self._log_comparison(expected, result, message or "不相等性检查")
        self._raise_if_failed(result, f"期望值不相等，但实际值 {self.actual} == {expected}")
        return self
    
    def is_none(self, message: str = "") -> 'AssertionManager':
        """None断言"""
        result = self.actual is None
        self._log_comparison(None, result, message or "None检查")
        self._raise_if_failed(result, f"期望值为None，但实际值为 {self.actual}")
        return self
    
    def is_not_none(self, message: str = "") -> 'AssertionManager':
        """非None断言"""
        result = self.actual is not None
        self._log_comparison("not None", result, message or "非None检查")
        self._raise_if_failed(result, "期望值不为None，但实际值为 None")
        return self
    
    def is_true(self, message: str = "") -> 'AssertionManager':
        """True断言"""
        result = self.actual is True
        self._log_comparison(True, result, message or "True检查")
        self._raise_if_failed(result, f"期望值为True，但实际值为 {self.actual}")
        return self
    
    def is_false(self, message: str = "") -> 'AssertionManager':
        """False断言"""
        result = self.actual is False
        self._log_comparison(False, result, message or "False检查")
        self._raise_if_failed(result, f"期望值为False，但实际值为 {self.actual}")
        return self
    
    def is_truthy(self, message: str = "") -> 'AssertionManager':
        """真值断言"""
        result = bool(self.actual)
        self._log_comparison("truthy", result, message or "真值检查")
        self._raise_if_failed(result, f"期望值为真值，但实际值为 {self.actual}")
        return self
    
    def is_falsy(self, message: str = "") -> 'AssertionManager':
        """假值断言"""
        result = not bool(self.actual)
        self._log_comparison("falsy", result, message or "假值检查")
        self._raise_if_failed(result, f"期望值为假值，但实际值为 {self.actual}")
        return self
    
    # 深度比较断言
    def deep_equals(self, expected: Any, message: str = "") -> 'AssertionManager':
        """深度相等断言，支持忽略字段和部分匹配"""
        actual_data = self._process_ignore_fields(self.actual)
        expected_data = self._process_ignore_fields(expected)
        
        if self.partial_match:
            expected_data = self._extract_partial_data(actual_data, expected_data)
        
        diff = DeepDiff(
            actual_data, 
            expected_data,
            ignore_order=not self.strict_order,
            significant_digits=self.precision
        )
        
        result = len(diff) == 0
        self._log_comparison(expected, result, message or "深度相等检查")
        
        if not result:
            log.error(f"深度比较差异详情: {diff}")
            self._analyze_diff(diff)
        
        self._raise_if_failed(result, f"深度比较失败: {diff}")
        return self
    
    def _process_ignore_fields(self, data: Any) -> Any:
        """
        处理忽略字段 - 支持递归忽略和路径忽略
        
        支持两种忽略模式：
        1. 简单字段名: ["uuid", "img"] - 递归忽略所有同名字段
        2. 路径形式: ["data.uuid", "data.img"] - 忽略特定路径的字段
        """
        if not self.ignore_fields:
            return data
        
        return self._recursive_ignore_fields(data, self.ignore_fields, [])
    
    def _recursive_ignore_fields(self, data: Any, ignore_fields: List[str], current_path: List[str]) -> Any:
        """递归处理忽略字段"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # 构建当前字段的完整路径
                field_path = '.'.join(current_path + [key])
                
                # 检查是否应该忽略这个字段
                should_ignore = False
                
                # 方式1: 检查简单字段名
                if key in ignore_fields:
                    should_ignore = True
                    
                # 方式2: 检查完整路径
                if field_path in ignore_fields:
                    should_ignore = True
                
                if not should_ignore:
                    # 递归处理嵌套结构
                    processed_value = self._recursive_ignore_fields(value, ignore_fields, current_path + [key])
                    result[key] = processed_value
                    
            return result
            
        elif isinstance(data, list):
            # 对列表中的每个元素递归应用忽略逻辑
            return [self._recursive_ignore_fields(item, ignore_fields, current_path) for item in data]
            
        else:
            return data
    
    def _extract_partial_data(self, actual: Any, expected: Any) -> Any:
        """提取部分匹配数据"""
        if isinstance(expected, dict) and isinstance(actual, dict):
            return {k: v for k, v in expected.items() if k in actual}
        return expected
    
    def _analyze_diff(self, diff: Dict):
        """分析差异详情"""
        if 'values_changed' in diff:
            log.error(f"值变更: {diff['values_changed']}")
        if 'type_changes' in diff:
            log.error(f"类型变更: {diff['type_changes']}")
        if 'dictionary_item_added' in diff:
            log.error(f"缺失字段: {diff['dictionary_item_added']}")
        if 'dictionary_item_removed' in diff:
            log.warning(f"多余字段: {diff['dictionary_item_removed']}")
        if 'iterable_item_added' in diff:
            log.error(f"列表新增项: {diff['iterable_item_added']}")
        if 'iterable_item_removed' in diff:
            log.error(f"列表缺失项: {diff['iterable_item_removed']}")
    
    # 包含性断言
    def contains(self, expected: Any, message: str = "") -> 'AssertionManager':
        """包含断言"""
        if isinstance(self.actual, (str, list, tuple, set)):
            result = expected in self.actual
        elif isinstance(self.actual, dict):
            result = expected in self.actual.values()
        else:
            result = False
        
        self._log_comparison(expected, result, message or "包含性检查")
        self._raise_if_failed(result, f"期望包含 {expected}，但在 {self.actual} 中未找到")
        return self
    
    def not_contains(self, expected: Any, message: str = "") -> 'AssertionManager':
        """不包含断言"""
        if isinstance(self.actual, (str, list, tuple, set)):
            result = expected not in self.actual
        elif isinstance(self.actual, dict):
            result = expected not in self.actual.values()
        else:
            result = True
        
        self._log_comparison(expected, result, message or "不包含性检查")
        self._raise_if_failed(result, f"期望不包含 {expected}，但在 {self.actual} 中找到了")
        return self
    
    def contains_key(self, key: str, message: str = "") -> 'AssertionManager':
        """包含键断言"""
        if not isinstance(self.actual, dict):
            self._raise_if_failed(False, f"期望字典类型，但实际类型为 {type(self.actual)}")
        
        result = key in self.actual
        self._log_comparison(key, result, message or "包含键检查")
        self._raise_if_failed(result, f"期望包含键 '{key}'，但在字典中未找到")
        return self
    
    def not_contains_key(self, key: str, message: str = "") -> 'AssertionManager':
        """不包含键断言"""
        if not isinstance(self.actual, dict):
            self._raise_if_failed(False, f"期望字典类型，但实际类型为 {type(self.actual)}")
        
        result = key not in self.actual
        self._log_comparison(key, result, message or "不包含键检查")
        self._raise_if_failed(result, f"期望不包含键 '{key}'，但在字典中找到了")
        return self
    
    # 类型断言
    def is_instance(self, expected_type: type, message: str = "") -> 'AssertionManager':
        """类型断言"""
        result = isinstance(self.actual, expected_type)
        self._log_comparison(expected_type.__name__, result, message or "类型检查")
        self._raise_if_failed(result, f"期望类型 {expected_type.__name__}，但实际类型为 {type(self.actual).__name__}")
        return self
    
    def has_length(self, expected_length: int, message: str = "") -> 'AssertionManager':
        """长度断言"""
        if not hasattr(self.actual, '__len__'):
            self._raise_if_failed(False, f"对象 {self.actual} 没有长度属性")
        
        actual_length = len(self.actual)
        result = actual_length == expected_length
        self._log_comparison(expected_length, result, message or "长度检查")
        self._raise_if_failed(result, f"期望长度 {expected_length}，但实际长度为 {actual_length}")
        return self
    
    # 自定义断言
    def satisfies(self, condition: Callable[[Any], bool], message: str = "") -> 'AssertionManager':
        """自定义条件断言"""
        try:
            result = condition(self.actual)
        except Exception as e:
            self._raise_if_failed(False, f"条件检查时发生异常: {e}")
        
        self._log_comparison("custom condition", result, message or "自定义条件检查")
        self._raise_if_failed(result, f"自定义条件检查失败: {message}")
        return self
    
    # 专业化断言方法
    def as_json(self) -> 'JsonAssertions':
        """转换为JSON断言器"""
        return JsonAssertions(self.actual, self)
    
    def as_array(self) -> 'ArrayAssertions':
        """转换为数组断言器"""
        return ArrayAssertions(self.actual, self)
    
    def as_string(self) -> 'StringAssertions':
        """转换为字符串断言器"""
        return StringAssertions(self.actual, self)
    
    def as_number(self) -> 'NumberAssertions':
        """转换为数值断言器"""
        return NumberAssertions(self.actual, self)
    
    def as_response(self) -> 'ResponseAssertions':
        """转换为响应断言器"""
        return ResponseAssertions(self.actual, self)


class JsonAssertions:
    """JSON专业断言类"""
    
    def __init__(self, actual: Any, parent: AssertionManager):
        self.actual = actual
        self.parent = parent
    
    def contains_key(self, key: str) -> 'JsonAssertions':
        """包含指定键"""
        self.parent.contains_key(key)
        return self
    
    def has_field_type(self, field: str, expected_type: type) -> 'JsonAssertions':
        """验证字段类型"""
        if not isinstance(self.actual, dict):
            raise AssertionError(f"期望字典类型，但实际类型为 {type(self.actual)}")
        
        if field not in self.actual:
            raise AssertionError(f"字段 '{field}' 不存在")
        
        actual_type = type(self.actual[field])
        if actual_type != expected_type:
            raise AssertionError(f"字段 '{field}' 期望类型 {expected_type.__name__}，但实际类型为 {actual_type.__name__}")
        
        log.info(f"字段类型验证通过: {field} -> {expected_type.__name__}")
        return self
    
    def field_matches_pattern(self, field: str, pattern: str) -> 'JsonAssertions':
        """验证字段值匹配正则"""
        if not isinstance(self.actual, dict):
            raise AssertionError(f"期望字典类型，但实际类型为 {type(self.actual)}")
        
        if field not in self.actual:
            raise AssertionError(f"字段 '{field}' 不存在")
        
        field_value = self.actual[field]
        if not isinstance(field_value, str):
            raise AssertionError(f"字段 '{field}' 不是字符串类型")
        
        import re
        if not re.match(pattern, field_value):
            raise AssertionError(f"字段 '{field}' 值 '{field_value}' 不匹配模式 '{pattern}'")
        
        log.info(f"字段正则验证通过: {field} -> {pattern}")
        return self
    
    def has_exact_fields(self, *fields) -> 'JsonAssertions':
        """验证具有确切的字段（不多不少）"""
        if not isinstance(self.actual, dict):
            raise AssertionError(f"期望字典类型，但实际类型为 {type(self.actual)}")
        
        expected_fields = set(fields)
        actual_fields = set(self.actual.keys())
        
        extra_fields = actual_fields - expected_fields
        missing_fields = expected_fields - actual_fields
        
        if extra_fields:
            raise AssertionError(f"多余字段: {list(extra_fields)}")
        if missing_fields:
            raise AssertionError(f"缺失字段: {list(missing_fields)}")
        
        log.info(f"字段精确匹配验证通过: {list(fields)}")
        return self
    
    def equals(self, expected: Dict) -> 'JsonAssertions':
        """验证JSON对象相等"""
        if not isinstance(self.actual, dict):
            raise AssertionError(f"期望字典类型，但实际类型为 {type(self.actual)}")
        
        if self.actual != expected:
            raise AssertionError(f"JSON对象不相等，期望: {expected}，实际: {self.actual}")
        
        log.info(f"JSON对象相等验证通过")
        return self
    
    def not_equals(self, expected: Dict) -> 'JsonAssertions':
        """验证JSON对象不相等"""
        if not isinstance(self.actual, dict):
            raise AssertionError(f"期望字典类型，但实际类型为 {type(self.actual)}")
        
        if self.actual == expected:
            raise AssertionError(f"JSON对象不应该相等，但实际相等: {self.actual}")
        
        log.info(f"JSON对象不等验证通过")
        return self
    
    def is_none(self) -> 'JsonAssertions':
        """验证JSON对象为None"""
        if self.actual is not None:
            raise AssertionError(f"期望值为None，但实际值为 {self.actual}")
        
        log.info("JSON对象None验证通过")
        return self
    
    def is_not_none(self) -> 'JsonAssertions':
        """验证JSON对象不为None"""
        if self.actual is None:
            raise AssertionError("期望值不为None，但实际值为 None")
        
        log.info(f"JSON对象非None验证通过")
        return self


class ArrayAssertions:
    """数组专业断言类"""
    
    def __init__(self, actual: Any, parent: AssertionManager):
        self.actual = actual
        self.parent = parent
    
    def has_length(self, expected_length: int) -> 'ArrayAssertions':
        """验证数组长度"""
        self.parent.has_length(expected_length)
        return self
    
    def has_length_between(self, min_length: int, max_length: int) -> 'ArrayAssertions':
        """验证数组长度在范围内"""
        if not hasattr(self.actual, '__len__'):
            raise AssertionError(f"对象 {self.actual} 没有长度属性")
        
        actual_length = len(self.actual)
        if not (min_length <= actual_length <= max_length):
            raise AssertionError(f"期望长度在 {min_length}-{max_length} 之间，但实际长度为 {actual_length}")
        
        log.info(f"数组长度范围验证通过: {actual_length} in [{min_length}, {max_length}]")
        return self
    
    def is_sorted(self, reverse: bool = False) -> 'ArrayAssertions':
        """验证数组是否已排序"""
        if not isinstance(self.actual, (list, tuple)) or len(self.actual) <= 1:
            log.info("数组排序验证通过（空数组或单元素数组）")
            return self
        
        try:
            sorted_list = sorted(self.actual, reverse=reverse)
            if list(self.actual) != sorted_list:
                raise AssertionError(f"数组未按 {'降序' if reverse else '升序'} 排列")
        except TypeError:
            raise AssertionError("数组元素不可比较，无法验证排序")
        
        log.info(f"数组排序验证通过: {'降序' if reverse else '升序'}")
        return self
    
    def all_items_match(self, condition: Callable[[Any], bool]) -> 'ArrayAssertions':
        """验证所有元素满足条件"""
        if not isinstance(self.actual, (list, tuple, set)):
            raise AssertionError(f"期望数组类型，但实际类型为 {type(self.actual)}")
        
        for i, item in enumerate(self.actual):
            if not condition(item):
                raise AssertionError(f"数组元素[{i}] = {item} 不满足条件")
        
        log.info("数组元素条件验证通过")
        return self
    
    def equals(self, expected: List[Any]) -> 'ArrayAssertions':
        """验证数组相等"""
        if not isinstance(self.actual, (list, tuple)):
            raise AssertionError(f"期望数组类型，但实际类型为 {type(self.actual)}")
        
        if list(self.actual) != list(expected):
            raise AssertionError(f"数组不相等，期望: {expected}，实际: {list(self.actual)}")
        
        log.info(f"数组相等验证通过")
        return self
    
    def not_equals(self, expected: List[Any]) -> 'ArrayAssertions':
        """验证数组不相等"""
        if not isinstance(self.actual, (list, tuple)):
            raise AssertionError(f"期望数组类型，但实际类型为 {type(self.actual)}")
        
        if list(self.actual) == list(expected):
            raise AssertionError(f"数组不应该相等，但实际相等: {list(self.actual)}")
        
        log.info(f"数组不等验证通过")
        return self
    
    def is_none(self) -> 'ArrayAssertions':
        """验证数组为None"""
        if self.actual is not None:
            raise AssertionError(f"期望值为None，但实际值为 {self.actual}")
        
        log.info("数组None验证通过")
        return self
    
    def is_not_none(self) -> 'ArrayAssertions':
        """验证数组不为None"""
        if self.actual is None:
            raise AssertionError("期望值不为None，但实际值为 None")
        
        log.info(f"数组非None验证通过")
        return self


class StringAssertions:
    """字符串专业断言类"""
    
    def __init__(self, actual: Any, parent: AssertionManager):
        self.actual = actual
        self.parent = parent
    
    def matches_pattern(self, pattern: str) -> 'StringAssertions':
        """验证匹配正则表达式"""
        if not isinstance(self.actual, str):
            raise AssertionError(f"期望字符串类型，但实际类型为 {type(self.actual)}")
        
        import re
        if not re.match(pattern, self.actual):
            raise AssertionError(f"字符串 '{self.actual}' 不匹配模式 '{pattern}'")
        
        log.info(f"字符串正则验证通过: '{self.actual}' matches '{pattern}'")
        return self
    
    def starts_with(self, prefix: str, case_sensitive: bool = True) -> 'StringAssertions':
        """验证字符串前缀"""
        if not isinstance(self.actual, str):
            raise AssertionError(f"期望字符串类型，但实际类型为 {type(self.actual)}")
        
        actual_str = self.actual if case_sensitive else self.actual.lower()
        prefix_str = prefix if case_sensitive else prefix.lower()
        
        if not actual_str.startswith(prefix_str):
            raise AssertionError(f"字符串 '{self.actual}' 不以 '{prefix}' 开始")
        
        log.info(f"字符串前缀验证通过: '{self.actual}' starts with '{prefix}'")
        return self
    
    def ends_with(self, suffix: str, case_sensitive: bool = True) -> 'StringAssertions':
        """验证字符串后缀"""
        if not isinstance(self.actual, str):
            raise AssertionError(f"期望字符串类型，但实际类型为 {type(self.actual)}")
        
        actual_str = self.actual if case_sensitive else self.actual.lower()
        suffix_str = suffix if case_sensitive else suffix.lower()
        
        if not actual_str.endswith(suffix_str):
            raise AssertionError(f"字符串 '{self.actual}' 不以 '{suffix}' 结尾")
        
        log.info(f"字符串后缀验证通过: '{self.actual}' ends with '{suffix}'")
        return self
    
    def is_valid_email(self) -> 'StringAssertions':
        """验证邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return self.matches_pattern(email_pattern)
    
    def is_valid_url(self) -> 'StringAssertions':
        """验证URL格式"""
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$'
        return self.matches_pattern(url_pattern)
    
    def equals(self, expected: str, case_sensitive: bool = True) -> 'StringAssertions':
        """验证字符串相等"""
        if not isinstance(self.actual, str):
            raise AssertionError(f"期望字符串类型，但实际类型为 {type(self.actual)}")
        
        actual_str = self.actual if case_sensitive else self.actual.lower()
        expected_str = expected if case_sensitive else expected.lower()
        
        if actual_str != expected_str:
            raise AssertionError(f"期望字符串 '{expected}'，但实际为 '{self.actual}'")
        
        log.info(f"字符串相等验证通过: '{self.actual}' == '{expected}'")
        return self
    
    def not_equals(self, expected: str, case_sensitive: bool = True) -> 'StringAssertions':
        """验证字符串不相等"""
        if not isinstance(self.actual, str):
            raise AssertionError(f"期望字符串类型，但实际类型为 {type(self.actual)}")
        
        actual_str = self.actual if case_sensitive else self.actual.lower()
        expected_str = expected if case_sensitive else expected.lower()
        
        if actual_str == expected_str:
            raise AssertionError(f"期望字符串不等于 '{expected}'，但实际为 '{self.actual}'")
        
        log.info(f"字符串不等验证通过: '{self.actual}' != '{expected}'")
        return self
    
    def is_none(self) -> 'StringAssertions':
        """验证字符串为None"""
        if self.actual is not None:
            raise AssertionError(f"期望值为None，但实际值为 '{self.actual}'")
        
        log.info("字符串None验证通过")
        return self
    
    def is_not_none(self) -> 'StringAssertions':
        """验证字符串不为None"""
        if self.actual is None:
            raise AssertionError("期望值不为None，但实际值为 None")
        
        log.info(f"字符串非None验证通过: '{self.actual}'")
        return self
    
    def has_length(self, expected_length: int) -> 'StringAssertions':
        """验证字符串长度"""
        if not isinstance(self.actual, str):
            raise AssertionError(f"期望字符串类型，但实际类型为 {type(self.actual)}")
        
        actual_length = len(self.actual)
        if actual_length != expected_length:
            raise AssertionError(f"期望长度 {expected_length}，但实际长度为 {actual_length}")
        
        log.info(f"字符串长度验证通过: {actual_length}")
        return self


class NumberAssertions:
    """数值专业断言类"""
    
    def __init__(self, actual: Any, parent: AssertionManager):
        self.actual = actual
        self.parent = parent
    
    def is_between(self, min_value: Union[int, float], max_value: Union[int, float], 
                   inclusive: bool = True) -> 'NumberAssertions':
        """验证数值范围"""
        if not isinstance(self.actual, (int, float)):
            raise AssertionError(f"期望数值类型，但实际类型为 {type(self.actual)}")
        
        if inclusive:
            if not (min_value <= self.actual <= max_value):
                raise AssertionError(f"期望值在 [{min_value}, {max_value}] 范围内，但实际值为 {self.actual}")
        else:
            if not (min_value < self.actual < max_value):
                raise AssertionError(f"期望值在 ({min_value}, {max_value}) 范围内，但实际值为 {self.actual}")
        
        range_desc = f"[{min_value}, {max_value}]" if inclusive else f"({min_value}, {max_value})"
        log.info(f"数值范围验证通过: {self.actual} in {range_desc}")
        return self
    
    def is_positive(self) -> 'NumberAssertions':
        """验证正数"""
        if not isinstance(self.actual, (int, float)):
            raise AssertionError(f"期望数值类型，但实际类型为 {type(self.actual)}")
        
        if self.actual <= 0:
            raise AssertionError(f"期望正数，但实际值为 {self.actual}")
        
        log.info(f"正数验证通过: {self.actual}")
        return self
    
    def is_negative(self) -> 'NumberAssertions':
        """验证负数"""
        if not isinstance(self.actual, (int, float)):
            raise AssertionError(f"期望数值类型，但实际类型为 {type(self.actual)}")
        
        if self.actual >= 0:
            raise AssertionError(f"期望负数，但实际值为 {self.actual}")
        
        log.info(f"负数验证通过: {self.actual}")
        return self
    
    def is_close_to(self, expected: Union[int, float], tolerance: float = 1e-9) -> 'NumberAssertions':
        """验证数值接近"""
        if not isinstance(self.actual, (int, float)):
            raise AssertionError(f"期望数值类型，但实际类型为 {type(self.actual)}")
        
        if abs(self.actual - expected) > tolerance:
            raise AssertionError(f"期望值接近 {expected}（误差±{tolerance}），但实际值为 {self.actual}")
        
        log.info(f"数值接近验证通过: {self.actual} ≈ {expected} (±{tolerance})")
        return self
    
    def equals(self, expected: Union[int, float]) -> 'NumberAssertions':
        """验证数值相等"""
        if not isinstance(self.actual, (int, float)):
            raise AssertionError(f"期望数值类型，但实际类型为 {type(self.actual)}")
        
        if self.actual != expected:
            raise AssertionError(f"期望值 {expected}，但实际值为 {self.actual}")
        
        log.info(f"数值相等验证通过: {self.actual} == {expected}")
        return self
    
    def not_equals(self, expected: Union[int, float]) -> 'NumberAssertions':
        """验证数值不相等"""
        if not isinstance(self.actual, (int, float)):
            raise AssertionError(f"期望数值类型，但实际类型为 {type(self.actual)}")
        
        if self.actual == expected:
            raise AssertionError(f"期望值不等于 {expected}，但实际值为 {self.actual}")
        
        log.info(f"数值不等验证通过: {self.actual} != {expected}")
        return self
    
    def is_none(self) -> 'NumberAssertions':
        """验证数值为None"""
        if self.actual is not None:
            raise AssertionError(f"期望值为None，但实际值为 {self.actual}")
        
        log.info("数值None验证通过")
        return self
    
    def is_not_none(self) -> 'NumberAssertions':
        """验证数值不为None"""
        if self.actual is None:
            raise AssertionError("期望值不为None，但实际值为 None")
        
        log.info(f"数值非None验证通过: {self.actual}")
        return self


class ResponseAssertions:
    """响应专业断言类"""
    
    def __init__(self, actual: Any, parent: AssertionManager):
        self.actual = actual
        self.parent = parent
    
    def status_code(self, expected_code: int) -> 'ResponseAssertions':
        """验证状态码"""
        actual_code = getattr(self.actual, 'status_code', None)
        if actual_code != expected_code:
            raise AssertionError(f"期望状态码 {expected_code}，但实际状态码为 {actual_code}")
        
        log.info(f"状态码验证通过: {actual_code}")
        return self
    
    def is_success(self) -> 'ResponseAssertions':
        """验证成功响应（2xx）"""
        actual_code = getattr(self.actual, 'status_code', None)
        if not (200 <= actual_code < 300):
            raise AssertionError(f"期望成功响应（2xx），但状态码为 {actual_code}")
        
        log.info(f"成功响应验证通过: {actual_code}")
        return self
    
    def is_json(self) -> 'ResponseAssertions':
        """验证JSON响应"""
        content_type = getattr(self.actual, 'headers', {}).get('Content-Type', '')
        actual_type = content_type.split(';')[0].strip()
        
        if actual_type != 'application/json':
            raise AssertionError(f"期望JSON响应，但Content-Type为 {actual_type}")
        
        log.info(f"JSON响应验证通过: {actual_type}")
        return self
    
    def json_contains(self, expected_data: Dict, ignore_fields: List[str] = None,
                     partial_match: bool = True) -> 'ResponseAssertions':
        """验证JSON响应包含指定数据"""
        try:
            if hasattr(self.actual, 'json'):
                actual_json = self.actual.json()
            else:
                response_text = getattr(self.actual, 'text', str(self.actual))
                actual_json = json.loads(response_text)
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            raise AssertionError(f"JSON解析失败: {e}")
        
        from .comparator import JsonComparator
        comparator = JsonComparator(actual_json)
        result = comparator.deep_compare(
            expected_data, 
            ignore_fields=ignore_fields,
            partial_match=partial_match
        )
        
        if not result['passed']:
            raise AssertionError(f"JSON内容验证失败: {result['details']}")
        
        log.info("JSON内容验证通过")
        return self
