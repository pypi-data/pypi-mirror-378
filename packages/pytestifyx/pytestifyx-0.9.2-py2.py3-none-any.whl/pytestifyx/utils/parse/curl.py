"""
Curl命令转换为测试用例生成器

支持解析curl命令并自动生成PyTestifyx测试用例模板。
"""

import json
import re
import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union
from urllib.parse import urlparse, parse_qsl, unquote

from pytestifyx.utils.public.get_project_path import get_project_path
from pytestifyx.utils.public.trans_param_style import convert_string
try:
    from .templates import CodeTemplates, TemplateConfig
except ImportError:
    from templates import CodeTemplates, TemplateConfig

# 重用fiddler.py中的HttpRequest数据模型和其他组件
try:
    from .fiddler import HttpRequest, PathManager, FileGenerator
except ImportError:
    from fiddler import HttpRequest, PathManager, FileGenerator


class CurlParser:
    """Curl命令解析器"""
    
    @staticmethod
    def parse_curl_command(curl_command: str) -> HttpRequest:
        """
        解析curl命令，返回HttpRequest对象
        
        Args:
            curl_command: curl命令字符串
            
        Returns:
            HttpRequest对象
            
        Raises:
            ValueError: 当curl命令格式无效时
        """
        # 清理和标准化curl命令
        curl_command = CurlParser._clean_curl_command(curl_command)
        
        # 使用shlex安全解析命令行参数
        try:
            args = shlex.split(curl_command)
        except ValueError as e:
            raise ValueError(f"无效的curl命令格式: {e}")
        
        if not args or args[0] != 'curl':
            raise ValueError("命令必须以 'curl' 开头")
        
        # 解析参数
        parsed_data = CurlParser._parse_arguments(args[1:])
        
        # 构建HttpRequest对象
        return HttpRequest(
            method=parsed_data['method'],
            url=parsed_data['url'],
            headers=parsed_data['headers'],
            body=parsed_data['body'],
            query_params=parsed_data['query_params']
        )
    
    @staticmethod
    def _clean_curl_command(curl_command: str) -> str:
        """清理curl命令字符串"""
        # 移除多余的空白字符
        curl_command = re.sub(r'\s+', ' ', curl_command.strip())
        
        # 处理换行符和反斜杠转义
        curl_command = curl_command.replace('\\\n', ' ')
        curl_command = curl_command.replace('\\', '')
        
        return curl_command
    
    @staticmethod
    def _parse_arguments(args: List[str]) -> Dict:
        """解析curl命令参数"""
        result = {
            'method': 'GET',
            'url': '',
            'headers': {},
            'body': None,
            'query_params': None
        }
        
        i = 0
        while i < len(args):
            arg = args[i]
            
            # 处理HTTP方法
            if arg in ['-X', '--request']:
                if i + 1 < len(args):
                    result['method'] = args[i + 1].upper()
                    i += 2
                else:
                    raise ValueError("缺少HTTP方法参数")
                continue
            
            # 处理请求头
            if arg in ['-H', '--header']:
                if i + 1 < len(args):
                    header = args[i + 1]
                    CurlParser._parse_header(header, result['headers'])
                    i += 2
                else:
                    raise ValueError("缺少请求头参数")
                continue
            
            # 处理请求体数据
            if arg in ['-d', '--data', '--data-raw']:
                if i + 1 < len(args):
                    data = args[i + 1]
                    result['body'] = CurlParser._parse_data(data)
                    # 如果没有显式设置Content-Type，默认为application/json
                    if 'Content-Type' not in result['headers']:
                        result['headers']['Content-Type'] = 'application/json'
                    i += 2
                else:
                    raise ValueError("缺少请求体数据参数")
                continue
            
            # 处理URL编码数据
            if arg in ['--data-urlencode']:
                if i + 1 < len(args):
                    data = args[i + 1]
                    result['body'] = CurlParser._parse_form_data(data)
                    result['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
                    i += 2
                else:
                    raise ValueError("缺少URL编码数据参数")
                continue
            
            # 处理用户认证
            if arg in ['-u', '--user']:
                if i + 1 < len(args):
                    # 基础认证会自动添加到headers中
                    import base64
                    auth_string = base64.b64encode(args[i + 1].encode()).decode()
                    result['headers']['Authorization'] = f'Basic {auth_string}'
                    i += 2
                else:
                    raise ValueError("缺少用户认证参数")
                continue
            
            # 处理其他常见选项
            if arg in ['-i', '--include', '-v', '--verbose', '-s', '--silent', 
                      '-L', '--location', '-k', '--insecure', '--compressed']:
                i += 1
                continue
            
            # 如果不是选项参数，则认为是URL
            if not arg.startswith('-'):
                if not result['url']:
                    result['url'] = arg
                    # 解析URL中的查询参数
                    parsed_url = urlparse(arg)
                    if parsed_url.query:
                        result['query_params'] = dict(parse_qsl(parsed_url.query))
                i += 1
                continue
            
            # 跳过不识别的参数
            i += 1
        
        # 验证必要参数
        if not result['url']:
            raise ValueError("缺少URL参数")
        
        return result
    
    @staticmethod
    def _parse_header(header_string: str, headers: Dict[str, str]) -> None:
        """解析单个请求头"""
        if ':' in header_string:
            name, value = header_string.split(':', 1)
            headers[name.strip()] = value.strip()
        else:
            raise ValueError(f"无效的请求头格式: {header_string}")
    
    @staticmethod
    def _parse_data(data_string: str) -> Optional[Dict]:
        """解析请求体数据"""
        if not data_string:
            return None
        
        # 尝试解析为JSON
        try:
            return json.loads(data_string)
        except json.JSONDecodeError:
            # 如果不是JSON格式，尝试解析为form数据
            try:
                return dict(parse_qsl(data_string))
            except:
                # 如果都失败了，返回原始字符串
                return {"raw_data": data_string}
    
    @staticmethod
    def _parse_form_data(data_string: str) -> Dict:
        """解析表单数据"""
        try:
            return dict(parse_qsl(data_string))
        except:
            return {"form_data": data_string}


class CurlToTestGenerator:
    """Curl转测试用例生成器主类"""
    
    def __init__(self, project_root: Optional[str] = None, template_config: TemplateConfig = None):
        self.project_root = project_root or get_project_path()
        self.template_config = template_config or TemplateConfig()
    
    def generate_from_curl(self, curl_command: str, application_name: str) -> None:
        """
        从curl命令生成测试项目
        
        Args:
            curl_command: curl命令字符串
            application_name: 应用名称
        """
        try:
            print(f"正在解析curl命令...")
            
            # 解析curl命令
            request = CurlParser.parse_curl_command(curl_command)
            print(f"✅ 成功解析curl命令")
            print(f"   - 方法: {request.method}")
            print(f"   - URL: {request.url}")
            print(f"   - API名称: {request.api_name}")
            
            # 设置路径管理器
            path_manager = PathManager(self.project_root, application_name)
            path_manager.ensure_directories()
            
            # 设置文件生成器
            file_generator = FileGenerator(path_manager, self.template_config)
            
            # 生成文件
            print(f"正在生成 {request.api_name} 相关文件...")
            file_generator.generate_core_files(request)
            file_generator.generate_test_files(request)
            
            # 生成单个API的流程测试
            file_generator.generate_flow_test([request.api_name])
            
            print(f"🎉 测试项目生成完成！项目路径: {path_manager.app_path}")
            
        except Exception as e:
            print(f"❌ 生成过程中出现错误: {e}")
            raise
    
    def generate_from_curl_list(self, curl_commands: List[str], application_name: str) -> None:
        """
        从多个curl命令生成测试项目
        
        Args:
            curl_commands: curl命令列表
            application_name: 应用名称
        """
        try:
            print(f"正在解析 {len(curl_commands)} 个curl命令...")
            
            # 解析所有curl命令
            requests = []
            for i, curl_command in enumerate(curl_commands, 1):
                try:
                    request = CurlParser.parse_curl_command(curl_command)
                    requests.append(request)
                    print(f"✅ 成功解析第 {i} 个curl命令: {request.api_name}")
                except Exception as e:
                    print(f"⚠️  解析第 {i} 个curl命令失败: {e}")
                    continue
            
            if not requests:
                print("❌ 未找到有效的curl命令")
                return
            
            print(f"✅ 成功解析 {len(requests)} 个有效的curl命令")
            
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
    
    def generate_from_curl_file(self, curl_file_path: str, application_name: str) -> None:
        """
        从包含curl命令的文件生成测试项目
        
        Args:
            curl_file_path: 包含curl命令的文件路径
            application_name: 应用名称
        """
        try:
            print(f"正在读取curl命令文件: {curl_file_path}")
            
            # 读取文件内容
            with open(curl_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 按行分割并过滤有效的curl命令
            curl_commands = []
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and 'curl' in line:
                    curl_commands.append(line)
            
            if not curl_commands:
                print("❌ 文件中未找到有效的curl命令")
                return
            
            print(f"✅ 从文件中读取到 {len(curl_commands)} 个curl命令")
            
            # 使用列表方式生成
            self.generate_from_curl_list(curl_commands, application_name)
            
        except FileNotFoundError:
            print(f"❌ 文件不存在: {curl_file_path}")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            raise


def trans_curl_to_test():
    """Curl转测试用例入口函数"""
    try:
        print("🚀 Curl命令转测试用例生成器")
        print("支持的输入方式:")
        print("1. 直接输入curl命令")
        print("2. 输入包含curl命令的文件路径")
        print("3. 输入多个curl命令（用分号分隔）")
        
        input_type = input("\n请选择输入方式 (1/2/3) [默认: 1]: ").strip()
        if not input_type:
            input_type = "1"
        
        application_name = input("请输入生成应用包的名称 💼: ").strip()
        if not application_name:
            print("❌ 应用包名称不能为空")
            return
        
        generator = CurlToTestGenerator()
        
        if input_type == "1":
            # 单个curl命令
            curl_command = input("请输入curl命令 🌐: ").strip()
            if not curl_command:
                print("❌ curl命令不能为空")
                return
            
            generator.generate_from_curl(curl_command, application_name)
            
        elif input_type == "2":
            # 从文件读取
            file_path = input("请输入包含curl命令的文件路径 📁: ").strip()
            if not file_path:
                print("❌ 文件路径不能为空")
                return
            
            generator.generate_from_curl_file(file_path, application_name)
            
        elif input_type == "3":
            # 多个curl命令
            print("请输入多个curl命令，用分号(;)分隔，或按回车结束输入:")
            curl_commands_input = input("🌐: ").strip()
            if not curl_commands_input:
                print("❌ curl命令不能为空")
                return
            
            # 按分号分割命令
            curl_commands = [cmd.strip() for cmd in curl_commands_input.split(';') if cmd.strip()]
            if not curl_commands:
                print("❌ 未找到有效的curl命令")
                return
            
            generator.generate_from_curl_list(curl_commands, application_name)
            
        else:
            print("❌ 无效的输入方式")
            return
        
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
    except Exception as e:
        print(f"❌ 执行失败: {e}")


if __name__ == '__main__':
    trans_curl_to_test()
