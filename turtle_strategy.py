#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海龟交易法则策略 — 完整实现 (Turtle Trading Strategy)

核心组件:
  1. 唐奇安通道 (Donchian Channel) — 入场/退出信号
  2. 平均真实波幅 (ATR) — 波动率测量与仓位管理
  3. 交易信号生成 — 突破入场 / 跌破退出
  4. 回测引擎 — 模拟交易与绩效评估
  5. 可视化 — 多面板图表输出

海龟交易法则由 Richard Dennis 和 William Eckhardt 在 1980 年代创立，
是量化交易历史上最具影响力的趋势跟踪策略之一。

作者: 量化交易工作坊 TASK4
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

warnings.filterwarnings('ignore')

# ============================================================
# 全局配置
# ============================================================

def setup_chinese_font():
    """自动检测并配置中文字体"""
    font_candidates = {
        'Windows': ['SimHei', 'Microsoft YaHei', 'FangSong', 'KaiTi'],
        'Darwin': ['Arial Unicode MS', 'STHeiti', 'Heiti SC', 'PingFang SC'],
        'Linux': ['WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'WenQuanYi Zen Hei'],
    }
    import platform
    candidates = font_candidates.get(platform.system(), [])
    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams['font.sans-serif'] = [font]
            break
    plt.rcParams['axes.unicode_minus'] = False

setup_chinese_font()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
IMAGE_DIR = os.path.join(BASE_DIR, 'images')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')

for d in [DATA_DIR, IMAGE_DIR, REPORT_DIR]:
    os.makedirs(d, exist_ok=True)

# ============================================================
# 海龟策略参数 (经典设定)
# ============================================================
DEFAULT_ENTRY_PERIOD = 20    # 入场通道周期 (唐奇安通道上轨)
DEFAULT_EXIT_PERIOD = 10     # 退出通道周期 (唐奇安通道下轨)
DEFAULT_ATR_PERIOD = 20      # ATR 计算周期
DEFAULT_STOP_MULTIPLE = 2.0  # 止损倍数 (ATR)
DEFAULT_RISK_FRACTION = 0.01 # 单笔风险占账户比例 (1%)

DEFAULT_STOCK = '688418.SH'  # 震有科技

# 股票名称映射
STOCK_NAMES = {
    '688418.SH': '震有科技',
    '600118.SH': '中国卫星',
    '601698.SH': '中国卫通',
    '300045.SZ': '华力创通',
}

# ============================================================
# 1. 数据加载
# ============================================================

def load_stock_data(ts_code: str = DEFAULT_STOCK) -> pd.DataFrame:
    """
    从 CSV 文件加载股票日线数据

    参数:
        ts_code: 股票代码, 如 '688418.SH'

    返回:
        DataFrame, 包含日期和 OHLCV 数据, 按日期升序排列
    """
    filename = ts_code.replace('.', '_') + '_daily.csv'
    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        raise FileNotFoundError(f'数据文件不存在: {filepath}')

    df = pd.read_csv(filepath, encoding='utf-8-sig')
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='mixed')
    df.sort_values('trade_date', inplace=True)
    df.reset_index(drop=True, inplace=True)

    for col in ['open', 'high', 'low', 'close', 'vol', 'amount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


def list_available_stocks() -> list:
    """列出 data 目录下所有可用的股票代码"""
    stocks = []
    for f in os.listdir(DATA_DIR):
        if f.endswith('_daily.csv'):
            parts = f.replace('_daily.csv', '').split('_')
            if len(parts) >= 2:
                stocks.append(parts[0] + '.' + parts[1])
    return stocks


# ============================================================
# 2. 唐奇安通道 (Donchian Channel)
# ============================================================

def calc_donchian_channel(df: pd.DataFrame, period: int,
                          shift: int = 1) -> pd.DataFrame:
    """
    计算唐奇安通道 (Donchian Channel)

    唐奇安通道由 Richard Donchian 发明, 是海龟策略的核心指标:
    - 上轨 (Upper Band): 过去 N 日的最高价
    - 下轨 (Lower Band): 过去 N 日的最低价

    海龟策略使用两条通道:
    - 入场通道 (系统一): 20 日突破 → 做多信号
    - 退出通道 (系统二): 10 日跌破 → 平仓信号

    参数:
        df: 包含 'high', 'low' 列的 DataFrame
        period: 通道周期 (经典: 20 入场, 10 退出)
        shift: 偏移量 (1 表示使用前一日数据, 避免未来函数)

    返回:
        新增 'donchian_upper', 'donchian_lower' 列的 DataFrame
    """
    result = df.copy()
    result['donchian_upper'] = df['high'].rolling(window=period).max().shift(shift)
    result['donchian_lower'] = df['low'].rolling(window=period).min().shift(shift)
    return result


# ============================================================
# 3. 平均真实波幅 (Average True Range, ATR)
# ============================================================

def calc_true_range(df: pd.DataFrame) -> pd.Series:
    """
    计算真实波幅 (True Range, TR)

    TR = max(
        |High - Low|,           # 当日振幅
        |High - Prev Close|,    # 跳空高开
        |Low - Prev Close|      # 跳空低开
    )

    参数:
        df: 包含 'high', 'low', 'close' 列的 DataFrame

    返回:
        True Range 序列
    """
    prev_close = df['close'].shift(1)
    tr1 = df['high'] - df['low']
    tr2 = (df['high'] - prev_close).abs()
    tr3 = (df['low'] - prev_close).abs()
    return pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)


def calc_atr(df: pd.DataFrame, period: int = DEFAULT_ATR_PERIOD,
             shift: int = 1) -> pd.Series:
    """
    计算平均真实波幅 (Average True Range, ATR)

    使用 Wilder 平滑方法 (指数加权):
    - 首个 ATR = 前 N 期 TR 的简单平均
    - 后续 ATR = (前一ATR × (N-1) + 当期TR) / N

    海龟策略中 ATR 的核心作用:
    1. 仓位规模计算: 根据 ATR 确定每单位交易量
    2. 止损设置: 止损价 = 入场价 - N × ATR
    3. 加仓间距: 每 0.5 ATR 移动一个单位

    参数:
        df: 包含 'high', 'low', 'close' 列的 DataFrame
        period: ATR 计算周期 (经典: 20)
        shift: 偏移量

    返回:
        ATR 序列
    """
    tr = calc_true_range(df)
    atr = pd.Series(np.nan, index=df.index, dtype=float)

    if len(df) < period:
        return atr

    # Wilder 初始值: 前 N 期 TR 的简单平均
    atr.iloc[period - 1] = tr.iloc[:period].mean()

    # Wilder 递归平滑
    for i in range(period, len(df)):
        atr.iloc[i] = (atr.iloc[i - 1] * (period - 1) + tr.iloc[i]) / period

    return atr.shift(shift)


# ============================================================
# 4. 交易信号生成
# ============================================================

@dataclass
class Signal:
    """交易信号常量"""
    BUY: int = 1
    SELL: int = -1
    HOLD: int = 0


def generate_turtle_signals(df: pd.DataFrame,
                            entry_period: int = DEFAULT_ENTRY_PERIOD,
                            exit_period: int = DEFAULT_EXIT_PERIOD,
                            atr_period: int = DEFAULT_ATR_PERIOD) -> pd.DataFrame:
    """
    生成海龟交易信号

    信号逻辑:
    - 买入信号 (系统一入场):
      当日收盘价 > 过去 20 日最高价 (唐奇安通道上轨) → 突破买入
    - 卖出信号 (系统二退出):
      当日收盘价 < 过去 10 日最低价 (唐奇安通道下轨) → 跌破卖出

    设计思想:
    - 入场: "追涨" — 价格创新高说明上升趋势确立
    - 退出: "杀跌" — 价格创新低说明上升趋势可能终结
    - 核心: 让利润奔跑, 截断亏损 (Cut losses short, let profits run)

    参数:
        df: 行情数据
        entry_period: 入场通道周期 (经典: 20)
        exit_period: 退出通道周期 (经典: 10)
        atr_period: ATR 周期

    返回:
        新增 'entry_upper', 'entry_lower', 'exit_upper', 'exit_lower',
        'atr', 'signal' 列的 DataFrame
    """
    result = df.copy()

    # 计算入场通道 (系统一: 20 日)
    result = calc_donchian_channel(result, entry_period, shift=1)
    result.rename(columns={'donchian_upper': 'entry_upper',
                           'donchian_lower': 'entry_lower'}, inplace=True)

    # 计算退出通道 (系统二: 10 日)
    result = calc_donchian_channel(result, exit_period, shift=1)
    result.rename(columns={'donchian_upper': 'exit_upper',
                           'donchian_lower': 'exit_lower'}, inplace=True)

    # 计算 ATR
    result['atr'] = calc_atr(result, atr_period, shift=1)

    # 生成信号
    result['signal'] = Signal.HOLD

    # 买入: 收盘价突破入场通道上轨
    buy_cond = (result['close'] > result['entry_upper']) & result['entry_upper'].notna()
    result.loc[buy_cond, 'signal'] = Signal.BUY

    # 卖出: 收盘价跌破退出通道下轨
    sell_cond = (result['close'] < result['exit_lower']) & result['exit_lower'].notna()
    result.loc[sell_cond, 'signal'] = Signal.SELL

    return result


# ============================================================
# 5. 回测引擎
# ============================================================

@dataclass
class BacktestResult:
    """海龟策略回测结果"""
    stock_name: str = ''
    entry_period: int = DEFAULT_ENTRY_PERIOD
    exit_period: int = DEFAULT_EXIT_PERIOD
    atr_period: int = DEFAULT_ATR_PERIOD
    total_days: int = 0
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0
    cumulative_return: float = 0.0
    total_return_pct: float = 0.0
    annualized_return: float = 0.0
    max_drawdown_pct: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    trade_log: pd.DataFrame = field(default_factory=pd.DataFrame)
    equity_curve: pd.Series = field(default_factory=pd.Series)
    drawdown_series: pd.Series = field(default_factory=pd.Series)


def backtest_turtle(df: pd.DataFrame,
                    initial_capital: float = 100000.0,
                    entry_period: int = DEFAULT_ENTRY_PERIOD,
                    exit_period: int = DEFAULT_EXIT_PERIOD,
                    atr_period: int = DEFAULT_ATR_PERIOD,
                    stop_multiple: float = DEFAULT_STOP_MULTIPLE,
                    risk_fraction: float = DEFAULT_RISK_FRACTION,
                    stock_name: str = '') -> BacktestResult:
    """
    海龟策略回测

    回测规则:
    1. 入场: 收盘价突破 20 日唐奇安通道上轨 → 全仓买入
    2. 退出: 收盘价跌破 10 日唐奇安通道下轨 → 全仓卖出
    3. 止损: 价格跌破 (入场价 - 2 × ATR) → 止损平仓
    4. 仓位: 基于 ATR 的风险预算管理 (单笔风险 = 账户 1%)
    5. 只能先买后卖 (不做空)

    参数:
        df: 行情数据
        initial_capital: 初始资金 (默认 100,000)
        entry_period: 入场通道周期
        exit_period: 退出通道周期
        atr_period: ATR 周期
        stop_multiple: 止损 ATR 倍数
        risk_fraction: 单笔风险比例
        stock_name: 股票名称

    返回:
        BacktestResult 对象
    """
    data = generate_turtle_signals(df, entry_period, exit_period, atr_period)

    cash = initial_capital
    shares = 0
    position = 0
    entry_price = 0.0
    entry_atr = 0.0
    stop_price = 0.0

    trade_log = []
    equity = []

    for i in range(len(data)):
        row = data.iloc[i]
        date = row['trade_date']
        price = row['close']
        atr_val = row['atr']
        signal = row['signal']

        # --- 止损检查 ---
        if position == 1 and not pd.isna(price) and price < stop_price:
            capital_recovered = shares * price
            cash = capital_recovered
            shares = 0
            position = 0
            trade_log.append({
                'date': date, 'type': '止损平仓', 'price': price,
                'shares': 0, 'capital': cash
            })

        # --- 卖出信号 ---
        elif signal == Signal.SELL and position == 1:
            capital_recovered = shares * price
            cash = capital_recovered
            shares = 0
            position = 0
            trade_log.append({
                'date': date, 'type': '卖出', 'price': price,
                'shares': 0, 'capital': cash
            })

        # --- 买入信号 ---
        elif signal == Signal.BUY and position == 0:
            if not pd.isna(atr_val) and atr_val > 0:
                risk_amount = cash * risk_fraction
                shares_to_buy = int(risk_amount / (stop_multiple * atr_val))
                if shares_to_buy < 100:
                    shares_to_buy = 100
                cost = shares_to_buy * price
                if cost <= cash:
                    shares = shares_to_buy
                    cash -= cost
                    position = 1
                    entry_price = price
                    entry_atr = atr_val
                    stop_price = entry_price - stop_multiple * entry_atr
                    trade_log.append({
                        'date': date, 'type': '买入', 'price': price,
                        'shares': shares, 'capital': cash + shares * price
                    })
            else:
                shares = cash / price
                cash = 0
                position = 1
                entry_price = price
                trade_log.append({
                    'date': date, 'type': '买入', 'price': price,
                    'shares': shares, 'capital': shares * price
                })

        total_equity = cash + (shares * price if position == 1 else 0)
        equity.append(total_equity)

    # 最终清仓
    if position == 1:
        final_price = data.iloc[-1]['close']
        cash = shares * final_price
        shares = 0
        trade_log.append({
            'date': data.iloc[-1]['trade_date'], 'type': '清仓',
            'price': final_price, 'shares': 0, 'capital': cash
        })
        equity[-1] = cash

    # --- 绩效指标 ---
    equity_series = pd.Series(equity, index=data['trade_date'].values)
    cumulative_return = equity[-1] / initial_capital
    total_return_pct = (cumulative_return - 1) * 100

    daily_returns = equity_series.pct_change().dropna()
    n_days = len(data)
    annualized_return = cumulative_return ** (252 / max(n_days, 1)) - 1

    volatility = daily_returns.std() * np.sqrt(252) if len(daily_returns) > 1 else 0
    sharpe_ratio = ((daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
                    if len(daily_returns) > 1 and daily_returns.std() > 0 else 0.0)

    rolling_max = equity_series.cummax()
    drawdown = (equity_series - rolling_max) / rolling_max * 100
    max_drawdown_pct = drawdown.min()

    trade_df = pd.DataFrame(trade_log)
    if len(trade_df) > 0:
        buys = trade_df[trade_df['type'] == '买入']
        sells = trade_df[trade_df['type'].isin(['卖出', '止损平仓', '清仓'])]
        total_trades = min(len(buys), len(sells))
        wins = 0
        for j in range(total_trades):
            if sells.iloc[j]['price'] > buys.iloc[j]['price']:
                wins += 1
        win_rate = wins / total_trades * 100 if total_trades > 0 else 0
    else:
        total_trades = 0
        wins = 0
        win_rate = 0.0

    return BacktestResult(
        stock_name=stock_name,
        entry_period=entry_period,
        exit_period=exit_period,
        atr_period=atr_period,
        total_days=n_days,
        total_trades=total_trades,
        winning_trades=wins,
        losing_trades=total_trades - wins,
        win_rate=win_rate,
        cumulative_return=cumulative_return,
        total_return_pct=total_return_pct,
        annualized_return=annualized_return,
        max_drawdown_pct=max_drawdown_pct,
        volatility=volatility,
        sharpe_ratio=sharpe_ratio,
        trade_log=trade_df,
        equity_curve=equity_series,
        drawdown_series=drawdown,
    )


# ============================================================
# 6. 可视化
# ============================================================

def plot_turtle_strategy(df: pd.DataFrame, result: BacktestResult,
                         save_path: Optional[str] = None):
    """
    绘制海龟策略完整可视化 (4 面板)

    面板布局:
    - 图A: 股价 + 唐奇安通道 (入场/退出) + 买卖信号
    - 图B: 资金曲线 vs 买入持有基准
    - 图C: 回撤曲线
    - 图D: ATR 走势

    参数:
        df: 原始行情数据
        result: 回测结果
        save_path: 保存路径 (None 则显示)
    """
    data = generate_turtle_signals(df, result.entry_period,
                                   result.exit_period, result.atr_period)

    fig = plt.figure(figsize=(18, 14))
    gs = fig.add_gridspec(4, 1, height_ratios=[3, 2, 1.5, 1.5], hspace=0.15)

    title = (f'{result.stock_name} ({result.entry_period}/{result.exit_period}日通道)'
             f' — 海龟交易策略回测')
    fig.suptitle(title, fontsize=16, fontweight='bold', y=0.97)

    dates = data['trade_date']

    # ---- 图A: 价格 + 通道 + 信号 ----
    ax_a = fig.add_subplot(gs[0])

    ax_a.plot(dates, data['close'], label='收盘价', color='#1a73e8',
              linewidth=0.8, alpha=0.85)

    ax_a.plot(dates, data['entry_upper'], label=f'{result.entry_period}日通道上轨 (入场)',
              color='#e53935', linewidth=1.0, linestyle='--', alpha=0.7)
    ax_a.plot(dates, data['entry_lower'], label=f'{result.entry_period}日通道下轨',
              color='#e53935', linewidth=0.6, linestyle=':', alpha=0.5)

    ax_a.plot(dates, data['exit_lower'], label=f'{result.exit_period}日通道下轨 (退出)',
              color='#f9a825', linewidth=1.0, linestyle='--', alpha=0.7)

    buy_signals = data[data['signal'] == Signal.BUY]
    ax_a.scatter(buy_signals['trade_date'], buy_signals['close'],
                 color='#43a047', marker='^', s=140, zorder=5,
                 label=f'买入信号 (突破{result.entry_period}日高点)',
                 edgecolors='white', linewidth=1.2)

    sell_signals = data[data['signal'] == Signal.SELL]
    ax_a.scatter(sell_signals['trade_date'], sell_signals['close'],
                 color='#e53935', marker='v', s=140, zorder=5,
                 label=f'卖出信号 (跌破{result.exit_period}日低点)',
                 edgecolors='white', linewidth=1.2)

    ax_a.set_ylabel('价格 (元)', fontsize=11)
    ax_a.legend(loc='upper left', fontsize=8, ncol=2)
    ax_a.grid(True, alpha=0.15)
    ax_a.set_title('图1: 股价走势、唐奇安通道与海龟交易信号', fontsize=12, loc='left',
                   fontweight='bold')

    # ---- 图B: 资金曲线 ----
    ax_b = fig.add_subplot(gs[1])
    equity = result.equity_curve

    ax_b.plot(equity.index, equity.values, label='海龟策略资金曲线',
              color='#1a73e8', linewidth=1.8)

    bench = equity.iloc[0] * (data['close'] / data['close'].iloc[0])
    ax_b.plot(dates, bench, label='买入持有 (基准)',
              color='#888888', linewidth=1, linestyle='--', alpha=0.6)

    ax_b.axhline(y=equity.iloc[0], color='gray', linewidth=0.5,
                 linestyle=':', alpha=0.4)

    final_ret = result.total_return_pct
    bench_ret = (data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100
    ax_b.annotate(
        f'策略: {final_ret:+.2f}% | 基准: {bench_ret:+.2f}%',
        xy=(equity.index[-1], equity.iloc[-1]),
        xytext=(-200, -15), textcoords='offset points',
        fontsize=9, color='#1a73e8', fontweight='bold')

    ax_b.set_ylabel('资产 (元)', fontsize=11)
    ax_b.legend(loc='upper left', fontsize=9)
    ax_b.grid(True, alpha=0.15)
    ax_b.set_title('图2: 策略资金曲线 vs 买入持有基准', fontsize=12, loc='left',
                   fontweight='bold')

    # ---- 图C: 回撤曲线 ----
    ax_c = fig.add_subplot(gs[2])
    dd = result.drawdown_series

    ax_c.fill_between(dd.index, 0, dd.values, color='#e53935', alpha=0.25)
    ax_c.plot(dd.index, dd.values, color='#e53935', linewidth=0.8)
    ax_c.axhline(y=0, color='gray', linewidth=0.5)

    min_dd_idx = dd.idxmin()
    min_dd_val = dd.min()
    ax_c.annotate(f'最大回撤: {min_dd_val:.2f}%',
                  xy=(min_dd_idx, min_dd_val),
                  xytext=(15, -25), textcoords='offset points',
                  fontsize=10, color='#c62828', fontweight='bold',
                  arrowprops=dict(arrowstyle='->', color='#c62828', lw=1.5))

    ax_c.set_ylabel('回撤 (%)', fontsize=11)
    ax_c.grid(True, alpha=0.15)
    ax_c.set_title('图3: 策略回撤曲线', fontsize=12, loc='left', fontweight='bold')

    # ---- 图D: ATR 走势 ----
    ax_d = fig.add_subplot(gs[3])
    ax_d.fill_between(dates, 0, data['atr'], color='#7b1fa2', alpha=0.2)
    ax_d.plot(dates, data['atr'], color='#7b1fa2', linewidth=0.8)
    ax_d.set_ylabel('ATR (元)', fontsize=11)
    ax_d.set_xlabel('日期', fontsize=11)
    ax_d.grid(True, alpha=0.15)
    ax_d.set_title(f'图4: {result.atr_period}日平均真实波幅 (ATR) 走势', fontsize=12,
                   loc='left', fontweight='bold')

    for ax in [ax_a, ax_b, ax_c, ax_d]:
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

    fig.autofmt_xdate()
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f'  ✓ 策略图表已保存: {save_path}')
    else:
        plt.show()
    plt.close(fig)


def plot_parameter_comparison(results: List[BacktestResult],
                              save_path: Optional[str] = None):
    """
    绘制不同参数组合的绩效对比图

    参数:
        results: 多个回测结果列表
        save_path: 保存路径
    """
    if not results:
        return

    fig, axes = plt.subplots(2, 3, figsize=(18, 11))
    fig.suptitle('海龟策略 — 多参数组合绩效对比', fontsize=16,
                 fontweight='bold', y=0.98)

    labels = [f'{r.stock_name}\n{r.entry_period}/{r.exit_period}日' for r in results]
    x = np.arange(len(labels))
    colors = ['#1a73e8', '#e53935', '#43a047', '#f9a825', '#7b1fa2', '#00acc1']

    metric_configs = [
        ('total_return_pct', '总收益率 (%)'),
        ('sharpe_ratio', '夏普比率'),
        ('max_drawdown_pct', '最大回撤 (%)'),
        ('win_rate', '胜率 (%)'),
        ('annualized_return', '年化收益率 (%)'),
        ('total_trades', '交易次数'),
    ]

    for ax, (attr, title), color in zip(axes.flat, metric_configs, colors):
        values = [getattr(r, attr) for r in results]
        bars = ax.bar(x, values, color=color, alpha=0.75, width=0.55, edgecolor='white')
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=7.5, rotation=15)
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.axhline(y=0, color='gray', linewidth=0.5, linestyle='--')
        ax.grid(True, alpha=0.15, axis='y')

        for bar, val in zip(bars, values):
            offset = max(abs(v) for v in values) * 0.02 if values else 0.1
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + offset,
                    f'{val:.2f}', ha='center', va='bottom', fontsize=7)

    plt.tight_layout(rect=[0, 0, 1, 0.95])

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f'  ✓ 参数对比图已保存: {save_path}')
    else:
        plt.show()
    plt.close(fig)


# ============================================================
# 7. 结果输出
# ============================================================

def print_results(result: BacktestResult):
    """打印回测结果摘要"""
    print('\n' + '=' * 60)
    print(f'  🐢 {result.stock_name}  —  '
          f'海龟策略 ({result.entry_period}/{result.exit_period}日通道)')
    print('=' * 60)
    print(f'  {"交易天数":16s}  {result.total_days}')
    print(f'  {"交易次数":16s}  {result.total_trades}')
    print(f'  {"盈利次数":16s}  {result.winning_trades}')
    print(f'  {"亏损次数":16s}  {result.losing_trades}')
    print(f'  {"胜率":16s}  {result.win_rate:.2f}%')
    print(f'  {"累计回报率":16s}  {result.total_return_pct:+.2f}%')
    print(f'  {"年化收益率":16s}  {result.annualized_return * 100:.2f}%')
    print(f'  {"最大回撤":16s}  {result.max_drawdown_pct:.2f}%')
    print(f'  {"夏普比率":16s}  {result.sharpe_ratio:.4f}')
    print(f'  {"年化波动率":16s}  {result.volatility * 100:.2f}%')
    print('=' * 60)


def results_to_dataframe(results: List[BacktestResult]) -> pd.DataFrame:
    """将回测结果列表转为 DataFrame"""
    rows = []
    for r in results:
        rows.append({
            '股票': r.stock_name,
            '入场通道(日)': r.entry_period,
            '退出通道(日)': r.exit_period,
            'ATR周期': r.atr_period,
            '交易次数': r.total_trades,
            '胜率(%)': f'{r.win_rate:.1f}',
            '累计回报(%)': f'{r.total_return_pct:+.2f}',
            '年化收益(%)': f'{r.annualized_return * 100:.2f}',
            '最大回撤(%)': f'{r.max_drawdown_pct:.2f}',
            '夏普比率': f'{r.sharpe_ratio:.4f}',
            '年化波动率(%)': f'{r.volatility * 100:.2f}',
        })
    return pd.DataFrame(rows)


# ============================================================
# 8. 主程序
# ============================================================

if __name__ == '__main__':
    print('=' * 60)
    print('  🐢 海龟交易法则 — 策略回测分析')
    print('=' * 60)

    stocks = list_available_stocks()
    print(f'\n可用股票 ({len(stocks)}):')
    for s in stocks:
        name = STOCK_NAMES.get(s, s)
        print(f'  - {s} ({name})')

    # ====== 单策略详细分析 ======
    print('\n' + '-' * 60)
    print('【单策略详细回测】震有科技 — 经典海龟参数 (20/10日)')
    print('-' * 60)

    df = load_stock_data('688418.SH')
    result_default = backtest_turtle(
        df,
        entry_period=20,
        exit_period=10,
        atr_period=20,
        stock_name=STOCK_NAMES.get('688418.SH', '688418.SH')
    )
    print_results(result_default)

    plot_turtle_strategy(df, result_default,
                         save_path=os.path.join(IMAGE_DIR,
                         'turtle_688418_default.png'))

    # ====== 通道周期参数调优 ======
    print('\n' + '-' * 60)
    print('【参数调优】震有科技 — 不同通道周期对比')
    print('-' * 60)

    param_configs = [
        (10, 5, 20),
        (15, 7, 20),
        (20, 10, 20),
        (30, 15, 20),
        (40, 20, 20),
        (55, 20, 20),
    ]

    param_results = []
    for entry, exit_, atr in param_configs:
        r = backtest_turtle(df, entry_period=entry, exit_period=exit_,
                            atr_period=atr,
                            stock_name=STOCK_NAMES.get('688418.SH', '688418.SH'))
        param_results.append(r)
        print_results(r)

    plot_parameter_comparison(
        param_results,
        save_path=os.path.join(IMAGE_DIR, 'turtle_param_comparison.png'))

    # ====== 多股票对比 ======
    print('\n' + '-' * 60)
    print('【多股票对比】经典海龟参数 (20/10日) 在不同股票上的表现')
    print('-' * 60)

    stock_results = []
    for ts_code in stocks:
        name = STOCK_NAMES.get(ts_code, ts_code)
        try:
            sdf = load_stock_data(ts_code)
            r = backtest_turtle(sdf,
                                entry_period=20, exit_period=10, atr_period=20,
                                stock_name=name)
            stock_results.append(r)
            print_results(r)

            plot_turtle_strategy(sdf, r,
                                 save_path=os.path.join(
                                     IMAGE_DIR,
                                     f'turtle_{ts_code.replace(".", "_")}.png'))
        except Exception as e:
            print(f'  ❌ {name} ({ts_code}): {e}')

    plot_parameter_comparison(
        stock_results,
        save_path=os.path.join(IMAGE_DIR, 'turtle_stock_comparison.png'))

    # ====== 汇总导出 ======
    all_results = param_results + stock_results
    summary_df = results_to_dataframe(all_results)
    summary_path = os.path.join(REPORT_DIR, 'turtle_backtest_summary.csv')
    summary_df.to_csv(summary_path, index=False, encoding='utf-8-sig')
    print(f'\n  ✓ 回测汇总已保存: {summary_path}')

    print('\n' + '=' * 60)
    print('  ✅ 海龟策略回测全部完成！')
    print('=' * 60)
