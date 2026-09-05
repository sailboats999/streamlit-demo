import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy.integrate import trapezoid as trapz

# -------------------------- 页面全局配置（只保留一次） --------------------------
st.set_page_config(page_title="通信原理交互式教学", layout="wide")
# ====================== Matplotlib 中文字体 ======================
# Streamlit Cloud：优先使用系统中文字体；本地 Windows 也可正常运行。
import os
import glob
import matplotlib.pyplot as plt
from matplotlib import font_manager

# 这些是常见的 Linux / Windows 中文字体位置。
# fonts-noto-cjk 由 packages.txt 安装后，通常会出现在 /usr/share/fonts 下。
_font_paths = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.otf",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.otf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/msyh.ttf",
    "C:/Windows/Fonts/simhei.ttf",
]

# 再从系统字体目录中搜索 Noto / 中文字体。
_search_dirs = [
    "/usr/share/fonts",
    "/usr/local/share/fonts",
    os.path.expanduser("~/.fonts"),
]
for _directory in _search_dirs:
    if os.path.isdir(_directory):
        _font_paths.extend(glob.glob(os.path.join(_directory, "**", "*.ttf"), recursive=True))
        _font_paths.extend(glob.glob(os.path.join(_directory, "**", "*.otf"), recursive=True))

# 本地 Windows 再补充系统字体。
if os.path.isdir("C:/Windows/Fonts"):
    _font_paths.extend(glob.glob("C:/Windows/Fonts/*.ttf"))
    _font_paths.extend(glob.glob("C:/Windows/Fonts/*.otf"))

# 去重并优先中文字体。
_font_paths = list(dict.fromkeys(_font_paths))
_font_paths.sort(key=lambda p: (
    0 if any(k in os.path.basename(p).lower() for k in ["noto", "cjk", "wqy", "ukai", "uming", "yahei", "simhei", "simsun"]) else 1,
    p.lower()
))

CHINESE_FONT_PATH = None
CHINESE_FONT_NAME = None

# 检查字体是否真的包含常用中文字符“中”“国”“信”“号”。
for _path in _font_paths:
    if not os.path.isfile(_path):
        continue
    try:
        _font = font_manager.get_font(_path)
        _charmap = _font.get_charmap()
        if all(ord(_char) in _charmap for _char in ["中", "国", "信", "号"]):
            CHINESE_FONT_PATH = _path
            CHINESE_FONT_NAME = font_manager.FontProperties(fname=_path).get_name()
            break
    except Exception:
        continue

if CHINESE_FONT_PATH and CHINESE_FONT_NAME:
    # 注册实际字体文件，避免 Matplotlib 回退到 default。
    try:
        font_manager.fontManager.addfont(CHINESE_FONT_PATH)
    except Exception:
        pass
    plt.rcParams["font.family"] = [CHINESE_FONT_NAME]
    plt.rcParams["font.sans-serif"] = [CHINESE_FONT_NAME]
else:
    # 找不到中文字体时至少不要静默；本地环境可继续使用这些常见字体。
    plt.rcParams["font.family"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]

plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.labelsize"] = 13
plt.rcParams["xtick.labelsize"] = 11
plt.rcParams["ytick.labelsize"] = 11

# Plotly 使用浏览器字体；页面 CSS 同时指定 Noto Sans CJK，
# 让 Plotly 标题、坐标轴和 Streamlit 页面文字也优先使用中文字体。
PLOTLY_FONT = "Noto Sans CJK SC, Noto Sans SC, Microsoft YaHei, Arial, sans-serif"

st.markdown("""
<style>
/* 中文字体：优先使用云端可用的 Noto Sans CJK；浏览器端负责 Plotly 和 Streamlit 文字 */
@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700&display=swap");

html, body, [class*="css"],
div[data-testid="stAppViewContainer"],
div[data-testid="stMarkdownContainer"],
button, input, textarea, select, label,
h1, h2, h3, h4, h5, h6, p, span {
    font-family: "Noto Sans SC", "Noto Sans CJK SC", "Microsoft YaHei", Arial, sans-serif !important;
}

div.markdown-text-container p {font-size:16px !important;}
h1 {font-size:24px !important;}
h2 {font-size:20px !important;}
h3 {font-size:18px !important;}

/* 主页面横向radio大卡片按钮样式 */
.stRadio [role="radiogroup"]{
    display:flex;
    gap:16px;
}
.stRadio [role="radiogroup"] label{
    flex:1;
    font-size:19px !important;
    font-weight:600;
    padding:16px 20px !important;
    border-radius:16px !important;
    background: linear-gradient(135deg, #f7f9fc 0%, #eaf4ff 100%);
    color:#2c3e50;
    border:2px solid #dce6f5;
    box-shadow:0 4px 12px rgba(0,0,0,0.08);
    margin:4px 0 !important;
}
.stRadio [role="radiogroup"] label[data-checked="true"]{
    background: linear-gradient(135deg, #1f77b4 0%, #45a7ff 100%) !important;
    color:white !important;
    border-color:#1f77b4;
    box-shadow:0 6px 16px rgba(31, 119, 180, 0.35);
}

/* 侧边栏radio保持原始大小，不要放大侧边栏 */
section[data-testid="stSidebar"] .stRadio [role="radiogroup"]{
    display:block;
    gap:4px;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label{
    flex:none;
    font-size:14px !important;
    padding:4px 6px !important;
    border-radius:4px !important;
    background:transparent;
    border:none;
    box-shadow:none;
    margin:0 !important;
}
section[data-testid="stSidebar"] .stRadio [role="radiogroup"] label[data-checked="true"]{
    background:transparent !important;
    color:inherit !important;
    border:none;
    box-shadow:none;
}
</style>
""", unsafe_allow_html=True)

# ====================== 侧边栏 ======================
with st.sidebar:
    st.markdown("#### 章节")
    chapter_sel = st.radio(
        label="",
        options=["第2章 信号与信道"],
        index=0
    )

    st.markdown("#### 模块")
    module_sel = st.radio(
        label="",
        options=["2.1 时域与频域", "2.2 信道分类与建模", "2.3 衰减、时延与多径", "2.4 AWGN"],
        index=0
    )
    st.markdown("---")
    st.caption(f"当前：{chapter_sel}｜{module_sel}")

# ====================== 2.1 时域与频域 ======================
if chapter_sel == "第2章 信号与信道" and module_sel == "2.1 时域与频域":

    # 用两列+原生按钮模拟单选切换，强制等宽，不再用st.radio
    col_btn1, col_btn2 = st.columns([1,1])
    # 用session_state存选中状态
    if "demo_2_1_mode" not in st.session_state:
        st.session_state.demo_2_1_mode = "fourier"

    with col_btn1:
        if st.button("📚傅里叶级数与傅里叶变换交互式教学", use_container_width=True,
                     type="primary" if st.session_state.demo_2_1_mode=="fourier" else "secondary"):
            st.session_state.demo_2_1_mode = "fourier"
    with col_btn2:
        if st.button("📡信号卷积交互式教学", use_container_width=True,
                     type="primary" if st.session_state.demo_2_1_mode=="conv" else "secondary"):
            st.session_state.demo_2_1_mode = "conv"

    demo_mode = st.session_state.demo_2_1_mode
    st.markdown("---")

    # ========== 分支A：傅里叶级数与傅里叶变换 ==========
    if demo_mode == "fourier":
        st.title("📚 傅里叶级数与傅里叶变换 交互式教学")
        st.markdown("---")

        # ===================== 1. 信号时域表示 =====================
        st.subheader("1. 信号时域表示：横坐标为时间")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(""" > 信号时域表示：横坐标为时间 """)

            t = np.linspace(0, 2, 1000)
        with col2:
            fig1, ax1 = plt.subplots(figsize=(6,2.6))
            sig1 = np.sin(2 * np.pi * 3 * t)
            ax1.plot(t, sig1, color="#1f77b4", linewidth=2)
            ax1.set_xlabel("时间 t")
            ax1.set_ylabel("幅值")
            ax1.set_title("单一时域信号")
            ax1.grid(True, alpha=0.3)
            plt.subplots_adjust(left=0.12, bottom=0.22, right=0.96, top=0.82)
            st.pyplot(fig1)
            plt.close(fig1)

        st.markdown("---")

        # ===================== 2. 多个信号时域叠加 =====================
        st.subheader("2. 多个信号时域叠加，时域波形看起来就会混乱")
        col_a, col_b = st.columns([1,1])
        with col_a:
            st.markdown(""" > 多个信号时域叠加，时域波形看起来就会混乱 """)
            n_comp = st.slider("叠加正弦信号数量", min_value=1, max_value=8, value=4)
            t2 = np.linspace(0,2,1000)
            sum_sig = np.zeros_like(t2)
            for k in range(1, n_comp+1):
                sum_sig += (1/k)*np.sin(2*np.pi * k * 2 * t2)
        with col_b:
            fig2, ax2 = plt.subplots(figsize=(6,2.6))
            ax2.plot(t2, sum_sig, color="#d62728", linewidth=2)
            ax2.set_xlabel("时间 t")
            ax2.set_ylabel("叠加后幅值")
            ax2.set_title("多信号叠加后的混乱时域波形")
            ax2.grid(True, alpha=0.3)
            plt.subplots_adjust(left=0.12, bottom=0.22, right=0.96, top=0.82)
            st.pyplot(fig2)
            plt.close(fig2)

        st.markdown("---")

        # ===================== 3.傅里叶级数拆分+2D图 =====================
        st.subheader("3. 经过傅里叶级数拆分，原复杂信号被拆解为多个简单信号，侧面投影就是信号频域图，横坐标为角频率")

        col_c_text, col_c_fig = st.columns([1, 2.2])
        with col_c_text:
            st.markdown(""" > 复杂时域信号经过**傅里叶级数分解**，拆成一组不同频率、不同幅度的正弦/余弦基础分量。
>
> - 时域：横轴时间，观察信号随时间如何变化；
> - 把各个分量的幅值向频率轴做**侧面投影**，就得到频域；
> - 频域图横坐标为角频率 $\\omega$，竖轴为各频率分量的幅度；
> - 周期信号分解出来是一根根离散谱线。

调节滑块改变分解谐波数量，可以观察：
- 时域各个基础正弦分量；
- 投影得到的频域谱线随之变化。
""")
            n_decomp = st.slider("傅里叶分解谐波数目", min_value=1, max_value=8, value=4)
            t3 = np.linspace(0, 2, 1000)
            f0 = 2
            components = []
            sum_comp = np.zeros_like(t3)
            for k in range(1, n_decomp+1):
                amp_k = 1.0 / k
                s_k = amp_k * np.sin(2 * np.pi * k * f0 * t3)
                components.append((k, amp_k, s_k))
                sum_comp += s_k

        with col_c_fig:
            fig3 = plt.figure(figsize=(10,4.2))
            gs = fig3.add_gridspec(2, 2, width_ratios=[2,1], height_ratios=[1,1])

            ax_sum = fig3.add_subplot(gs[0, 0])
            ax_sum.plot(t3, sum_comp, color="#c41e3a", lw=2.2)
            ax_sum.set_title("原始复杂时域信号")
            ax_sum.set_xlabel("时间 t")
            ax_sum.grid(alpha=0.3)

            ax_parts = fig3.add_subplot(gs[1, 0])
            color_list = ["#1f77b4","#2ca02c","#ff7f0e","#9467bd","#8c564b","#17becf","#d62728","#7f7f7f"]
            for idx,(k,amp,sig) in enumerate(components):
                ax_parts.plot(t3, sig, color=color_list[idx%len(color_list)], label=f"k={k}", alpha=0.8)
            ax_parts.set_title("傅里叶级数拆解得到的各路基础正弦分量")
            ax_parts.set_xlabel("时间 t")
            ax_parts.legend(fontsize=8)
            ax_parts.grid(alpha=0.3)

            ax_spec = fig3.add_subplot(gs[:,1])
            freqs_omega = []
            amps_spec = []
            for k, amp, _ in components:
                omega_k = 2 * np.pi * k * f0
                freqs_omega.append(omega_k)
                amps_spec.append(amp)
            ax_spec.stem(freqs_omega, amps_spec, basefmt=" ", linefmt="#ff4444", markerfmt="o")
            ax_spec.set_title("侧面投影 → 频域（离散谱线）")
            ax_spec.set_xlabel("角频率 ω")
            ax_spec.set_ylabel("分量幅度")
            ax_spec.grid(alpha=0.3)

            plt.subplots_adjust(left=0.07, bottom=0.12, right=0.97, top=0.92, hspace=0.42, wspace=0.32)
            st.pyplot(fig3)
            plt.close(fig3)

        st.markdown("""
> ✨理解重点：
> 同一个信号两种视角：
> - 正着看（X=时间）：时域波形；
> - 转90度侧面看（X=角频率）：频域，每一根竖线代表某一个频率分量的强弱。
""")

        # --------3‑1 三维投影示意图【改为Plotly3D】--------
        st.subheader("3‑1 三维直观演示：时域分量向频率平面做侧面投影")
        col3d_left, col3d_right = st.columns([1,1.3])
        with col3d_left:
            st.markdown("""
**三维视图说明**
- X轴：时间 $t$
- Y轴：角频率 $\\omega$（不同谐波分布在不同Y高度）
- Z轴：信号幅值

每一条曲线代表一个谐波在自己频率上随时间振荡；
灰色虚线：**向Y‑Z平面（ω‑幅度平面）投影**；
投影之后就得到右侧2D频域谱线。
""")

        with col3d_right:
            fig_proj_3d = go.Figure()
            color_list3d = ["#1f77b4","#2ca02c","#ff7f0e","#9467bd","#8c564b","#17becf","#d62728","#7f7f7f"]
            for idx,(k, amp, sig) in enumerate(components):
                omega_k = 2 * np.pi * k * f0
                c = color_list3d[idx % len(color_list3d)]
                fig_proj_3d.add_trace(go.Scatter3d(
                    x=t3,
                    y=np.full_like(t3, omega_k),
                    z=sig,
                    mode="lines",
                    line=dict(color=c, width=3),
                    name=f"k={k}"
                ))
                # 灰色投影虚线
                fig_proj_3d.add_trace(go.Scatter3d(
                    x=[0,0], y=[omega_k, omega_k], z=[0, amp],
                    mode="lines",
                    line=dict(color="#888888", dash="dash", width=2),
                    showlegend=False
                ))
                fig_proj_3d.add_trace(go.Scatter3d(
                    x=[0], y=[omega_k], z=[amp],
                    mode="markers",
                    marker=dict(color=c, size=4),
                    showlegend=False
                ))

            fig_proj_3d.update_layout(
                title=dict(text="傅里叶分量三维 + 侧面投影示意", x=0.5),
                scene=dict(
                    xaxis_title="时间 t",
                    yaxis_title="角频率 ω",
                    zaxis_title="幅值",
                ),
                height=520,
                margin=dict(l=0,r=0,b=0,t=40)
            )
            st.plotly_chart(fig_proj_3d, use_container_width=True)

        st.markdown("---")

        # ===================== 4.周期函数频域离散 =====================
        st.subheader("4. 周期函数的频域是离散的，周期越大，频域谱线越密集")
        col_e, col_f = st.columns([1,1])
        with col_e:
            st.markdown(""" > 周期函数的频域是离散的，周期越大，侧面的信号频域图越密集 """)
            T_period = st.slider("设置信号周期 T", min_value=0.5, max_value=4.0, value=1.0, step=0.25)
        with col_f:
            N4 = 1200
            t4 = np.linspace(0, 8, N4, endpoint=False)
            omega0 = 2*np.pi / T_period
            sig_sq = np.zeros_like(t4)
            harmonics = list(range(1,13,2))
            for n in harmonics:
                sig_sq += (4/(n*np.pi)) * np.sin(n * omega0 * t4)

            fft4 = np.fft.fft(sig_sq)
            freq4 = np.fft.fftfreq(N4, d=t4[1]-t4[0])
            omega4 = 2*np.pi*freq4
            amp4 = np.abs(fft4)/N4

            fig4, (ax4t, ax4f) = plt.subplots(2,1, figsize=(6,3.6))
            ax4t.plot(t4, sig_sq, color="#9467bd")
            ax4t.set_title(f"周期T={T_period} 的方波时域")
            ax4t.set_xlabel("时间 t")
            ax4t.grid(alpha=0.3)

            mask4 = omega4 >= 0
            ax4f.stem(omega4[mask4], amp4[mask4], basefmt=" ", linefmt="#ff7f0e")
            ax4f.set_title("离散频域谱线，周期越大谱线越密")
            ax4f.set_xlabel("角频率 ω")
            ax4f.grid(alpha=0.3)
            plt.subplots_adjust(left=0.13, bottom=0.14, right=0.96, top=0.91, hspace=0.42)
            st.pyplot(fig4)
            plt.close(fig4)

        st.markdown("---")

        # ===================== 5.非周期函数频域连续 =====================
        st.subheader("5. 非周期函数：周期视作无限大 → 频域变为连续")
        col_g, col_h = st.columns([1,1])
        with col_g:
            st.markdown(""" > 非周期函数可以理解为周期无限大的周期信号，频域图就是连续的 """)
        with col_h:
            t5 = np.linspace(-4,4,2000)
            tau = 1.0
            rect = np.where(np.abs(t5)<tau/2, 1, 0)
            N5 = len(t5)
            dt5 = t5[1]-t5[0]
            fft5 = np.fft.fftshift(np.fft.fft(rect))
            omega5 = np.fft.fftshift(np.fft.fftfreq(N5, d=dt5)) * 2*np.pi
            amp5 = np.abs(fft5)*dt5

            fig5, (ax5t, ax5f) = plt.subplots(2,1, figsize=(6,3.6))
            ax5t.plot(t5, rect, color="#8c564b")
            ax5t.set_title("非周期矩形脉冲时域")
            ax5t.set_xlabel("时间 t")
            ax5t.grid(alpha=0.3)

            ax5f.plot(omega5, amp5, color="#e377c2")
            ax5f.set_title("非周期信号 → 连续频谱（无离散谱线）")
            ax5f.set_xlabel("角频率 ω")
            ax5f.set_xlim([-30,30])
            ax5f.grid(alpha=0.3)
            plt.subplots_adjust(left=0.13, bottom=0.14, right=0.96, top=0.91, hspace=0.42)
            st.pyplot(fig5)
            plt.close(fig5)

        st.markdown("---")

        # ===================== 6.核心公式总结 =====================
        st.subheader("6.核心公式总结")
        st.markdown(r"""
> **傅里叶变换：实现时域和频域转换**
> **傅里叶级数：任何周期函数都可以用正弦函数和余弦函数构成的无穷级数表示**
> 把一个复杂的周期波形分解成了多个高矮不同的正余弦波形
#### 欧拉公式（连接三角函数与复指数）
$$ e^{j\omega t}=\cos(\omega t)+j\sin(\omega t) $$
$$ \cos(\omega t)=\frac{e^{j\omega t}+e^{-j\omega t}}{2},\quad \sin(\omega t)=\frac{e^{j\omega t}-e^{-j\omega t}}{2j} $$
### 傅里叶级数三角形式：
$$ f(t)=\frac{a_0}{2}+\sum_{n=1}^{\infty}\big[a_n\cos(n\omega_0 t)+b_n\sin(n\omega_0 t)\big] $$
$$ a_n=\frac{2}{T}\int_{0}^{T}f(t)\cos(n\omega_0 t)dt,\quad b_n=\frac{2}{T}\int_{0}^{T}f(t)\sin(n\omega_0 t)dt $$

### 傅里叶级数指数（复指数）形式
$$ f(t)=\sum_{n=-\infty}^{+\infty} c_n e^{jn\omega_0 t} $$
$$ c_n=\frac{1}{T}\int_{0}^{T} f(t) e^{-jn\omega_0 t} dt $$

**傅里叶变换：**
$$ F(\omega)=\int_{-\infty}^{+\infty} f(t) e^{-j\omega t} dt $$
""")

        st.markdown("---")

        # ===================== 7.方波三维分解【Plotly3D重写】 =====================
        st.subheader("7. 🎯三维可视化：周期方波分解为多层正余弦分量")
        st.markdown("> 复杂周期信号通过傅里叶级数分解成多个正余弦信号的三维图")

        col_ctrl, col_plot3d = st.columns([1, 2])
        with col_ctrl:
            num_harm = st.slider("选取谐波分解数量", min_value=1, max_value=15, value=5)
            t_3d = np.linspace(0, 2*np.pi, 600)
            omega0_3d = 1.0

        with col_plot3d:
            fig3d = go.Figure()
            accum = np.zeros_like(t_3d)
            harmonic_list = [2*k-1 for k in range(1, num_harm+1)]
            color_list3d = ["#1f77b4","#2ca02c","#ff7f0e","#9467bd","#8c564b","#17becf","#d62728","#7f7f7f"]
            for idx, n in enumerate(harmonic_list):
                amp = 4/(n*np.pi)
                comp = amp * np.sin(n * omega0_3d * t_3d)
                fig3d.add_trace(go.Scatter3d(
                    x=t_3d,
                    y=np.full_like(t_3d, n),
                    z=comp,
                    mode="lines",
                    line=dict(color=color_list3d[idx%len(color_list3d)], width=3),
                    name=f"n={n}谐波"
                ))
                accum += comp

            max_n = harmonic_list[-1]
            fig3d.add_trace(go.Scatter3d(
                x=t_3d,
                y=np.full_like(t_3d, max_n+2),
                z=accum,
                mode="lines",
                line=dict(color="red", width=4),
                name="合成复杂周期信号"
            ))

            fig3d.update_layout(
                title=dict(text="傅里叶级数三维分解：每层代表一个正余弦分量", x=0.5),
                scene=dict(
                    xaxis_title="时间 t",
                    yaxis_title="谐波阶数 n（代表不同频率）",
                    zaxis_title="信号幅值",
                ),
                height=520,
                margin=dict(l=0,r=0,b=0,t=40),
                legend=dict(orientation="v")
            )
            st.plotly_chart(fig3d, use_container_width=True)

        st.markdown("""
💡三维图解读：
- X轴：时间； Y轴：谐波阶数（对应不同频率）； Z轴：信号幅值
- 每一层Y高度上的曲线：就是傅里叶级数里的某一条正弦分量
- 红色曲线：把所有层正余弦全部叠加，还原原始复杂周期波形

调节滑块增加谐波数量，可以看到合成波形越来越接近方波。
""")
        st.markdown("---")

        # ===================== 8.能量谱、功率谱 =====================
        st.subheader("8. 能量谱和功率谱")
        st.markdown(r"""
        幅度谱$|F(\omega)|$只反映各个频率分量的幅度大小。通信系统中，我们更关心**能量、功率在频率维度如何分布**，也就是能量谱密度ESD、功率谱密度PSD。

            > ⚠核心前提：信号分为**能量信号**和**功率信号**，二者不能混用公式！
            > - 能量信号：总能量有限，平均功率为0，适合非周期脉冲；
            > - 功率信号：平均功率有限，总能量无穷大，适合周期信号、随机噪声。
        """)

        st.markdown("#### 8.1 能量信号与功率信号判定")
        col_def1, col_def2 = st.columns(2)
        with col_def1:
            st.markdown(r"""
        **🔹能量信号**
        $$
        E=\int_{-\infty}^{+\infty}|f(t)|^2 dt < \infty
        $$
        - 总能量$E$有限；
        - 平均功率 $P=0$；
        - 典型例子：单脉冲、矩形脉冲；
        - 只能定义**能量谱密度ESD**，不能求平均功率。
        """)
        with col_def2:
            st.markdown(r"""
        **🔹功率信号**
        $$
        P=\lim_{T \to \infty}\frac{1}{T}\int_{-T/2}^{T/2}|f(t)|^2 dt < \infty
        $$
        - 平均功率$P$有限；
        - 总能量 $E\to\infty$；
        - 典型例子：周期方波、正弦波、AWGN噪声；
        - 只能定义**功率谱密度PSD**，不能求总能量。
        """)

        st.info("💡考试易错：能量信号不要计算平均功率；功率信号不要计算总能量，二者公式不能交叉套用。")
        st.markdown("""
        |类型|总能量E|平均功率P|适用谱|典型信号|
        |----|-------|---------|------|--------|
        |能量信号|有限|0|能量谱ESD|单矩形脉冲|
        |功率信号|无穷大|有限|功率谱PSD|周期方波、正弦、噪声|
        """)

        import streamlit as st

        st.markdown("#### 8.2 帕塞瓦尔能量定理（能量信号）")
        st.markdown(r"""
        帕塞瓦尔定理：信号时域总能量 = 频域积分总能量，能量在时域、频域守恒。

        $$
        E=\int_{-\infty}^{+\infty}|f(t)|^2 dt =\frac{1}{2\pi}\int_{-\infty}^{+\infty}|F(\omega)|^2 d\omega
        $$

        **能量谱密度ESD定义：**

        $$
        \boldsymbol{E(\omega)=|F(\omega)|^2}
        $$

        $E(\omega)$：单位角频率上的信号能量，单位 $\text{J/rad}$。
        对能量谱密度在全角频率积分，就得到信号总能量。

        $$
        E=\frac{1}{2\pi}\int_{-\infty}^{+\infty} E(\omega)\,d\omega
        $$

        > $|F(\omega)|$：幅度谱；$|F(\omega)|^2$：能量谱密度。
        """)

        st.markdown("#### 8.3 帕塞瓦尔功率定理（功率信号）")
        st.markdown(r"""
        周期信号（功率信号），傅里叶级数复系数 $c_n$，各次谐波功率相加等于信号平均功率。

        $$
        P=\sum_{n=-\infty}^{\infty}|c_n|^2
        $$

        **功率谱密度PSD $P(\omega)$**：描述功率在角频率上的分布，单位 $\text{W/rad}$。
        - 周期信号PSD：是冲激串，冲激强度等于 $2\pi|c_n|^2$，离散；
        - 非周期随机信号（AWGN噪声）PSD：连续曲线。

        > 周期信号功率全部集中在离散谱线位置；随机噪声功率散布在整个连续频率轴。
        """)

        st.divider()
        st.subheader("📊交互式演示1：能量信号 — 矩形脉冲（能量谱ESD）")
        st.markdown("矩形脉冲是非周期能量信号，观察：时域→幅度谱→能量谱。")
        col_esd_ctrl, col_esd_fig = st.columns([1, 2.3])
        with col_esd_ctrl:
            tau_esd = st.slider("矩形脉冲脉宽 τ", min_value=0.2, max_value=2.0, value=1.0, step=0.1)
            t_esd = np.linspace(-6, 6, 2500)
            dt_esd = t_esd[1] - t_esd[0]
            rect_esd = np.where(np.abs(t_esd) < tau_esd / 2, 1.0, 0.0)
            N_esd = len(t_esd)

            # FFT 正确缩放，连续傅里叶变换近似
            fft_esd = np.fft.fftshift(np.fft.fft(rect_esd))
            omega_esd = np.fft.fftshift(np.fft.fftfreq(N_esd, d=dt_esd)) * 2 * np.pi
            Fw_esd = fft_esd * dt_esd

            Amp_spec = np.abs(Fw_esd)  # 幅度谱 |F(ω)|
            ESD_spec = np.abs(Fw_esd) ** 2  # 能量谱密度 E(ω)=|F(ω)|²

            # 数值计算总能量，时域 & 频域，验证帕塞瓦尔
            E_time = trapz(np.abs(rect_esd) ** 2, t_esd)
            E_freq = (1 / (2 * np.pi)) * trapz(ESD_spec, omega_esd)
            st.success(f"时域计算总能量E={E_time:.3f}，频域帕塞瓦尔E={E_freq:.3f}")
            st.markdown("""
        💡观察现象：
        1. 脉宽τ越小，脉冲越窄；频谱主瓣越宽；
        2. 幅度谱是Sa函数形状；
        3. 能量谱等于幅度谱平方，能量主要集中在主瓣；
        """)

        with col_esd_fig:
            fig_esd_all, axes_esd = plt.subplots(3, 1, figsize=(10, 5.2))
            axet, ax_amp, ax_esd = axes_esd

            axet.plot(t_esd, rect_esd, color="#2ca02c", lw=2)
            axet.set_title(f"时域：矩形脉冲 τ={tau_esd}")
            axet.set_xlabel("$t$")
            axet.grid(alpha=0.3)
            axet.set_xlim([-6, 6])

            ax_amp.plot(omega_esd, Amp_spec, color="#1f77b4", lw=1.8)
            ax_amp.set_title("幅度谱 $|F(\\omega)|$")
            ax_amp.set_xlabel("$\\omega$")
            ax_amp.set_xlim([-40, 40])
            ax_amp.grid(alpha=0.3)

            ax_esd.plot(omega_esd, ESD_spec, color="#d62728", lw=1.8)
            ax_esd.set_title("能量谱密度 $E(\\omega)=|F(\\omega)|^2$")
            ax_esd.set_xlabel("$\\omega$")
            ax_esd.set_xlim([-40, 40])
            ax_esd.grid(alpha=0.3)

            plt.subplots_adjust(left=0.09, bottom=0.08, right=0.96, top=0.94, hspace=0.48)
            st.pyplot(fig_esd_all)
            plt.close(fig_esd_all)

        st.divider()
        st.subheader("📊交互式演示2：功率信号 — 周期方波（功率谱PSD）")
        st.markdown("周期方波属于功率信号，频谱为离散谱线；功率谱为 $|c_n|^2$。")
        col_psd_ctrl, col_psd_fig = st.columns([1, 2.3])
        with col_psd_ctrl:
            T_psd = st.slider("方波周期T", min_value=1.0, max_value=4.0, value=2.0, step=0.25)
            N_harm_show = st.slider("显示谐波最高阶数", min_value=1, max_value=15, value=9, step=2)
            w0_psd = 2 * np.pi / T_psd

            t_psd = np.linspace(0, 6, 2000, endpoint=False)
            sq_psd = np.zeros_like(t_psd)
            harm_n_list = list(range(1, N_harm_show + 1, 2))
            c_n_list = []
            w_list_psd = []
            for n in harm_n_list:
                cn_amp = 4 / (n * np.pi)
                sq_psd += cn_amp * np.sin(n * w0_psd * t_psd)
                c_n_list.append(cn_amp)
                w_list_psd.append(n * w0_psd)

            power_harm = np.array(c_n_list) ** 2
            P_calc = np.sum(power_harm)
            st.success(f"由傅里叶级数系数计算平均功率P ≈ {P_calc:.3f}")
            st.markdown("""
        💡观察现象：
        1. 周期信号频谱是离散谱线，只存在奇次谐波；
        2. 功率谱是 $|c_n|^2$，谱线高度快速衰减；
        3. 周期T变大，基波角频率$\\omega_0$变小，谱线变密集。
        """)

        with col_psd_fig:
            fig_psd_all, axes_psd = plt.subplots(3, 1, figsize=(10, 5.2))
            axpt, ax_amp_spec, ax_psd_spec = axes_psd

            axpt.plot(t_psd, sq_psd, color="#9467bd", lw=2)
            axpt.set_title(f"时域周期方波，周期T={T_psd}")
            axpt.set_xlabel("$t$")
            axpt.grid(alpha=0.3)

            ax_amp_spec.stem(w_list_psd, np.array(c_n_list), basefmt=" ", linefmt="#ff7f0e", markerfmt="o")
            ax_amp_spec.set_title("幅度谱 |$c_n$| 离散谱线")
            ax_amp_spec.set_xlabel("$\\omega$")
            ax_amp_spec.grid(alpha=0.3)

            ax_psd_spec.stem(w_list_psd, power_harm, basefmt=" ", linefmt="#d62728", markerfmt="o")
            ax_psd_spec.set_title("功率谱 $|c_n|^2$")
            ax_psd_spec.set_xlabel("$\\omega$")
            ax_psd_spec.grid(alpha=0.3)

            plt.subplots_adjust(left=0.09, bottom=0.08, right=0.96, top=0.94, hspace=0.48)
            st.pyplot(fig_psd_all)
            plt.close(fig_psd_all)

        st.divider()
        st.subheader("📊交互式演示3：随机功率信号 AWGN噪声功率谱（衔接2.4章节）")
        st.markdown("AWGN噪声是典型随机功率信号，时域无规律，功率谱密度为常数（白）。")
        col_awgn_ctrl, col_awgn_fig = st.columns([1, 2.3])
        with col_awgn_ctrl:
            np.random.seed(123)
            sigma_noise = st.slider("噪声σ", min_value=0.2, max_value=1.2, value=0.5, step=0.1)
            fs_awgn = 2000
            dur_awgn = 1.5
            t_awgn = np.linspace(0, dur_awgn, int(fs_awgn * dur_awgn))
            noise_awgn = sigma_noise * np.random.normal(0, 1, size=len(t_awgn))
            # 周期图法估计功率谱
            fft_noise = np.fft.fftshift(np.fft.fft(noise_awgn))
            f_awgn = np.fft.fftshift(np.fft.fftfreq(len(t_awgn), 1 / fs_awgn))
            psd_est = (np.abs(fft_noise) ** 2) / (fs_awgn * dur_awgn)
        with col_awgn_fig:
            fig_awgn, (axn_t, axn_f) = plt.subplots(2, 1, figsize=(10, 4.4))
            axn_t.plot(t_awgn, noise_awgn, color="#444444", lw=0.8)
            axn_t.set_title("AWGN噪声时域（随机，无确定波形）")
            axn_t.set_xlabel("$t$")
            axn_t.grid(alpha=0.3)

            axn_f.plot(f_awgn, psd_est, color="#17becf", alpha=0.7)
            axn_f.set_title("AWGN噪声功率谱（近似平坦）")
            axn_f.set_xlabel("$f$ (Hz)")
            axn_f.set_xlim([-800, 800])
            axn_f.grid(alpha=0.3)

            plt.subplots_adjust(left=0.09, bottom=0.10, right=0.96, top=0.93, hspace=0.42)
            st.pyplot(fig_awgn)
            plt.close(fig_awgn)

        st.markdown(r"""
> ✨重点总结复习（考试背诵）
> 1. 能量信号：$E<\infty,P=0$；能量谱 $E(\omega)=|F(\omega)|^2$；帕塞瓦尔能量守恒；非周期脉冲。
> 2. 功率信号：$P<\infty,E\to\infty$；周期信号功率谱离散，由$|c_n|^2$计算；周期信号、噪声。
> 3. 幅度谱：$|F(\omega)|$；能量谱：幅度谱平方；二者不要混淆。
> 4. 周期信号：频谱离散；非周期能量信号频谱连续；AWGN随机信号功率谱连续平坦。
""")
        st.markdown("---")

    # ========== 分支B：卷积交互式教学 ==========
    elif demo_mode == "conv":
        st.title("📡 信号与系统 — 卷积运算交互式演示")
        st.markdown(r"""
卷积是线性时不变系统LTI的核心运算
> 连续：$y(t)=x(t)*h(t)=\int_{-\infty}^{+\infty}x(\tau)h(t-\tau)d\tau$
>
> 离散：$y[n]=x[n]*h[n]=\sum_{k=-\infty}^{+\infty}x[k]h[n-k]$
""")

        mode = st.radio("请选择模块",
                    ["🔹连续信号卷积", "🔸离散信号卷积", "📌卷积重要性质"],
                    horizontal=True)

        # -------------------------- 模块1：连续信号卷积 --------------------------
        if mode == "🔹连续信号卷积":
            st.header("1. 连续时间信号卷积")
            st.subheader("📖卷积定义")
            st.latex(r"y(t) = x(t) * h(t) = \int_{-\infty}^{+\infty} x(\tau)\, h(t-\tau)\, d\tau")
            st.info("""
💡图解法四步：
1.反转：$h(\tau) \Rightarrow h(-\tau)$
2.移位：时移 $t$，得到 $h(t-\tau)$
3.相乘：$x(\tau) \cdot h(t-\tau)$
4.积分：相乘曲线下面积，就是 $y(t)$ 在该时刻的值
""")

            st.divider()
            sub_tab1, sub_tab2, sub_tab3 = st.tabs(["🎨图解法计算", "📝函数式计算法", "⚡利用卷积性质计算"])

            with sub_tab1:
                st.subheader("图解法演示：两个矩形脉冲卷积")
                t_shift = st.slider("时移参数 t (拖动滑块观察 h(t‑τ)移动)", min_value=-1.0, max_value=5.0, value=1.0, step=0.1)
                tau = np.linspace(-3, 7, 1200)

                # 定义门函数 0~2 幅度1
                def x_cont(t):
                    return np.where((t >= 0) & (t <= 2), 1.0, 0.0)
                def h_cont(t):
                    return np.where((t >= 0) & (t <= 2), 1.0, 0.0)

                x_tau = x_cont(tau)
                h_t_shift = h_cont(t_shift - tau)
                product = x_tau * h_t_shift
                area = trapz(product, tau)

                fig, axes = plt.subplots(2, 2, figsize=(14, 8))
                ax1, ax2 = axes[0]
                ax3, ax4 = axes[1]

                ax1.plot(tau, x_tau, "b", lw=2.2, label=r"$x(\tau)$")
                ax1.set_title(r"① 原信号 $x(\tau)$")
                ax1.grid(alpha=0.3)
                ax1.legend()

                ax2.plot(tau, h_t_shift, "r", lw=2.2, label=f"$h(t-\\tau),\ t={t_shift:.2f}$")
                ax2.set_title(r"②反转+移位 $h(t-\tau)$")
                ax2.grid(alpha=0.3)
                ax2.legend()

                ax3.plot(tau, product, color="#229922", lw=2)
                ax3.fill_between(tau, product, alpha=0.45, color="#22bb22")
                ax3.set_title(f"③相乘结果，阴影积分面积 = {area:.3f}")
                ax3.grid(alpha=0.3)

                # 解析生成三角波，消除数值积分bug
                t_full = np.linspace(-2, 8, 1000)
                y_full = np.zeros_like(t_full)
                for i, t in enumerate(t_full):
                    if 0 <= t < 2:
                        y_full[i] = t
                    elif 2 <= t < 4:
                        y_full[i] = 4 - t
                    else:
                        y_full[i] = 0

                ax4.plot(t_full, y_full, "m", lw=2.5, label="$y(t)=x(t)*h(t)$")
                ax4.axvline(t_shift, color="k", linestyle="--", label=f"当前t={t_shift:.2f}")
                ax4.scatter(t_shift, area, c="black", s=70, zorder=10)
                ax4.set_title("④完整卷积输出 y(t)")
                ax4.grid(alpha=0.3)
                ax4.legend()
                ax4.set_ylim(-0.1, 2.2)

                plt.subplots_adjust(left=0.07, bottom=0.08, right=0.97, top=0.94, hspace=0.44, wspace=0.32)
                st.pyplot(fig)
                plt.close(fig)

            with sub_tab2:
                st.subheader("函数式解析计算法")
                st.markdown("""
已知两个矩形脉冲： $x(t)=u(t)-u(t-2)$，$h(t)=u(t)-u(t-2)$
$$ y(t)=x(t)*h(t)=\int_{-\infty}^{+\infty}x(\tau)h(t-\tau)d\tau $$
需要分段讨论积分上下限，得到分段结果：
""")
                st.latex(r"""
y(t)=
\begin{cases}
0 & t<0\\
t & 0\le t<2\\
4-t & 2\le t<4\\
0 & t\ge4
\end{cases}
""")
                st.warning("⚠函数式计算难点：需要分段判断两个信号重叠区间，确定积分上下限。")

            with sub_tab3:
                st.subheader("利用卷积性质计算（考试快速解题）")
                st.markdown("""
不用直接算复杂积分，借助性质化简：
1. **微分性质**：$x*h = x'(t) * \int h(\tau)d\tau$
2. 矩形脉冲求导得到冲激信号，冲激卷积直接移位复制信号
3. 结合时移、分配律、结合律快速求解

> 做题技巧：遇到门函数、三角脉冲优先微分得到冲激，用冲激卷积性质简化运算。
""")
                st.latex(r"x(t)*h(t)=\frac{dx(t)}{dt} * \left(\int_{-\infty}^t h(\tau)d\tau\right)")

        # --------------------------模块2：离散信号卷积 --------------------------
        elif mode == "🔸离散信号卷积":
            st.header("2.离散时间信号卷积")
            st.subheader("📖卷积定义")
            st.latex(r"y[n]=x[n]*h[n]=\sum_{k=-\infty}^{\infty} x[k]\, h[n-k]")
            st.info("离散卷积四步：反转 →移位 →相乘 →求和")

            st.divider()
            s1, s2, s3 = st.tabs(["🎲图解法演示", "✏对位相乘法", "💻函数式numpy计算"])

            with s1:
                st.subheader("自定义输入序列，观察卷积结果")
                c1, c2 = st.columns(2)
                with c1:
                    x_str = st.text_input("输入x[n]，逗号分隔数字", value="1,2,3")
                with c2:
                    h_str = st.text_input("输入h[n]，逗号分隔数字", value="1,1")
                try:
                    xn = np.array([float(i.strip()) for i in x_str.split(",")])
                    hn = np.array([float(i.strip()) for i in h_str.split(",")])
                    yn = np.convolve(xn, hn)
                    Nx = len(xn)
                    Nh = len(hn)
                    Ny = len(yn)
                    st.write(f"$x[n] = $ {xn}")
                    st.write(f"$h[n] = $ {hn}")
                    st.success(f"卷积结果 $y[n]=x[n]*h[n] =$ {yn}")

                    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16,4))
                    ax1.stem(np.arange(Nx), xn, basefmt=" ")
                    ax1.set_title("$x[n]$")
                    ax1.grid(alpha=0.3)
                    ax2.stem(np.arange(Nh), hn, basefmt=" ")
                    ax2.set_title("$h[n]$")
                    ax2.grid(alpha=0.3)
                    ax3.stem(np.arange(Ny), yn, basefmt=" ")
                    ax3.set_title("$y[n]=x[n]*h[n]$")
                    ax3.grid(alpha=0.3)
                    plt.subplots_adjust(left=0.05, bottom=0.18, right=0.97, top=0.86, wspace=0.35)
                    st.pyplot(fig)
                    plt.close(fig)
                    st.markdown(f">输出序列长度公式：$N_y = N_x + N_h -1 = {Nx}+{Nh}-1={Ny}$")
                except Exception as err:
                    st.warning(f"输入格式错误！请输入数字，逗号隔开。错误信息：{str(err)}")

            with s2:
                st.subheader("对位相乘法（手写考试专用）")
                st.markdown("""
做题步骤：
1.两个序列右对齐，像竖式乘法
2.逐位相乘，**相同n位置累加求和**
3.最终输出长度 $N_x+N_h-1$
> ⚠注意：不需要进位，只做相加！
""")
                st.code("""
示例 x=[1,2,3]  h=[4,5]
        1   2   3
    ×      4   5
-------------------
        5  10  15
     4   8  12
-------------------
     4  13  22  15
y[n] = [4, 13, 22, 15]
""")

            with s3:
                st.subheader("函数式计算 numpy.convolve")
                st.code("""
import numpy as np
x = np.array([1,2,3])
h = np.array([4,5])
y = np.convolve(x, h)
print(y)
""")
                st.markdown("""
`np.convolve(mode='full')` 默认完整卷积，对应信号课本定义。
其他模式：`same`/`valid`，信号系统一般使用 full。
""")

        # --------------------------新增模块3：卷积重要性质--------------------------
        elif mode == "📌卷积重要性质":
            st.header("3. 卷积重要性质（连续+离散）")
            prop_tab1, prop_tab2, prop_tab3, prop_tab4, prop_tab5 = st.tabs([
                "交换律｜结合律｜分配律",
                "时移性质",
                "冲激函数卷积性质",
                "微分性质",
                "积分性质"
            ])

            with prop_tab1:
                st.subheader("交换律、结合律、分配律")
                st.markdown(r"""
#### 交换律
连续：
$$ x(t)*h(t)=h(t)*x(t) $$
离散：
$$ x[n]*h[n]=h[n]*x[n] $$
> 物理含义：输入信号 $x$ 经过系统 $h$，等价于信号 $h$ 经过系统 $x$。

#### 结合律
$$ \big(x(t)*h_1(t)\big)*h_2(t) = x(t)*\big(h_1(t)*h_2(t)\big) $$
> 物理含义：两个LTI系统级联，总单位响应等于各自单位响应卷积；顺序可以调换。

#### 分配律
$$ x(t)*\big[h_1(t)+h_2(t)\big] = x(t)*h_1(t)+x(t)*h_2(t) $$
> 物理含义：两个LTI系统并联，总单位响应等于单位响应相加。
""")
                st.success("💡做题记忆：卷积满足交换、结合、分配，类似普通乘法；但是**没有除法**，不能直接“除去卷积”。")

            with prop_tab2:
                st.subheader("时移性质")
                st.markdown(r"""
> 若 $y(t)=x(t)*h(t)$
连续：
$$ x(t-t_0)*h(t) = y(t-t_0) $$
$$ x(t)*h(t-t_0) = y(t-t_0) $$

离散：若 $y[n]=x[n]*h[n]$
$$ x[n-n_0] * h[n] = y[n-n_0] $$

**文字总结：** 其中一个信号整体时移 $t_0$，卷积输出结果也整体时移 $t_0$。
""")
                st.warning("⚠两个信号同时移位：$x(t-t_1)*h(t-t_2)=y(t-t_1-t_2)$，移位相加。")

            with prop_tab3:
                st.subheader("冲激函数卷积性质（最常用）")
                st.markdown(r"""
$\delta(t)$ 单位冲激；$\delta[n]$ 单位样值序列。

连续：
$$ x(t)*\delta(t) = x(t) $$
$$ x(t)*\delta(t-t_0) = x(t-t_0) $$

离散：
$$ x[n]*\delta[n] = x[n] $$
$$ x[n]*\delta[n-n_0] = x[n-n_0] $$

> ✨核心结论：信号与冲激函数卷积，等价于**把信号复制一份，搬移到冲激所在位置**。
> 做题利器：任意信号可以分解成无数加权移位冲激的叠加，LTI系统输出就是各个冲激响应的移位叠加。
""")
                st.divider()
                st.markdown("示例：$x[n]=[1,3,2]$ 和移位冲激 $\\delta[n-2]$ 卷积")
                x_imp = np.array([1,3,2])
                delta2 = np.array([0,0,1])
                y_imp = np.convolve(x_imp, delta2)
                st.write(f"$x[n] = {x_imp}$")
                st.write(f"$\\delta[n-2] = {delta2}$")
                st.success(f"$x[n]*\\delta[n-2] = {y_imp}$，信号整体向右移位2位")

            with prop_tab4:
                st.subheader("卷积微分性质")
                st.markdown(r"""
$$ \frac{d}{dt}\big[x(t)*h(t)\big] = \frac{dx(t)}{dt} * h(t) = x(t) * \frac{dh(t)}{dt} $$
> 卷积之后再求导，等价于其中一个信号先求导，再卷积另一个原始信号。

**变形（高频）：**
$$ x(t)*h(t) = \frac{dx(t)}{dt} * \left(\int_{-\infty}^t h(\tau)d\tau\right) $$
> 含义：一个求导，另一个做积分，卷积结果不变。门函数求导得到冲激，就可以用冲激卷积性质快速计算，避开复杂积分。
""")

            with prop_tab5:
                st.subheader("卷积积分性质")
                st.markdown(r"""
定义 $x^{(-1)}(t)=\int_{-\infty}^{t}x(\tau)d\tau$ 代表信号的一次积分。
$$ \big[x(t)*h(t)\big]^{(-1)} = x^{(-1)}(t)*h(t) = x(t)*h^{(-1)}(t) $$
> 卷积之后积分 = 其中一个先积分，再卷积另一个原信号。
""")

# ====================== 2.2 信道分类与建模 ======================
elif module_sel == "2.2 信道分类与建模":
    st.title("📻 2.2 信道分类与建模")
    tab1, tab2, tab3, tab4 = st.tabs(["信道分类", "恒参信道", "随参信道", "信道数学模型"])

    with tab1:
        st.subheader("信道的定义")
        st.markdown(r"""
信道：发送端到接收端信号传输的物理媒介。
通信模型：
$$ \boldsymbol{s(t)} \xrightarrow{\text{信道}} \boldsymbol{r(t)} $$
接收信号 $r(t)$ 是发送信号经过信道畸变+噪声叠加。
""")
        st.subheader("信道分类")
        col_left, col_right = st.columns([1,1])
        with col_left:
            st.markdown("""
**1.按传输媒介划分**
- 有线信道：双绞线、同轴电缆、光纤
- 无线信道：自由空间、无线电波

**2.按参数是否随时间变化**
- **恒参信道**：信道参数不随时间变化（光纤、有线电缆）
- **随参信道**：信道参数随时间快速变化（移动通信无线信道）

**3.按输入输出信号类型**
- 连续信道（模拟信道）
- 离散信道（数字信道）

**4.有无噪声**
- 无噪声信道
- 有噪声信道
""")
        with col_right:
            # ========== 【最终防重叠版本】信道分类树状图 ==========
            fig, ax = plt.subplots(figsize=(12.5, 6.8))

            # 留出足够边距，防止左右边缘裁切
            ax.set_xlim(-0.5, 13.5)
            ax.set_ylim(0, 10)
            ax.axis("off")

            # 定义节点样式
            bbox_root = dict(boxstyle="round,pad=0.32", fc="#1f77b4", ec="black", alpha=0.75, color="white")
            bbox_level1 = dict(boxstyle="round,pad=0.28", fc="#ff7f0e", alpha=0.65)
            bbox_level2 = dict(boxstyle="round,pad=0.25", fc="#2ca02c", alpha=0.6)

            # 字体大小统一设置，避免自动缩放导致重叠
            font_root = {"fontsize": 15, "weight": "bold"}
            font_level1 = {"fontsize": 11}
            font_level2 = {"fontsize": 10}

            # 根节点：居中靠上
            root_x, root_y = 6.5, 9.2
            ax.text(root_x, root_y, "信道", ha="center", va="center", **font_root, bbox=bbox_root)

            # 一级节点：4个大类，横向均匀拉开
            level1 = [
                {"label": "按传输媒介", "x": 2.0, "y": 6.4},
                {"label": "按时变特性", "x": 4.3, "y": 6.4},
                {"label": "按信号类型", "x": 6.7, "y": 6.4},
                {"label": "按有无噪声", "x": 9.0, "y": 6.4},
            ]

            # 二级节点：每个一级节点下方左右分布
            children = [
                # 按传输媒介
                {"parent_x": 2.0, "parent_y": 6.4, "label": "有线信道", "x": 1.1, "y": 3.7},
                {"parent_x": 2.0, "parent_y": 6.4, "label": "无线信道", "x": 2.9, "y": 3.7},

                # 按时变特性
                {"parent_x": 4.3, "parent_y": 6.4, "label": "恒参信道", "x": 3.4, "y": 3.7},
                {"parent_x": 4.3, "parent_y": 6.4, "label": "随参信道", "x": 5.2, "y": 3.7},

                # 按信号类型
                {"parent_x": 6.7, "parent_y": 6.4, "label": "连续信道", "x": 5.8, "y": 3.7},
                {"parent_x": 6.7, "parent_y": 6.4, "label": "离散信道", "x": 7.6, "y": 3.7},

                # 按有无噪声
                {"parent_x": 9.0, "parent_y": 6.4, "label": "无噪声信道", "x": 8.1, "y": 3.7},
                {"parent_x": 9.0, "parent_y": 6.4, "label": "有噪声信道", "x": 9.9, "y": 3.7},
            ]

            # 绘制连接线：先画线，再画文字，避免文字被线遮挡
            for item in level1:
                ax.plot([root_x, item["x"]], [root_y, item["y"]], c="#333333", lw=1.2)

            for ch in children:
                ax.plot([ch["parent_x"], ch["x"]], [ch["parent_y"], ch["y"]], c="#555555", lw=1.0)

            # 绘制一级节点
            for item in level1:
                ax.text(item["x"], item["y"], item["label"], ha="center", va="center",
                        **font_level1, bbox=bbox_level1)

            # 绘制二级节点
            for ch in children:
                ax.text(ch["x"], ch["y"], ch["label"], ha="center", va="center",
                        **font_level2, bbox=bbox_level2)

            ax.set_title("信道分类树状图", fontsize=14, pad=20)

            # 调整边距，避免标题和节点被裁切
            plt.subplots_adjust(left=0.01, bottom=0.01, right=0.99, top=0.96)

            st.pyplot(fig)
            plt.close(fig)

    with tab2:
        st.subheader("恒参信道（时不变信道 LTI）")
        st.markdown(r"""
信道冲激响应 $h(t)$ 不随时间改变，属于**线性时不变LTI系统**。

接收信号：
$$ r(t) = s(t) * h(t) + n(t) $$

特点：
1. 冲激响应固定；
2. 会产生幅度衰减、固定时延；
3. 存在幅频失真、相频失真；
4. 光纤、有线电缆属于典型恒参信道。
""")
        col_ctrl, col_plot = st.columns([1,2])
        with col_ctrl:
            atten = st.slider("幅度衰减系数", min_value=0.2, max_value=1.0, value=0.7, step=0.05)
            delay = st.slider("信道固定时延", min_value=0.0, max_value=0.8, value=0.2, step=0.05)
            t = np.linspace(0,3,1000)
            s = np.sin(2*np.pi*3*t)*np.where((t>0.2)&(t<1.8),1,0)
            # 恒参信道：衰减+固定时延
            r_const = np.zeros_like(t)
            idx_delay = np.searchsorted(t, delay)
            r_const[idx_delay:] = atten * s[:len(t)-idx_delay]
        with col_plot:
            fig, (ax1,ax2) = plt.subplots(2,1,figsize=(9,4.2))
            ax1.plot(t,s,color="#1f77b4",label="发送信号 s(t)")
            ax1.set_title("发送信号")
            ax1.grid(alpha=0.3)
            ax1.legend()
            ax2.plot(t,r_const,color="#d62728",label="接收信号 r(t)（恒参信道）")
            ax2.set_title("经过恒参信道：衰减 + 固定时延")
            ax2.grid(alpha=0.3)
            ax2.legend()
            plt.subplots_adjust(left=0.08, bottom=0.14, right=0.96, top=0.92, hspace=0.4)
            st.pyplot(fig)
            plt.close(fig)

    with tab3:
        st.subheader("随参信道（时变信道 LTV）")
        st.markdown(r"""
冲激响应 $h(t,\tau)$ 同时和时间 $t$（观测时刻）、时延 $\tau$ 有关，**线性时变LTV系统**。

接收信号：
$$ r(t)=\int_{-\infty}^{+\infty} h(t,\tau)\, s(t-\tau) d\tau + n(t) $$

成因：多径传播，不同路径时延、增益随时间随机变化。
现象：**多径衰落、多普勒频移、瑞利衰落**。移动通信属于典型随参信道。
""")
        col_ctrl2, col_plot2 = st.columns([1,2])
        with col_ctrl2:
            multipath_count = st.slider("多径分量数目", min_value=2, max_value=6, value=3)
            t = np.linspace(0,3,1000)
            s_src = np.sin(2*np.pi*3*t)*np.where((t>0.2)&(t<1.8),1,0)
            r_timevar = np.zeros_like(t)
            np.random.seed(42)
            for _ in range(multipath_count):
                gain = np.random.uniform(0.2,0.8)
                dly = np.random.uniform(0.05,0.7)
                i_d = np.searchsorted(t, dly)
                if i_d < len(t):
                    r_timevar[i_d:] += gain * s_src[:len(t)-i_d]
        with col_plot2:
            fig, (ax1,ax2) = plt.subplots(2,1,figsize=(9,4.2))
            ax1.plot(t,s_src,color="#1f77b4",label="发送 s(t)")
            ax1.set_title("原始发送脉冲信号")
            ax1.grid(alpha=0.3)
            ax1.legend()
            ax2.plot(t,r_timevar,color="#9467bd",label="随参信道多径叠加 r(t)")
            ax2.set_title("随参信道：多条路径叠加，波形严重畸变")
            ax2.grid(alpha=0.3)
            ax2.legend()
            plt.subplots_adjust(left=0.08, bottom=0.14, right=0.96, top=0.92, hspace=0.4)
            st.pyplot(fig)
            plt.close(fig)

    with tab4:
        st.subheader("信道数学模型总结")
        st.markdown(r"""
1. **恒参信道（LTI）**
$$ r(t)=s(t)*h(t)+n(t) $$
冲激响应 $h(t)$ 与观测时刻 $t$ 无关。

2. **随参信道（LTV）**
$$ r(t)=\int h(t,\tau)s(t-\tau)d\tau + n(t) $$
$h(t,\tau)$：$t$ 接收时刻，$\tau$ 多径时延。

> 无线移动通信核心就是研究随参信道；光纤、有线直接用LTI模型。
""")
        st.warning("考试高频考点：区分恒参/随参信道；记住对应的冲激响应形式。")

# ====================== 2.3 衰减、时延与多径传播（重写增强版） ======================
elif module_sel == "2.3 衰减、时延与多径":
    st.title("📡 2.3 衰减、时延与多径传播")
    st.markdown("""
> 💡现实无线通信中，信号从发射端到接收端会发生三件事：
> ①**衰减**：信号越传越弱，功率不断下降；
> ②**传播时延**：信号传播需要时间，波形整体向后推迟；
> ③**多径效应**：信号经过反射散射产生多条副本，不同副本叠加造成波形畸变。
""")
    tab_atten, tab_delay, tab_multipath, tab_doppler = st.tabs(["🔻信号衰减", "⏱传播时延", "📶多径效应与时延扩展", "💨多普勒频移"])

    with tab_atten:
        st.subheader("🔻 什么是信号衰减（路径损耗）")
        st.markdown(r"""
**衰减：**信号在空间传输过程中，能量不断扩散损耗，距离越远，接收得到的信号功率越小。
自由空间电磁波向四周扩散，功率被摊薄；障碍物遮挡会进一步加剧衰减。

- $P_t$：发射功率
- $P_r$：接收功率
- $d$：收发之间距离
- $n$：路径损耗指数，代表环境衰减剧烈程度
  - 自由空间视距：$n=2$
  - 城市地面移动通信：$n=3\sim4$，衰减更快

功率关系：
$$
P_r \propto \frac{P_t}{d^n} 
$$

dB形式路径损耗：
$$
L_p(\text{dB})=10n\log_{10}(d) + C 
$$
> dB数值越大，代表损耗越大，收到信号越弱。
""")
        col_c, col_f = st.columns([1,2])
        with col_c:
            n_loss = st.slider("路径损耗指数 n", min_value=2.0, max_value=4.0, value=2.0, step=0.2)
            d_arr = np.linspace(1,100,500)
            Pr = 10/(d_arr**n_loss)
            st.info(f"n={n_loss}：n越大，随着距离增加，功率下降越猛烈。")
        with col_f:
            fig,ax = plt.subplots(figsize=(8,3.6))
            ax.plot(d_arr, 10*np.log10(Pr), color="#d62728", lw=2)
            ax.set_title(f"路径损耗曲线，n={n_loss}")
            ax.set_xlabel("传输距离 d")
            ax.set_ylabel("接收功率(dB)")
            ax.grid(alpha=0.3)
            plt.subplots_adjust(left=0.12, bottom=0.16, right=0.96, top=0.9)
            st.pyplot(fig)
            plt.close(fig)
        st.warning("📝考试要点：距离增大，接收功率下降；n越大衰减越快。")

    with tab_delay:
        st.subheader("⏱什么是传播时延")
        st.markdown("""
**传播时延：**电磁波传播速度有限，信号跑一段距离，需要消耗时间。
电磁波在空气中近似光速：

$$
c \approx 3 \times 10^8 \text{ m/s}
$$

$$
t_d = \frac{d}{c}
$$

- $d$：传输距离（米）
- $t_d$：传播时延（秒）

通俗理解：就像扔石头到水面，波纹不会瞬间到达对岸，需要等待一段时间。
- 有线信道：距离固定，时延固定；
- 无线多径场景：**每一条传播路径距离不一样，每一条路径的时延各不相同**。
""")
        d_input = st.number_input("传输距离 d (km)", min_value=1, max_value=1000, value=30)
        c = 3e8
        td = (d_input*1000)/c
        st.success(f"距离 {d_input} km，传播时延 $t_d$ = {td*1e6:.3f} μs")
        st.markdown(f"> {d_input}公里的距离，信号要跑 {td*1e6:.3f} 微秒才到达接收端。")

        # 时延波形可视化对比
        st.divider()
        st.subheader("波形直观演示：信号经过时延之后，整体向后平移")
        col_delay_ctrl, col_delay_fig = st.columns([1, 2])
        with col_delay_ctrl:
            t_delay_slider = st.slider("设置时延大小", min_value=0.0, max_value=0.8, value=0.2, step=0.05)
            t_demo = np.linspace(0,3,1000)
            s_origin = np.sin(2*np.pi*3*t_demo)*np.where((t_demo>0.2)&(t_demo<1.8),1,0)
            r_delay = np.zeros_like(t_demo)
            idx_d = np.searchsorted(t_demo, t_delay_slider)
            if idx_d < len(t_demo):
                r_delay[idx_d:] = s_origin[:len(t_demo)-idx_d]
        with col_delay_fig:
            fig_d, (axd1, axd2) = plt.subplots(2,1,figsize=(9,4.2))
            axd1.plot(t_demo, s_origin, color="#1f77b4", label="原始发送信号")
            axd1.set_title("发送信号")
            axd1.grid(alpha=0.3)
            axd1.legend()
            axd2.plot(t_demo, r_delay, color="#2ca02c", label=f"接收信号，时延={t_delay_slider:.2f}s")
            axd2.set_title("经过传播时延：波形形状不变，整体向后平移")
            axd2.grid(alpha=0.3)
            axd2.legend()
            plt.subplots_adjust(left=0.08, bottom=0.14, right=0.96, top=0.92, hspace=0.4)
            st.pyplot(fig_d)
            plt.close(fig_d)

    with tab_multipath:
        st.subheader("📶什么是多径效应 & 时延扩展")
        st.markdown("""
**多径效应：**无线信号遇到建筑、山体、树木发生反射、散射。
发射的同一个信号，会沿着多条不同路径到达接收天线。

每一条路径有自己的：
- 路径增益$a_i$（衰减大小）
- 传播时延$\tau_i$（路径长短不同）

接收信号就是所有路径副本叠加：
$$ r(t)=\sum_{i} a_i \cdot s(t-\tau_i) + n(t) $$

**时延扩展$\sigma_\tau$：**所有多径分量中，最大时延减去最小时延。
> ⚠严重后果：时延扩展过大，脉冲会被“拉长”，产生**码间干扰ISI**，前一个符号拖尾干扰后一个符号。
""")
        col_ctrl_mp, col_plot_mp = st.columns([1, 2])
        with col_ctrl_mp:
            path_num = st.slider("多径路径数量", min_value=2, max_value=7, value=4)
            t = np.linspace(0, 2, 1200)
            s_pulse = np.where(np.abs(t-0.4)<0.12, 1.0,0.0)
            r_mp = np.zeros_like(t)
            np.random.seed(10)
            for i in range(path_num):
                amp = np.random.uniform(0.2,0.9)
                tau_i = np.random.uniform(0.1,1.2)
                shift_idx = np.searchsorted(t, tau_i)
                if shift_idx < len(t):
                    r_mp[shift_idx:] += amp * s_pulse[:len(t)-shift_idx]
        with col_plot_mp:
            fig, (ax1,ax2) = plt.subplots(2,1,figsize=(9,4.4))
            ax1.plot(t,s_pulse,"b",lw=2,label="发送窄脉冲")
            ax1.set_title("发送端：一个很窄的脉冲")
            ax1.grid(alpha=0.3)
            ax1.legend()
            ax2.plot(t,r_mp,"#c41e3a",lw=2,label="多径叠加接收波形")
            ax2.set_title("接收端：多条路径叠加，脉冲被展宽（时延扩展）")
            ax2.grid(alpha=0.3)
            ax2.legend()
            plt.subplots_adjust(left=0.08, bottom=0.14, right=0.96, top=0.92, hspace=0.42)
            st.pyplot(fig)
            plt.close(fig)
        st.warning("💡考试高频：时延扩展 > 符号周期 → 码间干扰ISI，需要均衡器消除干扰。")
        st.info("💡生活例子：山谷里喊话，你会听到原声音+多次回声，回声就是多径分量。")

    with tab_doppler:
        st.subheader("💨什么是多普勒频移")
        st.markdown(r"""
**多普勒频移：**发射端和接收端存在相对运动，接收信号载波频率发生偏移。

物理现象：车向你开过来声音变尖，远离声音变低沉，无线通信同理。

$$ f_d = \frac{v}{\lambda}\cos\theta $$
- $v$：收发相对移动速度(m/s)
- $\lambda$：载波波长
- $\theta$：入射信号与运动方向夹角

- 移动速度越快，最大多普勒频移越大；
- 多普勒扩展大，代表信道随时间变化剧烈，属于**快衰落信道**。
""")
        v = st.slider("移动速度 v (km/h)", min_value=0, max_value=120, value=60)
        fc = st.number_input("载波频率 fc(MHz)", min_value=100, max_value=3000, value=900)
        v_ms = v / 3.6
        c = 3e8
        lam = c/(fc*1e6)
        fd_max = v_ms / lam
        st.success(f"最大多普勒频移 $f_d$ = {fd_max:.2f} Hz")

        fig,ax = plt.subplots(figsize=(7,3))
        v_list = np.linspace(0,120,200)
        vlist_ms = v_list/3.6
        fd_list = vlist_ms / lam
        ax.plot(v_list, fd_list, color="#2ca02c", lw=2)
        ax.axvline(v, linestyle="--",color="red", label=f"当前速度 {v} km/h")
        ax.set_xlabel("移动速度 km/h")
        ax.set_ylabel("最大多普勒频移 Hz")
        ax.set_title("多普勒频移随移动速度变化")
        ax.grid(alpha=0.3)
        ax.legend()
        plt.subplots_adjust(left=0.12, bottom=0.16, right=0.96, top=0.9)
        st.pyplot(fig)
        plt.close(fig)
        st.info("📝知识点：多径带来时延扩展（时域）；移动带来多普勒扩展（频域）。")

# ====================== 2.4 AWGN 加性高斯白噪声信道 ======================
elif module_sel == "2.4 AWGN":
    st.title("🔊 2.4 AWGN 加性高斯白噪声信道")
    tab_def, tab_time, tab_freq, tab_snr, tab_formula = st.tabs(["定义", "时域波形", "功率谱", "SNR信噪比", "核心公式总结"])

    with tab_def:
        st.markdown(r"""
### AWGN：Additive White Gaussian Noise 加性高斯白噪声
模型：
$$ r(t) = s(t)+n(t) $$
- **加性**：噪声直接叠加到信号上；
- **白**：功率谱密度在全频率范围内为常数；
- **高斯**：噪声时域采样服从高斯正态分布。

双边功率谱密度：
$$ P_n(f)=\frac{N_0}{2} \quad (\text{W/Hz}) $$
$N_0$ 为单边噪声功率谱密度。

> AWGN是通信最基础信道模型，课本大部分推导基于AWGN信道。
""")
        st.info("注意：白≠白色；白指功率谱平坦；高斯指幅度概率分布。")

    with tab_time:
        st.subheader("AWGN噪声时域波形")
        col_ctrl_t, col_plot_t = st.columns([1,2])
        with col_ctrl_t:
            noise_amp = st.slider("噪声强度", min_value=0.1, max_value=1.5, value=0.4, step=0.05)
            fs = 2000
            dur = 2
            t = np.linspace(0, dur, fs*dur)
            noise = noise_amp * np.random.normal(loc=0, scale=1, size=len(t))
            s_signal = np.sin(2*np.pi*5*t)
            r_rx = s_signal + noise
        with col_plot_t:
            fig, (ax1,ax2,ax3) = plt.subplots(3,1,figsize=(9,5.2))
            ax1.plot(t,s_signal,color="#1f77b4")
            ax1.set_title("原始发送信号 s(t)")
            ax1.grid(alpha=0.3)
            ax2.plot(t,noise,color="#d62728")
            ax2.set_title("AWGN噪声 n(t)")
            ax2.grid(alpha=0.3)
            ax3.plot(t,r_rx,color="#2ca02c")
            ax3.set_title("接收 r(t)=s(t)+n(t)")
            ax3.grid(alpha=0.3)
            plt.subplots_adjust(left=0.08, bottom=0.1, right=0.96, top=0.94, hspace=0.45)
            st.pyplot(fig)
            plt.close(fig)

    with tab_freq:
        st.subheader("AWGN功率谱密度")
        st.markdown(r"""
白噪声：功率谱密度在全部频率上保持恒定。
双边谱 $P_n(f)=\frac{N_0}{2}$。
""")
        N0_half = 0.3
        f_axis = np.linspace(-10,10,400)
        psd = np.full_like(f_axis, N0_half)
        fig,ax = plt.subplots(figsize=(8,3.6))
        ax.plot(f_axis, psd, color="#9467bd", lw=2)
        ax.set_title("AWGN双边功率谱密度")
        ax.set_xlabel("频率 f")
        ax.set_ylabel("$P_n(f)$")
        ax.set_ylim(0,0.6)
        ax.grid(alpha=0.3)
        plt.subplots_adjust(left=0.12, bottom=0.16, right=0.96, top=0.9)
        st.pyplot(fig)
        plt.close(fig)
        st.markdown("> 实际系统带宽有限，只有在系统带宽内表现为白色。")

    with tab_snr:
        st.subheader("信噪比 SNR")
        st.markdown(r"""
信噪比定义：信号功率 / 噪声功率
$$ SNR=\frac{P_s}{P_n} $$
dB形式：
$$ SNR(\text{dB})=10\log_{10}\left(\frac{P_s}{P_n}\right) $$
- SNR越大，噪声相对越小，接收质量越好；
- SNR越小，噪声大，信号被淹没。
""")
        snr_dB = st.slider("设置SNR(dB)", min_value=-10, max_value=20, value=6, step=1)
        Ps = 1.0
        Pn = Ps / (10**(snr_dB/10))
        sigma = np.sqrt(Pn)
        t_snr = np.linspace(0,1,1000)
        s_snr = np.cos(2*np.pi*4*t_snr)
        n_snr = sigma * np.random.normal(0,1,size=len(t_snr))
        r_snr = s_snr + n_snr

        fig, (ax1,ax2) = plt.subplots(2,1,figsize=(9,4.2))
        ax1.plot(t_snr, s_snr, "b")
        ax1.set_title("原始信号")
        ax1.grid(alpha=0.3)
        ax2.plot(t_snr, r_snr, "#c41e3a")
        ax2.set_title(f"接收信号 SNR={snr_dB} dB")
        ax2.grid(alpha=0.3)
        plt.subplots_adjust(left=0.08, bottom=0.14, right=0.96, top=0.92, hspace=0.4)
        st.pyplot(fig)
        plt.close(fig)
        st.success(f"信号功率Ps={Ps:.2f}，噪声功率Pn={Pn:.3f}")

    with tab_formula:
        st.subheader("AWGN核心公式汇总")
        st.markdown(r"""
1. 信道模型
$$ r(t)=s(t)+n(t) $$

2. 双边功率谱密度
$$ P_n(f)=\frac{N_0}{2} \quad (\text{W/Hz}) $$

3. 带宽B内噪声总功率
$$ P_n = N_0 \cdot B $$

4. 信噪比
$$ SNR=\frac{P_s}{P_n},\quad SNR_{\text{dB}}=10\log_{10}\frac{P_s}{P_n} $$

5. 噪声采样概率密度函数
$$ p(n)=\frac{1}{\sqrt{2\pi}\sigma}\exp\left(-\frac{n^2}{2\sigma^2}\right) $$
噪声方差 $\sigma^2=P_n$。
""")
        st.warning("考试高频：记住噪声功率 = $N_0 \\times B$；区分单边 $N_0$ 和双边 $N_0/2$。")
