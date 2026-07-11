# 交接文档 — ai-quant-turtle (TASK4 海龟交易法则)

## 项目背景

本项目是量化交易工作坊 TASK4 的完整实现，主题为"复刻传奇：海龟交易法则实战演练"。项目使用 Python 实现了经典的海龟交易策略（Turtle Trading Rules），包括唐奇安通道、ATR、止损、回测引擎和可视化分析。

数据沿用 TASK1-TASK3 使用的四只 A 股卫星通信产业链相关股票，确保分析方法的一致性和可比性。

## 当前完成状态

### 作业要求逐项检查

#### 1. 了解海龟策略，给出核心思想与关键优势
- 状态：✓ 已完成
- 完成情况：在 PDF 报告第一部分和 README.md 中有详细阐述
- 相关文件：generate_report.py (报告第一部分), README.md

#### 2. 解释唐奇安通道、ATR、止损条件等概念
- 状态：✓ 已完成
- 完成情况：在 PDF 报告第二部分中对三个核心概念有完整的定义、公式和解读
- 相关文件：generate_report.py (报告第二部分)

#### 3. Python 编程实现 (6个子任务)
- 状态：✓ 已完成
- 完成情况：
  - (1) 加载已存储的股价数据：turtle_strategy.py 中的 load_stock_data() 函数
  - (2) 计算高低价格通道：calc_donchian_channel() 支持自定义周期
  - (3) 计算 ATR：calc_atr() 使用 Wilder 递归平滑方法
  - (4) 计算买卖信号：generate_turtle_signals() 基于通道突破
  - (5) 绘制可视化图形：plot_turtle_strategy() 4面板图表 + plot_parameter_comparison() 对比图
  - (6) 模拟交易回测：backtest_turtle() 完整回测引擎
- 相关文件：turtle_strategy.py

#### 4. 参数调优与心得总结
- 状态：✓ 已完成
- 完成情况：测试了6组不同通道周期参数 + 4只股票对比，在 PDF 报告中有详细图表解读和场景分析
- 相关文件：turtle_strategy.py (参数扫描逻辑), generate_report.py (报告总结部分)

### 总体概览

| # | 要求 | 状态 |
|---|------|------|
| 1 | 海龟策略核心思想与优势 | ✓ |
| 2 | 核心概念解释 (通道/ATR/止损) | ✓ |
| 3.1 | 加载股价数据 | ✓ |
| 3.2 | 计算高低价格通道 | ✓ |
| 3.3 | 计算 ATR | ✓ |
| 3.4 | 计算买卖信号 | ✓ |
| 3.5 | 绘制可视化图形 | ✓ |
| 3.6 | 模拟交易回测 | ✓ |
| 4 | 参数调优与心得总结 | ✓ |

## 技术栈

- Python 3
- pandas, numpy, matplotlib, fpdf2
- 数据源：Tushare Pro API (A股日线数据, CSV格式)
- 分析标的：688418.SH (震有科技), 600118.SH (中国卫星), 601698.SH (中国卫通), 300045.SZ (华力创通)

## 新 session 需要做的

所有作业要求已完成。新 session 可以参考以下方向进行扩展：

1. 增加做空逻辑：当前仅支持做多，可扩展为双向交易
2. 多品种组合回测：实现多品种同时运行的组合回测引擎
3. 动态参数优化：使用滚动窗口进行样本外参数优化
4. 交易成本建模：加入更真实的滑点、冲击成本模型
5. 实时信号推送：将策略改造为实时监控和信号推送系统

## 已部署

- 仓库地址：https://github.com/Yuki0256/ai-quant-turtle
- Pages 地址：https://yuki0256.github.io/ai-quant-turtle/
