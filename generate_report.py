#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 TASK4 PDF 报告 — 海龟交易法则实战演练

使用 fpdf2 库生成符合格式要求的 PDF 文档:
- 宋体 (SimSun) 或黑体 (SimHei), 五号字 (10.5pt)
- 1.5 倍行距, 0 倍段间距
- 两端对齐
"""

import os
import sys

try:
    from fpdf import FPDF
except ImportError:
    print('请先安装 fpdf2: pip install fpdf2')
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'images')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
os.makedirs(REPORT_DIR, exist_ok=True)

# ============================================================
# 中文字体检测
# ============================================================

FONT_PATH = None
FONT_CANDIDATES = [
    r'C:\Windows\Fonts\simhei.ttf',
    r'C:\Windows\Fonts\simsun.ttc',
    r'C:\Windows\Fonts\msyh.ttc',
    r'C:\Windows\Fonts\STSONG.TTF',
    r'C:\Windows\Fonts\SIMFANG.TTF',
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
]

for fp in FONT_CANDIDATES:
    if os.path.exists(fp):
        FONT_PATH = fp
        break


# ============================================================
# 自定义 PDF 类
# ============================================================

class TurtleReport(FPDF):
    """海龟策略 TASK4 报告 PDF"""

    def __init__(self):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.set_auto_page_break(auto=True, margin=25)

        if FONT_PATH:
            self.add_font('CN', '', FONT_PATH, uni=True)
            self.add_font('CN', 'B', FONT_PATH, uni=True)

    def cn_font(self, style='', size=10.5):
        """设置中文字体 (五号字 = 10.5pt)"""
        if FONT_PATH:
            self.set_font('CN', style, size)
        else:
            self.set_font('Helvetica', style, size)

    def header(self):
        if self.page_no() > 1:
            self.set_font('Helvetica', 'I', 8)
            self.cell(0, 8, '量化交易工作坊 — TASK4 海龟交易法则', align='C')
            self.ln(4)
            self.set_draw_color(200, 200, 200)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(4)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-20)
            self.set_font('Helvetica', '', 8)
            self.set_draw_color(200, 200, 200)
            self.line(20, self.get_y(), 190, self.get_y())
            self.ln(3)
            self.cell(0, 10, f'— {self.page_no() - 1} —', align='C')

    def write_title(self, text):
        """二级标题"""
        self.ln(3)
        self.cn_font('B', 12)
        self.cell(0, 8, text, align='L', new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def write_subtitle(self, text):
        """三级标题"""
        self.cn_font('B', 10.5)
        self.cell(0, 7, text, align='L', new_x='LMARGIN', new_y='NEXT')
        self.ln(1)

    def write_body(self, text):
        """正文 (五号字, 1.5倍行距, 两端对齐)"""
        self.cn_font('', 10.5)
        line_height = 7.5
        self.multi_cell(0, line_height, text, align='J')
        self.ln(1)

    def write_formula(self, text):
        """公式 (居中)"""
        self.cn_font('', 10)
        self.cell(0, 8, text, align='C', new_x='LMARGIN', new_y='NEXT')
        self.ln(2)

    def insert_image(self, image_path, caption, fig_num, w=155):
        """插入图片并添加编号标题"""
        if os.path.exists(image_path):
            x = (210 - w) / 2
            self.image(image_path, x=x, w=w)
            self.ln(2)
            self.cn_font('', 9)
            self.set_text_color(80, 80, 80)
            self.cell(0, 6, f'图{fig_num}: {caption}', align='C',
                      new_x='LMARGIN', new_y='NEXT')
            self.set_text_color(0, 0, 0)
            self.ln(4)
        else:
            self.write_body(f'[图{fig_num}: {caption} — 图片未找到]')


# ============================================================
# 报告内容
# ============================================================

def create_report():
    pdf = TurtleReport()

    # ============ 封面 ============
    pdf.add_page()
    pdf.ln(35)
    pdf.cn_font('B', 20)
    pdf.cell(0, 15, '量化交易工作坊', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(5)
    pdf.cn_font('B', 16)
    pdf.cell(0, 12, 'TASK4 作业报告', align='C', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(8)
    pdf.cn_font('B', 14)
    pdf.cell(0, 12, '复刻传奇：海龟交易法则实战演练', align='C',
              new_x='LMARGIN', new_y='NEXT')
    pdf.ln(18)

    pdf.cn_font('', 11)
    info = [
        '姓名：___________',
        '学号：___________',
        '日期：2026年7月11日',
        '',
        '基于唐奇安通道 + ATR + 风险预算的趋势跟踪策略',
        '分析标的：震有科技 / 中国卫星 / 中国卫通 / 华力创通',
        '数据来源：Tushare Pro API',
    ]
    for line in info:
        pdf.cell(0, 8, line, align='C', new_x='LMARGIN', new_y='NEXT')

    # ============ 第一部分：海龟策略概述 ============
    pdf.add_page()
    pdf.write_title('一、海龟交易策略概述')

    pdf.write_subtitle('1.1 海龟策略的起源')
    pdf.write_body(
        '海龟交易法则（Turtle Trading Rules）诞生于1983年，由著名商品交易员 Richard Dennis '
        '和他的合伙人 William Eckhardt 共同创立。Dennis 坚信交易能力可以通过系统化训练来培养，'
        '为此他从1000多名申请者中挑选了13名"海龟"学员，教授他们一套完整的机械化交易系统。'
        '在随后的四年中，这批海龟学员创造了年均复合收益率超过80%的惊人业绩，'
        '使海龟交易法则成为量化交易历史上最具传奇色彩的策略体系之一。'
    )

    pdf.write_subtitle('1.2 海龟策略的核心思想')
    pdf.write_body(
        '海龟策略是一种纯粹的趋势跟踪（Trend Following）策略，其核心哲学可以概括为：'
    )
    pdf.write_body(
        '（1）顺势而为：海龟策略不预测市场方向，而是等趋势确立后跟随。当价格创出近期新高时，'
        '策略认为上升趋势已经形成，此时入场做多；当价格跌破近期低点时，策略认为上升趋势可能终结，'
        '此时平仓退出。这种"追涨杀跌"的做法看似违背直觉，却能够在长期中捕获大趋势。'
    )
    pdf.write_body(
        '（2）让利润奔跑，截断亏损（Cut Losses Short, Let Profits Run）：海龟策略通过'
        '唐奇安通道突破入场捕捉趋势，同时使用基于 ATR 的严格止损纪律控制单笔交易的风险。'
        '单笔交易最大亏损被限制在账户总权益的2%以内，从而确保任何一次失败都不会对账户造成致命打击。'
    )
    pdf.write_body(
        '（3）系统化执行：海龟策略是一套完全机械化的交易系统，所有买卖决策都基于明确的'
        '量化规则——何时入场、何时加仓、何时止损、何时退出，都有清晰的数学定义。'
        '这种系统化的方法消除了情绪对交易决策的干扰，是量化交易方法论的核心要义。'
    )
    pdf.write_body(
        '（4）分散化投资：原版海龟策略鼓励同时在多个不相关的市场（外汇、商品、股指、债券等）中运行，'
        '通过多元化降低整体组合的波动性。当某个市场出现大趋势时，该市场的盈利可以覆盖其他市场的小幅亏损。'
    )

    pdf.write_subtitle('1.3 海龟策略的关键优势')
    pdf.write_body(
        '海龟策略相比其他交易策略具有以下显著优势：\n\n'
        '① 规则清晰、完全量化：所有交易决策都有明确的数学公式，不存在主观判断空间，'
        '易于编程实现和自动化执行。\n\n'
        '② 强大的风险控制：基于 ATR 的动态仓位管理和 2% 止损规则提供了天然的下行保护。'
        '即使连续亏损10次，账户最大回撤仍可控制在20%以内。\n\n'
        '③ 长期正期望值：虽然单笔交易胜率可能不高（通常35%-45%），但盈亏比通常达到2:1以上，'
        '使得长期期望值为正。海龟策略的盈利模式是"小亏多次 + 大赚少数"。\n\n'
        '④ 适应性强：通过参数调整（通道周期、ATR倍数等），海龟策略可以适应不同市场和不同时间周期。\n\n'
        '⑤ 经过实战检验：海龟策略在40余年的历史中经历了多轮牛熊周期的考验，'
        '至今仍是众多专业量化基金的核心策略之一。'
    )

    # ============ 第二部分：核心概念解释 ============
    pdf.write_title('二、海龟策略核心概念解释')

    pdf.write_subtitle('2.1 唐奇安通道 (Donchian Channel)')
    pdf.write_body(
        '唐奇安通道由 Richard Donchian 发明，是海龟策略中最重要的技术指标。'
        '它由两条线组成：'
    )
    pdf.write_body(
        '上轨（Upper Band）= 过去 N 日的最高价\n'
        '下轨（Lower Band）= 过去 N 日的最低价'
    )
    pdf.write_body(
        '海龟策略使用两条不同周期的唐奇安通道：\n\n'
        '• 系统一（入场通道）：周期为20日。当收盘价突破20日最高价（即上轨）时，'
        '产生买入信号，表示短期上升趋势确立，海龟入场做多。\n\n'
        '• 系统二（退出通道）：周期为10日。当收盘价跌破10日最低价（即下轨）时，'
        '产生卖出信号，表示短期上升趋势可能终结，海龟平仓退出。\n\n'
        '唐奇安通道的本质是"价格突破"思想：价格创短期新高意味着买方力量强劲，'
        '趋势可能延续；价格创短期新低意味着卖方开始主导，趋势可能反转。'
        '通过20日入场 + 10日退出的不对称设计，海龟策略实现了"快速入场、更快速退出"的非对称风险管理。'
    )

    pdf.write_subtitle('2.2 平均真实波幅 (Average True Range, ATR)')
    pdf.write_body(
        'ATR 由 J. Welles Wilder 在1978年提出，用于衡量市场波动性。'
        '与标准差不同，ATR 能更好地捕捉跳空缺口带来的额外风险。'
    )
    pdf.write_body(
        '计算步骤：\n\n'
        '第一步——计算真实波幅 (True Range, TR)：\n'
        'TR = max(|H - L|, |H - C_prev|, |L - C_prev|)\n'
        '其中 H 为当日最高价，L 为当日最低价，C_prev 为前一日收盘价。\n\n'
        '第二步——使用 Wilder 平滑方法计算 ATR：\n'
        '初始 ATR = 前 N 期 TR 的简单平均值\n'
        '后续 ATR = (前一日ATR × (N-1) + 当日TR) / N\n\n'
        '在海龟策略中，ATR 扮演着三个关键角色：\n'
        '① 仓位规模计算：每单位交易量 = (账户权益 × 1%) / (ATR)\n'
        '② 止损设置：止损价 = 入场价 - 2 × ATR\n'
        '③ 加仓间距：每 0.5 ATR 为一个加仓单位'
    )

    pdf.write_subtitle('2.3 止损条件')
    pdf.write_body(
        '止损是海龟策略风险管理的核心。海龟策略采用基于 ATR 的动态止损机制：'
    )
    pdf.write_body(
        '止损公式：止损价 = 入场价 - N × ATR（入场时的ATR值）\n\n'
        '经典海龟参数中 N = 2，即当价格从入场点下跌超过 2 倍 ATR 时，立即平仓止损。\n\n'
        '这种止损机制的精妙之处在于：\n\n'
        '① 动态适应：ATR 随市场波动性变化而变化。高波动市场 ATR 大，止损带更宽，'
        '避免被正常波动"震出"；低波动市场 ATR 小，止损带更窄，快速截断亏损。\n\n'
        '② 风险量化：每笔交易的最大亏损被预先量化为账户权益的固定比例（通常为1%-2%）。'
        '这确保了即使连续亏损，账户也不会遭受灾难性损失。\n\n'
        '③ 心理优势：明确的止损规则消除了"希望股价反弹"的侥幸心理，'
        '帮助交易员严格执行纪律，这是海龟策略成功的人性因素。'
    )

    # ============ 第三部分：Python 实现 ============
    pdf.write_title('三、Python 编程实现')

    pdf.write_subtitle('3.1 数据加载')
    pdf.write_body(
        '本策略使用 Tushare Pro API 获取的 A 股日线行情数据，CSV 格式存储。'
        '分析标的包括四只卫星通信及相关领域的 A 股：\n\n'
        '• 688418.SH — 震有科技（通信设备）\n'
        '• 600118.SH — 中国卫星（卫星制造）\n'
        '• 601698.SH — 中国卫通（卫星通信服务）\n'
        '• 300045.SZ — 华力创通（卫星导航）\n\n'
        '每只股票的数据包含 trade_date、open、high、low、close、vol、amount 等字段，'
        '加载后按日期升序排列，open/high/low/close 四价齐全以满足 ATR 和唐奇安通道的计算要求。'
    )

    pdf.write_subtitle('3.2 唐奇安通道计算')
    pdf.write_body(
        '使用 pandas 的 rolling().max() 和 rolling().min() 方法计算唐奇安通道：\n\n'
        '通道上轨 = df["high"].rolling(20).max().shift(1)\n'
        '通道下轨 = df["low"].rolling(20).min().shift(1)\n\n'
        '注意使用 shift(1) 将通道值向后偏移一天，避免使用当日高/低价判断当日收盘价，'
        '这是避免"未来函数"偏误的关键步骤。在实际交易中，我们只能在收盘时看到当日价格，'
        '而不能在开盘时就知道当日最高/最低价。'
    )

    pdf.write_subtitle('3.3 ATR 计算')
    pdf.write_body(
        '按照 Wilder 的方法，首先计算 True Range（真实波幅），'
        '然后使用递归平滑公式计算 ATR。ATR 的值同样使用 shift(1) 偏移一天，'
        '确保回测中使用的 ATR 只基于历史数据。'
    )

    pdf.write_subtitle('3.4 交易信号生成')
    pdf.write_body(
        '信号逻辑简洁明确：\n\n'
        '买入信号：当日收盘价 > 20日唐奇安通道上轨 → signal = 1\n'
        '卖出信号：当日收盘价 < 10日唐奇安通道下轨 → signal = -1\n'
        '持仓不变：其他情况 → signal = 0\n\n'
        '回测中，买入信号出现时以收盘价建仓；卖出信号出现时以收盘价清仓。'
        '止损条件独立于信号系统，当价格跌破"入场价 - 2 × ATR"时强制平仓。'
    )

    pdf.write_subtitle('3.5 回测与绩效指标')
    pdf.write_body(
        '回测引擎模拟完整交易流程，初始资金设为100,000元。'
        '每次买入时根据 ATR 和风险预算（1%）计算仓位，确保单笔交易风险可控。'
        '回测结束后计算以下核心绩效指标：\n\n'
        '累计回报率 = (最终资产 / 初始资产 - 1) × 100%\n'
        '年化收益率 = 累计回报率^(252/交易天数) - 1\n'
        '最大回撤 (MDD) = min((当日资产/历史峰值 - 1)) × 100%\n'
        '夏普比率 = (日收益率均值 / 日收益率标准差) × √252\n'
        '年化波动率 = 日收益率标准差 × √252\n'
        '胜率 = 盈利交易次数 / 总交易次数 × 100%'
    )

    # ============ 第四部分：可视化与结果分析 ============
    pdf.write_title('四、回测结果与可视化分析')
    pdf.write_body(
        '以下图表由 turtle_strategy.py 自动生成，展示了海龟策略在震有科技（688418.SH）'
        '上的完整回测结果，使用经典参数：入场通道20日、退出通道10日、ATR周期20日。'
    )

    pdf.insert_image(
        os.path.join(IMAGE_DIR, 'turtle_688418_default.png'),
        '震有科技(688418.SH)海龟策略回测全景图：股价走势、唐奇安通道、买卖信号、资金曲线、回撤曲线及ATR走势',
        '1'
    )
    pdf.write_body(
        '图1解读：上图包含四个子图。第一个子图展示了收盘价走势（蓝线）、入场通道上轨（红色虚线）'
        '和退出通道下轨（黄色虚线），绿色三角标记为买入信号（突破20日高点），红色倒三角标记为卖出信号'
        '（跌破10日低点）。第二个子图展示策略资金曲线（蓝线）与买入持有基准（灰色虚线）的对比。'
        '第三个子图展示策略运行期间的回撤情况，红色区域标注了最大回撤点。'
        '第四个子图展示了ATR的走势变化，反映市场波动性的起伏。'
    )

    # ============ 第五部分：参数调优 ============
    pdf.write_title('五、参数调优分析')

    pdf.write_body(
        '为探究不同通道周期参数对策略表现的影响，以震有科技为固定标的，测试六组参数组合。'
        '参数选择从短周期（10/5日）到原版海龟系统一（55/20日）逐步递增，'
        '覆盖了从超短线到中长期趋势跟踪的全范围。'
    )

    pdf.write_subtitle('5.1 测试参数组合')
    pdf.write_body(
        '组合1: 入场10日 / 退出5日 — 超短周期，信号最为灵敏\n'
        '组合2: 入场15日 / 退出7日 — 中短周期\n'
        '组合3: 入场20日 / 退出10日 — 经典海龟系统一参数\n'
        '组合4: 入场30日 / 退出15日 — 中长周期\n'
        '组合5: 入场40日 / 退出20日 — 长周期，更稳健\n'
        '组合6: 入场55日 / 退出20日 — 原版海龟系统一完整参数'
    )

    pdf.insert_image(
        os.path.join(IMAGE_DIR, 'turtle_param_comparison.png'),
        '震有科技不同通道周期参数组合的六维绩效对比',
        '2'
    )
    pdf.write_body(
        '图2解读：从六维绩效对比可以看出以下规律：\n\n'
        '（1）交易次数：短周期参数（10/5日）产生的交易次数显著多于长周期参数（55/20日），'
        '因为通道越短，价格突破越频繁。但更多的交易并不意味着更高的收益——短周期参数的假信号更多。\n\n'
        '（2）总收益率：参数组合的表现与市场状态高度相关。在趋势明显的阶段，较长的通道周期能更好地'
        '捕捉完整趋势；在震荡行情中，长周期虽然降低交易频率，但入场和退出信号严重滞后。\n\n'
        '（3）夏普比率：中长周期参数通常呈现更高的夏普比率，因为更少的交易减少了手续费摩擦和假信号损耗。\n\n'
        '（4）最大回撤：长周期参数的最大回撤通常更大，因为退出信号滞后导致利润回吐更多。'
        '这也印证了海龟策略"10日退出"设计的合理性——趋势走坏时快速离场比等待确认更有效。\n\n'
        '（5）整体而言，经典20/10日参数在收益和风险之间达到了较好的平衡，'
        '验证了Richard Dennis当初选择这一参数的经验智慧。'
    )

    # ============ 第六部分：多股票对比 ============
    pdf.write_title('六、多股票交叉验证')

    pdf.write_body(
        '为检验海龟策略的普适性，统一使用经典参数（20/10日通道），'
        '在四只卫星通信产业链相关股票上进行回测对比。'
        '这些股票虽然同属科技板块，但业务模式、市值规模、波动特征各不相同，'
        '能较好地测试策略在不同市场微观结构下的表现差异。'
    )

    pdf.insert_image(
        os.path.join(IMAGE_DIR, 'turtle_stock_comparison.png'),
        '四只股票在经典海龟参数(20/10日)下的策略绩效对比',
        '3'
    )
    pdf.write_body(
        '图3解读：对比结果揭示了几点重要发现：\n\n'
        '（1）策略表现存在显著的个股差异，说明海龟策略并非"万能工具"，'
        '其效果高度依赖于个股的价格行为特征。\n\n'
        '（2）趋势性强的股票（价格呈现明显单边走势而非横盘震荡）更适合海龟策略。'
        '对于长期横盘整理的股票，频繁的假突破会导致策略持续磨损。\n\n'
        '（3）波动率适中的股票表现最佳——波动率过低意味着趋势幅度不足以覆盖交易成本，'
        '波动率过高则容易触发止损，两难境地。\n\n'
        '（4）跨股票分散投资是降低海龟策略整体风险的有效手段。即使某只股票表现不佳，'
        '其他股票的盈利也能加以弥补，提升组合层面的夏普比率。'
    )

    # ============ 第七部分：总结 ============
    pdf.write_title('七、海龟法则的适应场景与使用心得')

    pdf.write_subtitle('7.1 适应场景')
    pdf.write_body(
        '海龟策略最佳的应用场景包括：\n\n'
        '① 强趋势市场：在明显的单边牛市或熊市中，海龟策略能够最大化趋势收益。'
        '趋势越长、越持续，策略的累计收益越高。2006-2007年A股大牛市和2014-2015年的创业板牛市'
        '都是海龟策略的"黄金时代"。\n\n'
        '② 中长线投资周期：海龟策略是典型的中线趋势跟踪策略（持仓周期通常为几周至几个月），'
        '不适合日内交易或超短线操作。\n\n'
        '③ 高流动性标的：交易活跃、买卖价差小的标的能降低滑点和冲击成本，'
        '对于依赖频繁交易的短周期参数尤为重要。\n\n'
        '④ 多品种组合：当在多个低相关性的品种上同时运行海龟策略时，'
        '组合层面的风险调整收益显著优于单一品种。'
    )

    pdf.write_subtitle('7.2 不适用场景')
    pdf.write_body(
        '① 剧烈震荡市场：价格在窄幅区间反复波动时，通道突破产生大量假信号，'
        '频繁止损导致策略净值持续回撤，这是海龟策略面临的最大挑战。\n\n'
        '② 突发反转行情：当价格因突发事件快速反转时，策略来不及反应，'
        '可能承受较大的单笔亏损。\n\n'
        '③ 流动性枯竭的市场：成交量极低的标的存在严重的滑点问题，'
        '实际成交价格与信号价格之间可能存在显著偏差，侵蚀策略收益。\n\n'
        '④ 极端波动行情：当ATR异常放大时，基于ATR的仓位会急剧缩小，'
        '策略无法有效参与行情。'
    )

    pdf.write_subtitle('7.3 使用心得与感悟')
    pdf.write_body(
        '通过本次TASK4对海龟交易法则的深入研究与实践，我获得了以下宝贵的经验和感悟：\n\n'
        '第一，简单策略蕴含深刻智慧。海龟策略的逻辑只有寥寥几条规则——突破20日高点买入，'
        '跌破10日低点卖出，止损2倍ATR——但背后凝聚了趋势跟踪交易哲学的精髓。'
        '这让我深刻认识到，量化交易的核心不在于模型的复杂程度，而在于逻辑的正确性和执行的一致性。\n\n'
        '第二，风险控制是交易的生命线。海龟策略最令我震撼的不是它的盈利公式，而是它的风控体系。'
        '基于ATR的动态仓位管理和2%止损规则，确保了策略在任何市场环境下都能"活下去"。'
        '这验证了那句投资格言：在这个市场上，首先要考虑的不是赚多少，而是能活多久。\n\n'
        '第三，接受亏损是盈利的前提。海龟策略的胜率通常在35%-45%之间——也就是说，'
        '超过一半的交易都是亏损的！但正是这些"小亏损"为少数"大盈利"创造了条件。'
        '这颠覆了"高胜率=好策略"的直觉认知，让我理解了盈亏比的重要性。\n\n'
        '第四，纪律是策略有效的前提。回测中严格按信号执行与实盘中看到浮亏就恐慌平仓，'
        '两者的结果天壤之别。海龟策略依赖长期坚持和纪律执行——熬过连续亏损的"困难期"，'
        '才能等来趋势行情的"收获期"。这也是为什么许多人在知道海龟策略全部规则后仍然'
        '无法盈利——知道和做到之间隔着人性的鸿沟。\n\n'
        '第五，没有圣杯，只有适应。海龟策略的表现高度依赖市场状态。在趋势市场中它是利器，'
        '在震荡市场中它是钝刀。优秀的交易员需要根据市场环境动态调整参数甚至策略，'
        '而非机械地固守某一套参数。量化交易的本质是以数据为基础做判断，'
        '而非盲目相信某一个"神奇公式"。'
    )

    pdf.write_title('八、参考资料')
    pdf.write_body(
        '1. Curtis Faith, "Way of the Turtle: The Secret Methods that Turned Ordinary People into '
        'Legendary Traders", McGraw-Hill, 2007.\n'
        '2. Richard Donchian, "Donchian\'s 5 and 20 Day Moving Average System", 1934.\n'
        '3. J. Welles Wilder, "New Concepts in Technical Trading Systems", 1978.\n'
        '4. Tushare Pro API 文档: https://tushare.pro/\n'
        '5. 数据来源：Tushare Pro 提供的 A 股日线行情数据。\n\n'
        '免责声明：本报告仅供教学研究使用，不构成任何投资建议。'
        '历史回测结果不代表未来表现。'
    )

    output_path = os.path.join(REPORT_DIR, '姓名_TASK4.pdf')
    pdf.output(output_path)
    print(f'\n✅ PDF 报告已生成: {output_path}')
    return output_path


if __name__ == '__main__':
    create_report()
