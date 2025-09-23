"""
OpenAPI/Swagger文件解析器

解析OpenAPI 3.0格式的接口文档，生成测试代码模板。
"""

import json
import re
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from urllib.parse import urljoin
from dataclasses import dataclass

from pytestifyx.utils.public.get_project_path import get_project_path

try:
    from .fiddler import HttpRequest, PathManager, FileGenerator
    from .templates import CodeTemplates, TemplateConfig
except ImportError:
    from fiddler import HttpRequest, PathManager, FileGenerator
    from templates import CodeTemplates, TemplateConfig


@dataclass
class OpenAPIEndpoint:
    """OpenAPI端点信息"""
    path: str
    method: str
    operation_id: str
    summary: str
    description: str
    tags: List[str]
    parameters: List[Dict]
    request_body: Optional[Dict]
    responses: Dict[str, Any]
    security: List[Dict]
    
    @property
    def api_name(self) -> str:
        """生成API方法名"""
        if self.operation_id:
            # 使用operationId作为方法名
            name = self.operation_id
        else:
            # 从路径和方法生成方法名
            path_parts = [part for part in self.path.split('/') if part and not part.startswith('{')]
            method_name = self.method.lower()
            if path_parts:
                name = f"{method_name}_{'_'.join(path_parts)}"
            else:
                name = method_name
        
        # 清理方法名，确保是有效的Python标识符
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        return name
    
    def to_http_request(self, base_url: str = "") -> HttpRequest:
        """转换为HttpRequest对象"""
        # 构建完整URL (路径保持原样，包含路径参数)
        full_url = urljoin(base_url, self.path) if base_url else self.path
        
        # 构建请求头
        headers = {'Content-Type': 'application/json'}
        
        # 处理安全认证
        if self.security:
            # 假设使用API Key认证
            headers['Authorization'] = 'Bearer YOUR_TOKEN'
        
        # 处理请求体
        body = None
        if self.request_body:
            content = self.request_body.get('content', {})
            if 'application/json' in content:
                schema = content['application/json'].get('schema', {})
                body = self._generate_sample_data_from_schema(schema)
        
        # 处理查询参数
        query_params = {}
        for param in self.parameters:
            if param.get('in') == 'query':
                param_name = param.get('name')
                param_schema = param.get('schema', {})
                query_params[param_name] = self._get_sample_value_from_schema(param_schema)
        
        return HttpRequest(
            method=self.method.upper(),
            url=full_url,
            headers=headers,
            body=body,
            query_params=query_params if query_params else None
        )
    
    def _generate_sample_data_from_schema(self, schema: Dict) -> Dict:
        """从schema生成示例数据"""
        if not isinstance(schema, dict):
            return {}
        
        # 处理引用
        if '$ref' in schema:
            return {"ref": schema['$ref']}
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            required = schema.get('required', [])
            
            result = {}
            for prop_name, prop_schema in properties.items():
                # 只为必需字段生成示例值
                if prop_name in required:
                    result[prop_name] = self._get_sample_value_from_schema(prop_schema)
                else:
                    # 为可选字段生成注释
                    result[f"# {prop_name}"] = f"可选字段: {prop_schema.get('description', 'N/A')}"
            
            return result
        
        elif schema_type == 'array':
            items_schema = schema.get('items', {})
            return [self._get_sample_value_from_schema(items_schema)]
        
        else:
            return self._get_sample_value_from_schema(schema)
    
    def _get_sample_value_from_schema(self, schema: Dict) -> Any:
        """从schema获取示例值"""
        if not isinstance(schema, dict):
            return "sample_value"
        
        # 检查是否有示例值
        if 'example' in schema:
            return schema['example']
        
        schema_type = schema.get('type', 'string')
        
        type_samples = {
            'string': 'string_value',
            'integer': 0,
            'number': 0.0,
            'boolean': True,
            'array': [],
            'object': {}
        }
        
        return type_samples.get(schema_type, 'unknown_value')
    
    def get_path_parameters(self) -> list:
        """
        提取路径中的参数名列表
        
        Returns:
            路径参数名列表，如 ['code']
        """
        import re
        # 提取所有大括号中的参数名
        path_params = re.findall(r'\{([^}]+)\}', self.path)
        return path_params


class OpenAPIParser:
    """OpenAPI文档解析器"""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.openapi_doc = self._load_document()
        self.endpoints = self._parse_endpoints()
    
    def _load_document(self) -> Dict:
        """加载OpenAPI文档"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"OpenAPI文件不存在: {self.file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"OpenAPI文件格式错误: {e}")
    
    def _parse_endpoints(self) -> List[OpenAPIEndpoint]:
        """解析所有端点"""
        endpoints = []
        paths = self.openapi_doc.get('paths', {})
        
        for path, path_info in paths.items():
            for method, operation in path_info.items():
                if method.lower() in ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']:
                    endpoint = OpenAPIEndpoint(
                        path=path,
                        method=method.upper(),
                        operation_id=operation.get('operationId', ''),
                        summary=operation.get('summary', ''),
                        description=operation.get('description', ''),
                        tags=operation.get('tags', []),
                        parameters=operation.get('parameters', []),
                        request_body=operation.get('requestBody'),
                        responses=operation.get('responses', {}),
                        security=operation.get('security', [])
                    )
                    endpoints.append(endpoint)
        
        return endpoints
    
    def get_info(self) -> Dict:
        """获取API基本信息"""
        return self.openapi_doc.get('info', {})
    
    def get_servers(self) -> List[str]:
        """获取服务器URL列表"""
        servers = self.openapi_doc.get('servers', [])
        return [server.get('url', '') for server in servers]
    
    def get_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for endpoint in self.endpoints:
            tags.update(endpoint.tags)
        return list(tags)
    
    def get_endpoints_by_tag(self, tag: str) -> List[OpenAPIEndpoint]:
        """根据标签获取端点"""
        return [ep for ep in self.endpoints if tag in ep.tags]
    
    def get_application_name(self) -> str:
        """从文档中提取应用名称"""
        info = self.get_info()
        title = info.get('title', '')
        
        # 从标题中提取应用名称
        if '：' in title:
            app_name = title.split('：')[1].split('_')[0]
        else:
            app_name = title.split('_')[0] if '_' in title else title
        
        # 清理应用名称
        app_name = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]', '', app_name)
        return app_name or 'api_test'


class OpenAPIToTestGenerator:
    """OpenAPI转测试用例生成器"""
    
    def __init__(self, project_root: Optional[str] = None, template_config: TemplateConfig = None):
        self.project_root = project_root or get_project_path()
        self.template_config = template_config or TemplateConfig()
    
    def generate_from_openapi(self, openapi_file: str, application_name: str = None) -> None:
        """
        从OpenAPI文件生成测试项目
        
        Args:
            openapi_file: OpenAPI文件路径
            application_name: 应用名称，如果不提供则从文档中提取
        """
        try:
            print(f"正在解析OpenAPI文件: {openapi_file}")
            
            # 解析OpenAPI文档
            parser = OpenAPIParser(openapi_file)
            
            # 确定应用名称
            if not application_name:
                application_name = parser.get_application_name()
                print(f"从文档中提取应用名称: {application_name}")
            
            print(f"✅ 成功解析OpenAPI文档")
            print(f"   - 标题: {parser.get_info().get('title', 'N/A')}")
            print(f"   - 版本: {parser.get_info().get('version', 'N/A')}")
            print(f"   - 端点数量: {len(parser.endpoints)}")
            print(f"   - 标签: {', '.join(parser.get_tags())}")
            
            # 设置路径管理器
            path_manager = PathManager(self.project_root, application_name)
            path_manager.ensure_directories()
            
            # 设置文件生成器
            file_generator = FileGenerator(path_manager, self.template_config)
            
            # 生成所有端点的文件
            api_names = []
            base_url = parser.get_servers()[0] if parser.get_servers() else "http://localhost:8080"
            
            print(f"正在生成测试文件...")
            for endpoint in parser.endpoints:
                # 转换为HttpRequest对象
                request = endpoint.to_http_request(base_url)
                api_names.append(request.api_name)
                
                print(f"  - 生成 {endpoint.summary or endpoint.api_name} ({endpoint.method} {endpoint.path})")
                
                # 生成核心文件和测试文件
                file_generator.generate_core_files(request)
                file_generator.generate_test_files(request)
            
            # 生成完整流程测试
            if api_names:
                print(f"正在生成流程测试...")
                file_generator.generate_flow_test(api_names)
            
            print(f"🎉 测试项目生成完成！项目路径: {path_manager.app_path}")
            
        except Exception as e:
            print(f"❌ 生成过程中出现错误: {e}")
            raise
    
    def generate_from_openapi_by_tag(self, openapi_file: str, tag: str, application_name: str = None) -> None:
        """
        从OpenAPI文件按标签生成测试项目
        
        Args:
            openapi_file: OpenAPI文件路径
            tag: 要生成的标签
            application_name: 应用名称
        """
        try:
            print(f"正在解析OpenAPI文件: {openapi_file}")
            
            # 解析OpenAPI文档
            parser = OpenAPIParser(openapi_file)
            
            # 确定应用名称
            if not application_name:
                application_name = parser.get_application_name()
            
            # 获取指定标签的端点
            endpoints = parser.get_endpoints_by_tag(tag)
            if not endpoints:
                print(f"❌ 未找到标签 '{tag}' 相关的端点")
                return
            
            print(f"✅ 找到 {len(endpoints)} 个 '{tag}' 相关的端点")
            
            # 设置路径管理器
            path_manager = PathManager(self.project_root, application_name)
            path_manager.ensure_directories()
            
            # 设置文件生成器
            file_generator = FileGenerator(path_manager, self.template_config)
            
            # 生成指定标签的端点文件
            api_names = []
            base_url = parser.get_servers()[0] if parser.get_servers() else "http://localhost:8080"
            
            print(f"正在生成 '{tag}' 相关的测试文件...")
            for endpoint in endpoints:
                # 转换为HttpRequest对象
                request = endpoint.to_http_request(base_url)
                api_names.append(request.api_name)
                
                print(f"  - 生成 {endpoint.summary or endpoint.api_name} ({endpoint.method} {endpoint.path})")
                
                # 生成核心文件和测试文件
                file_generator.generate_core_files(request)
                file_generator.generate_test_files(request)
            
            # 生成标签相关的流程测试
            if api_names:
                print(f"正在生成 '{tag}' 流程测试...")
                file_generator.generate_flow_test(api_names)
            
            print(f"🎉 '{tag}' 相关测试项目生成完成！项目路径: {path_manager.app_path}")
            
        except Exception as e:
            print(f"❌ 生成过程中出现错误: {e}")
            raise


def trans_openapi_to_test():
    """OpenAPI转测试用例入口函数"""
    try:
        print("🚀 PyTestifyx OpenAPI转测试用例工具")
        print("=" * 50)
        
        openapi_file_path = input("请输入OpenAPI文件的路径 📄: ").strip()
        if not openapi_file_path:
            print("❌ OpenAPI文件路径不能为空")
            return
        
        application_name = input("请输入生成应用包的名称 💼: ").strip()
        if not application_name:
            # 如果用户没有输入应用名称，尝试从文档中提取
            print("📝 未提供应用名称，将从OpenAPI文档中自动提取...")
            application_name = None
        
        # 询问是否按标签生成
        use_tag = input("是否按标签生成测试用例？(y/N) 🏷️: ").strip().lower()
        
        generator = OpenAPIToTestGenerator()
        
        if use_tag in ['y', 'yes']:
            # 先解析文档获取可用标签
            try:
                parser = OpenAPIParser(openapi_file_path)
                available_tags = parser.get_tags()
                
                if not available_tags:
                    print("❌ 该OpenAPI文档中没有定义标签")
                    return
                
                print(f"📋 可用标签: {', '.join(available_tags)}")
                tag = input("请选择要生成的标签 🎯: ").strip()
                
                if not tag:
                    print("❌ 标签不能为空")
                    return
                
                if tag not in available_tags:
                    print(f"❌ 标签 '{tag}' 不存在，可用标签: {', '.join(available_tags)}")
                    return
                
                generator.generate_from_openapi_by_tag(openapi_file_path, tag, application_name)
                
            except Exception as e:
                print(f"❌ 解析OpenAPI文档失败: {e}")
                return
        else:
            generator.generate_from_openapi(openapi_file_path, application_name)
        
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
    except Exception as e:
        print(f"❌ 执行失败: {e}")


if __name__ == '__main__':
    trans_openapi_to_test()
