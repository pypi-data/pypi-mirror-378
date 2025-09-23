# image2hex

image 转 hex，用于分析 image magic number

## 安装

推荐使用虚拟环境（macOS/Linux）：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

在项目根目录执行安装：

```bash
pip install -U .
```

或开发模式：

```bash
pip install -U -e .
```

安装完成后，命令行工具在当前虚拟环境下可用：

```bash
image2hex --help
```

## 使用

命令行：

```bash
image2hex --dry-run
```

JSON 子命令最简调用（只传测试者邮箱也可省略，使用默认 Base64 邮箱）：

```bash
image2hex json --dry-run
```

默认项说明：
- 省略 `endpoint` 时使用 `DEFAULT_ENDPOINT_B64`
- 省略 `--tester` 时使用 `DEFAULT_TESTER_B64`
- 省略内容相关参数时使用 `DEFAULT_B64`

## 依赖

- `requests`

## 许可

MIT
