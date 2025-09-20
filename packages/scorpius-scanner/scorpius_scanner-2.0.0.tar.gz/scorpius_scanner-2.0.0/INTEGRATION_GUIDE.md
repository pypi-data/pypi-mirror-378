# 🔌 Scanner Integration Guide

This guide shows how to integrate the Enhanced Audit Learning System with your smart contract scanner to create a learning-powered vulnerability detection engine.

## 🎯 Integration Overview

The Enhanced Audit Learning System can be integrated with any scanner through:

1. **Python API**: Direct integration using the learning database classes
2. **REST API**: HTTP-based integration for any programming language  
3. **CLI Tools**: Command-line integration for batch processing
4. **File Export**: Export learned patterns to your scanner's format

## 🚀 Quick Integration Examples

### 1. Direct Python Integration

```python
import asyncio
from enhanced_audit_learning_system import MassiveAuditLearningDatabase

class LearningScanner:
    def __init__(self):
        self.learning_db = MassiveAuditLearningDatabase()
        self.detection_rules = []
    
    async def initialize(self):
        """Initialize the learning system"""
        # Load existing patterns
        await self.load_learned_patterns()
        
    async def load_learned_patterns(self):
        """Load learned vulnerability patterns"""
        # Export patterns from learning database
        patterns_file = await self.learning_db.export_patterns_for_scanner()
        
        with open(patterns_file, 'r') as f:
            patterns_data = json.load(f)
        
        # Convert to scanner-specific format
        for pattern in patterns_data['patterns']:
            detection_rule = self.convert_pattern_to_rule(pattern)
            self.detection_rules.append(detection_rule)
    
    def convert_pattern_to_rule(self, pattern):
        """Convert learned pattern to scanner detection rule"""
        return {
            'id': pattern['id'],
            'name': pattern['name'],
            'severity': pattern['severity'],
            'confidence': pattern['confidence'],
            'regex_patterns': [rule['pattern'] for rule in pattern['detection_rules'] if rule['type'] == 'regex'],
            'ast_patterns': [rule['pattern'] for rule in pattern['detection_rules'] if rule['type'] == 'ast'],
            'description': pattern['description'],
            'mitigation': pattern['mitigation']
        }
    
    async def scan_contract(self, contract_code: str, contract_path: str):
        """Enhanced scanning with learning predictions"""
        vulnerabilities = []
        
        # Traditional rule-based scanning
        traditional_vulns = self.traditional_scan(contract_code)
        vulnerabilities.extend(traditional_vulns)
        
        # ML-powered prediction
        prediction = await self.learning_db.predict_vulnerability_type(contract_code)
        
        if prediction['overall_confidence'] > 0.7:
            ml_vuln = {
                'type': prediction['predicted_type'],
                'severity': prediction['predicted_severity'],
                'confidence': prediction['overall_confidence'],
                'source': 'ml_prediction',
                'recommendation': prediction['recommendation'],
                'similar_patterns': prediction['similar_patterns']
            }
            vulnerabilities.append(ml_vuln)
        
        # Feed scan results back to learning system
        await self.feed_scan_results(contract_code, contract_path, vulnerabilities)
        
        return vulnerabilities
    
    def traditional_scan(self, contract_code: str):
        """Your existing scanning logic"""
        vulnerabilities = []
        
        # Apply learned detection rules
        for rule in self.detection_rules:
            if self.apply_rule(contract_code, rule):
                vulnerabilities.append({
                    'type': rule['name'],
                    'severity': rule['severity'],
                    'confidence': rule['confidence'],
                    'source': 'learned_pattern',
                    'rule_id': rule['id']
                })
        
        return vulnerabilities
    
    def apply_rule(self, code: str, rule: dict) -> bool:
        """Apply detection rule to code"""
        import re
        
        # Check regex patterns
        for pattern in rule['regex_patterns']:
            if re.search(pattern, code, re.IGNORECASE):
                return True
        
        # Add AST pattern checking here
        return False
    
    async def feed_scan_results(self, contract_code: str, contract_path: str, vulnerabilities: list):
        """Feed scan results back to learning system for continuous improvement"""
        
        # Convert vulnerabilities to learning format
        learning_vulns = []
        for vuln in vulnerabilities:
            learning_vuln = {
                'id': f"scan_{len(learning_vulns)+1:03d}",
                'type': vuln['type'],
                'severity': vuln['severity'],
                'title': f"{vuln['type']} detected in {contract_path}",
                'description': f"Scanner detected {vuln['type']} vulnerability",
                'code_snippet': self.extract_relevant_code(contract_code, vuln),
                'confidence': vuln['confidence'],
                'mitigation': vuln.get('recommendation', ''),
                'source': vuln.get('source', 'scanner')
            }
            learning_vulns.append(learning_vuln)
        
        # Create audit contract for learning
        from enhanced_audit_learning_system import AuditContract
        from datetime import datetime
        
        audit_contract = AuditContract(
            contract_id=f"scan_{contract_path}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source="integrated_scanner",
            project_name=contract_path.split('/')[-1],
            audit_firm="Learning Scanner",
            audit_date=datetime.now().strftime('%Y-%m-%d'),
            blockchain="ethereum",  # Detect from code or config
            category="unknown",     # Classify based on code patterns
            contract_code=contract_code,
            vulnerabilities=learning_vulns,
            severity_distribution={vuln['severity']: 1 for vuln in vulnerabilities},
            economic_impact=None,
            tvl_at_audit=None,
            post_audit_incidents=[],
            mitigation_effectiveness={},
            code_complexity_metrics={},
            dependency_analysis={},
            gas_optimization_opportunities=[],
            upgrade_patterns=[],
            governance_issues=[],
            oracle_dependencies=[],
            cross_chain_risks=[]
        )
        
        # Feed to learning system
        await self.learning_db.ingest_audit_contract(audit_contract)
    
    def extract_relevant_code(self, contract_code: str, vulnerability: dict) -> str:
        """Extract relevant code snippet for vulnerability"""
        # Simple implementation - in production, use AST parsing
        lines = contract_code.split('\n')
        
        # Find lines containing vulnerability-related keywords
        vuln_keywords = {
            'reentrancy': ['call{', '.call(', '.send(', '.transfer('],
            'access_control': ['onlyOwner', 'require(msg.sender', 'modifier'],
            'overflow': ['+', '-', '*', '/', 'SafeMath']
        }
        
        keywords = vuln_keywords.get(vulnerability['type'], [vulnerability['type']])
        
        relevant_lines = []
        for i, line in enumerate(lines):
            if any(keyword in line for keyword in keywords):
                # Include context (3 lines before and after)
                start = max(0, i-3)
                end = min(len(lines), i+4)
                relevant_lines.extend(lines[start:end])
                break
        
        return '\n'.join(relevant_lines) if relevant_lines else contract_code[:500]

# Usage example
async def main():
    scanner = LearningScanner()
    await scanner.initialize()
    
    # Scan a contract
    with open('contract.sol', 'r') as f:
        contract_code = f.read()
    
    vulnerabilities = await scanner.scan_contract(contract_code, 'contract.sol')
    
    for vuln in vulnerabilities:
        print(f"Found {vuln['type']} (severity: {vuln['severity']}, confidence: {vuln['confidence']:.3f})")

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. REST API Integration

```python
import httpx
import json
from typing import List, Dict, Any

class APILearningScanner:
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.client = httpx.AsyncClient()
    
    async def predict_vulnerabilities(self, code_snippet: str) -> Dict[str, Any]:
        """Predict vulnerabilities using the learning API"""
        
        response = await self.client.post(
            f"{self.api_base_url}/api/v1/predict/vulnerability",
            json={"code_snippet": code_snippet}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed: {response.status_code}")
    
    async def query_patterns(self, vulnerability_type: str = None, 
                           severity: str = None, 
                           min_confidence: float = 0.7) -> List[Dict[str, Any]]:
        """Query learned vulnerability patterns"""
        
        query_data = {
            "min_confidence": min_confidence,
            "limit": 100
        }
        
        if vulnerability_type:
            query_data["vulnerability_type"] = vulnerability_type
        if severity:
            query_data["severity"] = severity
        
        response = await self.client.post(
            f"{self.api_base_url}/api/v1/patterns/query",
            json=query_data
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Pattern query failed: {response.status_code}")
    
    async def submit_scan_results(self, contract_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit scan results to improve the learning system"""
        
        response = await self.client.post(
            f"{self.api_base_url}/api/v1/ingest/contract",
            json=contract_data
        )
        
        return response.json()
    
    async def enhanced_scan(self, contract_code: str, contract_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform enhanced scanning with ML predictions"""
        
        vulnerabilities = []
        
        # Get ML prediction
        try:
            prediction = await self.predict_vulnerabilities(contract_code)
            
            if prediction['overall_confidence'] > 0.7:
                vulnerabilities.append({
                    'type': prediction['predicted_type'],
                    'severity': prediction['predicted_severity'],
                    'confidence': prediction['overall_confidence'],
                    'source': 'ml_prediction',
                    'recommendation': prediction['recommendation']
                })
        except Exception as e:
            print(f"ML prediction failed: {e}")
        
        # Query for similar patterns
        try:
            patterns = await self.query_patterns(min_confidence=0.8)
            
            for pattern in patterns[:5]:  # Top 5 patterns
                if self.pattern_matches_code(pattern, contract_code):
                    vulnerabilities.append({
                        'type': pattern['vulnerability_type'],
                        'severity': pattern['severity'],
                        'confidence': pattern['confidence_score'],
                        'source': 'learned_pattern',
                        'pattern_id': pattern['pattern_id'],
                        'mitigation': pattern['mitigation']
                    })
        except Exception as e:
            print(f"Pattern query failed: {e}")
        
        # Submit results back for learning
        if vulnerabilities:
            scan_data = {
                "contract_id": f"api_scan_{contract_info.get('name', 'unknown')}",
                "source": "api_scanner",
                "project_name": contract_info.get('name', 'Unknown'),
                "audit_firm": "API Learning Scanner",
                "audit_date": "2024-01-15",
                "blockchain": contract_info.get('blockchain', 'ethereum'),
                "category": contract_info.get('category', 'unknown'),
                "vulnerabilities": [
                    {
                        "id": f"V-{i+1:03d}",
                        "type": vuln['type'],
                        "severity": vuln['severity'],
                        "title": f"{vuln['type']} vulnerability",
                        "description": f"Detected {vuln['type']} with {vuln['confidence']:.3f} confidence",
                        "confidence": vuln['confidence']
                    }
                    for i, vuln in enumerate(vulnerabilities)
                ]
            }
            
            await self.submit_scan_results(scan_data)
        
        return vulnerabilities
    
    def pattern_matches_code(self, pattern: Dict[str, Any], code: str) -> bool:
        """Check if a learned pattern matches the code"""
        import re
        
        # Simple pattern matching - enhance based on pattern format
        for rule in pattern.get('detection_rules', []):
            if rule.get('type') == 'regex':
                if re.search(rule['pattern'], code, re.IGNORECASE):
                    return True
        
        return False

# Usage example
async def api_scanner_example():
    scanner = APILearningScanner()
    
    contract_code = """
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount);
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success);
        balances[msg.sender] -= amount;
    }
    """
    
    contract_info = {
        "name": "TestContract",
        "blockchain": "ethereum",
        "category": "defi"
    }
    
    vulnerabilities = await scanner.enhanced_scan(contract_code, contract_info)
    
    for vuln in vulnerabilities:
        print(f"API Found: {vuln['type']} (confidence: {vuln['confidence']:.3f})")
```

### 3. CLI Integration

```bash
#!/bin/bash
# integrate_with_scanner.sh - Example CLI integration script

# Configuration
LEARNING_CLI="python audit_learning_cli.py"
CONTRACTS_DIR="./contracts"
RESULTS_DIR="./scan_results"
PATTERNS_FILE="./learned_patterns.json"

echo "🧠 Enhanced Scanner with Learning Integration"
echo "=============================================="

# Step 1: Export latest learned patterns
echo "📦 Exporting learned patterns..."
$LEARNING_CLI export scanner-patterns --format json --output $PATTERNS_FILE

if [ $? -eq 0 ]; then
    echo "✅ Patterns exported successfully"
else
    echo "❌ Failed to export patterns"
    exit 1
fi

# Step 2: Scan contracts with learned patterns
echo "🔍 Scanning contracts with learned patterns..."
mkdir -p $RESULTS_DIR

for contract in $CONTRACTS_DIR/*.sol; do
    if [ -f "$contract" ]; then
        contract_name=$(basename "$contract" .sol)
        echo "  📄 Scanning $contract_name..."
        
        # Use learning system for prediction
        prediction_result="$RESULTS_DIR/${contract_name}_prediction.json"
        $LEARNING_CLI query predict "$contract" > "$prediction_result"
        
        # Your traditional scanner integration here
        # traditional_scanner --input "$contract" --patterns "$PATTERNS_FILE" --output "$RESULTS_DIR/${contract_name}_scan.json"
        
        echo "  ✅ Completed $contract_name"
    fi
done

# Step 3: Feed results back to learning system
echo "📚 Feeding scan results back to learning system..."

# Convert scan results to learning format and ingest
# This would be customized based on your scanner's output format
for result_file in $RESULTS_DIR/*_scan.json; do
    if [ -f "$result_file" ]; then
        # Convert and ingest (implement based on your format)
        # python convert_results_to_learning_format.py "$result_file" | $LEARNING_CLI ingest file -
        echo "  📥 Processed $(basename $result_file)"
    fi
done

# Step 4: Retrain models if enough new data
echo "🤖 Checking if model retraining is needed..."
$LEARNING_CLI train models

echo "🎉 Enhanced scanning complete!"
echo "📊 View statistics: $LEARNING_CLI stats overview"
```

### 4. File-Based Integration

```python
# file_integration.py - Integration via file exports
import json
from pathlib import Path
from typing import List, Dict, Any

class FileBasedIntegration:
    def __init__(self, patterns_file: str = "./scanner_patterns.json"):
        self.patterns_file = Path(patterns_file)
        self.patterns = []
        self.load_patterns()
    
    def load_patterns(self):
        """Load learned patterns from exported file"""
        if self.patterns_file.exists():
            with open(self.patterns_file, 'r') as f:
                data = json.load(f)
                self.patterns = data.get('patterns', [])
            print(f"✅ Loaded {len(self.patterns)} learned patterns")
        else:
            print("❌ No patterns file found. Run: audit_learning_cli.py export scanner-patterns")
    
    def convert_to_scanner_rules(self) -> List[Dict[str, Any]]:
        """Convert learned patterns to your scanner's rule format"""
        scanner_rules = []
        
        for pattern in self.patterns:
            # Convert to your scanner's format
            rule = {
                'id': pattern['id'],
                'name': pattern['name'],
                'severity': pattern['severity'],
                'confidence': pattern['confidence'],
                'description': pattern['description'],
                'mitigation': pattern['mitigation'],
                'cwe_id': pattern.get('cwe_id'),
                'regex_rules': [],
                'ast_rules': []
            }
            
            # Extract detection rules
            for detection_rule in pattern.get('detection_rules', []):
                if detection_rule['type'] == 'regex':
                    rule['regex_rules'].append({
                        'pattern': detection_rule['pattern'],
                        'description': detection_rule['description'],
                        'confidence': detection_rule['confidence']
                    })
                elif detection_rule['type'] == 'ast':
                    rule['ast_rules'].append({
                        'pattern': detection_rule['pattern'],
                        'description': detection_rule['description'],
                        'confidence': detection_rule['confidence']
                    })
            
            scanner_rules.append(rule)
        
        return scanner_rules
    
    def export_to_scanner_format(self, output_file: str):
        """Export patterns to your scanner's native format"""
        rules = self.convert_to_scanner_rules()
        
        # Example: Export to SARIF format
        sarif_output = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "Learning Enhanced Scanner",
                        "version": "1.0.0",
                        "rules": [
                            {
                                "id": rule['id'],
                                "name": rule['name'],
                                "shortDescription": {"text": rule['description']},
                                "fullDescription": {"text": rule['description']},
                                "defaultConfiguration": {
                                    "level": self.severity_to_level(rule['severity'])
                                },
                                "properties": {
                                    "confidence": rule['confidence'],
                                    "cwe_id": rule.get('cwe_id'),
                                    "mitigation": rule['mitigation']
                                }
                            }
                            for rule in rules
                        ]
                    }
                }
            }]
        }
        
        with open(output_file, 'w') as f:
            json.dump(sarif_output, f, indent=2)
        
        print(f"✅ Exported {len(rules)} rules to {output_file}")
    
    def severity_to_level(self, severity: str) -> str:
        """Convert severity to SARIF level"""
        mapping = {
            'Critical': 'error',
            'High': 'error',
            'Medium': 'warning',
            'Low': 'note'
        }
        return mapping.get(severity, 'warning')

# Usage
if __name__ == "__main__":
    integration = FileBasedIntegration()
    
    # Export to SARIF format
    integration.export_to_scanner_format("learned_rules.sarif")
    
    # Get rules for direct integration
    rules = integration.convert_to_scanner_rules()
    print(f"Converted {len(rules)} patterns to scanner rules")
```

## 🔄 Continuous Learning Workflow

### 1. Initial Setup
```bash
# Initialize the learning system
python audit_learning_cli.py ingest massive --max-per-source 100

# Train initial models
python audit_learning_cli.py train models

# Export initial patterns
python audit_learning_cli.py export scanner-patterns --format json
```

### 2. Daily Operations
```bash
# Update with new audit data (automated)
python audit_learning_cli.py ingest massive --max-per-source 10 --categories defi nft

# Retrain models weekly
python audit_learning_cli.py train models --force

# Export updated patterns
python audit_learning_cli.py export scanner-patterns --format json
```

### 3. Feedback Loop
```python
# After each scan, feed results back
async def feedback_loop(scan_results: List[Dict], contract_info: Dict):
    learning_db = MassiveAuditLearningDatabase()
    
    # Convert scan results to audit contract format
    audit_contract = create_audit_contract_from_scan(scan_results, contract_info)
    
    # Feed back to learning system
    await learning_db.ingest_audit_contract(audit_contract)
    
    # Periodic retraining
    stats = await learning_db.get_learning_statistics()
    if stats['total_contracts'] % 100 == 0:  # Every 100 new contracts
        await learning_db.train_machine_learning_models()
```

## 📊 Performance Optimization

### 1. Caching Predictions
```python
import asyncio
from functools import lru_cache
import hashlib

class CachedLearningScanner:
    def __init__(self):
        self.learning_db = MassiveAuditLearningDatabase()
        self.prediction_cache = {}
    
    def get_code_hash(self, code: str) -> str:
        return hashlib.md5(code.encode()).hexdigest()
    
    async def cached_predict(self, code: str) -> Dict[str, Any]:
        code_hash = self.get_code_hash(code)
        
        if code_hash in self.prediction_cache:
            return self.prediction_cache[code_hash]
        
        prediction = await self.learning_db.predict_vulnerability_type(code)
        self.prediction_cache[code_hash] = prediction
        
        # Limit cache size
        if len(self.prediction_cache) > 1000:
            # Remove oldest entries
            oldest_keys = list(self.prediction_cache.keys())[:100]
            for key in oldest_keys:
                del self.prediction_cache[key]
        
        return prediction
```

### 2. Batch Processing
```python
async def batch_scan_contracts(contracts: List[str]) -> List[Dict[str, Any]]:
    learning_db = MassiveAuditLearningDatabase()
    
    # Process in batches for better performance
    batch_size = 10
    all_results = []
    
    for i in range(0, len(contracts), batch_size):
        batch = contracts[i:i + batch_size]
        
        # Process batch concurrently
        tasks = [learning_db.predict_vulnerability_type(code) for code in batch]
        batch_results = await asyncio.gather(*tasks)
        
        all_results.extend(batch_results)
    
    return all_results
```

## 🚨 Error Handling & Monitoring

```python
import logging
from typing import Optional

class RobustLearningScanner:
    def __init__(self):
        self.learning_db = MassiveAuditLearningDatabase()
        self.fallback_rules = self.load_fallback_rules()
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    async def safe_predict(self, code: str) -> Optional[Dict[str, Any]]:
        """Prediction with error handling and fallback"""
        try:
            return await self.learning_db.predict_vulnerability_type(code)
        except Exception as e:
            self.logger.error(f"ML prediction failed: {e}")
            
            # Fallback to rule-based detection
            return self.fallback_prediction(code)
    
    def fallback_prediction(self, code: str) -> Dict[str, Any]:
        """Fallback to traditional rule-based detection"""
        # Implement basic pattern matching
        detected_patterns = []
        
        for rule in self.fallback_rules:
            if self.apply_fallback_rule(code, rule):
                detected_patterns.append(rule)
        
        if detected_patterns:
            # Return highest severity finding
            highest_severity = max(detected_patterns, key=lambda x: x['severity_score'])
            return {
                'predicted_type': highest_severity['type'],
                'predicted_severity': highest_severity['severity'],
                'overall_confidence': 0.5,  # Lower confidence for fallback
                'source': 'fallback_rules',
                'recommendation': highest_severity['mitigation']
            }
        
        return {
            'predicted_type': 'unknown',
            'predicted_severity': 'Unknown',
            'overall_confidence': 0.0,
            'source': 'fallback',
            'recommendation': 'Manual review recommended'
        }
    
    def load_fallback_rules(self) -> List[Dict[str, Any]]:
        """Load basic fallback rules"""
        return [
            {
                'type': 'reentrancy',
                'pattern': r'\.call\{.*value.*\}.*\(\)',
                'severity': 'High',
                'severity_score': 8,
                'mitigation': 'Use reentrancy guard'
            },
            {
                'type': 'access_control',
                'pattern': r'onlyOwner|require\s*\(\s*msg\.sender\s*==',
                'severity': 'Medium',
                'severity_score': 6,
                'mitigation': 'Implement proper access control'
            }
        ]
    
    def apply_fallback_rule(self, code: str, rule: Dict[str, Any]) -> bool:
        """Apply fallback rule to code"""
        import re
        return bool(re.search(rule['pattern'], code, re.IGNORECASE))
```

## 🎯 Best Practices

### 1. Data Quality
- **Validate Input**: Always validate contract code and metadata
- **Deduplicate**: Prevent duplicate contracts from skewing results
- **Clean Data**: Remove malformed or incomplete audit data
- **Version Control**: Track pattern versions and evolution

### 2. Model Management
- **Regular Retraining**: Retrain models weekly or after significant data updates
- **Performance Monitoring**: Track accuracy, precision, and recall
- **A/B Testing**: Compare different model configurations
- **Rollback Capability**: Keep previous model versions for rollback

### 3. Integration Architecture
- **Graceful Degradation**: Always have fallback mechanisms
- **Caching Strategy**: Cache predictions for performance
- **Rate Limiting**: Implement rate limits for API calls
- **Monitoring**: Log all predictions and performance metrics

### 4. Security Considerations
- **Input Validation**: Sanitize all inputs to prevent injection attacks
- **Access Control**: Implement proper authentication for API endpoints
- **Data Privacy**: Don't store sensitive contract information
- **Audit Logging**: Log all learning system interactions

## 📈 Scaling Your Integration

### Horizontal Scaling
```yaml
# docker-compose.yml for scaled deployment
version: '3.8'
services:
  learning-api:
    image: your-org/audit-learning:latest
    deploy:
      replicas: 3
    environment:
      - DATABASE_PATH=/shared/audit_learning.db
    volumes:
      - shared-db:/shared

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf

volumes:
  shared-db:
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        
        print(f"{func.__name__} took {end_time - start_time:.3f} seconds")
        return result
    return wrapper

class MonitoredScanner(LearningScanner):
    @monitor_performance
    async def scan_contract(self, *args, **kwargs):
        return await super().scan_contract(*args, **kwargs)
```

## 🎉 Success Metrics

Track these metrics to measure integration success:

- **Detection Rate**: Percentage of known vulnerabilities detected
- **False Positive Rate**: Percentage of false alarms
- **Scan Performance**: Time per contract scan
- **Learning Effectiveness**: Improvement in detection over time
- **Pattern Coverage**: Number of unique vulnerability patterns learned

## 🔗 Additional Resources

- [API Documentation](http://localhost:8000/docs) - Complete API reference
- [CLI Reference](./CLI_REFERENCE.md) - All CLI commands and options  
- [Pattern Format](./PATTERN_FORMAT.md) - Vulnerability pattern specifications
- [Performance Tuning](./PERFORMANCE_GUIDE.md) - Optimization techniques
- [Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions

---

**Ready to supercharge your scanner with learning capabilities?** 🚀

Start with the direct Python integration for maximum control, or use the REST API for language-agnostic integration. The learning system will continuously improve your scanner's detection capabilities with every audit contract it processes!