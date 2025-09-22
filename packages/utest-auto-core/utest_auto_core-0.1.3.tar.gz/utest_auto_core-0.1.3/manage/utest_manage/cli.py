# -*- coding: utf-8 -*-
"""
utest-manage CLI 实现（已与根仓库解耦）

子命令：
- init：初始化脚本目录（从模板复制、创建虚拟环境并安装依赖）
- new-case：在 test_cases 下创建新用例
- build：构建包（优先 uv build）
- clean：清理构建产物
"""

import argparse
import os
import sys
import shutil
import subprocess
from pathlib import Path


class CommandLineTool:
    """命令行管理工具主类"""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="UTest 自动化测试框架管理工具",
            epilog="""
使用示例：
  # 初始化新的测试框架项目
  utest-manage init my_test_project
  
  # 进入框架目录并创建测试用例
  cd my_test_project
  utest-manage new-case MyTestCase
  
  # 打包框架为 zip 文件
  utest-manage build
  
  # 清理构建产物
  utest-manage clean
            """,
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        subparsers = self.parser.add_subparsers(dest="command", help="可用子命令")

        case_parser = subparsers.add_parser(
            "new-case",
            help="创建新的测试用例文件（需在框架目录中执行）",
            description="""在 test_cases 目录下创建完整的测试用例模板文件，包含：
• setup/teardown 前置后置操作示例
• 性能监控、录制、logcat 收集功能
• 多种断言方法使用示例
• 日志记录和截图功能
• 异常处理策略
• 性能数据记录

注意：必须在已初始化的框架目录中执行此命令。""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        case_parser.add_argument("name", help="测试用例文件名（不含 .py 扩展名，会自动转换为类名）")
        case_parser.set_defaults(func=self.new_case)

        build_parser = subparsers.add_parser(
            "build",
            help="打包测试框架为 zip 文件（需在框架目录中执行）",
            description="""将整个测试框架项目打包为 zip 文件，包含：
• 所有框架代码文件
• 测试用例目录
• 配置文件（config.yml、requirements.txt 等）
• 脚本文件（run.sh、update_config.py 等）

自动排除临时文件和构建产物（__pycache__、.venv、test_result 等）。

注意：必须在已初始化的框架目录中执行此命令。""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        build_parser.add_argument("--output", "-o", help="输出 zip 文件名（默认：{框架名}_{时间戳}.zip）")
        build_parser.set_defaults(func=self.build_zip)

        clean_parser = subparsers.add_parser(
            "clean",
            help="清理构建产物和临时文件（需在框架目录中执行）",
            description="""清理项目中的临时文件和构建产物，包括：
• 构建目录（dist/、build/）
• 测试结果目录（test_result/）
• Python 缓存文件（__pycache__/、*.pyc、*.pyo）
• 日志文件（*.log）
• 压缩包文件（*.zip、*.whl）
• 包信息目录（*.egg-info/）

注意：必须在已初始化的框架目录中执行此命令。""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        clean_parser.set_defaults(func=self.clean)

        # init 命令
        init_parser = subparsers.add_parser(
            "init",
            help="初始化新的测试框架项目（可在任何目录执行）",
            description="""从模板创建完整的测试框架项目，包括：
• 复制所有模板文件（配置文件、测试用例、脚本等）
• 自动安装 uv 工具（如果未安装）
• 创建 Python 3.10.12 虚拟环境
• 安装项目依赖
• 提供虚拟环境激活命令

此命令可在任何目录执行，会在指定目录创建新的框架项目。""",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        init_parser.add_argument("target", nargs="?", default=".", help="目标目录路径（默认：当前目录）")
        init_parser.add_argument("--force", action="store_true", help="强制覆盖已存在的文件（默认：检查冲突后退出）")
        init_parser.set_defaults(func=self.init_only_scripts)

    # ----------------- 子命令实现 -----------------

    def _check_framework_directory(self) -> bool:
        """检查当前目录是否为有效的框架目录"""
        required_files = ["config.yml", "start_test.py", "requirements.txt", "run.sh", "update_config.py", "uv.toml"]
        required_dirs = ["test_cases"]

        for file in required_files:
            if not Path(file).exists():
                print(f"❌ 当前目录不是有效的框架目录，缺少文件：{file}")
                print("请先使用 'init' 命令初始化框架，或切换到正确的框架目录")
                return False

        for dir_name in required_dirs:
            if not Path(dir_name).exists() or not Path(dir_name).is_dir():
                print(f"❌ 当前目录不是有效的框架目录，缺少目录：{dir_name}")
                print("请先使用 'init' 命令初始化框架，或切换到正确的框架目录")
                return False

        return True

    def init_only_scripts(self, args) -> None:
        """初始化脚本工程：
        1) 从 manage/templates 复制全部文件与目录到目标目录；
        2) 在目标目录创建虚拟环境：uv venv --python 3.10.12；
        3) 打印平台对应的激活命令；
        4) 使用虚拟环境安装 requirements.txt 依赖。
        """
        target_dir = Path(args.target).resolve()
        # 模板路径：优先使用包内的模板，如果不存在则使用开发环境的模板
        tpl_root = Path(__file__).parent / "templates"
        if not tpl_root.exists():
            tpl_root = Path(__file__).resolve().parents[1] / "templates"

        if not tpl_root.exists():
            print("未找到模板目录：manage/templates。")
            return

        # 防护：存在关键文件且未 --force 时不覆盖
        if target_dir.exists() and not args.force:
            key_files = [target_dir / "config.yml", target_dir / "start_test.py"]
            if any(p.exists() for p in key_files):
                print(f"目标目录 {target_dir} 已存在，并包含关键文件。使用 --force 覆盖。")
                return

        target_dir.mkdir(parents=True, exist_ok=True)

        # 复制模板全部内容
        for item in tpl_root.iterdir():
            dst = target_dir / item.name
            if item.is_dir():
                if dst.exists() and args.force:
                    shutil.rmtree(dst, ignore_errors=True)
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                if dst.exists() and args.force:
                    dst.unlink()
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst)

        # 检查并安装 uv
        def check_uv_installed() -> bool:
            """检查 uv 是否已安装"""
            try:
                subprocess.check_call(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except (subprocess.CalledProcessError, FileNotFoundError):
                return False

        def install_uv() -> bool:
            """根据操作系统安装 uv"""
            print("检测到未安装 uv，正在自动安装...")

            if os.name == "nt":  # Windows
                print("在 Windows 上安装 uv...")
                try:
                    cmd = [
                        "powershell", "-ExecutionPolicy", "ByPass", "-c",
                        "irm https://astral.sh/uv/install.ps1 | iex"
                    ]
                    subprocess.check_call(cmd)
                    print("✅ uv 安装完成")
                    return True
                except Exception as e:
                    print(f"❌ Windows 上安装 uv 失败：{e}")
                    print(
                        "请手动安装：powershell -ExecutionPolicy ByPass -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
                    return False
            else:  # Linux/macOS
                print("在 Linux/macOS 上安装 uv...")
                try:
                    # 尝试 curl
                    try:
                        cmd = ["curl", "-LsSf", "https://astral.sh/uv/install.sh", "|", "sh"]
                        subprocess.check_call("curl -LsSf https://astral.sh/uv/install.sh | sh", shell=True)
                        print("✅ uv 安装完成（使用 curl）")
                        return True
                    except:
                        # 如果 curl 失败，尝试 wget
                        cmd = ["wget", "-qO-", "https://astral.sh/uv/install.sh", "|", "sh"]
                        subprocess.check_call("wget -qO- https://astral.sh/uv/install.sh | sh", shell=True)
                        print("✅ uv 安装完成（使用 wget）")
                        return True
                except Exception as e:
                    print(f"❌ Linux/macOS 上安装 uv 失败：{e}")
                    print("请手动安装：")
                    print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
                    print("  或")
                    print("  wget -qO- https://astral.sh/uv/install.sh | sh")
                    return False

        # 检查 uv 是否已安装
        if not check_uv_installed():
            if not install_uv():
                print("❌ 无法安装 uv，请手动安装后重试")
                return
        else:
            print("✅ 检测到 uv 已安装")

        # 创建虚拟环境：uv venv --python 3.10.12
        def run(cmd, cwd=None, capture_output=False, shell=False) -> bool:
            """运行外部命令，失败时返回 False。"""
            try:
                if isinstance(cmd, str):
                    print("执行：" + cmd)
                else:
                    print("执行：" + " ".join(cmd))

                if capture_output:
                    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=shell)
                    if result.returncode != 0:
                        print(f"命令失败，返回码：{result.returncode}")
                        if result.stdout:
                            print(f"标准输出：{result.stdout}")
                        if result.stderr:
                            print(f"错误输出：{result.stderr}")
                        return False
                    return True
                else:
                    subprocess.check_call(cmd, cwd=cwd, shell=shell)
                    return True
            except Exception as e:
                print(f"命令失败：{e}")
                return False

        created = run(["uv", "venv", "--python", "3.10.12"], cwd=str(target_dir))
        if not created:
            print("❌ 未能创建虚拟环境，请检查 Python 3.10.12 是否可用")

        # 计算 venv 内 Python 路径（不要求已激活）
        if os.name == "nt":
            venv_python = target_dir / ".venv" / "Scripts" / "python.exe"
            activate_hint = ".\\.venv\\Scripts\\Activate.ps1"
        else:
            venv_python = target_dir / ".venv" / "bin" / "python"
            activate_hint = "source .venv/bin/activate"

        # 安装依赖：激活虚拟环境后使用 uv pip 安装
        req_file = target_dir / "requirements.txt"
        if req_file.exists():
            # 根据操作系统选择激活脚本
            if os.name == "nt":  # Windows
                # 优先尝试使用批处理文件激活（更稳定）
                activate_bat = target_dir / ".venv" / "Scripts" / "activate.bat"
                if activate_bat.exists():
                    # 使用正确的引号转义
                    install_cmd = f"call \"{activate_bat}\" && uv pip install -r requirements.txt"
                    print(f"尝试使用 CMD 激活虚拟环境并安装依赖...")
                    # 直接使用字符串而不是列表，避免引号问题
                    installed = run(f'cmd /c "{install_cmd}"', cwd=str(target_dir), capture_output=True, shell=True)
                else:
                    # 如果批处理文件不存在，尝试 PowerShell（需要设置执行策略）
                    activate_script = target_dir / ".venv" / "Scripts" / "Activate.ps1"
                    if activate_script.exists():
                        # 使用 -ExecutionPolicy Bypass 绕过执行策略限制
                        install_cmd = f"& '{activate_script}'; uv pip install -r requirements.txt"
                        print(f"尝试使用 PowerShell 激活虚拟环境并安装依赖...")
                        installed = run(f'powershell -ExecutionPolicy Bypass -Command "{install_cmd}"',
                                        cwd=str(target_dir), capture_output=True, shell=True)
                    else:
                        print("未找到虚拟环境激活脚本，跳过依赖安装。")
                        installed = False
            else:  # Linux/macOS
                activate_script = target_dir / ".venv" / "bin" / "activate"
                if activate_script.exists():
                    # 在 bash 中激活虚拟环境并安装依赖
                    install_cmd = f"source {activate_script} && uv pip install -r requirements.txt"
                    print(f"尝试使用 bash 激活虚拟环境并安装依赖...")
                    installed = run(f'bash -c "{install_cmd}"', cwd=str(target_dir), capture_output=True, shell=True)
                else:
                    print("未找到虚拟环境激活脚本，跳过依赖安装。")
                    installed = False

            if not installed:
                print("依赖安装失败，可手动在激活环境后执行：")
                if os.name == "nt":
                    print(
                        "  Windows CMD: .venv\\Scripts\\activate.bat && uv pip install -r requirements.txt --index-strategy unsafe-best-match")
                    print(
                        "  Windows PowerShell: .venv\\Scripts\\Activate.ps1 && uv pip install -r requirements.txt --index-strategy unsafe-best-match")
                else:
                    print(
                        "  Linux/macOS: source .venv/bin/activate && uv pip install -r requirements.txt --index-strategy unsafe-best-match")
        else:
            print("未找到 requirements.txt，跳过依赖安装。")

        # 打印激活提示（区分平台）
        print("虚拟环境已创建在目标目录下的 .venv")
        if os.name == "nt":
            print(f"PowerShell 激活命令：{activate_hint}")
            print("若使用 CMD：.\\.venv\\Scripts\\activate.bat")
        else:
            print(f"bash/zsh 激活命令：{activate_hint}")

        print(f"已初始化脚本工程：{target_dir}")

    def new_case(self, args) -> None:
        """在 test_cases 目录下创建一个完整的示例用例文件"""
        # 检查是否在框架目录中
        if not self._check_framework_directory():
            return

        name = args.name
        tc_dir = Path("test_cases")
        tc_dir.mkdir(parents=True, exist_ok=True)
        file_path = tc_dir / f"{name}.py"
        if file_path.exists():
            print(f"文件已存在：{file_path}")
            return

        content = (
            "# -*- coding: utf-8 -*-\n"
            "\"\"\"\n"
            "测试用例示例：{cls}\n"
            "\n"
            "本文件展示了完整的测试用例编写模式，包括：\n"
            "- setup/teardown 前置后置操作\n"
            "- 性能监控和录制功能\n"
            "- 多种断言方法\n"
            "- 日志记录和截图\n"
            "- 错误处理策略\n"
            "\"\"\"\n"
            "import time\n"
            "from core import TestCase, StepStatus, FailureStrategy\n"
            "\n"
            "\n"
            "class {cls}(TestCase):\n"
            "    \"\"\"{cls} 测试用例类\"\"\"\n"
            "\n"
            "    def __init__(self, device):\n"
            "        super().__init__(\n"
            "            name='{cls}',\n"
            "            description='完整的测试用例示例，展示各种功能用法',\n"
            "            device=device\n"
            "        )\n"
            "        # 配置测试用例参数\n"
            "        self.failure_strategy = FailureStrategy.STOP_ON_FAILURE  # 失败时停止\n"
            "        self.timeout = 300  # 5分钟超时\n"
            "        self.retry_count = 1  # 失败时重试1次\n"
            "        self.screenshot_on_failure = True  # 失败时截图\n"
            "        self.screenshot_on_success = False  # 成功时不截图\n"
            "\n"
            "    def setup(self):\n"
            "        \"\"\"测试前置操作\"\"\"\n"
            "        self.log_info(\"开始执行测试前置操作\")\n"
            "        \n"
            "        # 启动性能监控（可选）\n"
            "        self.log_info(\"启动性能监控\")\n"
            "        if self.start_perf(sub_process_name='com.example.app', case_name=self.name):\n"
            "            self.log_info(\"性能监控启动成功\")\n"
            "        else:\n"
            "            self.log_warning(\"性能监控启动失败\")\n"
            "        \n"
            "        # 启动录制（可选）\n"
            "        self.log_info(\"启动屏幕录制\")\n"
            "        if self.start_record():\n"
            "            self.log_info(\"屏幕录制启动成功\")\n"
            "        else:\n"
            "            self.log_warning(\"屏幕录制启动失败\")\n"
            "        \n"
            "        # 启动logcat收集（可选）\n"
            "        self.log_info(\"启动logcat收集\")\n"
            "        logcat_task = self.start_logcat(clear=True)\n"
            "        if logcat_task:\n"
            "            self.log_info(\"logcat收集启动成功\")\n"
            "        else:\n"
            "            self.log_warning(\"logcat收集启动失败\")\n"
            "        \n"
            "        # 等待设备稳定\n"
            "        self.log_info(\"等待设备稳定...\")\n"
            "        time.sleep(2)\n"
            "\n"
            "    def teardown(self):\n"
            "        \"\"\"测试后置操作\"\"\"\n"
            "        self.log_info(\"开始执行测试后置操作\")\n"
            "        \n"
            "        # 停止性能监控\n"
            "        if hasattr(self, '_perf_task'):\n"
            "            self.log_info(\"停止性能监控\")\n"
            "            if self.stop_perf():\n"
            "                self.log_info(\"性能监控停止成功\")\n"
            "            else:\n"
            "                self.log_warning(\"性能监控停止失败\")\n"
            "        \n"
            "        # 停止录制\n"
            "        self.log_info(\"停止屏幕录制\")\n"
            "        if self.stop_record():\n"
            "            self.log_info(\"屏幕录制停止成功\")\n"
            "        else:\n"
            "            self.log_warning(\"屏幕录制停止失败\")\n"
            "        \n"
            "        # 清理临时数据（可选）\n"
            "        self.log_info(\"清理测试数据\")\n"
            "        # 这里可以添加清理逻辑，比如删除临时文件等\n"
            "\n"
            "    def run_test(self):\n"
            "        \"\"\"执行测试用例主逻辑\"\"\"\n"
            "        \n"
            "        # 步骤1：基础功能验证\n"
            "        self.start_step('基础功能验证', '验证基本断言功能')\n"
            "        \n"
            "        # 基础断言示例\n"
            "        self.assert_true('True应该为真', True)\n"
            "        self.assert_false('False应该为假', False)\n"
            "        self.assert_equal('数字相等验证', 1 + 1, 2)\n"
            "        self.assert_not_equal('数字不等验证', 1, 2)\n"
            "        self.assert_contains('字符串包含验证', 'Hello World', 'World')\n"
            "        self.assert_not_contains('字符串不包含验证', 'Hello', 'Python')\n"
            "        self.assert_none('None值验证', None)\n"
            "        self.assert_not_none('非None值验证', 'Hello')\n"
            "        self.assert_greater_than('大于比较', 10, 5)\n"
            "        self.assert_less_than('小于比较', 3, 7)\n"
            "        \n"
            "        # 记录日志\n"
            "        self.log_info(\"基础断言验证完成\")\n"
            "        \n"
            "        # 截图示例\n"
            "        screenshot_path = self.take_screenshot('basic_verification')\n"
            "        if screenshot_path:\n"
            "            self.log_info(f\"截图已保存: {{screenshot_path}}\")\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        # 步骤2：设备信息获取\n"
            "        self.start_step('设备信息获取', '获取并验证设备相关信息')\n"
            "        \n"
            "        # 获取设备信息\n"
            "        device_serial = self.get_device_serial()\n"
            "        package_name = self.get_package_name()\n"
            "        \n"
            "        self.log_info(f\"设备序列号: {{device_serial}}\")\n"
            "        self.log_info(f\"测试包名: {{package_name}}\")\n"
            "        \n"
            "        # 验证设备信息不为空\n"
            "        self.assert_not_none('设备序列号不应为空', device_serial)\n"
            "        \n"
            "        # 等待一段时间模拟测试操作\n"
            "        self.log_info(\"模拟测试操作，等待3秒...\")\n"
            "        time.sleep(3)\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        # 步骤3：异常处理示例\n"
            "        self.start_step('异常处理测试', '测试异常情况的处理')\n"
            "        \n"
            "        try:\n"
            "            # 模拟可能出错的操作\n"
            "            result = 10 / 2  # 正常操作\n"
            "            self.assert_equal('除法运算结果', result, 5)\n"
            "            \n"
            "            # 模拟异常情况（注释掉，避免真的出错）\n"
            "            # result = 10 / 0  # 这会引发异常\n"
            "            \n"
            "            self.log_info(\"异常处理测试完成\")\n"
            "            \n"
            "        except Exception as e:\n"
            "            self.log_error(f\"捕获到异常: {{e}}\")\n"
            "            # 根据失败策略，这里会抛出异常或继续执行\n"
            "            self.assert_true('异常处理验证', False)  # 这会触发失败策略\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        # 步骤4：性能数据记录\n"
            "        self.start_step('性能数据记录', '记录测试过程中的性能数据')\n"
            "        \n"
            "        # 记录自定义性能数据\n"
            "        performance_data = {{\n"
            "            'test_duration': 10.5,\n"
            "            'memory_usage': 128.5,\n"
            "            'cpu_usage': 15.2,\n"
            "            'custom_metric': 'test_value'\n"
            "        }}\n"
            "        \n"
            "        self.record_performance_data(performance_data)\n"
            "        self.log_info(\"性能数据记录完成\")\n"
            "        \n"
            "        # 最终截图\n"
            "        self.take_screenshot('test_completion')\n"
            "        \n"
            "        self.end_step(StepStatus.PASSED)\n"
            "        \n"
            "        self.log_info(\"测试用例执行完成\")\n"
        ).format(cls=name[:1].upper() + name[1:])

        file_path.write_text(content, encoding="utf-8")
        print(f"已创建完整示例用例：{file_path}")
        print("该示例包含：")
        print("- setup/teardown 前置后置操作")
        print("- 性能监控、录制、logcat收集")
        print("- 多种断言方法示例")
        print("- 日志记录和截图功能")
        print("- 异常处理策略")
        print("- 性能数据记录")

    def build_zip(self, args) -> None:
        """打包整个框架为 zip 文件"""
        # 检查是否在框架目录中
        if not self._check_framework_directory():
            return

        import zipfile
        from datetime import datetime

        # 生成输出文件名
        if args.output:
            output_file = args.output
            if not output_file.endswith('.zip'):
                output_file += '.zip'
        else:
            # 获取当前目录名作为框架名
            framework_name = Path.cwd().name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{framework_name}_{timestamp}.zip"

        # 需要排除的文件和目录
        exclude_patterns = [
            "__pycache__",
            ".venv",
            "*.pyc",
            "*.pyo",
            ".git",
            ".gitignore",
            "test_result/",
            "*.zip",
            "*.whl",
            "dist/",
            "build/",
            "*.egg-info/",
            "*.log",
            "*.tmp",
            ".DS_Store",
            "Thumbs.db",
        ]

        print(f"开始打包框架为：{output_file}")

        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # 遍历当前目录下的所有文件和目录
                for root, dirs, files in os.walk('.'):
                    # 过滤排除的目录
                    dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]

                    for file in files:
                        # 过滤排除的文件
                        if any(pattern in file for pattern in exclude_patterns):
                            continue

                        file_path = Path(root) / file
                        arcname = file_path.relative_to(Path.cwd())
                        zipf.write(file_path, arcname)
                        print(f"  ✓ 添加文件：{arcname}")

            # 获取文件大小
            file_size = Path(output_file).stat().st_size
            size_mb = file_size / (1024 * 1024)

            print(f"✅ 框架打包完成：{output_file}")
            print(f"   文件大小：{size_mb:.2f} MB")
            print(f"   包含内容：框架代码、测试用例、配置文件等")

        except Exception as e:
            print(f"❌ 打包失败：{e}")
            # 清理可能创建的不完整文件
            if Path(output_file).exists():
                Path(output_file).unlink()
                print(f"已清理不完整的文件：{output_file}")

    def clean(self, args) -> None:
        """清理构建产物和临时文件"""
        # 检查是否在框架目录中
        if not self._check_framework_directory():
            return

        print("开始清理构建产物和临时文件...")

        # 需要清理的目录和文件
        cleanup_items = [
            "dist/",
            "build/",
            "test_result/",
            "*.egg-info/",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.log",
            "*.zip",
        ]

        cleaned_count = 0

        # 清理目录
        for pattern in cleanup_items:
            if pattern.endswith('/'):
                # 目录模式
                dir_name = pattern[:-1]
                if Path(dir_name).exists() and Path(dir_name).is_dir():
                    try:
                        shutil.rmtree(dir_name, ignore_errors=True)
                        print(f"  ✓ 已删除目录：{dir_name}")
                        cleaned_count += 1
                    except Exception as e:
                        print(f"  ⚠ 删除目录失败：{dir_name} - {e}")
            else:
                # 文件模式
                for item in Path('.').glob(pattern):
                    if item.is_file():
                        try:
                            item.unlink()
                            print(f"  ✓ 已删除文件：{item}")
                            cleaned_count += 1
                        except Exception as e:
                            print(f"  ⚠ 删除文件失败：{item} - {e}")
                    elif item.is_dir():
                        try:
                            shutil.rmtree(item, ignore_errors=True)
                            print(f"  ✓ 已删除目录：{item}")
                            cleaned_count += 1
                        except Exception as e:
                            print(f"  ⚠ 删除目录失败：{item} - {e}")

        # 清理 test_cases 下的 __pycache__
        test_cases_dir = Path("test_cases")
        if test_cases_dir.exists():
            for pycache_dir in test_cases_dir.rglob("__pycache__"):
                try:
                    shutil.rmtree(pycache_dir, ignore_errors=True)
                    print(f"  ✓ 已删除：{pycache_dir}")
                    cleaned_count += 1
                except Exception as e:
                    print(f"  ⚠ 删除失败：{pycache_dir} - {e}")

        if cleaned_count > 0:
            print(f"✅ 清理完成，共清理了 {cleaned_count} 个项目")
        else:
            print("ℹ️ 没有找到需要清理的文件或目录")


def main() -> None:
    tool = CommandLineTool()
    args = tool.parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        tool.parser.print_help()


if __name__ == "__main__":
    main()
