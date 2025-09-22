#!/usr/bin/env python3

import time
import traceback
import random
from core.test_case import TestCase, StepStatus, FailureStrategy
from ubox_py_sdk import DriverType, OSType, DeviceButton, EventHandler, Device


class TestCase1(TestCase):
    """基本兼容性测试脚本demo

    测试内容：
    1) 应用冷启动兼容性测试
    2) 应用后台保持稳定性测试
    3) 应用热启动兼容性测试
    4) 应用卸载兼容性测试
    """

    def __init__(self, device: Device):
        # 设置用例名称与描述（会显示在报告中）
        super().__init__(
            name="终端兼容性基础兼容性测试",
            description="测试步骤/断言/logcat/录制等能力",
            device=device
        )
        # 初始化事件处理器（如需使用，可在用例内添加 watcher 等逻辑）
        self.event_handler = self.device.handler
        # 失败策略：失败是否继续执行。这里采用“遇错即停”，更贴近日常回归诉求
        # 如需收集全部失败可切换为 FailureStrategy.CONTINUE_ON_FAILURE
        self.failure_strategy = FailureStrategy.STOP_ON_FAILURE

    def setup(self) -> None:
        """测试前置操作
        - 仅做通用初始化类工作
        - 如需启动被测应用，可通过 get_package_name() 获取配置中的包名并启动
        """
        self.log_info("开始准备测试环境...")

        # 示例：如果配置了包名，则启动APP
        package_name = self.get_package_name()
        if package_name:
            self.start_step("启动应用", f"启动应用: {package_name}")
            success = self.device.start_app(package_name)
            self.assert_true("应用应成功启动", success)
            self.end_step(StepStatus.PASSED if success else StepStatus.FAILED)
        else:
            self.log_info("未配置应用包名，跳过应用启动")

        # 开始录制，录制文件路径会自动记录到测试结果中
        self.start_record()

        # 启动 logcat 采集（返回 LogcatTask，无需手动停止；只记录文件路径用于报告展示）
        self.start_logcat()

    def teardown(self) -> None:
        """测试后置操作
        - 手动停止录制
        - 可选择性地关闭应用、回到桌面
        """
        self.log_info("开始清理测试环境...")

        # 停止录制（录制停止后会在报告中展示录屏文件路径）
        self.stop_record()

        # 如果需要，可在此处停止被测应用并回到主界面
        package_name = self.get_package_name()
        if package_name:
            self.device.stop_app(package_name)
            self.log_info(f"应用已停止: {package_name}")
        self.device.press(DeviceButton.HOME)
        self.log_info("已返回主界面")

    def run_test(self) -> None:
        """执行应用安装、冷启动、后台保持、热启动、卸载测试"""
        package_name = self.get_package_name()
        if not package_name:
            self.log_error("未配置应用包名，无法执行测试")
            return

        # 应用冷启动测试
        self.start_step("应用冷启动测试", "首次启动应用")
        self.device.stop_app(package_name)  # 确保应用已停止
        launch_time = self.device.start_app(package_name)
        self.assert_true("应用应成功启动", launch_time > 0)
        self.log_info(f"冷启动耗时: {launch_time}ms")
        self.end_step(StepStatus.PASSED if launch_time > 0 else StepStatus.FAILED)

        time.sleep(10)

        # 应用后台保持测试
        self.start_step("应用后台保持测试", "将应用放入后台并保持")
        self.device.press(DeviceButton.HOME)
        time.sleep(60)  # 后台保持60秒
        cmd = f"dumpsys activity processes | grep '{package_name}'"
        result = self.device.cmd_adb(cmd, timeout=10)
        self.assert_equal("应用应仍在后台运行", result == package_name)
        self.end_step(StepStatus.PASSED)

        time.sleep(10)

        # 应用热启动测试
        self.start_step("应用热启动测试", "从后台恢复应用")
        launch_time = self.device.start_app(package_name)
        self.assert_true("应用应成功恢复", launch_time > 0)
        self.log_info(f"热启动耗时: {launch_time}ms")
        self.end_step(StepStatus.PASSED if launch_time > 0 else StepStatus.FAILED)

        time.sleep(10)

        # 应用卸载测试
        self.start_step("应用卸载测试", "卸载被测应用")
        uninstalled = self.device.uninstall_app(package_name)
        self.assert_true("应用应成功卸载", uninstalled)
        self.end_step(StepStatus.PASSED if uninstalled else StepStatus.FAILED)