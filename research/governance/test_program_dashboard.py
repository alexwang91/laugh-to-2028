from __future__ import annotations
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DASHBOARD = ROOT / "research" / "governance" / "dashboard" / "index.html"
README = ROOT / "research" / "governance" / "dashboard" / "README.md"

class ProgramDashboardContractTests(unittest.TestCase):
    def setUp(self):
        self.html = DASHBOARD.read_text(encoding="utf-8")
        self.readme = README.read_text(encoding="utf-8")

    def test_canonical_history_sources(self):
        for path in (
            "research/results/pit_disp_0015/daily_equity.csv",
            "research/results/pit_disp_0015/daily_weights.csv",
            "research/results/funding_pnl_0003/full_window_daily_equity.csv",
        ):
            self.assertIn(path, self.html); self.assertIn(path, self.readme)

    def test_governed_registry_without_authority_change(self):
        self.assertIn("config/research_registry.json", self.html)
        self.assertIn("config/decision_registry.json", self.html)
        self.assertIn("production_authorized=false", self.html)
        self.assertIn("dashboard_record_authoritative=false", self.html)

    def test_phase6_candidate_still_requires_success_evidence_receipt(self):
        self.assertIn("run.conclusion==='success'&&ev&&rc", self.html)
        self.assertIn("phase6-evidence-", self.html)
        self.assertIn("phase6-receipt-", self.html)
        self.assertIn("scheduled_decision_credit_created=false", self.html)
        self.assertIn("看板不会创造有效记录", self.html)

    def test_backtest_shadow_real_pnl_remain_separate(self):
        for text in ("historical backtest NAV","Phase-6 hypothetical shadow PnL","future real-account PnL"):
            self.assertIn(text, self.readme)
        self.assertIn("!=", self.readme)

    def test_xrp_feature_only(self):
        self.assertIn("const TARGET_ASSETS=['BTC','ETH','SOL','BNB']", self.html)
        self.assertNotIn("TARGET_ASSETS=['BTC','ETH','SOL','BNB','XRP']", self.html)
        self.assertIn("XRP remains **feature-only**", self.readme)

    def test_v5_professional_chinese_presentation(self):
        self.assertIn('content="v5-pro-fund-terminal"', self.html)
        self.assertIn("<title>BRRK 策略投资看板</title>", self.html)
        for text in ("策略投资看板","投委会摘要","业绩表现","仓位结构","风险与换仓节奏","单日审计","详细规则","实盘未授权"):
            self.assertIn(text, self.html)
        self.assertIn("--navy:#0c1626", self.html)
        self.assertIn("background:linear-gradient(135deg,#091423", self.html)
        self.assertIn("font-variant-numeric:tabular-nums", self.html)
        self.assertIn("displayModeBar:false", self.html)
        self.assertIn("colors={BTC:'#243b64'", self.html)
        self.assertIn("executiveSummary", self.html)

    def test_range_statistics_keep_audit_semantics(self):
        for text in ("累计收益","上涨日占比","日收益盈亏比","最大回撤","目标变化天数","持仓周期胜率"):
            self.assertIn(text, self.html)
        self.assertIn("Positive-return-day ratio` is not labelled as holding-cycle win rate", self.readme)
        self.assertIn("metric('实际再平衡','暂无历史记录')", self.html)
        self.assertIn("metric('持仓周期胜率','暂无历史记录')", self.html)

    def test_p33_rule_not_reverse_inferred(self):
        self.assertIn("P33_REBALANCE_BAND=0.05", self.html)
        self.assertIn("总差距达到或超过 5%", self.html)
        self.assertIn("历史实际调仓动作：暂无记录", self.html)
        self.assertIn("historical_p3_3_execution_state_available=false", self.html)
        self.assertIn("execution_causality_asserted=false", self.html)
        self.assertIn("current_position_weights", self.readme)
        self.assertIn("l1_target_gap", self.readme)

    def test_target_decision_return_dates_separate(self):
        for text in ("这一天生成的目标仓位","下一次决策时间","当时可用的数据","这份目标仓位对应的收益日","是否使用未来数据"):
            self.assertIn(text, self.html)
        self.assertIn("uses completed daily data through D-1", self.readme)
        self.assertIn("does not introduce look-ahead", self.readme)

    def test_signal_rules_chinese_snapshot_not_invented(self):
        for text in ("BTC 逻辑","ETH 可获得仓位的条件","SOL 可获得仓位的条件","BNB 可获得仓位的条件","市场状态","历史每天的完整信号快照没有保存"):
            self.assertIn(text, self.html)
        self.assertIn("historical_signal_snapshot_available=false", self.html)
        self.assertIn("never reverse-engineers a 2023 signal/regime", self.readme)

    def test_target_actions_are_mechanical_only(self):
        self.assertIn("REBALANCE_EPS=1e-9", self.html)
        for action in ("新开仓","清仓","加仓","减仓","不变"):
            self.assertIn(action, self.html)
        self.assertIn("模型目标仓位变化，不等于账户真的在当天成交了", self.html)
        self.assertIn("target_change_mechanics_authoritative_from_canonical_weights=true", self.html)

    def test_public_marker(self):
        self.assertIn('content="v5-pro-fund-terminal"', self.html)
        self.assertIn("https://laugh-to-2028.vercel.app/", self.readme)

if __name__ == "__main__": unittest.main()
