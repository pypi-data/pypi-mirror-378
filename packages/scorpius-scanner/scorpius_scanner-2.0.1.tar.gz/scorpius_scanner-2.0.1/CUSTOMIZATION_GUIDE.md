# Scorpius Validation Kit - Customization Guide 🛠️

This guide walks you through customizing the validation kit for your specific Scorpius scanner implementation.

## 🚀 Quick Integration Steps

### 1. Configure Scorpius Scanner

Edit `scorpius_config.toml` with your scanner settings:

```toml
[scanner]
timeout_seconds = 300
max_parallel_jobs = 4
enable_formal_verification = true
enable_fuzzing = true

[detection]
confidence_threshold = 0.7
severity_threshold = "medium"

[simulation]
max_gas_limit = 10_000_000
enable_flash_loan_simulation = true
fork_block = "latest"

[output]
sarif_version = "2.1.0"
include_proof_packs = true
output_directory = "artifacts"
```

### 2. Implement Scanner Integration

Choose your integration method:

#### Option A: CLI Integration (Recommended)
Update `adapters/scorpius_base.py` with your CLI command:

```python
def run_scorpius_cli(self, contract_path: str, **kwargs) -> ScanResult:
    cmd = [
        "scorpius", "scan",
        f"--contract={contract_path}",
        f"--config={self.config_path}",
        f"--output-dir={artifacts_dir}",
        "--format=sarif",
        "--include-proof-packs",
    ]
    
    # Add your specific CLI flags
    if kwargs.get('chain'):
        cmd.append(f"--chain={kwargs['chain']}")
    if kwargs.get('block'):
        cmd.append(f"--block={kwargs['block']}")
    
    # Run and parse results
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    # ... parse SARIF output
```

#### Option B: Python API Integration
If you have a Python API:

```python
def run_scorpius_api(self, contract_path: str, **kwargs) -> ScanResult:
    import scorpius
    scanner = scorpius.Scanner(config_path=self.config_path)
    result = scanner.scan_contract(contract_path, **kwargs)
    
    return ScanResult(
        detected=result.detected,
        confidence=result.confidence,
        vulnerability_type=result.vulnerability_type,
        # ... map your API results to ScanResult
    )
```

### 3. Add Your Test Contracts

Organize your test corpus:

```
corpus/
├── ethernaut/
│   ├── E01.sol          # Fallback vulnerability
│   ├── E10.sol          # Reentrancy
│   └── ...
├── dvd/
│   ├── D02/             # Naive Receiver (can be directory)
│   ├── D04/             # Side Entrance  
│   └── ...
└── defi_incidents/
    ├── C01/             # Vault Share Inflation
    ├── C02/             # Timelock Bypass
    └── ...
```

### 4. Update Validation Cases

Edit `validation_cases.csv` to match your corpus:

```csv
Suite,CaseID,CaseName,Chain,Category,ExpectedVuln,ExpectedSeverity,ExploitExpected,Block,GasCeiling,Notes
ethernaut,E01,Fallback,ethereum,access-control,fallback-function,High,True,latest,6000000,
custom,C01,My Custom Test,ethereum,custom-category,my-vulnerability,Critical,True,18500000,8000000,Special setup needed
```

## 🔧 Advanced Customization

### Custom Adapters

Create new adapters for your specific test suites:

```python
# adapters/my_custom_suite.py
from .scorpius_base import ScorpiusAdapter

_adapter = ScorpiusAdapter()

def run_case(case: Dict[str, Any], workdir: str = ".") -> Dict[str, Any]:
    """Custom adapter for my test suite."""
    
    # Your custom logic here
    contract_path = Path(workdir) / "corpus" / "my_suite" / f"{case['CaseID']}.sol"
    
    if contract_path.exists():
        result = _adapter.run_scorpius_cli(
            str(contract_path),
            case_id=case["CaseID"],
            suite="my_suite",
            # Add custom parameters
            custom_param=case.get("CustomField")
        )
        
        return {
            "Detected": result.detected,
            "ConfScore": result.confidence,
            # ... map results
        }
    else:
        # Mock mode fallback
        return mock_results_for_case(case)
```

Don't forget to register it in `scripts/run_validation.py`:

```python
ADAPTERS = {
    "ethernaut": "adapters.ethernaut",
    "dvd": "adapters.dvd", 
    "defi_incidents": "adapters.defi_incidents",
    "my_suite": "adapters.my_custom_suite",  # Add this line
}
```

### Custom Metrics

Add custom metrics to `validation_scoring_weights.csv`:

```csv
Metric,Description,Weight
precision,TP / (TP + FP),0.20
recall,TP / (TP + FN),0.20
false_positive_rate,FP / (FP + TN) — lower is better,0.15
exploit_success,Share of exploitable findings that replay successfully,0.15
determinism,Identical results across 100 reruns,0.10
fork_fidelity,Receipt/trace match vs mainnet for chosen block,0.05
custom_metric,My custom performance metric,0.15
```

Then update `compute_scores.py` to calculate your custom metrics:

```python
def compute_metrics(df):
    # ... existing metrics
    
    # Add your custom metric calculation
    custom_metric = calculate_my_custom_metric(df)
    
    return {
        # ... existing metrics
        "custom_metric": round(custom_metric, 4),
    }
```

### Performance Tuning

Optimize scanner performance in `scorpius_config.toml`:

```toml
[scanner]
# Adjust based on your hardware
max_parallel_jobs = 8        # Number of CPU cores
timeout_seconds = 600        # Increase for complex contracts

[validation]
determinism_runs = 10        # Reduce for faster testing
performance_profiling = true # Enable detailed profiling
memory_limit_mb = 8192      # Set based on available RAM
```

### Custom Report Templates

Create custom report templates in `templates/`:

```markdown
# templates/my_custom_report.md
# {{company_name}} Custom Security Report

## Executive Summary
**Scanner Performance**: {{composite_score}}

{{#critical_vulnerabilities}}
### Critical: {{title}}
**Impact**: {{business_impact}}
**Recommendation**: {{recommendation}}
{{/critical_vulnerabilities}}

## Custom Metrics
- **My Metric**: {{custom_metric_value}}
- **ROI Analysis**: {{custom_roi}}

---
*Custom template for {{company_name}}*
```

### Competitor Benchmarking

Add new scanners to `benchmark_competitors.py`:

```python
def run_my_scanner(self, contract_path: str) -> ScannerResult:
    """Add support for another scanner."""
    try:
        cmd = ["my-scanner", "--input", contract_path, "--output", "json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        # Parse results and return ScannerResult
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return ScannerResult(
                scanner_name="my-scanner",
                detected=len(data.get("issues", [])) > 0,
                confidence=0.8,
                vulnerability_type="scanner-detected",
                severity="medium",
                scan_time=time.time() - start_time
            )
    except Exception as e:
        return ScannerResult("my-scanner", False, 0.0, "", "", 0.0, str(e))

# Add to scanners dict
self.scanners = {
    "scorpius": self.run_scorpius,
    "slither": self.run_slither,
    "mythril": self.run_mythril,
    "my-scanner": self.run_my_scanner,  # Add this
}
```

## 🎯 Enterprise Customization

### Branding & Styling

Update branding in `generate_enterprise_report.py`:

```python
self.branding = {
    "primary_color": "#your-color",
    "secondary_color": "#your-secondary", 
    "logo_url": "https://yourcompany.com/logo.png",
    "company_url": "https://yourcompany.com",
    "support_email": "support@yourcompany.com"
}
```

Customize CSS in `report.css`:

```css
:root {
  --bg: #your-bg-color;
  --accent: #your-accent-color;
  --text: #your-text-color;
}
```

### CI/CD Integration

Update `.github/workflows/validation.yml`:

```yaml
- name: Run Scorpius validation
  env:
    RPC_URL: ${{ secrets.RPC_URL }}
    YOUR_API_KEY: ${{ secrets.YOUR_API_KEY }}  # Add your secrets
  run: |
    # Replace with your actual CLI command
    python scripts/run_validation.py --suite ${{ matrix.suite }} --out validation_results.csv
    
    # Add any post-processing
    python scripts/post_process_results.py
```

### Custom Compliance Frameworks

Add compliance mappings to reports:

```python
# In generate_enterprise_report.py
def _get_compliance_status(self, vulnerabilities):
    """Map vulnerabilities to compliance frameworks."""
    return {
        "pci_dss": self._check_pci_compliance(vulnerabilities),
        "hipaa": self._check_hipaa_compliance(vulnerabilities),
        "gdpr": self._check_gdpr_compliance(vulnerabilities),
    }
```

## 🔍 Testing Your Customizations

### 1. Test Individual Components

```bash
# Test adapter
python -c "from adapters.ethernaut import run_case; print(run_case({'CaseID': 'E01', 'CaseName': 'Test'}))"

# Test scoring
python compute_scores.py

# Test report generation
python generate_enterprise_report.py --company "Test Corp"
```

### 2. Run End-to-End Validation

```bash
# Full validation pipeline
python scripts/run_validation.py --suite ethernaut --limit 5
python compute_scores.py
python generate_enterprise_report.py --company "Your Company"
```

### 3. Performance Testing

```bash
# Test performance
python performance_benchmark.py --mode single --contract corpus/ethernaut/E01.sol
python performance_benchmark.py --mode suite --suite ethernaut
```

### 4. Competitor Benchmarking

```bash
# Compare against other tools
python benchmark_competitors.py --suite ethernaut --scanners scorpius slither
```

## 📚 Best Practices

### 1. Version Control
- Keep `validation_scoring_weights.csv` stable once published
- Version your corpus with git tags
- Track configuration changes in `scorpius_config.toml`

### 2. Reproducibility
- Use fixed RPC endpoints and block numbers for deterministic testing
- Set random seeds in your scanner configuration
- Document environment requirements

### 3. Scalability
- Test with large corpus sizes (100+ contracts)
- Monitor memory usage during long runs
- Implement graceful timeout handling

### 4. Security
- Never commit API keys or secrets
- Use environment variables for sensitive configuration
- Validate all external inputs

## 🆘 Troubleshooting

### Common Issues

**"No module named 'adapters'"**
- Solution: Set `PYTHONPATH=/workspace` or run from project root

**"Scorpius command not found"**
- Solution: Install Scorpius or update CLI path in adapters

**"SARIF parsing error"**
- Solution: Check SARIF 2.1.0 format compliance in your scanner output

**"Memory errors during large corpus runs"**
- Solution: Reduce `max_parallel_jobs` or increase system memory

### Getting Help

1. **Check logs**: Look in `artifacts/` directory for detailed scan logs
2. **Validate configuration**: Run `scorpius --version` and check config syntax
3. **Test incrementally**: Start with single contracts before full corpus
4. **Community support**: Join the Scorpius Discord/Slack for help

---

## 🎉 Ready to Deploy?

Once customized, your validation kit should:
- ✅ Successfully run on your test corpus
- ✅ Generate accurate precision/recall metrics  
- ✅ Produce professional PDF reports
- ✅ Pass CI/CD pipeline tests
- ✅ Handle enterprise-scale workloads

**You're now ready to prove your scanner's enterprise-grade capabilities!** 🚀