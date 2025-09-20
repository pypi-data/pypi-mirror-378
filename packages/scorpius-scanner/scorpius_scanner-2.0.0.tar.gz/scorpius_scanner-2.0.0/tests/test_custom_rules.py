#!/usr/bin/env python3
"""
Test suite for the production rule system and KPI metrics
"""

import pytest
import tempfile
import os
from pathlib import Path

# Add the parent directory to sys.path so we can import our modules
import sys

sys.path.append(str(Path(__file__).parent.parent))

from core.detection_engines.custom_rules.rule_ops import (
    RuleOpsSystem,
    ProductionRule,
    RuleGate,
)
from core.detection_engines.custom_rules.kpi_metrics import KPICalculator, KPIMetrics
from core.detection_engines.custom_rules.oracle_staleness import scan as scan_oracle
from core.detection_engines.custom_rules.crosschain_replay import (
    scan as scan_crosschain,
)


class TestOracleStalenessDetector:
    """Test oracle staleness vulnerability detector"""

    def test_oracle_staleness_detected(self):
        """Test that oracle staleness is detected in vulnerable code"""
        # Use existing test file
        test_dir = "/workspace/tests/corpus/positive/oracle"
        hits = scan_oracle(test_dir)

        assert len(hits) > 0
        assert any(h["category"] == "Oracle.Staleness" for h in hits)

    def test_oracle_staleness_not_detected_when_safe(self):
        """Test that safe oracle usage is not flagged"""
        test_dir = "/workspace/tests/corpus/negative/oracle"
        hits = scan_oracle(test_dir)

        assert len(hits) == 0


class TestCrosschainReplayDetector:
    """Test cross-chain replay vulnerability detector"""

    def test_crosschain_replay_detected(self):
        """Test that cross-chain replay vulnerability is detected"""
        test_dir = "/workspace/tests/corpus/positive/crosschain"
        hits = scan_crosschain(test_dir)

        assert len(hits) > 0
        assert any(h["category"] == "CrossChain.Replay" for h in hits)

    def test_crosschain_replay_not_detected_when_safe(self):
        """Test that safe cross-chain handlers are not flagged"""
        test_dir = "/workspace/tests/corpus/negative/crosschain"
        hits = scan_crosschain(test_dir)

        assert len(hits) == 0


class TestKPIMetrics:
    """Test KPI metrics calculation"""

    def test_kpi_calculation_basic(self):
        """Test basic KPI calculation"""
        calc = KPICalculator()

        # Mock findings and ground truth
        findings = [
            {
                "severity": "High",
                "category": "Oracle.Staleness",
                "location": {"file": "test.sol"},
            },
            {
                "severity": "Medium",
                "category": "Other",
                "location": {"file": "test2.sol"},
            },
        ]

        ground_truth = [
            {
                "severity": "High",
                "category": "Oracle.Staleness",
                "location": {"file": "test.sol"},
            }
        ]

        kpis = calc.calculate_kpis(findings, ground_truth, 0.0, 1.0)

        assert isinstance(kpis, KPIMetrics)
        assert kpis.recall_high_plus == 1.0  # Found the high severity issue
        assert kpis.precision_high_plus == 1.0  # No false positives in high+
        assert kpis.scan_time_seconds == 1.0

    def test_production_standards_check(self):
        """Test production standards validation"""
        # Good metrics
        good_kpis = KPIMetrics(
            recall_high_plus=0.85,
            precision_high_plus=0.85,
            severity_weighted_f1=0.90,
            time_to_first_high=60.0,
            determinism_score=1.0,
            total_high_plus_found=10,
            total_high_plus_actual=10,
            false_positives_high_plus=0,
            scan_time_seconds=100.0,
        )
        assert good_kpis.meets_production_standards()

        # Bad metrics
        bad_kpis = KPIMetrics(
            recall_high_plus=0.50,  # Too low
            precision_high_plus=0.85,
            severity_weighted_f1=0.90,
            time_to_first_high=60.0,
            determinism_score=1.0,
            total_high_plus_found=5,
            total_high_plus_actual=10,
            false_positives_high_plus=0,
            scan_time_seconds=100.0,
        )
        assert not bad_kpis.meets_production_standards()


class TestRuleOpsSystem:
    """Test RuleOps system with gating"""

    def test_rule_loading(self):
        """Test loading rules from YAML files"""
        rules_dir = "/workspace/production_rules"
        rule_ops = RuleOpsSystem(rules_dir)

        assert len(rule_ops.rules) > 0
        assert "VR-4626-01" in rule_ops.rules or "OR-STALE-01" in rule_ops.rules

    def test_rule_execution(self):
        """Test basic rule execution"""
        rules_dir = "/workspace/production_rules"
        rule_ops = RuleOpsSystem(rules_dir)

        # Test with oracle staleness rule if available
        if "OR-STALE-01" in rule_ops.rules:
            rule = rule_ops.rules["OR-STALE-01"]
            test_file = "/workspace/tests/corpus/positive/oracle/stale_price.sol"
            result = rule_ops._execute_rule_on_file(rule, test_file)
            assert isinstance(result, bool)

    def test_default_gates_creation(self):
        """Test creation of default gates"""
        rules_dir = "/tmp/test_rules"
        os.makedirs(rules_dir, exist_ok=True)
        rule_ops = RuleOpsSystem(rules_dir)

        gates = rule_ops.create_default_gates()
        assert len(gates) == 5
        assert all(isinstance(gate, RuleGate) for gate in gates)
        assert any(gate.gate_id == "G1" for gate in gates)


class TestIntegration:
    """Integration tests combining multiple components"""

    def test_end_to_end_vulnerability_detection(self):
        """Test complete vulnerability detection workflow"""
        # Scan for vulnerabilities
        oracle_findings = scan_oracle(
            "/workspace/tests/corpus/positive/oracle"
        )
        crosschain_findings = scan_crosschain(
            "/workspace/tests/corpus/positive/crosschain"
        )

        all_findings = oracle_findings + crosschain_findings

        # Mock ground truth
        ground_truth = [
            {
                "severity": "High",
                "category": "Oracle.Staleness",
                "location": {"file": "stale_price.sol"},
            },
            {
                "severity": "High",
                "category": "CrossChain.Replay",
                "location": {"file": "replay_vulnerable.sol"},
            },
        ]

        # Calculate KPIs
        calc = KPICalculator()
        kpis = calc.calculate_kpis(all_findings, ground_truth, 0.0, 2.0)

        # Verify we found vulnerabilities
        assert len(all_findings) > 0
        assert kpis.total_high_plus_found > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
