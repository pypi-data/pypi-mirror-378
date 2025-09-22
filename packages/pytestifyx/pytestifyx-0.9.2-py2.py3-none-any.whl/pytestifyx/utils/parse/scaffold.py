"""
项目脚手架生成器

优化后的实现，采用面向对象设计，改善错误处理和配置管理。
"""

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    from .templates import CodeTemplates, TemplateConfig
except ImportError:
    from templates import CodeTemplates, TemplateConfig


@dataclass
class ProjectConfig:
    """项目配置数据类"""
    test_type: str
    application_name: str
    project_root: Optional[str] = None
    
    def __post_init__(self):
        """验证配置参数"""
        if self.test_type not in ['api', 'ui', 'app']:
            raise ValueError(f"不支持的测试类型: {self.test_type}，支持的类型: api, ui, app")
        
        if not self.application_name or not self.application_name.strip():
            raise ValueError("应用名称不能为空")
        
        self.application_name = self.application_name.strip()
        
        if self.project_root is None:
            self.project_root = os.getcwd()


class FileTemplate:
    """文件模板管理"""
    
    def __init__(self, template_config: TemplateConfig = None):
        self.templates = CodeTemplates(template_config or TemplateConfig())
    
    def get_init_file_content(self) -> str:
        """获取 __init__.py 文件内容"""
        return '# -*- coding: utf-8 -*-\n'
    
    def get_conftest_content(self) -> str:
        """获取 conftest.py 文件内容"""
        return self.templates.get_conftest_template()

    def get_requirements_content(self) -> str:
        """获取 requirements.txt 文件内容"""
        return '''# 测试依赖包
pytest>=7.0.0
pytest-cases>=3.6.0
pytest-html>=3.1.0
pytest-xdist>=2.5.0
requests>=2.28.0
'''

    def get_readme_content(self, project_name: str, test_type: str) -> str:
        """获取 README.md 文件内容"""
        return f'''# {project_name} 测试项目

## 项目描述
{project_name} 的 {test_type.upper()} 自动化测试项目

## 目录结构
```
{test_type}_test/
├── {project_name}/
│   ├── template/         # 测试模板
│   ├── test_case/        # 测试用例
│   ├── test_data/        # 测试数据
│   └── __init__.py
├── conftest.py          # pytest 配置
├── requirements.txt     # 依赖包
└── README.md           # 项目说明
```

## 使用方法
1. 安装依赖：`pip install -r requirements.txt`
2. 运行测试：`pytest`
3. 生成报告：`pytest --html=report.html`

## 测试类型
- busi: 业务逻辑测试
- conc: 并发测试  
- flow: 流程测试
'''


class DirectoryManager:
    """目录管理器"""
    
    def __init__(self, config: ProjectConfig):
        self.config = config
        self.project_path = Path(config.project_root) / f"{config.test_type}_test"
        self.app_path = self.project_path / config.application_name
    
    def create_project_structure(self) -> None:
        """创建项目目录结构"""
        try:
            # 检查项目目录是否已存在
            if self.project_path.exists():
                user_input = input(f"项目目录 {self.project_path} 已存在，是否继续？(y/N): ")
                if user_input.lower() not in ['y', 'yes']:
                    print("❌ 用户取消操作")
                    return
            
            # 创建目录结构
            directories = self._get_directory_structure()
            
            for directory in directories:
                self._create_directory_safely(directory)
                print(f"✅ 创建目录: {directory}")
            
        except Exception as e:
            raise RuntimeError(f"创建项目结构失败: {e}")
    
    def _get_directory_structure(self) -> List[Path]:
        """获取项目目录结构"""
        return [
            self.project_path,
            self.app_path,
            self.app_path / "template",
            self.app_path / "test_case", 
            self.app_path / "test_data"
        ]
    
    def _create_directory_safely(self, directory: Path) -> None:
        """安全创建目录"""
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"没有权限创建目录: {directory}")
        except OSError as e:
            raise OSError(f"创建目录失败: {directory}, 错误: {e}")


class FileManager:
    """文件管理器"""
    
    def __init__(self, config: ProjectConfig, directory_manager: DirectoryManager, template_config: TemplateConfig = None):
        self.config = config
        self.directory_manager = directory_manager
        self.template = FileTemplate(template_config)
    
    def create_project_files(self) -> None:
        """创建项目文件"""
        try:
            # 创建基础文件
            self._create_basic_files()
            
            # 从模板复制文件（如果模板目录存在）
            self._copy_template_files()
            
            print("✅ 项目文件创建完成")
            
        except Exception as e:
            raise RuntimeError(f"创建项目文件失败: {e}")
    
    def _create_basic_files(self) -> None:
        """创建基础文件"""
        files_to_create = [
            # __init__.py 文件
            (self.directory_manager.project_path / "__init__.py", self.template.get_init_file_content()),
            (self.directory_manager.app_path / "__init__.py", self.template.get_init_file_content()),
            (self.directory_manager.app_path / "template" / "__init__.py", self.template.get_init_file_content()),
            (self.directory_manager.app_path / "test_case" / "__init__.py", self.template.get_init_file_content()),
            (self.directory_manager.app_path / "test_data" / "__init__.py", self.template.get_init_file_content()),
            
            # 配置文件
            (self.directory_manager.project_path / "conftest.py", self.template.get_conftest_content()),
            (self.directory_manager.project_path / "requirements.txt", self.template.get_requirements_content()),
            (self.directory_manager.project_path / "README.md", 
             self.template.get_readme_content(self.config.application_name, self.config.test_type)),
        ]
        
        for file_path, content in files_to_create:
            self._create_file_safely(file_path, content)
            print(f"✅ 创建文件: {file_path}")
    
    def _copy_template_files(self) -> None:
        """从模板目录复制文件"""
        template_dir = Path(__file__).parent / "test_project" / f"{self.config.test_type}_test" / "test_application"
        
        if not template_dir.exists():
            print(f"⚠️  模板目录不存在: {template_dir}")
            return
        
        try:
            self._copy_directory_contents(template_dir, self.directory_manager.app_path)
            print(f"✅ 从模板复制文件: {template_dir}")
        except Exception as e:
            print(f"⚠️  复制模板文件失败: {e}")
    
    def _copy_directory_contents(self, source_dir: Path, target_dir: Path) -> None:
        """递归复制目录内容"""
        for item in source_dir.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(source_dir)
                target_file = target_dir / relative_path
                
                # 确保目标目录存在
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                # 复制文件内容
                content = item.read_text(encoding='utf-8')
                self._create_file_safely(target_file, content)
    
    def _create_file_safely(self, file_path: Path, content: str) -> None:
        """安全创建文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except PermissionError:
            raise PermissionError(f"没有权限创建文件: {file_path}")
        except OSError as e:
            raise OSError(f"创建文件失败: {file_path}, 错误: {e}")


class UserInteraction:
    """用户交互管理"""
    
    @staticmethod
    def get_project_config() -> ProjectConfig:
        """获取项目配置"""
        try:
            # 获取测试类型
            test_type = input("请选择测试类型(api/ui/app) 🏭 [默认: api]: ").strip().lower()
            if not test_type:
                test_type = "api"
            
            # 获取应用名称
            application_name = input("请输入应用名称 💼 [默认: test_application]: ").strip()
            if not application_name:
                application_name = "test_application"
            
            return ProjectConfig(
                test_type=test_type,
                application_name=application_name
            )
            
        except KeyboardInterrupt:
            print("\n❌ 用户取消操作")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 获取配置失败: {e}")
            sys.exit(1)
    
    @staticmethod
    def show_success_message(project_path: Path, app_name: str) -> None:
        """显示成功消息"""
        print("\n" + "="*50)
        print("🎉 项目脚手架创建成功！")
        print("="*50)
        print(f"📁 项目路径: {project_path}")
        print(f"📦 应用名称: {app_name}")
        print("\n📋 后续步骤:")
        print(f"1. cd {project_path}")
        print("2. pip install -r requirements.txt")
        print("3. 开始编写您的测试用例")
        print("="*50)


class ProjectScaffold:
    """项目脚手架主类"""
    
    def __init__(self, config: Optional[ProjectConfig] = None, template_config: Optional[TemplateConfig] = None):
        self.config = config
        self.template_config = template_config or TemplateConfig()
        self.directory_manager = None
        self.file_manager = None
    
    def create_project(self, config: Optional[ProjectConfig] = None) -> None:
        """创建项目"""
        try:
            # 使用提供的配置或默认配置
            if config:
                self.config = config
            elif not self.config:
                self.config = UserInteraction.get_project_config()
            
            print(f"\n🚀 开始创建 {self.config.test_type.upper()} 测试项目: {self.config.application_name}")
            
            # 初始化管理器
            self.directory_manager = DirectoryManager(self.config)
            self.file_manager = FileManager(self.config, self.directory_manager, self.template_config)
            
            # 创建项目结构
            self.directory_manager.create_project_structure()
            
            # 创建项目文件
            self.file_manager.create_project_files()
            
            # 显示成功消息
            UserInteraction.show_success_message(
                self.directory_manager.project_path, 
                self.config.application_name
            )
            
        except Exception as e:
            print(f"❌ 创建项目失败: {e}")
            raise


def create_scaffold() -> int:
    """创建项目脚手架（入口函数）"""
    try:
        scaffold = ProjectScaffold()
        scaffold.create_project()
        return 0
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
        return 1
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1


def main_scaffold():
    """项目脚手架处理程序入口"""
    sys.exit(create_scaffold())


if __name__ == '__main__':
    main_scaffold()