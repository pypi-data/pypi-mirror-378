import configparser
import os

import yaml
from pytestifyx.utils.public.get_project_path import get_project_path


def parse_ini_config(file_path):
    config = configparser.ConfigParser()
    base_path = get_project_path()
    full_path = os.path.join(str(base_path), file_path)
    config.read(full_path, encoding='utf-8')
    return config


# 默认配置
DEFAULT_CONFIG = {
    'config': {
        'is_cover_header': True,
        'encrypt_type': 'Single',
        'sign_type': 'Header',
        'request_type': 'HTTP',
        'request_method': 'POST',
        'content_type': 'json',
        'is_json_dumps': True,
        'delete_key': [],
        'concurrent_number': 1,
        'is_body_reload': True,
        'is_header_reload': True,
        'encrypt_flag': True,
        'encrypt_method': 'RSA',
        'sign_flag': True,
        'sign_method': 'RSA',
        'env_name': 'test',
        'assert_db': True,
        'is_request_log': True,
        'is_request_log_json_dumps': True,
        'is_response_log': True,
        'is_sql_log': True,
        'tenant_id': ''
    },
    'url_prefix': {
        'test': 'http://localhost:8080',
        'dev': 'http://dev.example.com',
        'pre': 'http://pre.example.com',
        'prod': 'http://prod.example.com'
    },
    'api_module': {
        'api_module_name': 'api_test'
    }
}

# 读取 YAML 配置文件
def parse_yaml_config(file_name='config.yaml'):
    base_path = get_project_path()
    file_path = os.path.join(base_path, file_name)
    
    # 如果文件不存在，返回默认配置
    if not os.path.exists(file_path):
        return DEFAULT_CONFIG
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
            if config is None:
                return DEFAULT_CONFIG
            return config
    except (FileNotFoundError, yaml.YAMLError, Exception):
        return DEFAULT_CONFIG

# 生成默认配置文件
def generate_default_config(file_name='config.yaml'):
    """生成默认的配置文件模板"""
    base_path = get_project_path()
    file_path = os.path.join(base_path, file_name)
    
    if os.path.exists(file_path):
        return f"配置文件 {file_name} 已存在，跳过生成"
    
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(DEFAULT_CONFIG, file, default_flow_style=False, allow_unicode=True, indent=2)
        return f"默认配置文件 {file_name} 生成成功"
    except Exception as e:
        return f"生成配置文件失败: {str(e)}"

if __name__ == '__main__':
    generate_default_config()