"""
验证器模块

提供响应验证和模式验证功能。
"""

import json
import re
from typing import Any, Dict, List

from pytestifyx.utils.logs.core import log

from .comparator import JsonComparator, StringComparator


class ResponseValidator:
    """HTTP响应验证器"""
    
    def __init__(self, response: Any):
        """
        初始化响应验证器
        
        Args:
            response: HTTP响应对象（支持requests.Response或包含相关属性的对象）
        """
        self.response = response
    
    def status_code(self, expected_code: int) -> bool:
        """验证状态码"""
        actual_code = getattr(self.response, 'status_code', None)
        result = actual_code == expected_code
        
        log.info(f'状态码验证 - 期望: {expected_code}, 实际: {actual_code}, 结果: {result}')
        return result
    
    def status_code_in(self, expected_codes: List[int]) -> bool:
        """验证状态码在指定列表中"""
        actual_code = getattr(self.response, 'status_code', None)
        result = actual_code in expected_codes
        
        log.info(f'状态码范围验证 - 期望范围: {expected_codes}, 实际: {actual_code}, 结果: {result}')
        return result
    
    def is_success(self) -> bool:
        """验证是否为成功响应（2xx）"""
        actual_code = getattr(self.response, 'status_code', None)
        result = 200 <= actual_code < 300 if actual_code else False
        
        log.info(f'成功响应验证 - 状态码: {actual_code}, 结果: {result}')
        return result
    
    def is_client_error(self) -> bool:
        """验证是否为客户端错误（4xx）"""
        actual_code = getattr(self.response, 'status_code', None)
        result = 400 <= actual_code < 500 if actual_code else False
        
        log.info(f'客户端错误验证 - 状态码: {actual_code}, 结果: {result}')
        return result
    
    def is_server_error(self) -> bool:
        """验证是否为服务器错误（5xx）"""
        actual_code = getattr(self.response, 'status_code', None)
        result = 500 <= actual_code < 600 if actual_code else False
        
        log.info(f'服务器错误验证 - 状态码: {actual_code}, 结果: {result}')
        return result
    
    def has_header(self, header_name: str, expected_value: str = None) -> bool:
        """验证响应头"""
        headers = getattr(self.response, 'headers', {})
        
        if header_name not in headers:
            log.error(f'响应头验证失败 - 缺失头部: {header_name}')
            return False
        
        if expected_value is not None:
            actual_value = headers[header_name]
            result = actual_value == expected_value
            log.info(f'响应头验证 - {header_name}: 期望={expected_value}, 实际={actual_value}, 结果={result}')
            return result
        
        log.info(f'响应头存在验证 - {header_name}: 通过')
        return True
    
    def content_type_is(self, expected_type: str) -> bool:
        """验证Content-Type"""
        content_type = getattr(self.response, 'headers', {}).get('Content-Type', '')
        # 只比较主要类型，忽略字符集等参数
        actual_type = content_type.split(';')[0].strip()
        result = actual_type == expected_type
        
        log.info(f'Content-Type验证 - 期望: {expected_type}, 实际: {actual_type}, 结果: {result}')
        return result
    
    def is_json(self) -> bool:
        """验证响应是否为JSON格式"""
        return self.content_type_is('application/json')
    
    def response_time_less_than(self, max_time: float) -> bool:
        """验证响应时间"""
        # 尝试获取响应时间（单位：秒）
        elapsed = getattr(self.response, 'elapsed', None)
        if elapsed:
            actual_time = elapsed.total_seconds()
        else:
            # 如果没有elapsed属性，尝试其他可能的属性
            actual_time = getattr(self.response, 'response_time', None)
        
        if actual_time is None:
            log.warning('无法获取响应时间，跳过验证')
            return True
        
        result = actual_time < max_time
        log.info(f'响应时间验证 - 期望<{max_time}秒, 实际={actual_time}秒, 结果={result}')
        return result
    
    def json_contains(self, expected_data: Dict, ignore_fields: List[str] = None,
                     partial_match: bool = True) -> bool:
        """验证JSON响应包含指定数据"""
        try:
            if hasattr(self.response, 'json'):
                actual_json = self.response.json()
            else:
                # 如果没有json方法，尝试直接解析text
                response_text = getattr(self.response, 'text', str(self.response))
                actual_json = json.loads(response_text)
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            log.error(f'JSON解析失败: {e}')
            return False
        
        comparator = JsonComparator(actual_json)
        result = comparator.deep_compare(
            expected_data, 
            ignore_fields=ignore_fields,
            partial_match=partial_match
        )
        
        return result['passed']
    
    def json_path_equals(self, json_path: str, expected_value: Any) -> bool:
        """验证JSON路径对应的值"""
        try:
            if hasattr(self.response, 'json'):
                actual_json = self.response.json()
            else:
                response_text = getattr(self.response, 'text', str(self.response))
                actual_json = json.loads(response_text)
        except (json.JSONDecodeError, AttributeError, TypeError) as e:
            log.error(f'JSON解析失败: {e}')
            return False
        
        # 简单的JSON路径解析（支持 a.b.c 和 a[0].b 格式）
        try:
            actual_value = self._extract_json_path_value(actual_json, json_path)
            result = actual_value == expected_value
            
            log.info(f'JSON路径验证 - 路径={json_path}, 期望={expected_value}, 实际={actual_value}, 结果={result}')
            return result
        except (KeyError, IndexError, TypeError) as e:
            log.error(f'JSON路径提取失败: {json_path}, 错误: {e}')
            return False
    
    def _extract_json_path_value(self, data: Any, path: str) -> Any:
        """提取JSON路径对应的值"""
        current = data
        
        # 简单的路径解析，支持点分隔和数组索引
        parts = re.split(r'[\.\[\]]', path)
        parts = [part for part in parts if part]  # 移除空字符串
        
        for part in parts:
            if part.isdigit():
                # 数组索引
                current = current[int(part)]
            else:
                # 对象键
                current = current[part]
        
        return current


class SchemaValidator:
    """数据模式验证器"""
    
    def __init__(self, data: Any):
        self.data = data
    
    def matches_schema(self, schema: Dict) -> bool:
        """验证数据是否符合指定模式"""
        try:
            result = self._validate_against_schema(self.data, schema)
            log.info(f'模式验证结果: {result}')
            return result
        except Exception as e:
            log.error(f'模式验证失败: {e}')
            return False
    
    def _validate_against_schema(self, data: Any, schema: Dict) -> bool:
        """递归验证数据模式"""
        schema_type = schema.get('type')
        
        if schema_type == 'object':
            return self._validate_object_schema(data, schema)
        elif schema_type == 'array':
            return self._validate_array_schema(data, schema)
        elif schema_type == 'string':
            return self._validate_string_schema(data, schema)
        elif schema_type == 'number':
            return self._validate_number_schema(data, schema)
        elif schema_type == 'integer':
            return self._validate_integer_schema(data, schema)
        elif schema_type == 'boolean':
            return isinstance(data, bool)
        elif schema_type == 'null':
            return data is None
        else:
            # 如果没有指定类型，只检查是否存在
            return data is not None
    
    def _validate_object_schema(self, data: Any, schema: Dict) -> bool:
        """验证对象模式"""
        if not isinstance(data, dict):
            return False
        
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        # 检查必需字段
        for field in required:
            if field not in data:
                log.error(f'缺失必需字段: {field}')
                return False
        
        # 验证每个属性
        for field, field_schema in properties.items():
            if field in data:
                if not self._validate_against_schema(data[field], field_schema):
                    log.error(f'字段 {field} 验证失败')
                    return False
        
        return True
    
    def _validate_array_schema(self, data: Any, schema: Dict) -> bool:
        """验证数组模式"""
        if not isinstance(data, list):
            return False
        
        min_items = schema.get('minItems')
        max_items = schema.get('maxItems')
        items_schema = schema.get('items')
        
        # 检查长度限制
        if min_items is not None and len(data) < min_items:
            return False
        if max_items is not None and len(data) > max_items:
            return False
        
        # 验证每个元素
        if items_schema:
            for item in data:
                if not self._validate_against_schema(item, items_schema):
                    return False
        
        return True
    
    def _validate_string_schema(self, data: Any, schema: Dict) -> bool:
        """验证字符串模式"""
        if not isinstance(data, str):
            return False
        
        min_length = schema.get('minLength')
        max_length = schema.get('maxLength')
        pattern = schema.get('pattern')
        
        # 检查长度限制
        if min_length is not None and len(data) < min_length:
            return False
        if max_length is not None and len(data) > max_length:
            return False
        
        # 检查正则模式
        if pattern and not re.match(pattern, data):
            return False
        
        return True
    
    def _validate_number_schema(self, data: Any, schema: Dict) -> bool:
        """验证数字模式"""
        if not isinstance(data, (int, float)):
            return False
        
        minimum = schema.get('minimum')
        maximum = schema.get('maximum')
        
        # 检查数值范围
        if minimum is not None and data < minimum:
            return False
        if maximum is not None and data > maximum:
            return False
        
        return True
    
    def _validate_integer_schema(self, data: Any, schema: Dict) -> bool:
        """验证整数模式"""
        if not isinstance(data, int):
            return False
        
        return self._validate_number_schema(data, schema)
    
    def has_required_fields(self, required_fields: List[str]) -> bool:
        """验证是否包含所有必需字段"""
        if not isinstance(self.data, dict):
            return False
        
        missing_fields = [field for field in required_fields if field not in self.data]
        result = len(missing_fields) == 0
        
        if not result:
            log.error(f'缺失必需字段: {missing_fields}')
        
        log.info(f'必需字段验证 - 期望字段: {required_fields}, 结果: {result}')
        return result
    
    def field_type_is(self, field_name: str, expected_type: type) -> bool:
        """验证指定字段的类型"""
        if not isinstance(self.data, dict) or field_name not in self.data:
            log.error(f'字段 {field_name} 不存在')
            return False
        
        actual_value = self.data[field_name]
        result = isinstance(actual_value, expected_type)
        
        log.info(f'字段类型验证 - {field_name}: 期望类型={expected_type.__name__}, '
                f'实际类型={type(actual_value).__name__}, 结果={result}')
        return result
    
    def field_matches_pattern(self, field_name: str, pattern: str) -> bool:
        """验证字段值是否匹配正则表达式"""
        if not isinstance(self.data, dict) or field_name not in self.data:
            log.error(f'字段 {field_name} 不存在')
            return False
        
        field_value = self.data[field_name]
        if not isinstance(field_value, str):
            log.error(f'字段 {field_name} 不是字符串类型')
            return False
        
        comparator = StringComparator(field_value)
        result = comparator.matches_pattern(pattern)
        
        log.info(f'字段正则验证 - {field_name}: 模式={pattern}, 值={field_value}, 结果={result}')
        return result
