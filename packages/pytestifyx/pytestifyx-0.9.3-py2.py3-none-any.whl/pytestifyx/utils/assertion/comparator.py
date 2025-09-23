"""
比较器模块

提供不同类型数据的专业化比较器。
"""

import json
import re
import math
from typing import Any, Union, Dict, List, Optional, Pattern
from deepdiff import DeepDiff

from pytestifyx.utils.logs.core import log


class BaseComparator:
    """基础比较器"""
    
    def __init__(self, actual: Any):
        self.actual = actual
    
    def _log_result(self, expected: Any, result: bool, operation: str):
        """记录比较结果"""
        log.info(f'{operation} - 实际值: {self.actual}, 期望值: {expected}, 结果: {result}')


class JsonComparator(BaseComparator):
    """JSON/字典专用比较器"""
    
    def deep_compare(self, expected: Dict, ignore_fields: List[str] = None, 
                    partial_match: bool = False, strict_order: bool = True) -> Dict:
        """
        深度比较JSON数据
        
        Args:
            expected: 期望的JSON数据
            ignore_fields: 忽略的字段列表
            partial_match: 是否进行部分匹配
            strict_order: 是否严格按顺序比较
            
        Returns:
            比较结果字典，包含是否通过和详细差异
        """
        actual_data = self._process_data(self.actual, ignore_fields)
        expected_data = self._process_data(expected, ignore_fields)
        
        if partial_match:
            expected_data = self._extract_partial_fields(actual_data, expected_data)
        
        diff = DeepDiff(
            actual_data,
            expected_data,
            ignore_order=not strict_order,
            view='tree'
        )
        
        result = {
            'passed': len(diff) == 0,
            'diff': diff,
            'details': self._format_diff_details(diff)
        }
        
        self._log_detailed_result(expected, result)
        return result
    
    def _process_data(self, data: Any, ignore_fields: List[str] = None) -> Any:
        """处理数据，移除忽略字段"""
        if ignore_fields is None:
            ignore_fields = []
        
        if isinstance(data, dict):
            return {k: self._process_data(v, ignore_fields) 
                   for k, v in data.items() if k not in ignore_fields}
        elif isinstance(data, list):
            return [self._process_data(item, ignore_fields) for item in data]
        return data
    
    def _extract_partial_fields(self, actual: Any, expected: Any) -> Any:
        """提取部分字段进行匹配"""
        if isinstance(expected, dict) and isinstance(actual, dict):
            return {k: self._extract_partial_fields(actual.get(k), v) 
                   for k, v in expected.items() if k in actual}
        elif isinstance(expected, list) and isinstance(actual, list):
            min_len = min(len(expected), len(actual))
            return [self._extract_partial_fields(actual[i], expected[i]) 
                   for i in range(min_len)]
        return expected
    
    def _format_diff_details(self, diff: Any) -> Dict:
        """格式化差异详情"""
        details = {}
        
        if hasattr(diff, 'get'):
            for change_type in ['values_changed', 'type_changes', 'dictionary_item_added', 
                              'dictionary_item_removed', 'iterable_item_added', 'iterable_item_removed']:
                if change_type in diff:
                    details[change_type] = diff[change_type]
        
        return details
    
    def _log_detailed_result(self, expected: Any, result: Dict):
        """记录详细比较结果"""
        log.info(f'JSON比较 - 实际数据: {json.dumps(self.actual, ensure_ascii=False, default=str)}')
        log.info(f'JSON比较 - 期望数据: {json.dumps(expected, ensure_ascii=False, default=str)}')
        
        if result['passed']:
            log.info('JSON比较通过')
        else:
            log.error('JSON比较失败')
            for change_type, changes in result['details'].items():
                log.error(f'{change_type}: {changes}')
    
    def contains_all_fields(self, expected_fields: List[str]) -> bool:
        """检查是否包含所有指定字段"""
        if not isinstance(self.actual, dict):
            return False
        
        missing_fields = [field for field in expected_fields if field not in self.actual]
        result = len(missing_fields) == 0
        
        if not result:
            log.error(f'缺失字段: {missing_fields}')
        
        self._log_result(expected_fields, result, '字段完整性检查')
        return result
    
    def has_exact_fields(self, expected_fields: List[str]) -> bool:
        """检查是否具有确切的字段（不多不少）"""
        if not isinstance(self.actual, dict):
            return False
        
        actual_fields = set(self.actual.keys())
        expected_fields_set = set(expected_fields)
        
        extra_fields = actual_fields - expected_fields_set
        missing_fields = expected_fields_set - actual_fields
        
        result = len(extra_fields) == 0 and len(missing_fields) == 0
        
        if extra_fields:
            log.warning(f'多余字段: {list(extra_fields)}')
        if missing_fields:
            log.error(f'缺失字段: {list(missing_fields)}')
        
        self._log_result(expected_fields, result, '字段精确匹配检查')
        return result


class ArrayComparator(BaseComparator):
    """数组/列表专用比较器"""
    
    def contains_all(self, expected_items: List[Any], strict_order: bool = False) -> bool:
        """检查是否包含所有期望项"""
        if not isinstance(self.actual, (list, tuple, set)):
            return False
        
        if strict_order and isinstance(self.actual, (list, tuple)):
            result = self._check_ordered_contains(expected_items)
        else:
            actual_set = set(self.actual) if not isinstance(self.actual, set) else self.actual
            expected_set = set(expected_items)
            result = expected_set.issubset(actual_set)
        
        self._log_result(expected_items, result, '数组包含性检查')
        return result
    
    def _check_ordered_contains(self, expected_items: List[Any]) -> bool:
        """检查有序包含"""
        actual_list = list(self.actual)
        expected_idx = 0
        
        for item in actual_list:
            if expected_idx < len(expected_items) and item == expected_items[expected_idx]:
                expected_idx += 1
        
        return expected_idx == len(expected_items)
    
    def has_length_between(self, min_length: int, max_length: int) -> bool:
        """检查长度是否在指定范围内"""
        if not hasattr(self.actual, '__len__'):
            return False
        
        actual_length = len(self.actual)
        result = min_length <= actual_length <= max_length
        
        self._log_result(f'{min_length}-{max_length}', result, f'数组长度检查(实际: {actual_length})')
        return result
    
    def is_sorted(self, reverse: bool = False, key_func: callable = None) -> bool:
        """检查数组是否已排序"""
        if not isinstance(self.actual, (list, tuple)) or len(self.actual) <= 1:
            return True
        
        try:
            sorted_list = sorted(self.actual, reverse=reverse, key=key_func)
            result = list(self.actual) == sorted_list
        except TypeError:
            # 如果元素不可比较，返回False
            result = False
        
        self._log_result(f'sorted(reverse={reverse})', result, '数组排序检查')
        return result
    
    def all_items_match(self, condition: callable) -> bool:
        """检查所有项是否满足条件"""
        if not isinstance(self.actual, (list, tuple, set)):
            return False
        
        try:
            result = all(condition(item) for item in self.actual)
        except Exception as e:
            log.error(f'条件检查时发生异常: {e}')
            result = False
        
        self._log_result('custom condition', result, '数组元素条件检查')
        return result


class StringComparator(BaseComparator):
    """字符串专用比较器"""
    
    def matches_pattern(self, pattern: Union[str, Pattern], flags: int = 0) -> bool:
        """正则表达式匹配"""
        if not isinstance(self.actual, str):
            return False
        
        if isinstance(pattern, str):
            pattern = re.compile(pattern, flags)
        
        result = bool(pattern.search(self.actual))
        self._log_result(pattern.pattern, result, '正则匹配检查')
        return result
    
    def starts_with(self, prefix: str, case_sensitive: bool = True) -> bool:
        """检查字符串是否以指定前缀开始"""
        if not isinstance(self.actual, str):
            return False
        
        actual_str = self.actual if case_sensitive else self.actual.lower()
        prefix_str = prefix if case_sensitive else prefix.lower()
        
        result = actual_str.startswith(prefix_str)
        self._log_result(prefix, result, '前缀检查')
        return result
    
    def ends_with(self, suffix: str, case_sensitive: bool = True) -> bool:
        """检查字符串是否以指定后缀结束"""
        if not isinstance(self.actual, str):
            return False
        
        actual_str = self.actual if case_sensitive else self.actual.lower()
        suffix_str = suffix if case_sensitive else suffix.lower()
        
        result = actual_str.endswith(suffix_str)
        self._log_result(suffix, result, '后缀检查')
        return result
    
    def contains_substring(self, substring: str, case_sensitive: bool = True) -> bool:
        """检查是否包含子字符串"""
        if not isinstance(self.actual, str):
            return False
        
        actual_str = self.actual if case_sensitive else self.actual.lower()
        substring_str = substring if case_sensitive else substring.lower()
        
        result = substring_str in actual_str
        self._log_result(substring, result, '子字符串检查')
        return result
    
    def has_length_between(self, min_length: int, max_length: int) -> bool:
        """检查字符串长度是否在指定范围内"""
        if not isinstance(self.actual, str):
            return False
        
        actual_length = len(self.actual)
        result = min_length <= actual_length <= max_length
        
        self._log_result(f'{min_length}-{max_length}', result, f'字符串长度检查(实际: {actual_length})')
        return result
    
    def is_valid_email(self) -> bool:
        """检查是否为有效的邮箱格式"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return self.matches_pattern(email_pattern)
    
    def is_valid_url(self) -> bool:
        """检查是否为有效的URL格式"""
        url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/[^?\s]*)?(?:\?[^#\s]*)?(?:#[^\s]*)?$'
        return self.matches_pattern(url_pattern)


class NumberComparator(BaseComparator):
    """数值专用比较器"""
    
    def is_between(self, min_value: Union[int, float], max_value: Union[int, float], 
                   inclusive: bool = True) -> bool:
        """检查数值是否在指定范围内"""
        if not isinstance(self.actual, (int, float)):
            return False
        
        if inclusive:
            result = min_value <= self.actual <= max_value
        else:
            result = min_value < self.actual < max_value
        
        range_desc = f'{min_value}-{max_value}({"inclusive" if inclusive else "exclusive"})'
        self._log_result(range_desc, result, f'数值范围检查(实际: {self.actual})')
        return result
    
    def is_positive(self) -> bool:
        """检查是否为正数"""
        if not isinstance(self.actual, (int, float)):
            return False
        
        result = self.actual > 0
        self._log_result('> 0', result, '正数检查')
        return result
    
    def is_negative(self) -> bool:
        """检查是否为负数"""
        if not isinstance(self.actual, (int, float)):
            return False
        
        result = self.actual < 0
        self._log_result('< 0', result, '负数检查')
        return result
    
    def is_zero(self) -> bool:
        """检查是否为零"""
        if not isinstance(self.actual, (int, float)):
            return False
        
        result = self.actual == 0
        self._log_result('== 0', result, '零值检查')
        return result
    
    def is_close_to(self, expected: Union[int, float], tolerance: float = 1e-9) -> bool:
        """检查数值是否接近期望值（用于浮点数比较）"""
        if not isinstance(self.actual, (int, float)):
            return False
        
        result = abs(self.actual - expected) <= tolerance
        self._log_result(f'{expected}±{tolerance}', result, f'数值近似检查(实际: {self.actual})')
        return result
    
    def is_integer(self) -> bool:
        """检查是否为整数"""
        if isinstance(self.actual, int):
            result = True
        elif isinstance(self.actual, float):
            result = self.actual.is_integer()
        else:
            result = False
        
        self._log_result('integer', result, '整数检查')
        return result
    
    def has_decimal_places(self, expected_places: int) -> bool:
        """检查小数位数"""
        if not isinstance(self.actual, (int, float)):
            return False
        
        if isinstance(self.actual, int):
            actual_places = 0
        else:
            # 转换为字符串来计算小数位数
            decimal_str = str(self.actual)
            if '.' in decimal_str:
                actual_places = len(decimal_str.split('.')[1])
            else:
                actual_places = 0
        
        result = actual_places == expected_places
        self._log_result(expected_places, result, f'小数位数检查(实际: {actual_places})')
        return result
