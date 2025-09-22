"""
SAZ文件转换为测试用例生成器

优化后的实现，采用面向对象设计，职责分离，提高代码可维护性和可读性。
"""

import zipfile
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qsl

from pytestifyx.utils.public.get_project_path import get_project_path, ensure_path_sep
from pytestifyx.utils.public.trans_param_style import convert_string
try:
    from .templates import CodeTemplates, TemplateConfig
except ImportError:
    from templates import CodeTemplates, TemplateConfig


@dataclass
class HttpRequest:
    """HTTP请求数据模型"""
    method: str
    url: str
    headers: Dict[str, str]
    body: Optional[Dict] = None
    query_params: Optional[Dict[str, str]] = None
    
    @property
    def api_name(self) -> str:
        """从URL路径提取API名称，过滤掉路径参数"""
        import re
        parsed_url = urlparse(self.url)
        path = parsed_url.path
        
        # 过滤掉路径参数 {param}，只保留静态路径段
        path_parts = [part for part in path.split('/') if part and not part.startswith('{')]
        api_name = '_'.join(path_parts) if path_parts else 'api'
        
        # 清理API名称，确保是有效的Python标识符
        api_name = re.sub(r'[^a-zA-Z0-9_]', '_', api_name)
        api_name = re.sub(r'_+', '_', api_name)
        api_name = api_name.strip('_')
        
        return api_name
    
    @property
    def domain(self) -> str:
        """提取域名"""
        parsed_url = urlparse(self.url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    @property
    def path(self) -> str:
        """提取路径"""
        return urlparse(self.url).path
    
    @property
    def content_type(self) -> str:
        """获取Content-Type，转换为PyTestifyx支持的格式"""
        raw_content_type = self.headers.get('Content-Type', 'application/json')
        # 转换为PyTestifyx支持的格式
        if 'application/json' in raw_content_type:
            return 'json'
        elif 'multipart/form-data' in raw_content_type:
            return 'multipart/form-data'
        else:
            return 'json'  # 默认为json




class PathManager:
    """路径管理器"""
    
    def __init__(self, project_root: str, application_name: str):
        self.project_root = Path(project_root)
        self.application_name = application_name
        self.app_path = self.project_root / "api_test" / application_name
    
    def get_template_path(self, filename: str) -> Path:
        """获取模板文件路径"""
        return self.app_path / "template" / filename
    
    def get_test_case_path(self, filename: str) -> Path:
        """获取测试用例文件路径"""
        return self.app_path / "test_case" / filename
    
    def get_test_data_path(self, filename: str) -> Path:
        """获取测试数据文件路径"""
        return self.app_path / "test_data" / filename
    
    def ensure_directories(self) -> None:
        """确保所有必要的目录存在"""
        directories = [
            self.app_path,
            self.app_path / "template",
            self.app_path / "test_case", 
            self.app_path / "test_data"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            init_file = directory / "__init__.py"
            if not init_file.exists():
                init_file.touch()


class SazFileParser:
    """SAZ文件解析器"""
    
    @staticmethod
    def parse_saz_file(file_path: str) -> List[HttpRequest]:
        """解析SAZ文件，返回HTTP请求列表"""
        requests = []
        
        try:
            with zipfile.ZipFile(file_path, 'r') as saz_file:
                for filename in saz_file.namelist():
                    if filename.endswith('_c.txt'):
                        request = SazFileParser._parse_request_file(saz_file, filename)
                        if request:
                            requests.append(request)
        except zipfile.BadZipFile:
            raise ValueError(f"无效的SAZ文件: {file_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"SAZ文件不存在: {file_path}")
        
        return requests
    
    @staticmethod
    def _parse_request_file(saz_file: zipfile.ZipFile, filename: str) -> Optional[HttpRequest]:
        """解析单个请求文件"""
        try:
            with saz_file.open(filename) as file:
                content = file.read().decode('utf-8')
                
            parts = content.strip().split('\r\n')
            if len(parts) < 1:
                return None
                
            # 解析请求行
            request_line_parts = parts[0].split(' ')
            if len(request_line_parts) < 2:
                return None
                
            method, url = request_line_parts[0], request_line_parts[1]
            
            # 分离请求头和请求体
            headers, body = SazFileParser._parse_headers_and_body(parts[1:])
            
            # 解析查询参数
            parsed_url = urlparse(url)
            query_params = dict(parse_qsl(parsed_url.query))
            
            return HttpRequest(
                method=method,
                url=url,
                headers=headers,
                body=body,
                query_params=query_params if query_params else None
            )
            
        except Exception as e:
            print(f"解析请求文件 {filename} 时出错: {e}")
            return None
    
    @staticmethod
    def _parse_headers_and_body(parts: List[str]) -> Tuple[Dict[str, str], Optional[Dict]]:
        """解析请求头和请求体"""
        headers = {}
        body = None
        
        try:
            # 找到空行分隔符
            empty_line_index = parts.index('')
            headers_block = parts[:empty_line_index]
            body_text = parts[empty_line_index + 1] if empty_line_index + 1 < len(parts) else None
        except ValueError:
            # 没有空行，全部都是请求头
            headers_block = parts
            body_text = None
        
        # 解析请求头
        for line in headers_block:
            if ': ' in line:
                name, value = line.split(': ', 1)
                headers[name] = value
        
        # 解析请求体
        if body_text:
            try:
                body = json.loads(body_text)
            except json.JSONDecodeError:
                # 如果不是JSON格式，忽略请求体
                pass
        
        return headers, body


class FileGenerator:
    """文件生成器"""
    
    def __init__(self, path_manager: PathManager, template_config: TemplateConfig = None):
        self.path_manager = path_manager
        self.templates = CodeTemplates(template_config or TemplateConfig())
        self.application_name = path_manager.application_name
    
    def generate_core_files(self, request: HttpRequest) -> None:
        """生成核心文件"""
        self._generate_core_py(request)
        self._generate_body_py(request)
        self._generate_headers_py(request)
        self._generate_url_py(request)
    
    def generate_test_files(self, request: HttpRequest) -> None:
        """生成测试文件"""
        self._generate_test_case_files(request)
        self._generate_test_data_files(request)
    
    def _generate_core_py(self, request: HttpRequest) -> None:
        """生成core.py文件"""
        core_file = self.path_manager.get_template_path("core.py")
        converted_name = convert_string(self.application_name)
        
        # 如果文件不存在，创建类定义
        if not core_file.exists():
            class_template = self.templates.get_core_class_template(self.application_name, converted_name)
            self._write_file(core_file, class_template)
        
        # 检查方法是否已存在，避免重复定义
        if not self._check_method_exists(core_file, request.api_name):
            method_template = self.templates.get_api_method_template(request.api_name, request.url, request.method)
            with open(core_file, 'a', encoding='utf-8') as f:
                f.write(method_template)
            print(f"✅ 添加API方法: {request.api_name}")
        else:
            print(f"⚠️  跳过重复的API方法: {request.api_name}")
    
    def _generate_body_py(self, request: HttpRequest) -> None:
        """生成body.py文件"""
        body_file = self.path_manager.get_template_path("body.py")
        
        # 如果文件不存在，先创建默认模板
        if not body_file.exists():
            default_content = self.templates.get_default_body_template()
            self._write_file(body_file, default_content)
            print(f"✅ 创建body.py文件")
        
        # 生成请求体
        if request.body:
            body_var_name = f"{request.method.upper()}_{request.api_name}"
            if not self._check_variable_exists(body_file, body_var_name):
                body_content = self.templates.get_body_template(request.method, request.api_name, request.body)
                with open(body_file, 'a', encoding='utf-8') as f:
                    f.write(body_content)
                print(f"✅ 添加请求体数据: {body_var_name}")
            else:
                print(f"⚠️  跳过重复的请求体数据: {body_var_name}")
        
        # 生成查询参数
        if request.query_params:
            query_var_name = f"{request.method.upper()}_{request.api_name}_query_params"
            if not self._check_variable_exists(body_file, query_var_name):
                query_content = f'\n{query_var_name} = {json.dumps(request.query_params, indent=4, ensure_ascii=False)}\n'
                with open(body_file, 'a', encoding='utf-8') as f:
                    f.write(query_content)
                print(f"✅ 添加查询参数: {query_var_name}")
            else:
                print(f"⚠️  跳过重复的查询参数: {query_var_name}")
    
    def _generate_headers_py(self, request: HttpRequest) -> None:
        """生成headers.py文件"""
        headers_file = self.path_manager.get_template_path("headers.py")
        headers_var_name = f"{request.api_name}_headers"
        
        # 检查请求头变量是否已存在，避免重复定义
        if not self._check_variable_exists(headers_file, headers_var_name):
            headers_content = self.templates.get_headers_template(request.api_name, request.headers)
            with open(headers_file, 'a', encoding='utf-8') as f:
                f.write(headers_content)
            print(f"✅ 添加请求头配置: {headers_var_name}")
        else:
            print(f"⚠️  跳过重复的请求头配置: {headers_var_name}")
    
    def _generate_url_py(self, request: HttpRequest) -> None:
        """生成url.py文件"""
        url_file = self.path_manager.get_template_path("url.py")
        api_path_var_name = f"{request.method.upper()}_{request.api_name}"
        
        # 检查文件是否存在以及是否已包含基础URL
        if not url_file.exists():
            # 文件不存在，创建完整的URL配置
            url_content = self.templates.get_url_template(request.method, request.api_name, request.domain, request.path)
            self._write_file(url_file, url_content)
            print(f"✅ 创建URL文件并添加API路径: {api_path_var_name}")
        else:
            # 文件已存在，检查是否需要添加基础URL
            existing_content = url_file.read_text(encoding='utf-8')
            if 'url_prefix_test' not in existing_content:
                # 如果不存在基础URL，先添加基础URL
                base_url_content = self.templates.get_base_url_template(request.domain)
                with open(url_file, 'a', encoding='utf-8') as f:
                    f.write(base_url_content)
                print("✅ 添加基础URL配置")
            
            # 检查API路径是否已存在，避免重复定义
            if not self._check_variable_exists(url_file, api_path_var_name):
                api_path_content = self.templates.get_api_path_template(request.method, request.api_name, request.path)
                with open(url_file, 'a', encoding='utf-8') as f:
                    f.write(api_path_content)
                print(f"✅ 添加API路径: {api_path_var_name}")
            else:
                print(f"⚠️  跳过重复的API路径: {api_path_var_name}")
    
    def _generate_test_case_files(self, request: HttpRequest) -> None:
        """生成测试用例文件"""
        test_cases = [
            ('busi', 1),
            ('conc', 5)
        ]
        converted_name = convert_string(self.application_name)
        
        for category, concurrent_number in test_cases:
            test_file = self.path_manager.get_test_case_path(f"{category}.py")
            
            # 生成类定义
            if not test_file.exists():
                class_template = self.templates.get_test_class_template(category, self.application_name, converted_name)
                self._write_file(test_file, class_template)
            
            # 添加测试方法
            method_template = self.templates.get_test_method_template(
                category, request.api_name, request.method, request.content_type, converted_name, concurrent_number
            )
            self._append_if_not_exists(test_file, method_template)
    
    def _generate_test_data_files(self, request: HttpRequest) -> None:
        """生成测试数据文件"""
        categories = ['busi', 'conc', 'flow']
        converted_name = convert_string(self.application_name)
        
        for category in categories:
            data_file = self.path_manager.get_test_data_path(f"{category}.py")
            
            # 生成类定义
            if not data_file.exists():
                class_template = self.templates.get_data_class_template(category, self.application_name, converted_name)
                self._write_file(data_file, class_template)
            
            # 添加数据方法
            api_name = request.api_name if category != 'flow' else 'all'
            method_template = self.templates.get_data_method_template(category, api_name)
            self._append_if_not_exists(data_file, method_template)
    
    def generate_flow_test(self, api_methods: List[str]) -> None:
        """生成流程测试文件"""
        flow_file = self.path_manager.get_test_case_path("flow.py")
        converted_name = convert_string(self.application_name)
        
        if not flow_file.exists():
            class_template = self.templates.get_flow_class_template(self.application_name, converted_name)
            self._write_file(flow_file, class_template)
        
        # 生成流程测试方法
        flow_method = self.templates.get_flow_method_template(api_methods, converted_name)
        self._append_if_not_exists(flow_file, flow_method)
    
    def _write_file(self, file_path: Path, content: str) -> None:
        """写入文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _append_if_not_exists(self, file_path: Path, content: str) -> None:
        """如果内容不存在则追加"""
        if file_path.exists():
            existing_content = file_path.read_text(encoding='utf-8')
            if content.strip() in existing_content:
                return
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _check_method_exists(self, file_path: Path, method_name: str) -> bool:
        """检查方法是否已存在于core.py文件中"""
        if not file_path.exists():
            return False
        
        existing_content = file_path.read_text(encoding='utf-8')
        method_signature = f"def {method_name}("
        return method_signature in existing_content
    
    def _check_variable_exists(self, file_path: Path, variable_name: str) -> bool:
        """检查变量是否已存在于文件中"""
        if not file_path.exists():
            return False
        
        existing_content = file_path.read_text(encoding='utf-8')
        variable_assignment = f"{variable_name} ="
        return variable_assignment in existing_content


class SazToTestGenerator:
    """SAZ转测试用例生成器主类"""
    
    def __init__(self, project_root: Optional[str] = None, template_config: TemplateConfig = None):
        self.project_root = project_root or get_project_path()
        self.template_config = template_config or TemplateConfig()
    
    def generate_test_project(self, saz_file_path: str, application_name: str) -> None:
        """生成测试项目"""
        try:
            # 解析SAZ文件
            print(f"正在解析SAZ文件: {saz_file_path}")
            requests = SazFileParser.parse_saz_file(saz_file_path)
            
            if not requests:
                print("❌ 未找到有效的HTTP请求")
                return
            
            print(f"✅ 成功解析 {len(requests)} 个HTTP请求")
            
            # 设置路径管理器
            path_manager = PathManager(self.project_root, application_name)
            path_manager.ensure_directories()
            
            # 设置文件生成器
            file_generator = FileGenerator(path_manager, self.template_config)
            
            # 生成文件
            api_methods = []
            for request in requests:
                print(f"正在生成 {request.api_name} 相关文件...")
                file_generator.generate_core_files(request)
                file_generator.generate_test_files(request)
                api_methods.append(request.api_name)
            
            # 生成流程测试
            file_generator.generate_flow_test(api_methods)
            
            print(f"🎉 测试项目生成完成！项目路径: {path_manager.app_path}")
            
        except Exception as e:
            print(f"❌ 生成过程中出现错误: {e}")
            raise


def trans_saz_to_test():
    """SAZ转测试用例入口函数"""
    try:
        saz_file_path = input("请输入SAZ文件的路径 🏭: ").strip()
        if not saz_file_path:
            print("❌ SAZ文件路径不能为空")
            return
        
        application_name = input("请输入生成应用包的名称 💼: ").strip()
        if not application_name:
            print("❌ 应用包名称不能为空")
            return
        
        generator = SazToTestGenerator()
        generator.generate_test_project(saz_file_path, application_name)
        
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
    except Exception as e:
        print(f"❌ 执行失败: {e}")


if __name__ == '__main__':
    trans_saz_to_test()