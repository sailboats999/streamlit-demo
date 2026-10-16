import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import signal


st.set_page_config(
    page_title="随机过程通过线性系统",
    layout="wide",
)


# ==================== 极简样式 ====================
st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    [data-testid="stToolbar"], [data-testid="stDecoration"],
    [data-testid="stStatusWidget"], [data-testid="stAppDeployButton"],
    [data-testid="stToolbarActions"] {display: none !important;}

    .stApp { background-color: #1e1e1e; }
    h1, h2, h3, h4, p, div, span, label, li { color: #E8E8E8 !important; }
    h1 { color: #50E3C2 !important; font-size: 1.8rem !important; }

    .block-container { max-width: 1200px; padding-top: 2rem; }

    [data-testid="stSelectbox"] *,
    [data-testid="stSelectbox"] input {
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }
    [data-testid="stSelectbox"] > div > div {
        background-color: #2a2a3e !important;
        border: 1px solid #4A90E2 !important;
        border-radius: 8px !important;
    }
    [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #2a2a3e !important;
    }
    [data-baseweb="popover"] * {
        background-color: #2a2a3e !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    [data-testid="stSlider"] * { color: #E8E8E8 !important; }
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
        background-color: #00FFFF !important;
    }

    [data-testid="stRadio"] label { color: #E8E8E8 !important; }

    .explain-box {
        background: rgba(42, 42, 62, 0.6);
        border-left: 4px solid #50E3C2;
        border-radius: 8px;
        padding: 16px 20px;
        margin: 12px 0;
        color: #E8E8E8;
        font-size: 15px;
        line-height: 1.8;
    }
    .explain-box b { color: #50E3C2; }
</style>
""", unsafe_allow_html=True)


# ==================== 导航 ====================
section = st.radio(
    "选择章节",
    ["引入 & LTI 系统", "时域关系", "频域关系", "白噪声实例"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("---")


# ==================== 工具函数 ====================
@st.cache_data
def gen_signal(t, kind, freq=2.0):
    if kind == "正弦波":
        return np.sin(2 * np.pi * freq * t)
    if kind == "方波":
        return signal.square(2 * np.pi * freq * t)
    if kind == "三角波":
        return signal.sawtooth(2 * np.pi * freq * t, width=0.5)
    if kind == "随机信号":
        return np.random.default_rng(42).standard_normal(len(t))
    return np.zeros_like(t)


@st.cache_data
def lti(t, x, tau_h):
    h = np.exp(-t ** 2 / (2 * tau_h ** 2))
    dt = t[1] - t[0]
    y = np.convolve(x, h, mode='same') * dt / (np.sqrt(2 * np.pi) * tau_h)
    return h, y


PLOTLY = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(30,30,40,0.5)",
    font=dict(color="#FFFFFF", size=14),
    margin=dict(l=70, r=30, t=80, b=60),
)

LEGEND_STYLE = dict(
    bgcolor="#2a2a3e",
    bordercolor="#4A90E2",
    borderwidth=1,
    font=dict(color="#FFFFFF", size=13),
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
)

AXIS_STYLE = dict(
    color="#FFFFFF",
    gridcolor="rgba(150,150,180,0.2)",
    title_font=dict(color="#FFFFFF", size=14),
    tickfont=dict(color="#CCCCCC", size=12),
)

# ★ 子图标题统一样式
SUBTITLE_STYLE = dict(
    font=dict(color="#FFFFFF", size=15)
)


# ==================== 页面 ====================
if section == "引入 & LTI 系统":
    st.title("随机过程通过线性系统")
    st.markdown("#### 核心问题：随机信号经过系统后，统计特性如何变化？")

    st.markdown("")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style="display:flex; align-items:flex-start; justify-content:center; gap:20px; padding:20px;">
            <div style="text-align:center;">
                <div style="padding:18px 28px; border:2px solid #4A90E2; border-radius:10px; color:#4A90E2; font-size:22px;">X(t)</div>
                <div style="color:#888; font-size:14px; margin-top:8px;">原信号</div>
            </div>
            <div style="font-size:22px; color:#888; padding-top:18px;">→</div>
            <div style="text-align:center;">
                <div style="padding:18px 28px; background:#F5A623; border-radius:10px; color:#1e1e1e; font-size:22px; font-weight:bold;">h(t)</div>
                <div style="color:#888; font-size:14px; margin-top:8px;">线性系统响应</div>
            </div>
            <div style="font-size:22px; color:#888; padding-top:18px;">→</div>
            <div style="text-align:center;">
                <div style="padding:18px 28px; border:2px solid #50E3C2; border-radius:10px; color:#50E3C2; font-size:22px;">Y(t)</div>
                <div style="color:#888; font-size:14px; margin-top:8px;">输出信号</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("#### LTI 系统核心性质")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**线性**")
        st.latex(r"a\, x_1 + b\, x_2 \;\to\; a\, y_1 + b\, y_2")
    with col2:
        st.markdown("**时不变**")
        st.latex(r"x(t - t_0) \;\to\; y(t - t_0)")
    with col3:
        st.markdown("**卷积关系**")
        st.latex(r"Y(t) = X(t) * h(t)")

    st.markdown("---")

    st.markdown("#### 交互演示")

    c1, c2, c3 = st.columns(3)
    with c1:
        signal_type = st.selectbox("信号类型", ["正弦波", "方波", "三角波", "随机信号"])
    with c2:
        freq = st.slider("信号频率", 0.2, 3.0, 0.5, 0.1)
    with c3:
        tau_h = st.slider("系统响应宽度", 0.02, 0.8, 0.1, 0.02)

    t = np.linspace(-5, 5, 800)
    x = gen_signal(t, signal_type, freq)
    h, y = lti(t, x, tau_h)

    # ★ 图表标题（用 subplot_titles）
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            "① 输入信号 X(t)",
            "② 系统冲激响应 h(t)",
            "③ 输出信号 Y(t)",
        ),
        vertical_spacing=0.15,
    )
    fig.add_trace(go.Scatter(x=t, y=x, line=dict(color="#4A90E2", width=2), name="X(t)"),
                  row=1, col=1)
    fig.add_trace(go.Scatter(x=t, y=h, line=dict(color="#F5A623", width=2), name="h(t)"),
                  row=2, col=1)
    fig.add_trace(go.Scatter(x=t, y=y, line=dict(color="#50E3C2", width=2), name="Y(t)"),
                  row=3, col=1)

    fig.update_layout(height=680, showlegend=False, **PLOTLY)
    fig.update_xaxes(color="#FFFFFF", gridcolor="rgba(150,150,180,0.2)",
                     tickfont=dict(color="#CCCCCC"))
    fig.update_yaxes(color="#FFFFFF", gridcolor="rgba(150,150,180,0.2)",
                     tickfont=dict(color="#CCCCCC"))
    fig.update_annotations(**SUBTITLE_STYLE)  # ★ 子图标题统一白色
    st.plotly_chart(fig, use_container_width=True)


elif section == "时域关系":
    st.title("时域关系")

    st.markdown("### ① 均值关系")
    st.markdown("系统对信号做**线性运算**，均值也按同样的方式变化：")
    st.latex(r"E[Y(t)] = E[X(t)] * h(t)")
    st.markdown("若 X(t) 平稳：")
    st.latex(r"m_Y = m_X \cdot H(0) = m_X \int_{-\infty}^{+\infty} h(t)\, dt")

    st.markdown("---")

    st.markdown("### ② 自相关关系")

    st.markdown("""
    <div class="explain-box">
    <b>直观结论：</b>系统会让自相关<b>变宽</b>。为什么？<br>
    输出 = 输入经过两次卷积（h(τ) 和 h(−τ)），相当于把输入的自相关做了两次"平滑"，<br>
    相关性被"抹开"了 —— 就像一滴墨水滴到水里，会慢慢扩散。
    </div>
    """, unsafe_allow_html=True)

    st.latex(r"R_Y(\tau) = R_X(\tau) * h(\tau) * h(-\tau)")

    st.markdown("")
    st.markdown("**拖动滑块，观察输出自相关如何变化：**")

    c1, c2 = st.columns(2)
    with c1:
        sigma_x = st.slider("输入自相关宽度 σ_X", 0.3, 1.5, 0.6, 0.05)
    with c2:
        sigma_h = st.slider("系统参数 σ_h", 0.3, 1.5, 0.7, 0.05)

    tau = np.linspace(-4, 4, 500)
    R_X = np.exp(-tau ** 2 / (2 * sigma_x ** 2))
    sigma_y = np.sqrt(sigma_x ** 2 + 2 * sigma_h ** 2)
    R_Y = np.exp(-tau ** 2 / (2 * sigma_y ** 2))

    c1, c2, c3 = st.columns(3)
    c1.metric("输入宽度 σ_X", f"{sigma_x:.2f}")
    c2.metric("系统参数 σ_h", f"{sigma_h:.2f}")
    c3.metric("输出宽度 σ_Y", f"{sigma_y:.2f}",
              delta=f"+{sigma_y - sigma_x:.2f}")

    st.markdown("")

    # ★ 加图表标题
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=tau, y=R_X, name="输入自相关 R_X(τ)",
        line=dict(color="#4A90E2", width=3),
        fill='tozeroy', fillcolor='rgba(74,144,226,0.08)',
    ))
    fig.add_trace(go.Scatter(
        x=tau, y=R_Y, name="输出自相关 R_Y(τ)",
        line=dict(color="#50E3C2", width=3),
        fill='tozeroy', fillcolor='rgba(80,227,194,0.08)',
    ))

    y_half = 0.5
    fig.add_shape(
        type="line", x0=-sigma_x, x1=sigma_x, y0=y_half, y1=y_half,
        line=dict(color="#4A90E2", width=1.5, dash="dot"),
    )
    fig.add_shape(
        type="line", x0=-sigma_y, x1=sigma_y, y0=y_half, y1=y_half,
        line=dict(color="#50E3C2", width=1.5, dash="dot"),
    )

    fig.add_annotation(
        x=-sigma_x - 0.1, y=y_half + 0.06,
        text=f"±σ_X = {sigma_x:.2f}",
        showarrow=False,
        font=dict(color="#4A90E2", size=12),
    )
    fig.add_annotation(
        x=sigma_y + 0.1, y=y_half - 0.12,
        text=f"±σ_Y = {sigma_y:.2f}",
        showarrow=False,
        font=dict(color="#50E3C2", size=12),
    )

    fig.add_annotation(
        x=sigma_y, y=0.15,
        ax=sigma_x, ay=0.15,
        xref="x", yref="y",
        axref="x", ayref="y",
        showarrow=True,
        arrowhead=2,
        arrowsize=1.2,
        arrowwidth=2,
        arrowcolor="#F5A623",
        text="",
    )
    fig.add_annotation(
        x=(sigma_x + sigma_y) / 2, y=0.22,
        text=f"展宽 +{sigma_y - sigma_x:.2f}",
        showarrow=False,
        font=dict(color="#F5A623", size=13),
    )

    fig.update_layout(
        height=500,
        title=dict(
            text="输入自相关 vs 输出自相关",
            font=dict(color="#FFFFFF", size=17, family="Microsoft YaHei"),
            x=0.5, xanchor="center",
        ),
        xaxis_title="时延 τ",
        yaxis_title="自相关函数 R(τ)",
        legend=LEGEND_STYLE,
        **PLOTLY,
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("")
    st.markdown(f"""
    <div class="explain-box">
    <b>定量关系：</b>输出宽度 = √(输入宽度² + 2 × 系统参数²)<br>
    <span style="font-family: monospace; color: #50E3C2; font-size: 15px;">
        σ_Y = √({sigma_x:.2f}² + 2 × {sigma_h:.2f}²) = {sigma_y:.2f}
    </span><br>
    <span style="color: #888;">
    → 系统参数 σ_h 越大，输出展宽越明显。σ_h = 0 时，σ_Y = σ_X（系统无影响）。
    </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("")
    st.info("💡 **平稳性结论**：若 X(t) 平稳，则 Y(t) 也平稳 —— 线性系统不会破坏平稳性。")


elif section == "频域关系":
    st.title("频域关系")

    st.markdown("""
    <div class="explain-box">
    <b>直观结论：</b>频域上，输出谱 = 输入谱 × 系统增益。<br>
    系统像一个<b>频率选择器</b>，把不需要的频率成分压低、需要的频率成分保留。
    </div>
    """, unsafe_allow_html=True)

    st.latex(r"S_Y(\omega) = |H(\omega)|^2 \, S_X(\omega)")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        sigma_x = st.slider("输入谱宽度 σ_X", 0.5, 3.0, 1.5, 0.1)
    with c2:
        sigma_h = st.slider("系统带宽 σ_h", 0.3, 3.0, 1.2, 0.1)

    omega = np.linspace(-6, 6, 500)
    S_X = np.exp(-omega ** 2 / (2 * sigma_x ** 2))
    H_sq = np.exp(-omega ** 2 / (2 * sigma_h ** 2))
    S_Y = H_sq * S_X

    # 计算输出谱宽度
    sigma_y = 1 / np.sqrt(1 / sigma_x ** 2 + 1 / sigma_h ** 2)

    # ★ 加图表标题
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=omega, y=S_X, name="输入功率谱 S_X(ω)",
                             line=dict(color="#4A90E2", width=2.5, dash='dot')))
    fig.add_trace(go.Scatter(x=omega, y=H_sq, name="系统功率增益 |H(ω)|²",
                             line=dict(color="#F5A623", width=2.5, dash='dot')))
    fig.add_trace(go.Scatter(x=omega, y=S_Y, name="输出功率谱 S_Y(ω)",
                             line=dict(color="#50E3C2", width=3.5),
                             fill='tozeroy', fillcolor='rgba(80,227,194,0.1)'))

    fig.update_layout(
        height=500,
        title=dict(
            text="功率谱密度：输入 × 系统增益 = 输出",
            font=dict(color="#FFFFFF", size=17, family="Microsoft YaHei"),
            x=0.5, xanchor="center",
        ),
        xaxis_title="角频率 ω",
        yaxis_title="功率谱密度 S(ω)",
        legend=LEGEND_STYLE,
        **PLOTLY,
    )
    fig.update_xaxes(**AXIS_STYLE)
    fig.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig, use_container_width=True)

    st.info(f"💡 输出谱的宽度由 '更窄的那个' 决定 —— 当前输出谱宽度 σ_Y ≈ {sigma_y:.2f}，比输入和系统都窄。")


elif section == "白噪声实例":
    st.title("白噪声通过线性系统")

    st.markdown("输入白噪声的功率谱为常数，输出功率谱被系统整形。下面先看系统本身，再看输入输出对比。")

    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        sigma_h = st.slider("系统带宽 σ_h（决定 h(t) 的宽度）", 0.2, 2.0, 0.8, 0.1)
    with c2:
        N0 = st.slider("白噪声功率谱密度 N₀/2", 0.1, 2.0, 1.0, 0.1)

    t = np.linspace(-4, 4, 500)
    h_t = np.exp(-t ** 2 / (2 * sigma_h ** 2))

    omega = np.linspace(-6, 6, 500)
    H_sq = np.exp(-omega ** 2 / (2 * sigma_h ** 2))
    S_X = np.full_like(omega, N0)
    S_Y = H_sq * S_X

    # ★ 三个子图都有清晰标题
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=(
            "① 系统冲激响应 h(t)   ——   时域特性",
            "② 系统频率响应 |H(ω)|²   ——   频域特性",
            "③ 输入功率谱 vs 输出功率谱   ——   白噪声被系统整形",
        ),
        vertical_spacing=0.20,
    )

    fig.add_trace(
        go.Scatter(x=t, y=h_t, name="h(t)",
                   line=dict(color="#F5A623", width=3),
                   fill='tozeroy', fillcolor='rgba(245,166,35,0.15)'),
        row=1, col=1,
    )

    fig.add_trace(
        go.Scatter(x=omega, y=H_sq, name="|H(ω)|²",
                   line=dict(color="#F5A623", width=3),
                   fill='tozeroy', fillcolor='rgba(245,166,35,0.15)'),
        row=2, col=1,
    )

    fig.add_trace(
        go.Scatter(x=omega, y=S_X, name="输入 S_X(ω)  平坦",
                   line=dict(color="#4A90E2", width=3, dash='dot')),
        row=3, col=1,
    )
    fig.add_trace(
        go.Scatter(x=omega, y=S_Y, name="输出 S_Y(ω)  被整形",
                   line=dict(color="#50E3C2", width=3),
                   fill='tozeroy', fillcolor='rgba(80,227,194,0.15)'),
        row=3, col=1,
    )

    fig.update_layout(
        height=880,
        showlegend=True,
        legend=dict(bgcolor="#2a2a3e", bordercolor="#4A90E2",
                    borderwidth=1, font=dict(color="#FFFFFF", size=12)),
        **PLOTLY,
    )

    fig.update_xaxes(color="#FFFFFF", gridcolor="rgba(150,150,180,0.2)",
                     tickfont=dict(color="#CCCCCC"))
    fig.update_yaxes(color="#FFFFFF", gridcolor="rgba(150,150,180,0.2)",
                     tickfont=dict(color="#CCCCCC"))
    fig.update_annotations(**SUBTITLE_STYLE)  # ★ 统一子图标题

    st.plotly_chart(fig, use_container_width=True)

    st.success(
        f"✅ **结论**：白噪声（平坦谱）通过系统后，输出功率谱被 |H(ω)|² 加权——"
        f"变成了与系统频率响应相同形状的曲线。"
    )