from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter,Terminal256Formatter,BBCodeFormatter,RtfFormatter,LatexFormatter,SvgFormatter,NullFormatter

code = """
import numpy as np
import matplotlib.pyplot as plt

print(np.array([1,2,3]))
"""
# 自定义颜色样式
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Number, Operator, Punctuation, Literal, Whitespace, Error, Other, Text

class CustomStyle(Style):
    # 定义颜色样式
    styles = {
        Keyword: '#FF0000',  # 关键字为红色
        Name: '#00FF00',     # 名称为绿色
        Comment: '#0000FF',  # 注释为蓝色
        String: '#FF00FF',   # 字符串为紫色
        Number: '#00FFFF',   # 数字为青色
    }

# 使用自定义样式
print("使用自定义颜色样式:")
print(highlight(code, PythonLexer(), 
      Terminal256Formatter(style=CustomStyle)))

# 使用内置样式
print("\n使用内置样式:")
print(highlight(code, PythonLexer(),
      Terminal256Formatter(style='monokai')))

# 可以使用不同的格式化器:
# 1. Terminal格式化 - 终端彩色输出
print(highlight(code, PythonLexer(), Terminal256Formatter()))

# 2. BBCode格式化 - 论坛BBCode格式
print(highlight(code, PythonLexer(), BBCodeFormatter()))

# 3. RTF格式化 - 富文本格式
print(highlight(code, PythonLexer(), RtfFormatter()))

# 4. LaTeX格式化 - LaTeX文档格式
print(highlight(code, PythonLexer(), LatexFormatter()))

# 5. SVG格式化 - 矢量图形格式
print(highlight(code, PythonLexer(), SvgFormatter()))

# 6. 原始文本格式化 - 无格式纯文本
print(highlight(code, PythonLexer(), NullFormatter()))

# 默认HTML格式化
print(highlight(code, PythonLexer(), HtmlFormatter()))