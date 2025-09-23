"""
断言工具模块

提供忽略字段、部分匹配等辅助功能。
"""

import copy
from typing import Any, Union, List, Optional, Callable


class IgnoreFields:
    """忽略字段工具类"""
    
    def __init__(self, fields: Union[str, List[str]]):
        """
        初始化忽略字段
        
        Args:
            fields: 要忽略的字段名或字段名列表
        """
        if isinstance(fields, str):
            self.fields = [fields]
        else:
            self.fields = list(fields)
    
    def apply(self, data: Any, recursive: bool = True) -> Any:
        """
        应用忽略字段到数据
        
        Args:
            data: 要处理的数据
            recursive: 是否递归处理嵌套结构
            
        Returns:
            处理后的数据
        """
        return self._remove_fields(data, self.fields, recursive)
    
    def _remove_fields(self, data: Any, fields: List[str], recursive: bool) -> Any:
        """递归移除指定字段"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                if key not in fields:
                    if recursive:
                        result[key] = self._remove_fields(value, fields, recursive)
                    else:
                        result[key] = value
            return result
        elif isinstance(data, list):
            if recursive:
                return [self._remove_fields(item, fields, recursive) for item in data]
            else:
                return data
        else:
            return data
    
    @staticmethod
    def create(*fields) -> 'IgnoreFields':
        """便捷创建方法"""
        return IgnoreFields(list(fields))


class PartialMatch:
    """部分匹配工具类"""
    
    def __init__(self, include_fields: Optional[List[str]] = None, 
                 exclude_fields: Optional[List[str]] = None):
        """
        初始化部分匹配
        
        Args:
            include_fields: 只包含这些字段
            exclude_fields: 排除这些字段
        """
        self.include_fields = include_fields
        self.exclude_fields = exclude_fields or []
    
    def apply(self, actual: Any, expected: Any) -> Any:
        """
        应用部分匹配，从expected中提取actual存在的字段
        
        Args:
            actual: 实际数据
            expected: 期望数据
            
        Returns:
            匹配后的期望数据
        """
        return self._extract_partial(actual, expected)
    
    def _extract_partial(self, actual: Any, expected: Any) -> Any:
        """递归提取部分匹配的数据"""
        if isinstance(expected, dict) and isinstance(actual, dict):
            result = {}
            
            # 确定要包含的字段
            if self.include_fields is not None:
                # 如果指定了include_fields，只处理这些字段
                target_fields = set(self.include_fields) & set(expected.keys()) & set(actual.keys())
            else:
                # 否则处理expected中存在且actual中也存在的字段
                target_fields = set(expected.keys()) & set(actual.keys())
            
            # 排除指定字段
            target_fields = target_fields - set(self.exclude_fields)
            
            for field in target_fields:
                result[field] = self._extract_partial(actual[field], expected[field])
            
            return result
        
        elif isinstance(expected, list) and isinstance(actual, list):
            # 对于列表，取较短长度进行比较
            min_length = min(len(expected), len(actual))
            return [self._extract_partial(actual[i], expected[i]) for i in range(min_length)]
        
        else:
            # 对于基本类型，直接返回expected
            return expected
    
    @staticmethod
    def include(*fields) -> 'PartialMatch':
        """便捷创建包含指定字段的部分匹配"""
        return PartialMatch(include_fields=list(fields))
    
    @staticmethod
    def exclude(*fields) -> 'PartialMatch':
        """便捷创建排除指定字段的部分匹配"""
        return PartialMatch(exclude_fields=list(fields))


class DataTransformer:
    """数据转换器"""
    
    def __init__(self):
        self.transformers = []
    
    def add_transformer(self, condition: Callable[[Any], bool], 
                       transformer: Callable[[Any], Any]) -> 'DataTransformer':
        """
        添加数据转换器
        
        Args:
            condition: 转换条件函数
            transformer: 转换函数
            
        Returns:
            self，支持链式调用
        """
        self.transformers.append((condition, transformer))
        return self
    
    def transform(self, data: Any) -> Any:
        """
        应用所有转换器
        
        Args:
            data: 要转换的数据
            
        Returns:
            转换后的数据
        """
        result = data
        for condition, transformer in self.transformers:
            if condition(result):
                result = transformer(result)
        return result
    
    def transform_recursive(self, data: Any) -> Any:
        """
        递归应用转换器
        
        Args:
            data: 要转换的数据
            
        Returns:
            转换后的数据
        """
        # 先转换当前层级
        transformed = self.transform(data)
        
        # 递归转换子结构
        if isinstance(transformed, dict):
            return {k: self.transform_recursive(v) for k, v in transformed.items()}
        elif isinstance(transformed, list):
            return [self.transform_recursive(item) for item in transformed]
        else:
            return transformed


class ComparisonConfig:
    """比较配置类"""
    
    def __init__(self):
        self.ignore_fields = []
        self.ignore_case = False
        self.ignore_order = False
        self.ignore_extra_fields = False
        self.partial_match = False
        self.precision = None
        self.custom_comparators = {}
    
    def ignore_field(self, *fields) -> 'ComparisonConfig':
        """忽略指定字段"""
        self.ignore_fields.extend(fields)
        return self
    
    def ignore_case_config(self, enabled: bool = True) -> 'ComparisonConfig':
        """配置忽略大小写"""
        self.ignore_case = enabled
        return self
    
    def ignore_order_config(self, enabled: bool = True) -> 'ComparisonConfig':
        """配置忽略顺序"""
        self.ignore_order = enabled
        return self
    
    def ignore_extra_fields_config(self, enabled: bool = True) -> 'ComparisonConfig':
        """配置忽略多余字段"""
        self.ignore_extra_fields = enabled
        return self
    
    def partial_match_config(self, enabled: bool = True) -> 'ComparisonConfig':
        """配置部分匹配"""
        self.partial_match = enabled
        return self
    
    def precision_config(self, precision: int) -> 'ComparisonConfig':
        """配置数值精度"""
        self.precision = precision
        return self
    
    def add_custom_comparator(self, field_path: str, 
                            comparator: Callable[[Any, Any], bool]) -> 'ComparisonConfig':
        """
        添加自定义比较器
        
        Args:
            field_path: 字段路径，如 'user.age' 或 'items[0].name'
            comparator: 比较函数，接受(actual, expected)参数，返回bool
        """
        self.custom_comparators[field_path] = comparator
        return self


class PathMatcher:
    """路径匹配器，用于在嵌套结构中查找特定路径的值"""
    
    @staticmethod
    def get_value_by_path(data: Any, path: str, default: Any = None) -> Any:
        """
        根据路径获取值
        
        Args:
            data: 数据对象
            path: 路径字符串，如 'user.profile.name' 或 'items[0].id'
            default: 默认值
            
        Returns:
            路径对应的值
        """
        try:
            current = data
            
            # 解析路径
            parts = PathMatcher._parse_path(path)
            
            for part in parts:
                if isinstance(part, str):
                    # 字典键
                    current = current[part]
                elif isinstance(part, int):
                    # 数组索引
                    current = current[part]
            
            return current
        except (KeyError, IndexError, TypeError):
            return default
    
    @staticmethod
    def set_value_by_path(data: Any, path: str, value: Any) -> bool:
        """
        根据路径设置值
        
        Args:
            data: 数据对象
            path: 路径字符串
            value: 要设置的值
            
        Returns:
            是否设置成功
        """
        try:
            parts = PathMatcher._parse_path(path)
            current = data
            
            # 导航到父级
            for part in parts[:-1]:
                if isinstance(part, str):
                    current = current[part]
                elif isinstance(part, int):
                    current = current[part]
            
            # 设置最终值
            final_part = parts[-1]
            if isinstance(final_part, str):
                current[final_part] = value
            elif isinstance(final_part, int):
                current[final_part] = value
            
            return True
        except (KeyError, IndexError, TypeError):
            return False
    
    @staticmethod
    def _parse_path(path: str) -> List[Union[str, int]]:
        """解析路径字符串为部分列表"""
        parts = []
        current_part = ""
        i = 0
        
        while i < len(path):
            char = path[i]
            
            if char == '.':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            elif char == '[':
                if current_part:
                    parts.append(current_part)
                    current_part = ""
                # 查找匹配的 ]
                j = i + 1
                while j < len(path) and path[j] != ']':
                    j += 1
                if j < len(path):
                    index_str = path[i+1:j]
                    try:
                        parts.append(int(index_str))
                    except ValueError:
                        # 如果不是数字，当作字符串键处理
                        parts.append(index_str)
                    i = j
                else:
                    current_part += char
            else:
                current_part += char
            
            i += 1
        
        if current_part:
            parts.append(current_part)
        
        return parts


class DataMasker:
    """数据脱敏工具"""
    
    def __init__(self):
        self.mask_rules = {}
    
    def add_mask_rule(self, field_pattern: str, mask_func: Callable[[str], str]) -> 'DataMasker':
        """
        添加脱敏规则
        
        Args:
            field_pattern: 字段模式（支持正则）
            mask_func: 脱敏函数
        """
        self.mask_rules[field_pattern] = mask_func
        return self
    
    def mask_data(self, data: Any) -> Any:
        """
        对数据进行脱敏
        
        Args:
            data: 要脱敏的数据
            
        Returns:
            脱敏后的数据
        """
        return self._mask_recursive(copy.deepcopy(data))
    
    def _mask_recursive(self, data: Any) -> Any:
        """递归脱敏数据"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # 检查是否需要脱敏
                masked_value = self._apply_mask_rules(key, value)
                if masked_value != value:
                    result[key] = masked_value
                else:
                    result[key] = self._mask_recursive(value)
            return result
        elif isinstance(data, list):
            return [self._mask_recursive(item) for item in data]
        else:
            return data
    
    def _apply_mask_rules(self, field_name: str, value: Any) -> Any:
        """应用脱敏规则"""
        import re
        
        for pattern, mask_func in self.mask_rules.items():
            if re.match(pattern, field_name) and isinstance(value, str):
                return mask_func(value)
        return value
    
    @staticmethod
    def phone_masker(phone: str) -> str:
        """手机号脱敏"""
        if len(phone) >= 11:
            return phone[:3] + '****' + phone[-4:]
        return phone
    
    @staticmethod
    def email_masker(email: str) -> str:
        """邮箱脱敏"""
        if '@' in email:
            local, domain = email.split('@', 1)
            if len(local) > 2:
                return local[:1] + '***' + local[-1:] + '@' + domain
        return email
    
    @staticmethod
    def id_card_masker(id_card: str) -> str:
        """身份证脱敏"""
        if len(id_card) >= 18:
            return id_card[:6] + '********' + id_card[-4:]
        elif len(id_card) >= 15:
            return id_card[:6] + '*****' + id_card[-4:]
        return id_card
