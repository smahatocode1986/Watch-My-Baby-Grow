CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');
:root { --ink:#23312f; --muted:#6f7a75; --cream:#f7f4ed; --paper:#fffdfa; --coral:#e8785f; --teal:#3f7770; --line:#e7e1d6; }
.stApp { background: var(--cream); color: var(--ink); font-family:'DM Sans',sans-serif; }
.stApp h1,.stApp h2,.stApp h3 { font-family:'DM Serif Display',serif; color:var(--ink); letter-spacing:-.02em; }
[data-testid="stHeader"] { background:transparent; }
#MainMenu { visibility:hidden; }
[data-testid="stSidebar"] { background:#f0ebe2; border-right:1px solid var(--line); }
[data-testid="stSidebar"] h1 { font-size:1.55rem; }
.block-container { max-width:1180px; padding-top:1.6rem; padding-bottom:4rem; }
.brand-kicker { font-size:.72rem; letter-spacing:.17em; text-transform:uppercase; color:var(--teal); font-weight:700; }
.hero { min-height:320px; border-radius:28px; overflow:hidden; background:#f5e6d4 center/cover no-repeat; padding:46px 48px; display:flex; align-items:center; box-shadow:0 12px 40px rgba(58,55,45,.08); }
.hero-copy { width:46%; position:relative; z-index:2; }
.hero h1 { font-size:3.35rem; line-height:.98; margin:.3rem 0 1rem; }
.hero p { color:#5b6661; font-size:1.05rem; line-height:1.65; max-width:480px; }
.nutrition-hero { min-height:340px; border-radius:28px; overflow:hidden; background:#f5eee5 center/cover no-repeat; display:flex; align-items:center; padding:42px 46px; box-shadow:0 12px 40px rgba(58,55,45,.08); position:relative; }
.nutrition-hero::before { content:""; position:absolute; inset:0; background:linear-gradient(90deg,rgba(255,253,250,.98) 0%,rgba(255,253,250,.90) 30%,rgba(255,253,250,.18) 58%,rgba(255,253,250,0) 75%); }
.nutrition-hero-copy { width:43%; position:relative; z-index:1; }
.nutrition-hero h1 { font-size:3rem; line-height:1; margin:.4rem 0 1rem; }
.nutrition-hero p { color:#5b6661; font-size:1rem; line-height:1.65; max-width:440px; }
.eyebrow { color:var(--coral); text-transform:uppercase; letter-spacing:.15em; font-size:.72rem; font-weight:700; }
.section-head { display:flex; align-items:end; justify-content:space-between; margin:2rem 0 1rem; }
.section-head h2 { margin:0; font-size:1.75rem; }
.section-head span { color:var(--muted); font-size:.88rem; }
.metric-card,.soft-card,.agenda-card,.insight-card { background:rgba(255,253,250,.88); border:1px solid var(--line); border-radius:18px; padding:20px; box-shadow:0 5px 18px rgba(58,55,45,.04); }
.metric-label { color:var(--muted); text-transform:uppercase; letter-spacing:.1em; font-size:.68rem; font-weight:700; }
.metric-value { font-family:'DM Serif Display'; font-size:2rem; margin:.25rem 0 0; }
.metric-sub { color:var(--muted); font-size:.8rem; }
[data-testid="stMetric"] { background:linear-gradient(145deg,#fffdfa,#f8eee8); border-color:#eadbd0 !important; box-shadow:0 7px 22px rgba(84,65,55,.06); }
[data-testid="stMetric"] [data-testid="stMetricValue"] { color:var(--coral); }
[data-testid="stImage"] img { border-radius:22px; box-shadow:0 10px 28px rgba(58,55,45,.10); }
.agenda-card { min-height:170px; border-top:4px solid var(--coral); margin-bottom:.6rem; }
.agenda-card.teal{border-top-color:#4f8b82}.agenda-card.yellow{border-top-color:#dfa940}.agenda-card.lavender{border-top-color:#9580a7}.agenda-card.blue{border-top-color:#648aa3}
.agenda-time { color:var(--muted); font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; }
.agenda-card h3 { font-family:'DM Sans'; font-size:1.02rem; margin:.55rem 0; }
.agenda-card p { color:#66706c; font-size:.84rem; line-height:1.45; min-height:52px; }
.pill { display:inline-block; padding:5px 9px; background:#f3eee6; border-radius:20px; color:#6e746f; font-size:.67rem; }
.insight-card { min-height:155px; }
.insight-icon { width:34px;height:34px;border-radius:50%;display:grid;place-items:center;background:#e5f0ed;color:var(--teal);font-weight:700; }
.insight-card h3 { font-family:'DM Sans';font-size:.95rem;margin:.8rem 0 .3rem; }
.insight-card p { color:var(--muted);font-size:.82rem;line-height:1.5; }
.story-paper { background:#fffdf7; border:1px solid #e8decf; border-radius:22px; padding:30px 36px; box-shadow:0 12px 30px rgba(64,54,39,.06); }
.story-paper p { font-family:Georgia,serif; line-height:1.8; color:#3e4844; }
.timeline-card { position:relative; margin-left:12px; padding:4px 0 22px 28px; border-left:2px solid #ded8cc; }
.timeline-dot { position:absolute; left:-7px; top:8px; width:12px; height:12px; border-radius:50%; background:var(--coral); box-shadow:0 0 0 5px var(--cream); }
.timeline-card h4 { margin:.2rem 0 .25rem; font-size:1rem; color:var(--ink); }
.timeline-card p { margin:0 0 .55rem; color:var(--muted); line-height:1.5; }
.timeline-date { color:var(--teal); text-transform:uppercase; letter-spacing:.08em; font-size:.68rem; font-weight:700; }
.food-tag { display:inline-block; margin:0 5px 4px 0; padding:4px 8px; border-radius:99px; background:#e5f0ed; color:#3d6e67; font-size:.68rem; font-weight:700; }
.food-chart-head { text-align:center; padding:.35rem 0 .2rem; }
.food-chart-head span { color:#e8607a; text-transform:uppercase; letter-spacing:.16em; font-size:.7rem; font-weight:700; }
.food-chart-head h3 { margin:.2rem 0 0; font-size:1.55rem; }
.food-chart-head p { margin:.2rem 0 .3rem; color:#9b8890; font-size:.78rem; }
.status-live,.status-demo { display:inline-block;border-radius:99px;padding:5px 9px;font-size:.7rem;font-weight:700; }
.status-live{background:#dcefe8;color:#28715d}.status-demo{background:#f8e8cf;color:#875f21}
.privacy { background:#e9f1ef;border-radius:14px;padding:12px 14px;color:#49645e;font-size:.78rem;line-height:1.45; }
.stButton>button { border-radius:999px; border:none; background:var(--coral); color:white; font-weight:700; padding:.58rem 1.2rem; }
.stButton>button:hover { background:#cc654f; color:white; border:none; }
.stTextInput input,.stTextArea textarea,.stSelectbox [data-baseweb="select"] { border-radius:12px; background:#fffdfa; }
[data-baseweb="tab-list"] { gap:8px; background:#eee8dd; padding:5px; border-radius:999px; width:max-content; }
[data-baseweb="tab"] { border-radius:999px; padding:8px 18px; }
[aria-selected="true"] { background:#fffdfa !important; }
@media(max-width:800px){.hero{padding:28px;background-position:65% center}.hero-copy{width:70%;background:rgba(255,253,247,.85);padding:18px;border-radius:16px}.hero h1{font-size:2.2rem}.nutrition-hero{min-height:300px;padding:26px;background-position:62% center}.nutrition-hero::before{background:rgba(255,253,250,.72)}.nutrition-hero-copy{width:78%;background:rgba(255,253,250,.84);padding:18px;border-radius:16px}.nutrition-hero h1{font-size:2.25rem}}
</style>
"""
