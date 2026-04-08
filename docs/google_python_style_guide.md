# Google Python 风格规范

> 来源: [Google 开源项目风格指南 (中文版)](https://zh-google-styleguide.readthedocs.io/en/latest/google-python-styleguide/python_style_rules.html)

---

## 分号

不要在行尾加分号, 也不要用分号将两条语句合并到一行.

## 行宽

最大行宽是 80 个字符.

例外:

1. 长的导入 (import) 语句.
2. 注释里的 URL、路径名以及长的标志 (flag).
3. 不便于换行、不包含空格、模块级的长字符串常量, 比如 URL 或路径名.
4. Pylint 禁用注释. (例如: `# pylint: disable=invalid-name`)

不要用反斜杠表示显式续行 (explicit line continuation).

应该利用 Python 的圆括号, 中括号和花括号的隐式续行 (implicit line joining). 如有需要, 你可以在表达式外围添加一对括号.

正确:

```python
foo_bar(self, width, height, color='黑', design=None, x='foo',
        emphasis=None, highlight=0)

if (width == 0 and height == 0 and
    color == '红' and emphasis == '加粗'):

(bridge_questions.clarification_on
 .average_airspeed_of.unladen_swallow) = '美国的还是欧洲的?'

with (
    very_long_first_expression_function() as spam,
    very_long_second_expression_function() as beans,
    third_thing() as eggs,
):
    place_order(eggs, beans, spam, beans)
```

错误:

```python
if width == 0 and height == 0 and \
    color == '红' and emphasis == '加粗':

bridge_questions.clarification_on \
    .average_airspeed_of.unladen_swallow = '美国的还是欧洲的?'

with very_long_first_expression_function() as spam, \
        very_long_second_expression_function() as beans, \
        third_thing() as eggs:
    place_order(eggs, beans, spam, beans)
```

如果字符串的字面量 (literal) 超过一行, 应该用圆括号实现隐式续行:

```python
x = ('这是一个很长很长很长很长很长很长'
     '很长很长很长很长很长的字符串')
```

最好在最外层的语法结构上分行. 如果你需要多次换行, 应该在同一层语法结构上换行.

正确:

```python
bridgekeeper.answer(
     name="亚瑟", quest=questlib.find(owner="亚瑟", perilous=True))

answer = (a_long_line().of_chained_methods()
          .that_eventually_provides().an_answer())

if (
    config is None
    or 'editor.language' not in config
    or config['editor.language'].use_spaces is False
):
    use_tabs()
```

错误:

```python
bridgekeeper.answer(name="亚瑟", quest=questlib.find(
    owner="亚瑟", perilous=True))

answer = a_long_line().of_chained_methods().that_eventually_provides(
    ).an_answer()

if (config is None or 'editor.language' not in config or config[
    'editor.language'].use_spaces is False):
    use_tabs()
```

必要时, 注释中的长 URL 可以独立成行.

正确:

```python
# 详情参见
# https://www.example.com/us/developer/documentation/api/content/v2.0/csv_file_name_extension_full_specification.html
```

错误:

```python
# 详情参见
# https://www.example.com/us/developer/documentation/api/content/\
# v2.0/csv_file_name_extension_full_specification.html
```

如果一行超过 80 个字符, 且 Black 或 Pyink 自动格式化工具无法继续缩减行宽, 则允许该行超过 80 个字符.

## 括号

使用括号时宁缺毋滥.

可以把元组 (tuple) 括起来, 但不强制. 不要在返回语句或条件语句中使用括号, 除非用于隐式续行或表示元组.

正确:

```python
if foo:
    bar()
while x:
    x = bar()
if x and y:
    bar()
if not x:
    bar()
onesie = (foo,)
return foo
return spam, beans
return (spam, beans)
for (x, y) in dict.items(): ...
```

错误:

```python
if (x):
    bar()
if not(x):
    bar()
return (foo)
```

## 缩进

用 4 个空格作为缩进.

不要使用制表符. 使用隐式续行时, 应该把括起来的元素垂直对齐(参见行宽章节的示例), 或者添加 4 个空格的悬挂缩进. 右括号可以置于表达式结尾或者另起一行. 另起一行时右括号应该和左括号所在的那一行缩进相同.

正确:

```python
# 与左括号对齐.
foo = long_function_name(var_one, var_two,
                         var_three, var_four)
meal = (spam,
        beans)

# 与字典的左括号对齐.
foo = {
    'long_dictionary_key': value1 +
                           value2,
    ...
}

# 4个空格的悬挂缩进; 首行没有元素
foo = long_function_name(
    var_one, var_two, var_three,
    var_four)
meal = (
    spam,
    beans)

# 右括号另起一行.
foo = long_function_name(
    var_one, var_two, var_three,
    var_four
)
meal = (
    spam,
    beans,
)

# 字典中的4空格悬挂缩进.
foo = {
    'long_dictionary_key':
        long_dictionary_value,
    ...
}
```

错误:

```python
# 首行不能有元素.
foo = long_function_name(var_one, var_two,
    var_three, var_four)

# 禁止2个空格的悬挂缩进.
foo = long_function_name(
  var_one, var_two, var_three,
  var_four)

# 字典没有悬挂缩进.
foo = {
    'long_dictionary_key':
    long_dictionary_value,
    ...
}
```

## 序列的尾部逗号

仅当 `]`, `)`, `}` 和最后一个元素不在同一行时, 推荐在序列尾部添加逗号. Python 自动格式化工具会把尾部的逗号视为一种格式提示.

## Shebang 行

大部分 `.py` 文件不必以 `#!` 开始. 可以根据 PEP-394, 在程序的主文件开头添加 `#!/usr/bin/env python3` (以支持 virtualenv) 或者 `#!/usr/bin/python3`.

内核会通过这行内容找到 Python 解释器, 但是 Python 解释器在导入模块时会忽略这行内容. 这行内容仅对需要直接运行的文件有效.

## 注释和文档字符串 (docstring)

模块、函数、方法的文档字符串和内部注释一定要采用正确的风格.

### 文档字符串

Python 的文档字符串用于注释代码. 文档字符串是包、模块、类或函数里作为第一个语句的字符串. 可以用对象的 `__doc__` 成员自动提取这些字符串, 并为 `pydoc` 所用. 文档字符串一定要用三重双引号 `"""` 的格式 (依据 PEP-257). 文档字符串应该是一行概述 (整行不超过 80 个字符), 以句号、问号或感叹号结尾. 如果要写更多注释 (推荐), 那么概述后面必须紧接着一个空行, 然后是剩下的内容, 缩进与文档字符串的第一行第一个引号对齐.

### 模块

每个文件应该包含一个许可协议模版. 文件的开头应该是文档字符串, 其中应该描述该模块内容和用法.

```python
"""模块或程序的一行概述, 以句号结尾.

留一个空行. 接下来应该写模块或程序的总体描述. 也可以选择简要描述导出的类和函数,
和/或描述使用示例.

经典的使用示例:

foo = ClassFoo()
bar = foo.FunctionBar()
"""
```

### 测试模块

测试文件不必包含模块级文档字符串. 只有在文档字符串可以提供额外信息时才需要写入文件.

不要使用不能提供额外信息的文档字符串.

错误:

```python
"""foo.bar 的测试."""
```

### 函数和方法

本节中的函数是指函数、方法、生成器 (generator) 和特性 (property).

满足下列任意特征的任何函数都必须有文档字符串:

1. 公开 API 的一部分
2. 长度过长
3. 逻辑不能一目了然

文档字符串应该提供充分的信息, 让调用者无需阅读函数的代码就能调用函数. 文档字符串应该描述函数的调用语法和语义信息, 而不应该描述具体的实现细节, 除非这些细节会影响函数的用法.

文档字符串可以是陈述句 (`"""Fetches rows from a Bigtable."""`) 或者祈使句 (`"""Fetch rows from a Bigtable."""`), 不过一个文件内的风格应当一致.

函数的部分特征应该在以下特殊小节中记录:

- **Args** (参数): 列出所有参数名. 参数名后面是一个冒号, 然后是描述. 如果代码没有类型注解, 则描述中应该说明所需的类型.
- **Returns** (返回): 描述返回值的类型和意义. 如果函数仅仅返回 `None`, 这一小节可以省略. 生成器应该用 "Yields:".
- **Raises** (抛出): 列出与接口相关的所有异常和异常描述.

```python
def fetch_smalltable_rows(
    table_handle: smalltable.Table,
    keys: Sequence[bytes | str],
    require_all_keys: bool = False,
) -> Mapping[bytes, tuple[str, ...]]:
    """从 Smalltable 获取数据行.

    从 table_handle 代表的 Table 实例中检索指定键值对应的行.

    参数:
        table_handle: 处于打开状态的 smalltable.Table 实例.
        keys: 一个字符串序列, 代表要获取的行的键值.
        require_all_keys: 如果为 True, 只返回那些所有键值都有对应数据的行.

    返回:
        一个字典, 把键值映射到行数据上.

    抛出:
        IOError: 访问 smalltable 时出现错误.
    """
```

### 类 (class)

类的定义下方应该有一个描述该类的文档字符串. 如果你的类包含公有属性, 应该在 `Attributes` (属性) 小节中记录这些属性, 格式与函数的 `Args` 小节类似.

```python
class SampleClass(object):
    """这里是类的概述.

    属性:
        likes_spam: 布尔值, 表示我们是否喜欢午餐肉.
        eggs: 用整数记录的下蛋的数量.
    """

    def __init__(self, likes_spam=False):
        """用某某某初始化 SampleClass."""
        self.likes_spam = likes_spam
        self.eggs = 0
```

类的文档字符串开头应该是一行概述, 描述类的实例所代表的事物.

### 块注释和行注释

应该在复杂的操作开始前写上若干行注释. 对于不是一目了然的代码, 应该在行尾添加注释.

```python
# 我们用加权的字典搜索, 寻找 i 在数组中的位置.
if i & (i-1) == 0:  # 如果 i 是 0 或者 2 的整数次幂, 则为真.
```

注释的井号和代码之间应有至少 2 个空格, 井号和注释之间应该至少有一个空格.

绝不要仅仅描述代码. 应该假设读代码的人比你更懂 Python, 只是不知道你的代码要做什么.

## 标点符号、拼写和语法

注意标点符号、拼写和语法. 文笔好的注释比差的注释更容易理解.

注释应该和记叙文一样可读, 使用恰当的大小写和标点. 一般而言, 完整的句子比残缺句更可读.

## 字符串

应该用 f-string、`%` 运算符或 `format` 方法来格式化字符串. 即使所有参数都是字符串, 也如此.

正确:

```python
x = f'名称: {name}; 分数: {n}'
x = '%s, %s!' % (imperative, expletive)
x = '{}, {}'.format(first, second)
x = a + b
```

错误:

```python
x = first + ', ' + second
x = '名称: ' + name + '; 分数: ' + str(n)
```

不要在循环中用 `+` 和 `+=` 操作符来堆积字符串. 作为替代方案, 你可以将每个子串加入列表, 然后在循环结束后用 `''.join` 拼接列表.

应该保持同一文件中字符串引号的一致性. 选择 `'` 或者 `"` 以后不要改变主意.

多行字符串推荐使用 `"""` 而非 `'''`.

### 日志

对于那些第一个参数是格式字符串的日志函数: 一定要用字符串字面量 (而非 f-string!) 作为第一个参数, 并用占位符的参数作为其他参数.

```python
logging.info('TensorFlow 的版本是: %s', tf.__version__)
```

### 错误信息

错误信息应该遵守以下三条规范:

1. 信息需要精确地匹配真正的错误条件.
2. 插入的片段一定要能清晰地分辨出来.
3. 要便于简单的自动化处理 (例如正则搜索).

```python
if not 0 <= p <= 1:
    raise ValueError(f'这不是概率值: {p!r}')
```

## 文件、套接字和类似的有状态资源

使用完文件和套接字以后, 显式地关闭它们.

推荐使用 `with` 语句管理文件和类似的资源:

```python
with open("hello.txt") as hello_file:
    for line in hello_file:
        print(line)
```

## TODO (待办) 注释

TODO 注释以 `TODO` 全部大写的词开头, 紧跟着是用括号括起来的上下文标识符 (最好是 bug 链接). TODO 后面应该解释待办的事情.

```python
# TODO(crbug.com/192795): 研究 cpufreq 的优化.
# TODO(你的用户名): 提交一个议题, 用 '*' 代表重复.
```

## 导入 (import) 语句的格式

导入语句应该各自独占一行. `typing` 和 `collections.abc` 的导入除外.

正确:

```python
from collections.abc import Mapping, Sequence
import os
import sys
from typing import Any, NewType
```

错误:

```python
import os, sys
```

导入语句必须在文件顶部, 位于模块的注释和文档字符串之后、全局变量和全局常量之前. 导入语句应该按照如下顺序分组:

1. `__future__` 导入
2. Python 标准库
3. 第三方模块和包
4. 代码仓库中的子包

在每个分组内部, 应该按照模块完整包路径的字典序排序, 忽略大小写.

## 语句

通常每个语句应该独占一行.

如果判断语句的主体与判断条件可以挤进一行, 你可以将它们放在同一行. 特别注意这不适用于 `try`/`except`. 只有在 `if` 语句没有对应的 `else` 时才适用.

正确:

```python
if foo: bar(foo)
```

错误:

```python
if foo: bar(foo)
else:   baz(foo)

try:               bar(foo)
except ValueError: baz(foo)
```

## 访问器 (getter) 和设置器 (setter)

在访问和设置变量值时, 如果访问器和设置器可以产生有意义的作用或效果, 则可以使用.

如果一对访问器和设置器仅仅用于读写一个内部属性, 你应该直接用公有属性取代它们. 如果设置操作会让部分状态无效化或引发重建, 则需要使用设置器.

## 命名

模块名: `module_name`; 包名: `package_name`; 类名: `ClassName`; 方法名: `method_name`; 异常名: `ExceptionName`; 函数名: `function_name`; 全局常量名: `GLOBAL_CONSTANT_NAME`; 全局变量名: `global_var_name`; 实例名: `instance_var_name`; 函数参数名: `function_parameter_name`; 局部变量名: `local_var_name`.

函数名、变量名和文件名应该是描述性的, 避免缩写.

### 需要避免的名称

1. 只有单个字符的名称, 除了计数器 (`i`, `j`, `k`, `v`), 异常 (`e`), 文件句柄 (`f`), 类型变量 (`_T`).
2. 包含连字符 (`-`) 的包名/模块名.
3. 首尾均为双下划线的名称 (Python 保留名称).
4. 包含冒犯性词语的名称.
5. 在不必要的情况下包含变量类型的名称 (例如 `id_to_name_dict`).

### 命名规范表

| 类型 | 公有 | 内部 |
| --- | --- | --- |
| 包 | `lower_with_under` | |
| 模块 | `lower_with_under` | `_lower_with_under` |
| 类 | `CapWords` | `_CapWords` |
| 异常 | `CapWords` | |
| 函数 | `lower_with_under()` | `_lower_with_under()` |
| 全局常量/类常量 | `CAPS_WITH_UNDER` | `_CAPS_WITH_UNDER` |
| 全局变量/类变量 | `lower_with_under` | `_lower_with_under` |
| 实例变量 | `lower_with_under` | `_lower_with_under` |
| 方法名 | `lower_with_under()` | `_lower_with_under()` |
| 函数参数/方法参数 | `lower_with_under` | |
| 局部变量 | `lower_with_under` | |

## 主程序

使用 Python 时, 提供给 `pydoc` 和单元测试的模块必须是可导入的. 如果一个文件是可执行文件, 该文件的主要功能应该位于 `main()` 函数中. 你的代码必须在执行主程序前检查 `if __name__ == '__main__'`.

```python
def main():
    ...

if __name__ == '__main__':
    main()
```

## 函数长度

函数应该小巧且专一.

若一个函数超过 40 行, 应该考虑在不破坏程序结构的前提下拆分这个函数.

## 类型注解 (type annotation)

### 通用规则

1. 熟读 PEP-484.
2. 仅在有额外类型信息时才需要注解方法中 `self` 或 `cls` 的类型.
3. 不需要注解 `__init__` 的返回值.
4. 对于不需要限制变量类型的情况, 使用 `Any`.
5. 无需注解模块中的所有函数, 但至少需要注解公开 API.

### 换行

尽量遵守缩进规则. 添加类型注解后, 很多函数签名会变成每行一个参数的形式.

```python
def my_method(
    self,
    first_var: int,
    second_var: Foo,
    third_var: Bar | None,
) -> int:
    ...
```

### 默认值

根据 PEP-008, 只有对于同时拥有类型注解和默认值的参数, `=` 的周围应该加空格.

正确:

```python
def func(a: int = 0) -> int:
    ...
```

错误:

```python
def func(a:int=0) -> int:
    ...
```

### NoneType

在类型注解中, `None` 是 `NoneType` 的别名. 如果一个变量可能为 `None`, 则必须声明这种情况.

正确:

```python
def modern_or_union(a: str | int | None, b: str | None = None) -> str:
    ...
```

错误:

```python
def implicit_optional(a: str = None) -> str:
    ...
```

### 类型别名

可以为复杂的类型声明一个别名. 别名的命名应该采用大驼峰. 若别名仅在当前模块使用, 应在名称前加 `_` 代表私有.

```python
from typing import TypeAlias

_LossAndGradient: TypeAlias = tuple[tf.Tensor, tf.Tensor]
ComplexTFMap: TypeAlias = Mapping[str, _LossAndGradient]
```

### 泛型 (generics)

在注解类型时, 尽量为泛型类型填入类型参数. 否则, 泛型参数默认为 `Any`.

正确:

```python
def get_names(employee_ids: Sequence[int]) -> Mapping[int, str]:
    ...
```

错误:

```python
def get_names(employee_ids: Sequence) -> Mapping:
    ...
```
