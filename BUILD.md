# 构建 APKM Repackager macOS 应用

本文档说明如何将 Python 应用编译成独立的 macOS .app 文件。

## 前提条件

在构建之前，确保已安装：

1. **macOS 10.14 或更高版本**
2. **Python 3.9 或更高版本**
   ```bash
   python3 --version
   ```
3. **Xcode Command Line Tools**
   ```bash
   xcode-select --install
   ```

## 方法 1: 使用构建脚本（推荐）

最简单的方法是使用提供的构建脚本：

```bash
./build_app.sh
```

脚本会自动：
- 安装所有依赖
- 清理之前的构建
- 构建 .app 文件
- 显示构建结果

构建完成后，应用位于：`dist/APKM Repackager.app`

## 方法 2: 手动构建

### 步骤 1: 安装依赖

```bash
pip3 install -r requirements.txt
```

这会安装：
- PyQt6 (GUI 框架)
- pyaxmlparser (APK 分析)
- py2app (macOS 打包工具)

### 步骤 2: 清理之前的构建（可选）

```bash
rm -rf build dist
```

### 步骤 3: 构建应用

```bash
python3 setup.py py2app
```

构建过程需要几分钟。完成后会看到：
```
creating dist/APKM Repackager.app
```

### 步骤 4: 运行应用

```bash
open "dist/APKM Repackager.app"
```

## 构建选项

### 开发模式（更快的构建）

开发模式不会打包所有依赖，构建更快，但需要 Python 环境：

```bash
python3 setup.py py2app -A
```

### 发布模式（独立应用）

默认的构建模式会创建完全独立的应用：

```bash
python3 setup.py py2app
```

## 创建 DMG 安装包

构建成功后，可以创建 DMG 文件用于分发：

```bash
hdiutil create -volname "APKM Repackager" \
    -srcfolder "dist/APKM Repackager.app" \
    -ov -format UDZO \
    APKM-Repackager.dmg
```

## 常见问题

### 问题 1: "No module named PyQt6"

**解决方案：**
```bash
pip3 install PyQt6
```

### 问题 2: py2app 构建失败

**解决方案：**
确保使用最新版本的 py2app：
```bash
pip3 install --upgrade py2app
```

### 问题 3: 应用无法打开（"已损坏"）

这是因为应用未签名。可以临时允许运行：
```bash
xattr -cr "dist/APKM Repackager.app"
```

或者在"系统偏好设置 > 安全性与隐私"中点击"仍要打开"。

### 问题 4: "Permission denied" 错误

给构建脚本添加执行权限：
```bash
chmod +x build_app.sh
```

## 应用签名（可选）

要正式分发应用，需要 Apple Developer 账户进行代码签名：

```bash
codesign --deep --force --sign "Developer ID Application: Your Name" \
    "dist/APKM Repackager.app"
```

然后进行公证（notarization）：

```bash
xcrun notarytool submit APKM-Repackager.dmg \
    --apple-id "your@email.com" \
    --password "app-specific-password" \
    --team-id "YOUR_TEAM_ID" \
    --wait
```

## 测试构建的应用

构建完成后，测试以下功能：

1. ✅ 应用能正常启动
2. ✅ 拖放 APKM 文件工作正常
3. ✅ 配置管理功能正常
4. ✅ 能成功转换 APKM 到 APK
5. ✅ 签名功能正常工作

## 目录结构

构建完成后的目录结构：

```
APKM-Repackager/
├── build/              # 临时构建文件
├── dist/               # 构建输出
│   └── APKM Repackager.app  # 最终应用
├── setup.py           # py2app 配置
└── build_app.sh       # 构建脚本
```

## 应用大小

预期的应用大小：
- 开发模式：~10 MB
- 发布模式：~80-100 MB（包含 Python 运行时和所有依赖）

## 分发

构建的 .app 文件可以：

1. **直接分享**：压缩成 ZIP 文件
   ```bash
   ditto -c -k --sequesterRsrc --keepParent \
       "dist/APKM Repackager.app" \
       APKM-Repackager.zip
   ```

2. **创建 DMG**：使用上面提到的 hdiutil 命令

3. **App Store**：需要完整的签名和公证流程

## 更新应用

修改代码后重新构建：

```bash
rm -rf build dist
./build_app.sh
```

## 调试

如果应用运行有问题，可以从终端运行查看日志：

```bash
"dist/APKM Repackager.app/Contents/MacOS/APKM Repackager"
```

这会在终端显示所有错误信息。

## 相关资源

- [py2app 文档](https://py2app.readthedocs.io/)
- [PyQt6 文档](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [macOS 代码签名指南](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)
