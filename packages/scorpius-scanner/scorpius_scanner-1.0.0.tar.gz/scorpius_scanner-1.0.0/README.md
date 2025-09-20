# Scorpius Validation Kit 🛡️

**Enterprise-grade validation pipeline for smart contract security scanners**

This kit provides a repeatable, buyer-grade validation framework that proves your scanner's efficacy with enterprise metrics and professional reporting. Perfect for justifying "$5k–$150k per year" pricing to CISOs.

## 🎯 What This Kit Proves

✅ **Technical Superiority**: Precision ≥ 0.90, Recall ≥ 0.90, FPR ≤ 3%  
✅ **Exploit Validation**: 95%+ success rate on reproducible exploits  
✅ **Enterprise Reliability**: Deterministic results, perfect fork fidelity  
✅ **Audit-Ready Artifacts**: SARIF 2.1.0, proof packs, on-chain hashes  

## 📁 Repository Structure

```
├── validation_cases.csv              # Curated test corpus (30 cases)
├── validation_scoring_weights.csv    # Metric weights for composite scoring
├── scripts/
│   └── run_validation.py            # Adapter-driven validation runner
├── adapters/
│   ├── ethernaut.py                 # Ethernaut challenge adapter
│   ├── dvd.py                       # Damn Vulnerable DeFi adapter
│   └── defi_incidents.py            # Real incident reproductions
├── compute_scores.py                # Scoring engine + report generator
├── report.css                       # Dark theme for HTML/PDF reports
├── .github/workflows/validation.yml # Nightly CI validation
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install pandas
# Optional: Install Foundry for DeFi testing
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

### 2. Implement Your Scanner Adapters

Edit the adapter files to integrate with your Scorpius scanner:

**`adapters/ethernaut.py`**:
```python
def run_case(case: Dict[str, Any], workdir: str = ".") -> Dict[str, Any]:
    # Replace with your scanner integration
    result = scorpius.scan_contract(
        contract_path=f"corpus/ethernaut/{case['CaseID']}.sol",
        chain="ethereum",
        block=case["Block"],
        gas_ceiling=case["GasCeiling"]
    )
    
    return {
        "Detected": result.detected,
        "ConfScore": result.confidence,
        "DetectedVuln": result.vulnerability_type,
        "DetectedSeverity": result.severity,
        "ExploitSimulated": result.exploit.success,
        "ProfitETH": result.exploit.profit_eth,
        "TimeToValidateSec": result.validation_time,
        "ForkFidelity": result.fork.fidelity_ok,
        "DeterminismPass": result.deterministic,
        "ProofPackHash": result.proof.hash,
        "SARIFPath": result.sarif_path,
        "ArtifactsPath": result.artifacts_dir,
    }
```

### 3. Add Your Test Corpus

Create corpus directories with your test cases:
```
corpus/
├── ethernaut/
│   ├── E01.sol      # Fallback vulnerability
│   ├── E10.sol      # Reentrancy
│   └── ...
├── dvd/
│   ├── D02/         # Naive Receiver
│   ├── D04/         # Side Entrance
│   └── ...
└── defi_incidents/
    ├── C01/         # Vault Share Inflation
    ├── C02/         # Governance Timelock Bypass
    └── ...
```

### 4. Run Local Validation

```bash
# Run specific suite
python scripts/run_validation.py --suite ethernaut --out validation_results.csv

# Run all suites
python scripts/run_validation.py --suite all --out validation_results.csv

# Generate scores and report
python compute_scores.py
```

### 5. Set Up CI Pipeline

Copy the GitHub Actions workflow:
```bash
cp .github/workflows/validation.yml .github/workflows/
git add .github/workflows/validation.yml
git commit -m "Add nightly validation pipeline"
git push
```

## 📊 Understanding the Metrics

### Core Metrics
- **Precision**: TP / (TP + FP) — How many detections are real vulnerabilities?
- **Recall**: TP / (TP + FN) — How many real vulnerabilities are detected?
- **False Positive Rate**: FP / (FP + TN) — How often do we cry wolf?
- **Exploit Success**: % of detected exploitable bugs that actually exploit
- **Determinism**: % of runs with identical results (same input → same output)
- **Fork Fidelity**: % perfect mainnet state replication

### Enterprise Targets
| Metric | Target | Justification |
|--------|--------|---------------|
| Precision | ≥ 0.90 | Minimize developer false alarm fatigue |
| Recall | ≥ 0.90 | Catch 90%+ of real vulnerabilities |
| FPR | ≤ 0.03 | <3% false positive rate for production use |
| Exploit Success | ≥ 0.95 | Prove exploitability with high confidence |
| Determinism | ≥ 0.99 | Consistent results for audit repeatability |
| Fork Fidelity | = 1.00 | Perfect mainnet simulation |

### Composite Score
Weighted combination of all metrics:
- Precision: 25%
- Recall: 25%  
- FPR (inverted): 20%
- Exploit Success: 15%
- Determinism: 10%
- Fork Fidelity: 5%

## 📈 Validation Corpus

### Ethernaut (10 cases)
Classic smart contract challenges covering fundamental vulnerabilities:
- Access control bypasses
- Reentrancy attacks  
- Storage manipulation
- Integer overflows
- Delegatecall misuse

### Damn Vulnerable DeFi (10 cases)  
DeFi-specific attack vectors:
- Flash loan exploits
- Oracle manipulation
- Governance attacks
- AMM price skewing
- Reward system gaming

### DeFi Incidents (10 cases)
Real-world incident reproductions:
- Vault share inflation
- TWAP manipulation
- ERC777 reentrancy
- Storage collisions
- Timelock bypasses

## 🛠️ Customization

### Adding New Test Cases
1. Add row to `validation_cases.csv`:
```csv
Suite,CaseID,CaseName,Chain,Category,ExpectedVuln,ExpectedSeverity,ExploitExpected,Block,GasCeiling,Notes
custom,C01,My Test Case,ethereum,custom-category,my-vulnerability,High,True,latest,8000000,Special setup notes
```

2. Add corpus files to `corpus/custom/`

3. Create adapter in `adapters/custom.py`

4. Update `ADAPTERS` dict in `scripts/run_validation.py`

### Tuning Scoring Weights
Edit `validation_scoring_weights.csv`:
```csv
Metric,Description,Weight
precision,TP / (TP + FP),0.30
recall,TP / (TP + FN),0.30
false_positive_rate,FP / (FP + TN) — lower is better,0.20
exploit_success,Share of exploitable findings that replay successfully,0.20
```

**⚠️ Keep weights stable once published for credibility**

## 📋 Output Files

### Generated Reports
- `out/scores_summary.csv` — Single-row global metrics
- `out/per_suite_scores.csv` — Breakdown by test suite  
- `out/validation_report.md` — Markdown report
- `out/validation_report.html` — Styled HTML report
- `out/validation_report.pdf` — PDF for executives

### CI Artifacts
- Nightly validation runs via GitHub Actions
- Automatic PDF generation with dark theme
- Artifact retention (30 days per suite, 90 days combined)
- PR comment integration for validation results

## 🎨 Report Themes

The included `report.css` provides a professional dark theme with:
- Cyan accent colors (#00e5ff, #5bffea)
- Color-coded metrics (green/yellow/red)
- Responsive design
- Print-friendly styles
- Modern typography (Inter + JetBrains Mono)

## 🔧 Integration Examples

### CLI Integration
```python
# In your adapter
import subprocess
result = subprocess.run([
    "scorpius", "scan", 
    f"--contract={contract_path}",
    f"--chain={chain}",
    f"--output=sarif"
], capture_output=True, text=True)
```

### Python API Integration  
```python
# In your adapter
import scorpius
scanner = scorpius.Scanner(config_path="scorpius.toml")
result = scanner.scan_contract(contract_path, chain="ethereum")
```

### Docker Integration
```python
# In your adapter  
import docker
client = docker.from_env()
result = client.containers.run(
    "scorpius:latest",
    f"scan --contract=/workspace/{contract_path}",
    volumes={workdir: {"bind": "/workspace", "mode": "ro"}}
)
```

## 🏆 Enterprise Readiness Checklist

### Technical Validation ✅
- [ ] Precision ≥ 0.90 on corpus
- [ ] Recall ≥ 0.90 on corpus  
- [ ] FPR ≤ 3% on clean contracts
- [ ] 95%+ exploit success rate
- [ ] 99%+ deterministic results
- [ ] Perfect fork fidelity

### Audit Trail ✅
- [ ] SARIF 2.1.0 export
- [ ] Proof pack generation
- [ ] On-chain proof hashes
- [ ] Reproducible builds
- [ ] Version-controlled corpus

### Enterprise Integration ✅
- [ ] CI/CD pipeline ready
- [ ] Professional PDF reports
- [ ] Metrics dashboard
- [ ] API documentation
- [ ] Support runbooks

## 📞 Support & Customization

Need help integrating this validation kit with your scanner?

**Enterprise Support Available:**
- Custom corpus development
- Scanner integration consulting  
- Advanced reporting themes
- Compliance framework mapping
- Performance optimization

## 📄 License

This validation kit is provided as-is for security scanner validation. 
Customize freely for your commercial security products.

---

**Ready to prove your scanner is worth enterprise pricing?** 🚀

Run your first validation:
```bash
python scripts/run_validation.py --suite ethernaut --limit 3
python compute_scores.py
open out/validation_report.html
```