CSS = r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=DM+Serif+Display&display=swap');

/* Light Theme (Default) */
:root {
  --ink: #23312f;
  --muted: #6f7a75;
  --cream: #f7f4ed;
  --paper: #fffdfa;
  --coral: #e8785f;
  --teal: #3f7770;
  --line: #e7e1d6;
  --text-primary: #23312f;
  --text-secondary: #6f7a75;
  --bg-primary: #f7f4ed;
  --bg-secondary: #fffdfa;
  --bg-tertiary: #f0ebe2;
  --card-bg: rgba(255, 253, 250, 0.88);
  --card-border: #e7e1d6;
  --shadow-light: rgba(58, 55, 45, 0.04);
  --shadow-medium: rgba(58, 55, 45, 0.06);
  --shadow-dark: rgba(58, 55, 45, 0.08);
  --shadow-darkest: rgba(58, 55, 45, 0.10);
}

/* Dark Theme */
@media (prefers-color-scheme: dark) {
  :root {
    --ink: #e8e5e0;
    --muted: #a0a8a5;
    --cream: #1a1915;
    --paper: #242220;
    --coral: #ff9d88;
    --teal: #6eb5ad;
    --line: #3a3530;
    --text-primary: #e8e5e0;
    --text-secondary: #a0a8a5;
    --bg-primary: #1a1915;
    --bg-secondary: #242220;
    --bg-tertiary: #2d2825;
    --card-bg: rgba(42, 40, 38, 0.6);
    --card-border: #3a3530;
    --shadow-light: rgba(0, 0, 0, 0.2);
    --shadow-medium: rgba(0, 0, 0, 0.3);
    --shadow-dark: rgba(0, 0, 0, 0.4);
    --shadow-darkest: rgba(0, 0, 0, 0.5);
  }
}

/* Base Styles */
.stApp {
  background: var(--bg-primary);
  color: var(--text-primary);
  font-family: 'DM Sans', sans-serif;
}

.stApp h1, .stApp h2, .stApp h3 {
  font-family: 'DM Serif Display', serif;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}

[data-testid="stHeader"] {
  background: transparent;
}

[data-testid="stSidebar"] {
  background: var(--bg-tertiary);
  border-right: 1px solid var(--card-border);
}

[data-testid="stSidebar"] h1 {
  font-size: 1.55rem;
}

.block-container {
  max-width: 1180px;
  padding-top: 1.6rem;
  padding-bottom: 4rem;
}

.brand-kicker {
  font-size: 0.72rem;
  letter-spacing: 0.17em;
  text-transform: uppercase;
  color: var(--teal);
  font-weight: 700;
}

/* Hero Section */
.hero {
  min-height: 320px;
  border-radius: 28px;
  overflow: hidden;
  background: #f5e6d4 center/cover no-repeat;
  padding: 46px 48px;
  display: flex;
  align-items: center;
  box-shadow: 0 12px 40px var(--shadow-dark);
}

@media (prefers-color-scheme: dark) {
  .hero {
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
  }
}

.hero-copy {
  width: 46%;
  position: relative;
  z-index: 2;
}

.hero h1 {
  font-size: 3.35rem;
  line-height: 0.98;
  margin: 0.3rem 0 1rem;
}

.hero p {
  color: #5b6661;
  font-size: 1.05rem;
  line-height: 1.65;
  max-width: 480px;
}

@media (prefers-color-scheme: dark) {
  .hero p {
    color: #b8bfbb;
  }
}

/* Nutrition Hero */
.nutrition-hero {
  min-height: 340px;
  border-radius: 28px;
  overflow: hidden;
  background: #f5eee5 center/cover no-repeat;
  display: flex;
  align-items: center;
  padding: 42px 46px;
  box-shadow: 0 12px 40px var(--shadow-dark);
  position: relative;
}

.nutrition-hero::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(255, 253, 250, 0.98) 0%, rgba(255, 253, 250, 0.90) 30%, rgba(255, 253, 250, 0.18) 58%, rgba(255, 253, 250, 0) 75%);
}

@media (prefers-color-scheme: dark) {
  .nutrition-hero::before {
    background: linear-gradient(90deg, rgba(36, 34, 32, 0.98) 0%, rgba(36, 34, 32, 0.90) 30%, rgba(36, 34, 32, 0.18) 58%, rgba(36, 34, 32, 0) 75%);
  }
}

.nutrition-hero-copy {
  width: 43%;
  position: relative;
  z-index: 1;
}

.nutrition-hero h1 {
  font-size: 3rem;
  line-height: 1;
  margin: 0.4rem 0 1rem;
}

.nutrition-hero p {
  color: #5b6661;
  font-size: 1rem;
  line-height: 1.65;
  max-width: 440px;
}

@media (prefers-color-scheme: dark) {
  .nutrition-hero p {
    color: #b8bfbb;
  }
}

/* Typography */
.eyebrow {
  color: var(--coral);
  text-transform: uppercase;
  letter-spacing: 0.15em;
  font-size: 0.72rem;
  font-weight: 700;
}

.section-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  margin: 2rem 0 1rem;
}

.section-head h2 {
  margin: 0;
  font-size: 1.75rem;
}

.section-head span {
  color: var(--text-secondary);
  font-size: 0.88rem;
}

/* Cards */
.metric-card, .soft-card, .agenda-card, .insight-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 18px;
  padding: 20px;
  box-shadow: 0 5px 18px var(--shadow-light);
}

.metric-label {
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-size: 0.68rem;
  font-weight: 700;
}

.metric-value {
  font-family: 'DM Serif Display';
  font-size: 2rem;
  margin: 0.25rem 0 0;
}

.metric-sub {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

[data-testid="stMetric"] {
  background: linear-gradient(145deg, #fffdfa, #f8eee8);
  border-color: #eadbd0 !important;
  box-shadow: 0 7px 22px rgba(84, 65, 55, 0.06);
}

@media (prefers-color-scheme: dark) {
  [data-testid="stMetric"] {
    background: linear-gradient(145deg, #2d2825, #3a3530);
    border-color: #4a4540 !important;
    box-shadow: 0 7px 22px rgba(0, 0, 0, 0.3);
  }
}

[data-testid="stMetric"] [data-testid="stMetricValue"] {
  color: var(--coral);
}

[data-testid="stImage"] img {
  border-radius: 22px;
  box-shadow: 0 10px 28px var(--shadow-darkest);
}

/* Agenda Cards */
.agenda-card {
  min-height: 170px;
  border-top: 4px solid var(--coral);
  margin-bottom: 0.6rem;
}

.agenda-card.teal {
  border-top-color: #4f8b82;
}

.agenda-card.yellow {
  border-top-color: #dfa940;
}

.agenda-card.lavender {
  border-top-color: #9580a7;
}

.agenda-card.blue {
  border-top-color: #648aa3;
}

@media (prefers-color-scheme: dark) {
  .agenda-card.teal {
    border-top-color: #7eb5ad;
  }

  .agenda-card.yellow {
    border-top-color: #e8b85e;
  }

  .agenda-card.lavender {
    border-top-color: #b8a5ce;
  }

  .agenda-card.blue {
    border-top-color: #8fb3cc;
  }
}

.agenda-time {
  color: var(--text-secondary);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.agenda-card h3 {
  font-family: 'DM Sans';
  font-size: 1.02rem;
  margin: 0.55rem 0;
}

.agenda-card p {
  color: #66706c;
  font-size: 0.84rem;
  line-height: 1.45;
  min-height: 52px;
}

@media (prefers-color-scheme: dark) {
  .agenda-card p {
    color: #a8b0ad;
  }
}

.pill {
  display: inline-block;
  padding: 5px 9px;
  background: #f3eee6;
  border-radius: 20px;
  color: #6e746f;
  font-size: 0.67rem;
}

@media (prefers-color-scheme: dark) {
  .pill {
    background: #3a3530;
    color: #a0a8a5;
  }
}

/* Insight Cards */
.insight-card {
  min-height: 155px;
}

.insight-icon {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background: #e5f0ed;
  color: var(--teal);
  font-weight: 700;
}

@media (prefers-color-scheme: dark) {
  .insight-icon {
    background: #1f4a47;
    color: #7eb5ad;
  }
}

.insight-card h3 {
  font-family: 'DM Sans';
  font-size: 0.95rem;
  margin: 0.8rem 0 0.3rem;
}

.insight-card p {
  color: var(--text-secondary);
  font-size: 0.82rem;
  line-height: 1.5;
}

/* Story Paper */
.story-paper {
  background: #fffdf7;
  border: 1px solid #e8decf;
  border-radius: 22px;
  padding: 30px 36px;
  box-shadow: 0 12px 30px rgba(64, 54, 39, 0.06);
}

@media (prefers-color-scheme: dark) {
  .story-paper {
    background: #2d2825;
    border: 1px solid #3a3530;
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.3);
  }
}

.story-paper p {
  font-family: Georgia, serif;
  line-height: 1.8;
  color: #3e4844;
}

@media (prefers-color-scheme: dark) {
  .story-paper p {
    color: #c8c5c0;
  }
}

/* Timeline */
.timeline-card {
  position: relative;
  margin-left: 12px;
  padding: 4px 0 22px 28px;
  border-left: 2px solid #ded8cc;
}

@media (prefers-color-scheme: dark) {
  .timeline-card {
    border-left-color: #3a3530;
  }
}

.timeline-dot {
  position: absolute;
  left: -7px;
  top: 8px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--coral);
  box-shadow: 0 0 0 5px var(--bg-primary);
}

.timeline-card h4 {
  margin: 0.2rem 0 0.25rem;
  font-size: 1rem;
  color: var(--text-primary);
}

.timeline-card p {
  margin: 0 0 0.55rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.timeline-date {
  color: var(--teal);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 0.68rem;
  font-weight: 700;
}

/* Food */
.food-tag {
  display: inline-block;
  margin: 0 5px 4px 0;
  padding: 4px 8px;
  border-radius: 99px;
  background: #e5f0ed;
  color: #3d6e67;
  font-size: 0.68rem;
  font-weight: 700;
}

@media (prefers-color-scheme: dark) {
  .food-tag {
    background: #1f4a47;
    color: #7eb5ad;
  }
}

.food-chart-head {
  text-align: center;
  padding: 0.35rem 0 0.2rem;
}

.food-chart-head span {
  color: #e8607a;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.7rem;
  font-weight: 700;
}

@media (prefers-color-scheme: dark) {
  .food-chart-head span {
    color: #ff9d88;
  }
}

.food-chart-head h3 {
  margin: 0.2rem 0 0;
  font-size: 1.55rem;
}

.food-chart-head p {
  margin: 0.2rem 0 0.3rem;
  color: #9b8890;
  font-size: 0.78rem;
}

@media (prefers-color-scheme: dark) {
  .food-chart-head p {
    color: #a8a0a0;
  }
}

/* Status Badges */
.status-live, .status-demo {
  display: inline-block;
  border-radius: 99px;
  padding: 5px 9px;
  font-size: 0.7rem;
  font-weight: 700;
}

.status-live {
  background: #dcefe8;
  color: #28715d;
}

.status-demo {
  background: #f8e8cf;
  color: #875f21;
}

@media (prefers-color-scheme: dark) {
  .status-live {
    background: #1f4a47;
    color: #7eb5ad;
  }

  .status-demo {
    background: #4a3d22;
    color: #e8b85e;
  }
}

/* Privacy Notice */
.privacy {
  background: #e9f1ef;
  border-radius: 14px;
  padding: 12px 14px;
  color: #49645e;
  font-size: 0.78rem;
  line-height: 1.45;
}

@media (prefers-color-scheme: dark) {
  .privacy {
    background: #1f4a47;
    color: #7eb5ad;
  }
}

/* Buttons */
.stButton > button {
  border-radius: 999px;
  border: none;
  background: var(--coral);
  color: white;
  font-weight: 700;
  padding: 0.58rem 1.2rem;
}

.stButton > button:hover {
  background: #cc654f;
  color: white;
  border: none;
}

@media (prefers-color-scheme: dark) {
  .stButton > button:hover {
    background: #ffb39e;
  }
}

/* Form Inputs */
.stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
  border-radius: 12px;
  background: #fffdfa;
  color: #23312f;
}

@media (prefers-color-scheme: dark) {
  .stTextInput input, .stTextArea textarea, .stSelectbox [data-baseweb="select"] {
    background: #2d2825;
    color: #e8e5e0;
    border-color: #3a3530 !important;
  }

  .stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #a0a8a5;
  }
}

/* Tabs */
[data-baseweb="tab-list"] {
  gap: 8px;
  background: #eee8dd;
  padding: 5px;
  border-radius: 999px;
  width: max-content;
}

@media (prefers-color-scheme: dark) {
  [data-baseweb="tab-list"] {
    background: #3a3530;
  }
}

[data-baseweb="tab"] {
  border-radius: 999px;
  padding: 8px 18px;
}

[aria-selected="true"] {
  background: #fffdfa !important;
}

@media (prefers-color-scheme: dark) {
  [aria-selected="true"] {
    background: #2d2825 !important;
  }
}

/* Responsive */
@media (max-width: 800px) {
  .hero {
    padding: 28px;
    background-position: 65% center;
  }

  .hero-copy {
    width: 70%;
    background: rgba(255, 253, 247, 0.85);
    padding: 18px;
    border-radius: 16px;
  }

  @media (prefers-color-scheme: dark) {
    .hero-copy {
      background: rgba(36, 34, 32, 0.85);
    }
  }

  .hero h1 {
    font-size: 2.2rem;
  }

  .nutrition-hero {
    min-height: 300px;
    padding: 26px;
    background-position: 62% center;
  }

  .nutrition-hero::before {
    background: rgba(255, 253, 250, 0.72);
  }

  @media (prefers-color-scheme: dark) {
    .nutrition-hero::before {
      background: rgba(36, 34, 32, 0.72);
    }
  }

  .nutrition-hero-copy {
    width: 78%;
    background: rgba(255, 253, 250, 0.84);
    padding: 18px;
    border-radius: 16px;
  }

  @media (prefers-color-scheme: dark) {
    .nutrition-hero-copy {
      background: rgba(36, 34, 32, 0.84);
    }
  }

  .nutrition-hero h1 {
    font-size: 2.25rem;
  }
}
</style>
"""
