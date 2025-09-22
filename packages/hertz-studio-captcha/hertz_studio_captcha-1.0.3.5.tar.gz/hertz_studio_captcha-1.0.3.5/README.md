# Hertz System Captcha

一个功能强大的Django验证码应用，提供简单易用的验证码生成、验证和刷新功能。

## 功能特性

- 🖼️ **验证码图片生成** - 支持自定义尺寸、颜色、字体
- 🔒 **安全性强** - 自动过滤易混淆字符，添加噪声干扰
- 🚀 **高性能** - 支持Redis缓存，提升响应速度
- ⚙️ **高度可配置** - 灵活的配置选项，适配不同需求
- 📱 **RESTful API** - 提供完整的API接口
- 🔄 **自动过期** - 验证码自动过期机制
- 🎨 **美观界面** - 支持多种字体和颜色配置

## 安装

### 使用pip安装（推荐）

**注意：本软件需要机器码验证才能安装。**

#### 安装流程

```bash
pip install hertz-system-captcha
```

安装过程中会：
1. 自动获取您的机器码
2. 验证机器码是否已注册
3. 如果未注册，会提示您填写注册信息
4. 自动完成机器码注册

### 手动安装

1. 下载源码
2. 进入项目目录
3. 运行安装命令：

```bash
python setup.py install
```

### 机器码验证说明

本软件使用机器码验证系统，确保软件的正版使用：

- **机器码生成**：基于您的硬件信息（CPU、MAC地址、系统信息等）生成唯一机器码
- **服务器验证**：机器码需要先在服务器注册才能安装
- **自动注册**：首次安装时会自动引导您完成注册
- **本地缓存**：注册信息会保存在本地，避免重复注册

### 获取安装权限

如果遇到安装问题，请联系作者：
- **作者**：杨坤豪 (yang kunhao)
- **邮箱**：563161210@qq.com
- **项目地址**：http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django

## 配置

### 1. 在Django项目中注册应用

在 `settings.py` 的 `INSTALLED_APPS` 中添加：

```python
INSTALLED_APPS = [
    # ... 其他应用
    'hertz_system_captcha',
]
```

### 2. 配置URL路由

在主项目的 `urls.py` 中添加：

```python
from django.urls import include

urlpatterns = [
    # ... 其他URL配置
    path('captcha/', include('hertz_system_captcha.urls')),
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
from hertz_system_captcha.captcha_generator import HertzCaptchaGenerator

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

## 使用示例

### 前端集成示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>验证码示例</title>
</head>
<body>
    <div id="captcha-container">
        <img id="captcha-image" src="" alt="验证码">
        <input type="text" id="captcha-input" placeholder="请输入验证码">
        <button onclick="verifyCaptcha()">验证</button>
        <button onclick="refreshCaptcha()">刷新</button>
    </div>

    <script>
        let currentCaptchaId = null;

        // 生成验证码
        function generateCaptcha() {
            fetch('/captcha/generate/')
                .then(response => response.json())
                .then(data => {
                    currentCaptchaId = data.captcha_id;
                    document.getElementById('captcha-image').src = data.image_data;
                });
        }

        // 验证验证码
        function verifyCaptcha() {
            const userInput = document.getElementById('captcha-input').value;
            fetch('/captcha/verify/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    captcha_id: currentCaptchaId,
                    code: userInput
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                if (data.valid) {
                    // 验证成功，执行后续操作
                } else {
                    // 验证失败，刷新验证码
                    generateCaptcha();
                }
            });
        }

        // 刷新验证码
        function refreshCaptcha() {
            generateCaptcha();
        }

        // 页面加载时生成验证码
        window.onload = generateCaptcha;
    </script>
</body>
</html>
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

**杨坤豪** (yang kunhao)  
邮箱：563161210@qq.com  
项目地址：http://hzgit.hzsystems.cn/hertz_studio/hertz_server_django

## 致谢

感谢所有为这个项目做出贡献的开发者！

## 更新日志

### v1.0.2
- 优化验证码生成算法
- 改进Redis缓存机制
- 增强错误处理
- 完善文档说明

### v1.0.1
- 初始版本发布
- 基础验证码功能
- Redis缓存支持
- REST API接口
