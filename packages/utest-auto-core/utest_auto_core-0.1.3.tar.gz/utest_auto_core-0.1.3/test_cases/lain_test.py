#!/usr/bin/env python3

import time
import traceback
import random
from core.test_case import TestCase, StepStatus, FailureStrategy
from ubox_py_sdk import DriverType, OSType, DeviceButton, EventHandler, Device


class TestCase1(TestCase):
    def __init__(self, device: Device):
        # 设置用例名称与描述（会显示在报告中）
        super().__init__(
            name="demo",
            description="演示步骤/断言/性能采集/logcat/录制等能力",
            device=device
        )
        # 初始化事件处理器（如需使用，可在用例内添加 watcher 等逻辑）
        self.event_handler = self.device.handler
        # 失败策略：失败是否继续执行。这里采用“遇错即停”，更贴近日常回归诉求
        # 如需收集全部失败可切换为 FailureStrategy.CONTINUE_ON_FAILURE
        self.failure_strategy = FailureStrategy.STOP_ON_FAILURE

    def run_test(self) -> None:
        self.device.screenshot("screenshot", "./", crop=(0.8, 0.9, 0.98, 0.99))
        # self.start_step("测试", "ceshi")
        # pos = self.device.find_cv(tpl="test_cases/20250919144138_screenshot_cropped.jpg", by=DriverType.CV, timeout=10)
        # self.log_info(pos)
        # res = self.device.click(loc="test_cases/20250919144138_screenshot_cropped.jpg", by=DriverType.CV, timeout=10)
        # # res = self.device.click_pos(pos)
        # self.assert_true("点击", res)
        # # self.device.screenshot(label="demo", img_path="./screenshots")
