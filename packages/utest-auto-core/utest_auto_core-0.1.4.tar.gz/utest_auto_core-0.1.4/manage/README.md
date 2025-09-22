utest-manage 管理工具

概述
- 提供脚手架与工程管理能力：`init`、`new-case`、`build`、`clean`。
- 与核心包解耦，作为独立可安装的 CLI 分发。

命令说明
- 查看帮助：
```bash
utest-manage --help
```

- 初始化仅脚本目录（依赖 utest-core，不复制 core 源码）：
```bash
utest-manage init .
utest-manage init ./my_tests --force
```

- 新建示例用例：
```bash
utest-manage new-case my_login_test
```

- 构建与清理：
```bash
utest-manage build
utest-manage clean
```

## 编译

```shell
uv build
```

## 发布包

```shell
uv publish --publish-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple
```

## 用户安装

```shell
uv tool install utest-auto-manage --index-url https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://mirrors.tencent.com/repository/pypi/tencent_pypi/simple
```