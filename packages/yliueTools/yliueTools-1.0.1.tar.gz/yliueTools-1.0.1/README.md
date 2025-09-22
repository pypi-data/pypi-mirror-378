# yLIueTools
MxTools包含自己正在使用的一些小工具
### 当前版本: 1.0.1
### 当前更新时间: 2025.09.21
## yLIue_Debug包使用说明
### 注意！！！
Debug包会调用Color包的函数，Color的**颜色显示**在**不支持ANSI转义序列**的终端会出现**乱码**的情况
你可以通过关闭颜色来让其正常显示
```python
	debug = Debug("Test", _color=False)
```
### 初步使用
1.引入该包
```python
	from MxTools import Debug
```
2.定义一个Debug对象
```python
	# debug = Debug('project_name') 
	# project_name 为项目名称 type:str
	debug = Debug('Test')
```
3.使用Debug模块打印信息
```python
	debug.log('Hello World!')
	# 输出
	# [2025-09-21 16:01:47,299] ING Test.default: Hello World!
```
### 过滤器教程
 使用log打印时有3个参数
 分别是
 msg(打印信息)
 name(发出位置,默认为default)
 type(类型，默认为ING)
 我们可以使用过滤器来过滤它们
 ```python
	debug = Debug('Test',_filterType = 'ING', _filterName = 'default')
	# 筛选出类型为ING 发出位置为 default的打印消息
 ```
### 关闭Debug输出
  ```python
	debug = Debug('Test', False)
 ```
## yLIue_Color包使用说明
### 注意！！！
Color包的**颜色显示**在**不支持ANSI转义序列**的终端会出现**乱码**的情况
### 初步使用
 1.引入该包
 ```python
	from MxTools import Color
 ```
 2.输出紫色字体
 ```python
	 print(Color.purple('Hello World!'))
 ```
### API
- purple 紫色
- grey 灰色
- green 绿色
- red	红色
- blue	蓝色
- yellow 黄色
- cyan	青色

## Update log
`Ver1.0.1 2025.09.21` 第一次上传