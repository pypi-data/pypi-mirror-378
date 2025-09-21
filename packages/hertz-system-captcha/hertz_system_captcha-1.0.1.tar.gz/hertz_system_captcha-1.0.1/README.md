# Hertz Captcha

一个功能强大的Django验证码应用，提供简单易用的验证码生成、验证和刷新功能。

## 功能特性

- 🖼️ **验证码图片生成** - 支持自定义尺寸、颜色、字体
- 🔒 **安全性强** - 自动过滤易混淆字符，添加噪声干扰
- 🚀 **高性能** - 支持Redis缓存，提升响应速度
- ⚙️ **高度可配置** - 灵活的配置选项，适配不同需求
- 📱 **RESTful API** - 提供完整的API接口
- 🔄 **自动过期** - 验证码自动过期机制

## 安装

### 使用pip安装（推荐）

```bash
pip install hertz-captcha
```

### 手动安装

1. 下载源码
2. 进入项目目录
3. 运行安装命令：

```bash
python setup.py install
```

## 配置

### 1. 在Django项目中注册应用

在 `settings.py` 的 `INSTALLED_APPS` 中添加：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'hertz_captcha',
]
```

### 2. 配置URL路由

在主项目的 `urls.py` 中添加：

```python
from django.urls import include

urlpatterns = [
    # ... 其他URL配置
    path('captcha/', include('hertz_captcha.urls')),
]
```

### 3. 配置缓存（可选但推荐）

为了获得更好的性能，建议配置Redis缓存：

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 4. 验证码配置选项

在 `settings.py` 中可以配置以下选项：

```python
# 验证码长度（默认：4）
HERTZ_CAPTCHA_LENGTH = 4

# 验证码图片宽度（默认：120）
HERTZ_CAPTCHA_WIDTH = 120

# 验证码图片高度（默认：50）
HERTZ_CAPTCHA_HEIGHT = 50

# 验证码字体大小（默认：30）
HERTZ_CAPTCHA_FONT_SIZE = 30

# 验证码过期时间（秒，默认：300）
HERTZ_CAPTCHA_TIMEOUT = 300

# 背景颜色（默认：#ffffff）
HERTZ_CAPTCHA_BACKGROUND_COLOR = '#ffffff'

# 文字颜色（默认：#000000）
HERTZ_CAPTCHA_FOREGROUND_COLOR = '#000000'

# 噪声级别（默认：0.3）
HERTZ_CAPTCHA_NOISE_LEVEL = 0.3

# Redis键前缀（默认：hertz_captcha:）
HERTZ_CAPTCHA_REDIS_KEY_PREFIX = 'hertz_captcha:'
```

## API使用

### 生成验证码

```python
from hertz_captcha.captcha_generator import HertzCaptchaGenerator

generator = HertzCaptchaGenerator()
captcha_data = generator.generate_captcha()

# 返回数据格式：
{
    'captcha_id': 'uuid-string',
    'image_data': 'data:image/png;base64,base64-string',
    'expires_in': 300
}
```

### 验证验证码

```python
is_valid = generator.verify_captcha(captcha_id, user_input)
```

### 刷新验证码

```python
new_captcha_data = generator.refresh_captcha(old_captcha_id)
```

## REST API接口

### 生成验证码

```
GET /captcha/generate/
```

响应：
```json
{
    "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
    "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "expires_in": 300
}
```

### 验证验证码

```
POST /captcha/verify/
```

请求体：
```json
{
    "captcha_id": "123e4567-e89b-12d3-a456-426614174000",
    "code": "ABCD"
}
```

响应：
```json
{
    "valid": true,
    "message": "验证码验证成功"
}
```

### 刷新验证码

```
POST /captcha/refresh/
```

请求体：
```json
{
    "captcha_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

响应：
```json
{
    "captcha_id": "123e4567-e89b-12d3-a456-426614174001",
    "image_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "expires_in": 300
}
```

## 依赖要求

- Python >= 3.7
- Django >= 3.0
- Pillow >= 8.0.0
- redis >= 4.0.0 (可选，用于Redis缓存)

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 作者

Your Name <your.email@example.com>

## 致谢

感谢所有为这个项目做出贡献的开发者！
