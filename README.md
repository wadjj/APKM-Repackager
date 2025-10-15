# APKM Repackager

macOS 图形界面应用，用于将 APKMirror 等渠道提供的 `.apkm` 包解包、筛选指定的 ABI / DPI / 语言切片后重新合成为单一 APK，并可通过网络 `adb` 直接安装到安卓电视等设备。

## 功能概览

- 拖拽 `.apkm` 文件到窗口即可开始处理。
- 预设 ABI、语言以及最大 DPI 限制，可随时调整并保存，下次启动自动记忆。
- 自动生成调试 keystore，调用 `apksigner` 进行签名，输出可直接安装的 APK。
- 记录常用的 `adb` 目标（如 `192.168.1.123:5555`），一键重新连接并安装。
- 支持直接调用 `adb install -r` 进行远程安装。

## 开发环境

- macOS 13+
- Python 3.10+
- 安装 [Android Platform Tools](https://developer.android.com/tools/releases/platform-tools)（需要 `adb` 和 `apksigner`）。
- 安装 JDK（提供 `keytool` 生成调试 keystore）。

推荐使用 `pipx` 或虚拟环境安装：

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

运行应用：

```bash
apkm-repackager
```

若需打包为 `.app`，可结合 `pyinstaller` 等工具：

```bash
pip install pyinstaller
pyinstaller --windowed --name "APKM Repackager" apkm_repackager/app.py
```

生成的配置文件位于 `~/Library/Application Support/APKM Repackager/`，包括：

- `config.json`：存储 ABI、语言、DPI、签名配置及最近的 `adb` 目标。
- `adb_history.json`：记录下拉框可选的历史 IP:端口。

## 使用说明

1. 首次运行时，依次设置想要保留的 ABI、语言及最大 DPI，必要时可以填写自定义的 `apksigner` 路径或 keystore。
2. 将 `.apkm` 文件拖入顶部区域，日志窗口会提示解析情况。
3. 点击“重新打包”生成单一 APK，或直接点击“打包并安装”在生成后立即推送到电视。
4. 安装成功后会在日志中显示 `adb` 输出信息。

> **提示**：
> - 如果系统未安装 JDK 或 Android Platform Tools，签名或安装步骤会提示错误并停止，按提示安装后重试即可。
> - 生成的 APK 默认保存在原 `.apkm` 同目录，文件名附加 `_filtered.apk` 后缀。

## 目录结构

```
apkm_repackager/
├── __init__.py
├── app.py            # PySide6 界面与交互逻辑
├── config.py         # 偏好设置的读写与持久化
├── repackager.py     # APKM 解包、合并、签名及 ADB 安装工具
└── split_filters.py  # 解析、筛选各类 split APK 的工具函数
pyproject.toml        # 项目配置
```

## 已知限制

- `.apkm` 中若包含复杂的资源拆分策略（例如多维度 qualifiers），目前按文件名解析，可能需要根据实际情况扩展 `split_filters.py` 中的规则。
- 重新合成 APK 过程中未执行 `zipalign`，但在大多数设备上不影响安装。如需可在签名前自行调用。
