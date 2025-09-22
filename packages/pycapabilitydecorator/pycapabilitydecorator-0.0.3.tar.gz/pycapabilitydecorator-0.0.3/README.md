
# PyCapabilityDecorator 说明文档
能力插件,将普通代码转换为能力插件

支持：
    1. 定义 capability 元数据，包括初始化参数描述 (init_params) 和语言类型 (language_type)。
    2. 注册顶级 CLI 命令（@option），支持可选的 alias，name 默认为函数名。
    3. 添加顶级 --capability 选项输出所有 capability 元数据。
    4. 添加顶级 init 命令执行初始化。
    5. init_params 元数据描述初始化参数。
    6. server(命令)      运行服务器 服务自动注册 pages 和 methods
        页面模板路径  assets/pages
        静态资源路径  assets/static

        访问页面:
            http://127.0.0.1:5000/capability/<>/pages/<>
        运行方法:
            http://127.0.0.1:5000/capability/<>/methods/<>



生命周期:
    1.register(命令)    注册 capability 元数据
    2.init(命令)        初始化
    3.start(命令)       启动能力
    4.stop(命令)        停止能力
    5.destroy(命令)     销毁能力


gitee:
https://gitee.com/iiixxxiii/py-capability-decorator.git





## 使用




### 安装
``` bash
pip install pycapabilitydecorator
```



### 示例

最简单的用法

```python
# simple.py
from pycapabilitydecorator  import capability

# ---- 最简单能力接入
@capability.option()
def function1():
    return {
        "code": 0,
        "message": "[function1]成功"
    }
```

启动

```bash
python simple.py  server
```

执行方法
参数m 或者 method

```bash
curl http://127.0.0.1:5000/methods/simple/function1
```

访问页面
```bash
curl http://127.0.0.1:5000/pages/simple/home.html
```

## 项目编译


```bash

# 构建
uv build



# 测试安装1
pip install dist/pycapabilitydecorator-0.0.1-py3-none-any.whl


# 测试安装2
pip install -e


# 运行示例文件

cd examples/simple

python capability_simple.py server


# 安装 twine
pip install twine

# 上传到 PyPI

python -m twine upload dist/*


pippy地址:
https://pypi.org/project/pycapabilitydecorator/

```

