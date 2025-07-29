# 实验数据管理系统

## 项目概述
本项目是一个用于实验数据管理的系统，提供了前端表格交互与后端数据处理的完整解决方案。系统支持动态表格创建、编辑、数据导入导出等功能，适用于实验室数据记录、实验配置管理等场景。

## 核心功能
- 动态创建和编辑可交互表格
- 支持表格行/列的添加与删除
- 数据粘贴功能，支持从剪贴板导入数据
- 表格数据的JSON序列化与反序列化
- 实验数据的保存与加载
- 支持悬浮窗式表格展示
- 实验配置的前后端交互

## 技术栈
- 前端：JavaScript (ES6+)
- 后端：Python + Flask
- 数据格式：JSON

## 主要模块

### 前端模块 (table.js)

#### EditableCell 类
- 可编辑单元格的基础组件
- 支持内容编辑、额外信息存储
- 提供单元格内容获取与设置方法

```javascript
// 创建单元格示例
const cell = new EditableCell("初始内容", { row: 0, col: 0 }, "cell-0-0");
```

#### EditableTable 类
- 动态表格核心类，管理单元格集合
- 支持表格行/列的添加、删除
- 提供数据提取、表格构建等功能

```javascript
// 创建表格示例
const table = new EditableTable(3, 4, "my-table");
table.addRow(); // 添加一行
table.addColumn(); // 添加一列
const data = table.extractContents(); // 提取表格数据
```

#### 表格操作工具
- 按钮创建与事件绑定
- 悬浮窗功能
- 从JSON或二维数组构建表格

### 后端模块

#### trial.py
- 实验数据模型定义
- 提供实验数据的保存与加载方法
- 支持实验组合功能

```python
# 创建实验示例
stock = trial.create_stock(
    stock_name="样本A",
    substance_conc=0.1,
    total_amount=100
)
stock.save_to_txt("experiment1.json")  # 保存数据
```

#### interface.py
- Flask接口定义
- 处理前端请求，实现数据交互
- 实验配置的接收与处理

## 使用方法

### 前端表格创建
1. 实例化`EditableTable`类创建表格
2. 使用`addRow()`和`addColumn()`方法扩展表格
3. 通过`editCell()`方法修改单元格内容
4. 使用`extractContents()`获取表格数据

### 数据持久化
1. 前端通过`fetch` API将数据发送到后端
2. 后端使用`trial`类的`save_to_txt()`方法保存数据
3. 加载时使用`load_from_txt()`方法恢复数据

### 实验配置
1. 通过`/config_acceptor`接口提交配置
2. 后端根据配置类型和指令进行处理
3. 支持多种表格类型和操作指令

## 扩展建议
1. 增加数据验证功能，确保实验数据的有效性
2. 添加用户认证机制，实现多用户数据隔离
3. 扩展图表展示功能，直观展示实验结果
4. 增加数据版本控制，追踪实验数据的变更历史

## 注意事项
- 表格数据更新采用全量更新机制，大规模数据操作时需注意性能
- 粘贴数据时请确保数据格式与表格结构匹配
- 实验数据ID生成依赖表格rootId，请注意保持唯一性
