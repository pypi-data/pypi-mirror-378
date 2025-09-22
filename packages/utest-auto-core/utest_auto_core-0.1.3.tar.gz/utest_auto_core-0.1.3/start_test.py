#!/usr/bin/env python3
"""
测试执行入口
"""
import os
import sys
import logging
import time
import traceback
from androguard.core.bytecodes import apk
from pathlib import Path
from ubox_py_sdk import EventHandler, OSType

# 添加框架路径
sys.path.insert(0, str(Path(__file__).parent))

from core.config_manager import ConfigManager
from core.test_runner import TestRunner
from core.utils.file_utils import make_dir, del_dir
from test_cases.internal.loader import create_test_collection

global g_log_file_dir, g_case_base_dir


# 延迟初始化的logger
class LazyLogger:
    """延迟初始化的logger类"""

    def __init__(self):
        self._logger = None

    def _get_logger(self):
        if self._logger is None:
            self._logger = logging.getLogger(__name__)
        return self._logger

    def info(self, msg, *args, **kwargs):
        self._get_logger().info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        self._get_logger().warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self._get_logger().error(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self._get_logger().debug(msg, *args, **kwargs)


# 创建全局logger实例
logger = LazyLogger()


# 工具函数：解析 app 名称/地址，判断是否需要安装
def parse_app_source(app_name: str) -> dict:
    """解析应用来源，判断是否为本地文件/包名

    Returns:
        dict: {
            'need_install': bool,
            'source_type': 'file'|'package',
            'package_name': str,          # 若能确定则填，否则空
            'file_path': str|None,        # 当为文件时
            'file_type': str|None,        # 文件类型：apk/ipa/hap
        }
    """
    result = {
        'need_install': False,
        'source_type': 'package',
        'package_name': '',
        'file_path': None,
        'file_type': None,
    }

    text = app_name.strip()

    # 文件路径或文件名判断（支持多种格式）
    file_extensions = ['.apk', '.ipa', '.hap']
    for ext in file_extensions:
        if text.lower().endswith(ext):
            result['file_type'] = ext[1:]  # 去掉点号

            # 绝对或相对路径存在
            i_test_app_path = os.path.join(os.path.dirname(os.getcwd()), text)
            if os.path.isabs(i_test_app_path) and os.path.exists(i_test_app_path):
                result['need_install'] = True
                result['source_type'] = 'file'
                result['file_path'] = i_test_app_path
                # 尝试解析包名
                result['package_name'] = extract_package_name(i_test_app_path, result['file_type'])
                return result
    # 兜底：当作包名
    result['need_install'] = False
    result['source_type'] = 'package'
    result['package_name'] = text
    return result


def extract_package_name(file_path: str, file_type: str) -> str:
    """从包文件中提取包名"""
    try:
        if file_type == 'apk':
            return extract_apk_package_name(file_path)
        elif file_type == 'ipa':
            return extract_ipa_package_name(file_path)
        elif file_type == 'hap':
            return extract_hap_package_name(file_path)
        else:
            logger.warning(f"不支持的文件类型: {file_type}")
            return ""
    except Exception as e:
        logger.warning(f"解析包名失败 {file_path}: {e}")
        return ""


def extract_apk_package_name(apk_path: str) -> str:
    """从APK文件中提取包名"""
    try:
        i_apk_info = apk.APK(apk_path)
        if i_apk_info is not None:
            i_pkg_name = i_apk_info.get_package()
            return i_pkg_name
    except Exception as e:
        logger.warning(f"aapt解析APK失败: {e}")
    return ""


def extract_ipa_package_name(ipa_path: str) -> str:
    """从IPA文件中提取包名"""
    try:
        import zipfile
        with zipfile.ZipFile(ipa_path, 'r') as ipa:
            # 查找Info.plist文件
            for file_info in ipa.filelist:
                if file_info.filename.endswith('Info.plist'):
                    plist_data = ipa.read(file_info.filename)
                    # 解析plist文件获取CFBundleIdentifier
                    import plistlib
                    plist = plistlib.loads(plist_data)
                    return plist.get('CFBundleIdentifier', '')
    except Exception as e:
        logger.warning(f"IPA包名解析失败: {e}")

    return ""


def extract_hap_package_name(hap_path: str) -> str:
    """从HAP文件中提取包名"""
    try:
        import zipfile
        with zipfile.ZipFile(hap_path, 'r') as hap:
            # 查找config.json文件
            for file_info in hap.filelist:
                if file_info.filename.endswith('config.json'):
                    config_data = hap.read(file_info.filename)
                    import json
                    config = json.loads(config_data.decode('utf-8'))
                    # 鸿蒙HAP的包名在config.json中
                    return config.get('app', {}).get('bundleName', '')
    except Exception as e:
        logger.warning(f"HAP包名解析失败: {e}")

    return ""


# 返回码定义（保持与旧版框架一致）
SUCCESS = 0
APP_CRASH_ANR_ERROR = 1
U2AT_RUNNER_ERROR = 2
INSTALL_ERROR = 3
BLACK_SCREEN_ERROR = 4
SCRIPT_ASSERT_ERROR = 5
DEVICE_OFFLINE = 6
U2AT_RUNNER_REBOOT = 7


def exit_result(code):
    """输出结果并退出"""
    if code == APP_CRASH_ANR_ERROR or code == SCRIPT_ASSERT_ERROR or code == U2AT_RUNNER_ERROR:
        result_json = [
            {"processName": "安装", "result": True},
            {"processName": "启动", "result": True},
            {"processName": "运行", "result": False},
            {"processName": "卸载", "result": True}
        ]
    elif code == INSTALL_ERROR:
        result_json = [
            {"processName": "安装", "result": False},
            {"processName": "启动", "result": False},
            {"processName": "运行", "result": False},
            {"processName": "卸载", "result": False}
        ]
    else:
        result_json = [
            {"processName": "安装", "result": True},
            {"processName": "启动", "result": True},
            {"processName": "运行", "result": True},
            {"processName": "卸载", "result": True}
        ]

    import json
    result_str = json.dumps(result_json, ensure_ascii=False)

    with open(os.path.join(g_log_file_dir, "deviceRunStep.json"), 'w', encoding='utf-8') as f:
        f.write(result_str)

    sys.exit(code)


def main():
    """主函数"""
    # 直接从配置文件读取参数
    global test_suite, g_log_file_dir, g_case_base_dir, i_os_type, i_job_id, i_auth_code, g_serial_num, i_app_name

    root_path = os.path.dirname(os.path.dirname(os.getcwd()))
    test_result_dir = os.path.join(root_path, 'test_result')
    log_base_dir = os.path.join(test_result_dir, 'log')
    case_base_dir = os.path.join(test_result_dir, 'case')
    # 创建基础目录结构
    del_dir(log_base_dir)
    del_dir(case_base_dir)
    make_dir(log_base_dir)
    make_dir(case_base_dir)
    g_log_file_dir = log_base_dir
    g_case_base_dir = case_base_dir
    # 使用基础目录作为日志目录（具体用例目录在加载测试用例后创建）

    log_file_path = os.path.join(log_base_dir, 'client_log.txt')
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger.info("从配置文件读取启动参数")

    # 配置文件路径
    config_file_path = os.path.join(os.path.dirname(__file__), 'config.yml')

    try:
        config_manager = ConfigManager(config_file_path)
        config = config_manager.load_config()

        # 验证任务配置完整性
        if not config_manager.validate_task_config():
            logger.error("任务配置验证失败")
            exit_result(U2AT_RUNNER_ERROR)

        i_job_id = config.task.job_id
        g_serial_num = config.task.serial_num
        i_os_type = config.task.os_type
        i_app_name = config.task.app_name
        i_auth_code = config.task.auth_code

    except Exception as e:
        logger.error(f"从配置文件读取参数失败: {e}")
        exit_result(U2AT_RUNNER_ERROR)

    logger.info(f'---UTEST测试--- job_id={i_job_id}, serial_num={g_serial_num}, '
                f'os_type={i_os_type}, auth_code={i_auth_code}, app_name={i_app_name}, test_result_path={test_result_dir}')
    try:
        # 确定平台类型
        platform_map = {
            "android": OSType.ANDROID,
            "ios": OSType.IOS,
            "hm": OSType.HM
        }
        platform = platform_map.get(i_os_type.lower(), OSType.ANDROID)

        # 从配置文件读取配置
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.yml')
        config_manager = ConfigManager(config_file_path)
        config = config_manager.load_config()
        config.device.udid = g_serial_num
        config.device.os_type = platform
        config.device.auth_code = i_auth_code
        # 解析 app 来源，确定是否需要安装
        app_info = parse_app_source(i_app_name)
        logger.info(f"应用来源解析: {app_info}")

        # 运行测试
        with TestRunner(config) as runner:
            # 设置测试上下文
            runner.test_context = {
                "package_name": app_info.get('package_name') or i_app_name,
                "job_id": i_job_id,
                "serial_num": g_serial_num,
                "need_install": app_info['need_install'],
                "app_source_type": app_info['source_type'],
                "package_file_path": app_info.get('file_path'),
                "file_type": app_info.get('file_type'),
                "raw_app_name": i_app_name,
                # 添加路径信息
                "test_result_dir": test_result_dir,
                "case_base_dir": case_base_dir,
                "log_base_dir": log_base_dir,
            }

            # 如需安装应用，尝试在运行前安装
            try:
                if runner.test_context.get('need_install') and runner.device:
                    package_path = runner.test_context.get('package_file_path')
                    file_type = runner.test_context.get('file_type', 'apk')
                    if package_path and os.path.exists(package_path):
                        install_pkg(runner.device, package_path, file_type)
                    else:
                        logger.error(f"应用包文件不存在: {package_path}")
                        exit_result(INSTALL_ERROR)
                else:
                    logger.info("无需安装应用包，按包名直接启动")
            except Exception as pre_e:
                logger.error(f"准备阶段异常: {pre_e}")
                logger.error(traceback.format_exc())
                exit_result(U2AT_RUNNER_ERROR)

            # 创建测试用例集合 - 自动加载test_cases目录下的所有测试用例
            try:
                # 从配置中获取指定的测试用例
                selected_tests = config.test.selected_tests
                if selected_tests and len(selected_tests) > 0:
                    logger.info(f"运行指定的测试用例: {selected_tests}")
                    test_suite = create_test_collection(selected_tests, device=runner.device)
                else:
                    logger.info("运行所有测试用例")
                    test_suite = create_test_collection(device=runner.device)
            except RuntimeError as e:
                logger.error(f"创建测试用例集合失败: {e}")
                exit_result(U2AT_RUNNER_ERROR)
            # 开启anr检测
            anr_start_success = False
            if platform in [OSType.ANDROID, OSType.HM]:
                # 防止上一次监测没有正常结束
                try:
                    runner.device.anr_stop()
                except Exception as e:
                    logger.warning("无需停止anr")
                anr_start_success = runner.device.anr_start(package_name=runner.test_context.get('package_name'))
            # 执行测试套件
            results = runner.run_test_suite(test_suite)
            # 结束anr检测
            if anr_start_success:
                anr_monitor_result = runner.device.anr_stop(g_log_file_dir)
                # 将ANR监控结果保存到runner的全局结果中
                if anr_monitor_result:
                    runner.set_global_monitor_result(anr_monitor_result)
            # 生成报告
            report_path = runner.generate_report()
            logger.info(f"测试报告生成: {report_path}")

            # 获取测试摘要
            summary = runner.get_test_summary()
            logger.info(f"测试摘要: {summary}")

            # 检查测试结果
            failed_tests = [r for r in results if r.status.value == "failed"]
            error_tests = [r for r in results if r.status.value == "error"]

            if error_tests:
                logger.error(f"测试错误: {len(error_tests)} 个测试用例出错")
                for test in error_tests:
                    logger.error(f"  - {test.test_name}: {test.error_message}")
                exit_result(U2AT_RUNNER_ERROR)
            elif failed_tests:
                logger.error(f"测试失败: {len(failed_tests)} 个测试用例失败")
                for test in failed_tests:
                    logger.error(f"  - {test.test_name}: {test.error_message}")
                exit_result(SCRIPT_ASSERT_ERROR)
            else:
                logger.info(f"测试成功: {len(results)} 个测试用例全部通过")
                exit_result(SUCCESS)

    except Exception as e:
        logger.error(f"测试执行异常: {e}")
        logger.error(traceback.format_exc())
        exit_result(U2AT_RUNNER_ERROR)


def handle_common_event(device, xml_element, smart_click):
    """处理通用事件的回调函数"""
    smart_click("已知悉该应用存在风险")
    time.sleep(2)
    smart_click("仍然继续")
    time.sleep(2)
    smart_click("授权本次安装")
    return True


def handle_vivo_event(device, xml_element, smart_click):
    """处理vivo手机事件的回调函数"""
    smart_click("已了解应用的风险检测")
    time.sleep(2)
    smart_click("继续安装")
    return True


def auto_input(device, xml_element, smart_click):
    """自动输入的回调函数"""
    print("Event occurred: auto_input")
    # 模拟输入密码
    device.input_text("mqq@2005")
    # 使用智能点击方法
    smart_click("安装")
    smart_click("继续")
    # 等待4秒
    import time
    time.sleep(4)
    # 点击指定坐标
    device.click_pos([0.521, 0.946])
    return True


def auto_press(device, xml_element, smart_click):
    """自动按键的回调函数"""
    print("Event occurred: auto_press")
    # 点击指定坐标
    device.click_pos([0.521, 0.946])
    return True


def install_pkg(device, package_path, file_type='apk'):
    """安装应用包（支持APK/IPA/HAP）"""
    try:
        device_info = device.device_info()
        if device_info:
            logger.info(f"设备型号: {device_info.get('model', 'Unknown')}")

        # 根据文件类型选择安装方法
        if file_type == 'apk':
            install_android_package(device, package_path)
        elif file_type == 'ipa':
            install_ios_package(device, package_path)
        elif file_type == 'hap':
            install_harmonyos_package(device, package_path)
        else:
            logger.error(f"不支持的文件类型: {file_type}")
            exit_result(INSTALL_ERROR)
        # 安装成功后截图：
        device.screenshot("install_res", g_case_base_dir)
    except Exception as ie:
        logger.error(f"安装失败: {ie}\n{traceback.format_exc()}")
        exit_result(INSTALL_ERROR)


def install_android_package(device, apk_path):
    """安装Android APK包"""
    try:
        device_info = device.device_info()
        event_handler: EventHandler = device.handler
        event_handler.reset()

        # 配置各种watcher（参考start_case.py的逻辑）
        event_handler.watcher("wsq1").with_match_mode("strict").when("已知悉该应用存在风险").call(handle_common_event)
        event_handler.watcher("wsq2").with_match_mode("strict").when("已了解应用的风险检测").call(handle_vivo_event)
        event_handler.watcher("wsq3").with_match_mode("strict").when(
            '//*[@resource-id="com.oplus.appdetail:id/et_login_passwd_edit"]').call(
            auto_input)
        event_handler.watcher("wsq4").with_match_mode("strict").when(
            '//*[@resource-id="com.coloros.safecenter:id/et_login_passwd_edit"]').call(
            auto_input)

        # 通用弹窗处理
        event_handler.watcher("始终允许").with_match_mode("strict").when("始终允许").click()
        event_handler.watcher("允许").with_match_mode("strict").when("允许").click()
        event_handler.watcher("允许").when("允许访问一次").click()
        event_handler.watcher("升级").with_match_mode("strict").when('//*[@content-desc="关闭弹窗"]').click()

        # OPPO手机继续安装
        event_handler.watcher("oppo安装").with_match_mode("strict").when(
            '//*[@resource-id="com.android.packageinstaller:id/confirm_bottom_button_layout"]').click()

        # 特殊处理
        if device_info and device_info.get("productName") in ["MT2110_CH", "RMX3357"]:
            event_handler.watcher("一加安装").with_match_mode("strict").when(
                '//*[@resource-id="com.android.packageinstaller:id/install_confirm_panel"]').call(auto_press)

        # 小米手机继续安装
        event_handler.watcher("继续安装").with_match_mode("strict").when("继续安装").click()
        event_handler.watcher("同意").with_match_mode("strict").when("同意").click()
        event_handler.watcher("同意并继续").with_match_mode("strict").when("同意并继续").click()

        # 微视关闭更新弹窗
        event_handler.watcher("微视更新弹窗").with_match_mode("strict").when(
            "//*[@resource-id='com.tencent.weishi:id/rfh']").click()
        # 微视青少年保护，腾讯视频
        event_handler.watcher("我知道了").with_match_mode("strict").when("我知道了").click()
        # 不升级软件
        event_handler.watcher("暂不").with_match_mode("strict").when("暂不").click()
        # 关闭一些提示页面
        event_handler.watcher("关闭").with_match_mode("strict").when("关闭").click()
        # 程序安装点击完成
        event_handler.watcher("完成").with_match_mode("strict").when("完成").click()
        # vivo手机安装程序点击"确定"
        event_handler.watcher("确定").with_match_mode("strict").when("确定").click()
        event_handler.watcher("稍后").with_match_mode("strict").when("稍后").click()
        event_handler.watcher("安装").with_match_mode("strict").when("安装").click()
        event_handler.watcher("仍然继续").with_match_mode("strict").when("仍然继续").click()
        event_handler.watcher("授权本次安装").with_match_mode("strict").when("授权本次安装").click()

        # 开始后台监控
        event_handler.start(2.0)
        logger.info(f"开始安装APK: {apk_path}")

        # 安装APK
        device.local_install_app(apk_path)
        # 停止监控
        event_handler.stop()
        logger.info("APK安装完成")

    except Exception as e:
        logger.error(f"Android包安装失败: {e}")
        raise


def install_ios_package(device, ipa_path):
    """安装iOS IPA包"""
    try:
        logger.info(f"开始安装IPA: {ipa_path}")

        # iOS安装通常需要开发者证书和描述文件
        # 这里使用设备提供的安装方法
        device.install_app(ipa_path)
        logger.info("IPA安装完成")
    except Exception as e:
        logger.error(f"iOS包安装失败: {e}")
        raise


def install_harmonyos_package(device, hap_path):
    """安装鸿蒙HAP包"""
    try:
        logger.info(f"开始安装HAP: {hap_path}")

        # 鸿蒙HAP包安装
        device.install_app(hap_path)
        logger.info("HAP安装完成")

    except Exception as e:
        logger.error(f"鸿蒙包安装失败: {e}")
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.error(f"main Exception: {e}\n{traceback.format_exc()}")
        exit_result(U2AT_RUNNER_ERROR)
