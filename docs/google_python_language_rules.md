# Google Python 语言规范

> 来源: [Google 开源项目风格指南 (中文版)](https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_language_rules.html)

---

## Lint

用 pylintrc 运行 pylint, 以检查你的代码.

pylint 是在 Python 代码中寻找 bug 和格式问题的工具. 一定要用 pylint 检查你的代码.

抑制不恰当的警告, 以免其他问题被警告淹没. 你可以用行注释来抑制警告:

```python
def do_PUT(self):  # WSGI 接口名, 所以 pylint: disable=invalid-name
    ...
```

如果有"参数未使用"的警告, 可以在函数体开头删除无用的变量, 并用注释说明:

```python
def viking_cafe_order(spam: str, beans: str, eggs: str | None = None) -> str:
    del beans, eggs  # 未被使用.
    return spam + spam + spam
```

## 导入

使用 `import` 语句时, 只导入包和模块, 而不单独导入函数或者类.

1. 用 `import x` 来导入包和模块.
2. 用 `from x import y`, 其中 x 是包前缀, y 是不带前缀的模块名.
3. 在以下情况使用 `from x import y as z`: 如果有两个模块都叫 `y`; 如果 `y` 和当前模块的某个全局名称冲突; 如果 `y` 是长度过长的名称.
4. 仅当缩写 `z` 是标准缩写时才能使用 `import y as z` (比如 `np` 代表 `numpy`).

例外: `typing`, `collections.abc`, `typing_extensions` 模块和 `six.moves` 中的重定向允许 `from x import y` 形式直接导入类/函数.

## 包

使用每个模块的完整路径名来导入模块.

正确:

```python
from absl import flags
from doctor.who import jodie
```

错误:

```python
import jodie  # 没有清晰地表达想要导入的模块
```

导入时禁止使用相对包名. 即使模块在同一个包中, 也要使用完整包名.

## 异常

允许使用异常, 但必须谨慎使用.

1. 优先使用合适的内置异常类. 比如, 用 `ValueError` 表示前置条件错误. 不要使用 `assert` 语句来验证公开 API 的参数值. 应该用 `assert` 来保证内部正确性.
2. 模块或包可以定义自己的异常类型, 必须继承已有的异常类. 异常类型名应该以 `Error` 为后缀.
3. 永远不要使用 `except:` 语句来捕获所有异常, 也不要捕获 `Exception` 或者 `StandardError`, 除非你想重新抛出或在隔离点记录并抑制异常.
4. 最小化 `try/except` 代码块中的代码量.
5. 用 `finally` 表示无论异常与否都应执行的代码, 常用于清理资源.

## 全局变量

避免全局变量.

在特殊情况下需要用到全局变量时, 应将全局变量声明为模块级变量或者类属性, 并在名称前加 `_` 以示为内部状态. 鼓励使用模块级常量, 常量名必须全部大写, 用下划线分隔单词.

```python
_MAX_HOLY_HANDGRENADE_COUNT = 3          # 内部常量
SIR_LANCELOTS_FAVORITE_COLOR = "blue"    # 公开API的常量
```

## 嵌套/局部/内部类和函数

可以用局部类和局部函数来捕获局部变量. 可以用内部类.

尽量避免使用嵌套函数和嵌套类, 除非需要捕获 `self` 和 `cls` 以外的局部变量. 不要仅仅为了隐藏一个函数而使用嵌套函数. 应将需要隐藏的函数定义在模块级别, 并给名称加上 `_` 前缀.

## 推导式和生成式

适用于简单情况.

每个部分不应超过一行: 映射表达式、for 语句和过滤表达式. 禁止多重 for 语句和多层过滤. 情况复杂时, 应该用循环.

正确:

```python
result = [mapping_expr for value in iterable if filter_expr]

result = [complicated_transform(x)
          for x in iterable if predicate(x)]

return {x: complicated_transform(x)
        for x in long_generator_function(parameter)
        if x is not None}

unique_names = {user.name for user in users if user is not None}
```

错误:

```python
result = [(x, y) for x in range(10) for y in range(5) if x * y > 10]

return ((x, y, z)
        for x in xrange(5)
        for y in xrange(5)
        if x != y
        for z in xrange(5)
        if y != z)
```

## 默认迭代器和操作符

只要可行, 就用列表、字典和文件等类型的默认迭代器和操作符.

正确:

```python
for key in adict: ...
if obj in alist: ...
for line in afile: ...
for k, v in adict.items(): ...
```

错误:

```python
for key in adict.keys(): ...
for line in afile.readlines(): ...
```

## 生成器

按需使用生成器.

生成器的文档字符串中应使用 "Yields:" 而不是 "Returns:". 如果生成器占用了大量资源, 一定要强制清理资源.

## Lambda 函数

适用于单行函数. 如果函数体超过 60-80 个字符, 最好还是定义为常规的嵌套函数.

对于乘法等常见操作, 应该用 `operator` 模块中的函数代替 lambda 函数. 例如, 推荐用 `operator.mul` 代替 `lambda x, y: x * y`.

## 条件表达式

适用于简单情况.

以下每部分均不得长于一行: 真值分支, if 部分和 else 部分. 情况复杂时应使用完整的 if 语句.

正确:

```python
one_line = 'yes' if predicate(value) else 'no'
slightly_split = ('yes' if predicate(value)
                  else 'no, nein, nyet')
```

错误:

```python
bad_line_breaking = ('yes' if predicate(value) else
                     'no')  # 换行位置错误
```

## 默认参数值

大部分情况下允许, 但有注意事项:

函数和方法的默认值不能是可变 (mutable) 对象.

正确:

```python
def foo(a, b=None):
    if b is None:
        b = []
def foo(a, b: Sequence = ()):  # 允许空元组, 因为元组是不可变的
```

错误:

```python
def foo(a, b=[]):
    ...
def foo(a, b=time.time()):  # 确定要用模块的导入时间吗???
    ...
def foo(a, b: Mapping = {}):  # 空字典是可变的
    ...
```

## 特性 (properties)

可以用特性来读取或设置涉及简单计算、逻辑的属性.

一个特性不能仅仅用于获取和设置一个内部属性 (不涉及计算时应该把该属性设为公有). 应该用 `@property` 装饰器来创建特性. 特性的继承机制难以理解, 不要用特性实现子类能覆写的计算功能.

## True/False 的求值

尽可能使用"隐式"假值.

注意事项:

1. 一定要用 `if foo is None:` (或者 `is not None`) 来检测 `None` 值.
2. 永远不要用 `==` 比较一个布尔值是否等于 `False`. 应该用 `if not x:`.
3. 多利用空序列是假值的特点. `if not seq:` 比 `if len(seq):` 更好.
4. 处理整数时, 显式比较整型值与 0 的关系 (`len()` 的返回值例外).

```python
# 正确
if not users:
    print('无用户')

if i % 10 == 0:
    self.handle_multiple_of_ten()

def f(x=None):
    if x is None:
        x = []

# 错误
if len(users) == 0:
    print('无用户')

if not i % 10:
    self.handle_multiple_of_ten()

def f(x=None):
    x = x or []
```

## 词法作用域 (Lexical Scoping)

可以使用.

嵌套的 Python 函数可以引用外层函数中定义的变量, 但是不能对这些变量赋值. 变量的绑定分析基于词法作用域.

注意: 如果在函数中对标识符赋值, Python 会将该标识符的所有引用变成局部变量, 即使读取语句写在赋值语句之前.

## 函数与方法装饰器

仅在有显著优势时, 审慎地使用装饰器.

- 避免使用 `staticmethod`, 除非为了兼容老代码库的 API. 应该把静态方法改写为模块级函数.
- 仅在以下情况可以使用 `classmethod`: 实现具名构造函数; 在类方法中修改必要的全局状态.
- 装饰器应该避免对外界的依赖 (文件, 套接字, 数据库连接等).

## 线程

不要依赖内置类型的原子性.

选择线程间的数据传递方式时, 应优先考虑 `queue` 模块的 `Queue` 数据类型. 如果不适用, 则使用 `threading` 模块及其提供的锁原语. 如果可行, 应该用条件变量和 `threading.Condition` 替代低级的锁.

## 威力过大的功能

避开这些功能.

诸如自定义元类 (metaclasses), 读取字节码 (bytecode), 动态继承, 对象基类重设, 导入技巧, 反射, 系统内部状态的修改, `__del__` 实现的自定义清理等等.

可以使用那些在内部利用了这些功能的标准模块和类, 比如 `abc.ABCMeta`, `dataclasses` 和 `enum`.

## 现代 Python: from \_\_future\_\_ imports

鼓励使用 `from __future__ import` 语句. 这样, 源代码从今天起就能使用更现代的 Python 语法. 当你不再需要支持老版本时, 请自行删除这些导入语句.

```python
from __future__ import generator_stop
```

除非你确定代码的运行环境已经足够现代, 否则不要删除 future 语句.

## 代码类型注释

可以根据 PEP-484 来对 Python3 代码进行注释, 并使用诸如 pytype 之类的类型检查工具来检查代码.

类型注释既可以写在源码里, 也可以写在 pyi 中. 推荐尽量写在源码里.

强烈推荐在更新代码时启用 Python 类型分析. 在添加或修改公开 API 时, 请添加类型注释.

```python
def func(a: int) -> list[int]:
    ...

a: SomeType = some_func()
```
