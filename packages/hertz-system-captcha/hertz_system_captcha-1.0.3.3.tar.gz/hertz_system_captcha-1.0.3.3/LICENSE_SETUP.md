# Hertz System Captcha 激活码安装指南

## 概述

Hertz System Captcha 现在需要激活码才能安装。这确保了软件的正版使用和授权管理。

## 安装方式

### 方式一：使用环境变量（推荐）

```bash
# Windows
set HERTZ_CAPTCHA_LICENSE=HERTZ-CAPTCHA-2024-ABCD1234
pip install hertz-system-captcha

# Linux/Mac
export HERTZ_CAPTCHA_LICENSE=HERTZ-CAPTCHA-2024-ABCD1234
pip install hertz-system-captcha
```

### 方式二：交互式输入

```bash
pip install hertz-system-captcha
# 安装过程中会提示输入激活码
```

## 激活码获取

请联系作者获取激活码：
- **作者**：杨坤豪 (yang kunhao)
- **邮箱**：563161210@qq.com
- **项目地址**：http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django

## 激活码格式

激活码格式：`HERTZ-CAPTCHA-2024-XXXXXXXX-YYYYMMDD-XXXX`

示例：
- `HERTZ-CAPTCHA-2024-ABCD1234-20241231-EFGH`
- `HERTZ-CAPTCHA-2024-EFGH5678-20241231-IJKL`

## 激活码管理工具

### 生成激活码

```bash
python generate_license.py
```

功能：
1. 生成单个激活码
2. 批量生成激活码
3. 验证激活码有效性

### 验证激活码

```python
from license_validator import license_validator

# 验证激活码
is_valid, message = license_validator.verify_license("HERTZ-CAPTCHA-2024-ABCD1234")
print(f"验证结果: {is_valid}, 消息: {message}")
```

## 常见问题

### Q: 激活码无效怎么办？
A: 请检查激活码是否正确，或联系作者获取新的激活码。

### Q: 激活码过期了怎么办？
A: 请联系作者获取新的激活码。

### Q: 可以离线安装吗？
A: 可以，激活码验证支持离线模式，但建议在线验证以获得更好的安全性。

### Q: 如何批量部署？
A: 可以设置环境变量 `HERTZ_CAPTCHA_LICENSE` 来避免交互式输入。

## 技术实现

### 激活码验证流程

1. **环境变量检查**：首先检查 `HERTZ_CAPTCHA_LICENSE` 环境变量
2. **交互式输入**：如果环境变量不存在，提示用户输入
3. **在线验证**：尝试连接服务器验证激活码
4. **离线验证**：如果在线验证失败，使用本地验证
5. **过期检查**：检查激活码是否过期

### 安全特性

- **HMAC签名**：激活码包含HMAC签名，防止伪造
- **时间戳验证**：激活码包含过期时间
- **服务器验证**：支持在线验证，可以实时控制授权
- **离线备用**：网络不可用时支持离线验证

## 开发者说明

### 修改激活码列表

编辑 `setup.py` 文件中的 `valid_keys` 列表：

```python
valid_keys = [
    "HERTZ-CAPTCHA-2024-ABCD1234",
    "HERTZ-CAPTCHA-2024-EFGH5678", 
    # 添加更多激活码...
]
```

### 配置服务器验证

编辑 `license_validator.py` 文件：

```python
self.license_server = "http://your-server.com/api/license/verify"
```

### 自定义验证逻辑

继承 `LicenseValidator` 类并重写验证方法：

```python
class CustomLicenseValidator(LicenseValidator):
    def verify_license(self, license_key):
        # 自定义验证逻辑
        pass
```

## 许可证

本激活码系统遵循 MIT 许可证。
