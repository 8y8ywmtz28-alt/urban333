BASE_STYLE = """
<style>
.block-container {padding-top: 1rem; padding-bottom: 1rem; max-width: 1220px;}
[data-testid="stSidebar"] {border-right: 1px solid #e9eef5;}
.card {
  background: linear-gradient(180deg,#fafcff 0%,#f7f9fc 100%);
  border: 1px solid #e8edf5;
  border-radius: 12px;
  padding: 0.9rem 1rem;
  transition: all .18s ease;
}
.card:hover {transform: translateY(-2px); box-shadow: 0 6px 18px rgba(28,55,90,.08);}
.badge {display:inline-block; padding:2px 8px; border-radius:999px; font-size:.78rem; background:#eef4ff; color:#3057a8; margin-right:6px;}
.section-title {font-size:1.06rem; font-weight:600; margin-top:.2rem; margin-bottom:.4rem;}
.fade-in {animation: fadein .25s ease-in;}
@keyframes fadein {from{opacity:.2} to{opacity:1}}
</style>
"""
