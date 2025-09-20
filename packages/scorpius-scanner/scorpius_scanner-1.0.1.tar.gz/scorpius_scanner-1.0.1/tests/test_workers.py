"""Worker task tests."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

from app.workers.tasks import (
    run_scan_task,
    _prepare_source,
    _calculate_fingerprint,
    _calculate_file_hash,
)


class TestScanTask:
    """Test scan execution task."""

    @patch("app.workers.tasks.SessionLocal")
    @patch("app.workers.tasks.S3Service")
    @patch("app.workers.tasks.SimulationClient")
    @patch("app.workers.tasks.PDFGenerator")
    def test_run_scan_success(
        self,
        mock_pdf,
        mock_sim,
        mock_s3,
        mock_db,
    ):
        """Test successful scan execution."""
        # Setup mocks
        mock_scan = Mock()
        mock_scan.id = "test-scan-id"
        mock_scan.mode = "fast"
        mock_scan.scan_metadata = {"upload_path": "/tmp/test.zip"}
        mock_scan.project.organization.id = "org-id"
        mock_scan.project.id = "project-id"
        mock_scan.project.default_chain = "ethereum"

        mock_db_instance = Mock()
        mock_db_instance.query.return_value.filter.return_value.first.return_value = (
            mock_scan
        )
        mock_db.return_value = mock_db_instance

        mock_s3_instance = Mock()
        mock_s3_instance.upload_file.return_value = "s3://bucket/file"
        mock_s3.return_value = mock_s3_instance

        mock_sim_instance = Mock()
        mock_sim_instance.simulate.return_value = {
            "status": "pass",
            "duration_sec": 2.0,
            "artifacts": {},
        }
        mock_sim.return_value = mock_sim_instance

        mock_pdf_instance = Mock()
        mock_pdf_instance.generate_report.return_value = Path("/tmp/report.pdf")
        mock_pdf.return_value = mock_pdf_instance

        # Create mock task
        task = Mock()
        task.db = mock_db_instance

        # Would need more setup for full test
        # result = run_scan_task.apply(args=["test-scan-id"])
        # assert result.successful()

    def test_calculate_fingerprint(self):
        """Test fingerprint calculation."""
        findings = [
            {
                "category": "Reentrancy",
                "severity": "High",
                "contract": "Vault",
                "function": "withdraw",
                "location": {"file": "Vault.sol", "line": 42},
            },
            {
                "category": "Oracle",
                "severity": "Medium",
                "contract": "PriceOracle",
                "function": "getPrice",
                "location": {"file": "Oracle.sol", "line": 15},
            },
        ]

        fingerprint1 = _calculate_fingerprint(findings)
        fingerprint2 = _calculate_fingerprint(findings)

        # Should be deterministic
        assert fingerprint1 == fingerprint2
        assert len(fingerprint1) == 64  # SHA256 hex

        # Different findings should produce different fingerprint
        findings[0]["severity"] = "Critical"
        fingerprint3 = _calculate_fingerprint(findings)
        assert fingerprint1 != fingerprint3

    def test_calculate_file_hash(self):
        """Test file hash calculation."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            f.flush()

            hash1 = _calculate_file_hash(Path(f.name))
            hash2 = _calculate_file_hash(Path(f.name))

            # Should be consistent
            assert hash1 == hash2
            assert len(hash1) == 64  # SHA256 hex

            # Known hash for "test content"
            expected = (
                "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"
            )
            assert hash1 == expected

        Path(f.name).unlink()

    @patch("subprocess.run")
    def test_prepare_source_git(self, mock_run):
        """Test source preparation from git."""
        mock_scan = Mock()
        mock_scan.scan_metadata = {"repo_url": "https://github.com/test/repo.git"}
        mock_scan.branch = "main"
        mock_scan.commit = None

        mock_run.return_value = Mock(returncode=0)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            result = _prepare_source(mock_scan, temp_path)

            assert result == temp_path / "source"
            mock_run.assert_called_once()

            # Check git clone command
            call_args = mock_run.call_args[0][0]
            assert "git" in call_args
            assert "clone" in call_args
            assert "--depth" in call_args
            assert "1" in call_args


class TestSimulationClient:
    """Test simulation service client."""

    @patch("httpx.Client")
    def test_simulate_success(self, mock_client):
        """Test successful simulation."""
        from app.sim.client import SimulationClient

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "pass",
            "artifacts": {},
            "env": {"anvil": "0.2.0"},
            "fingerprint": "sha256:abc123",
        }

        mock_client_instance = Mock()
        mock_client_instance.post.return_value = mock_response
        mock_client.return_value.__enter__.return_value = mock_client_instance

        client = SimulationClient()
        result = client.simulate(
            finding_id="test-finding",
            category="Oracle.Staleness",
            chain="ethereum",
        )

        assert result["status"] == "pass"
        assert "duration_sec" in result

    def test_get_scenario_mapping(self):
        """Test scenario mapping for categories."""
        from app.sim.client import SimulationClient

        client = SimulationClient()

        # Test exact match
        scenario = client._get_scenario("Oracle.Staleness")
        assert scenario["type"] == "oracle_freshness_check"

        # Test prefix match
        scenario = client._get_scenario("UUPS.InitializerNotDisabled")
        assert scenario["type"] == "uups_initializer_guard"

        # Test no match
        scenario = client._get_scenario("Unknown.Category")
        assert scenario is None
