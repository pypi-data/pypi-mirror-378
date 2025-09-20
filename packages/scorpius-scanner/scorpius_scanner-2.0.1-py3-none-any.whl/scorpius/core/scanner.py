#!/usr/bin/env python3
"""
Scorpius Scanner - Core Scanning Engine
Main scanner class that integrates all components
"""

import asyncio
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from .learning_system import LearningSystem
from .vulnerability_detector import VulnerabilityDetector
from ..reporting import EnterpriseReporter, ReportConfig

logger = logging.getLogger(__name__)

class ScorpiusScanner:
    """
    Main Scorpius Scanner class
    Integrates AI learning system with vulnerability detection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.learning_system = None
        self.vulnerability_detector = None
        self.is_initialized = False
        
        # Default configuration
        self.default_config = {
            'confidence_threshold': 0.5,
            'severity_filter': None,
            'enable_learning': True,
            'max_scan_time': 30.0,
            'output_format': 'json',
            'enable_exploit_simulation': True,
            'enable_semantic_analysis': True,
            'enable_defi_analysis': True,
            'enable_advanced_ml': True,
            'report_config': ReportConfig()
        }
        
        # Merge with provided config
        self.config = {**self.default_config, **self.config}
        
        # Initialize enterprise reporter
        self.reporter = EnterpriseReporter(self.config.get('report_config'))
    
    async def initialize(self):
        """Initialize the scanner components"""
        try:
            # Initialize learning system
            self.learning_system = LearningSystem()
            await self.learning_system.initialize()
            
            # Initialize vulnerability detector
            self.vulnerability_detector = VulnerabilityDetector(self.learning_system)
            await self.vulnerability_detector.initialize()
            
            self.is_initialized = True
            logger.info("✅ Scorpius Scanner initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize scanner: {e}")
            raise
    
    async def scan_contract(self, contract_code: str, contract_path: str = None) -> Dict[str, Any]:
        """
        Scan a smart contract for vulnerabilities
        
        Args:
            contract_code: Solidity contract source code
            contract_path: Optional path to the contract file
            
        Returns:
            Dictionary containing scan results
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Generate contract hash for tracking
            contract_hash = hashlib.sha256(contract_code.encode()).hexdigest()[:16]
            
            # Run vulnerability detection
            vulnerabilities = await self.vulnerability_detector.detect_vulnerabilities(
                contract_code, 
                contract_path
            )
            
            # Filter by confidence threshold
            filtered_vulnerabilities = [
                vuln for vuln in vulnerabilities 
                if vuln.get('confidence', 0) >= self.config['confidence_threshold']
            ]
            
            # Filter by severity if specified
            if self.config['severity_filter']:
                severity_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
                min_severity = severity_order.get(self.config['severity_filter'], 0)
                
                filtered_vulnerabilities = [
                    vuln for vuln in filtered_vulnerabilities
                    if severity_order.get(vuln.get('severity', 'Low'), 1) >= min_severity
                ]
            
            scan_time = time.time() - start_time
            
            # Prepare scan result
            scan_result = {
                'contract_hash': contract_hash,
                'contract_path': contract_path,
                'scan_time': scan_time,
                'timestamp': datetime.now().isoformat(),
                'scanner_version': '1.0.0',
                'vulnerabilities': filtered_vulnerabilities,
                'total_found': len(filtered_vulnerabilities),
                'summary': self._generate_summary(filtered_vulnerabilities),
                'recommendations': self._generate_recommendations(filtered_vulnerabilities)
            }
            
            # Feed back to learning system if enabled
            if self.config['enable_learning'] and filtered_vulnerabilities:
                await self._feed_scan_results(contract_code, contract_path, filtered_vulnerabilities)
            
            return scan_result
            
        except Exception as e:
            logger.error(f"❌ Scan failed: {e}")
            return {
                'contract_hash': hashlib.sha256(contract_code.encode()).hexdigest()[:16],
                'contract_path': contract_path,
                'scan_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat(),
                'scanner_version': '1.0.0',
                'error': str(e),
                'vulnerabilities': [],
                'total_found': 0
            }
    
    async def scan_directory(self, directory_path: str, recursive: bool = False) -> Dict[str, Any]:
        """
        Scan all contracts in a directory
        
        Args:
            directory_path: Path to directory containing contracts
            recursive: Whether to scan subdirectories
            
        Returns:
            Dictionary containing aggregated scan results
        """
        
        directory = Path(directory_path)
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        # Find contract files
        pattern = "**/*.sol" if recursive else "*.sol"
        contract_files = list(directory.glob(pattern))
        
        if not contract_files:
            return {
                'directory': str(directory),
                'files_scanned': 0,
                'total_vulnerabilities': 0,
                'scan_results': []
            }
        
        # Scan all contracts
        scan_results = []
        total_vulnerabilities = 0
        
        for contract_file in contract_files:
            try:
                with open(contract_file, 'r', encoding='utf-8') as f:
                    contract_code = f.read()
                
                result = await self.scan_contract(contract_code, str(contract_file))
                scan_results.append(result)
                total_vulnerabilities += result.get('total_found', 0)
                
            except Exception as e:
                logger.warning(f"Failed to scan {contract_file}: {e}")
                scan_results.append({
                    'contract_path': str(contract_file),
                    'error': str(e),
                    'vulnerabilities': [],
                    'total_found': 0
                })
        
        return {
            'directory': str(directory),
            'files_scanned': len(contract_files),
            'total_vulnerabilities': total_vulnerabilities,
            'scan_results': scan_results,
            'summary': self._generate_directory_summary(scan_results)
        }
    
    async def predict_vulnerability(self, code_snippet: str) -> Dict[str, Any]:
        """
        Predict vulnerability type for a code snippet
        
        Args:
            code_snippet: Solidity code to analyze
            
        Returns:
            Prediction results with confidence scores
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        return await self.learning_system.predict_vulnerability_type(code_snippet)
    
    def _generate_summary(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate vulnerability summary"""
        
        if not vulnerabilities:
            return {
                'total': 0,
                'by_severity': {},
                'by_type': {},
                'highest_severity': None,
                'average_confidence': 0.0
            }
        
        # Count by severity
        severity_counts = {}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'Unknown')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Count by type
        type_counts = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.get('type', 'unknown')
            type_counts[vuln_type] = type_counts.get(vuln_type, 0) + 1
        
        # Determine highest severity
        severity_order = ['Critical', 'High', 'Medium', 'Low']
        highest_severity = None
        for severity in severity_order:
            if severity in severity_counts:
                highest_severity = severity
                break
        
        # Calculate average confidence
        confidences = [vuln.get('confidence', 0) for vuln in vulnerabilities]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        return {
            'total': len(vulnerabilities),
            'by_severity': severity_counts,
            'by_type': type_counts,
            'highest_severity': highest_severity,
            'average_confidence': avg_confidence
        }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations"""
        
        if not vulnerabilities:
            return ["✅ No vulnerabilities detected. Your contract appears secure!"]
        
        recommendations = []
        
        # Severity-based recommendations
        critical_count = len([v for v in vulnerabilities if v.get('severity') == 'Critical'])
        high_count = len([v for v in vulnerabilities if v.get('severity') == 'High'])
        
        if critical_count > 0:
            recommendations.append(f"🚨 URGENT: Address {critical_count} Critical vulnerability(s) immediately")
        
        if high_count > 0:
            recommendations.append(f"⚠️ HIGH PRIORITY: Fix {high_count} High severity vulnerability(s)")
        
        # Type-specific recommendations
        vuln_types = set(v.get('type') for v in vulnerabilities)
        
        type_recommendations = {
            'reentrancy': 'Implement reentrancy guards and follow checks-effects-interactions pattern',
            'access_control': 'Add proper access control modifiers and role-based permissions',
            'oracle_manipulation': 'Use TWAP oracles and implement price deviation checks',
            'flash_loan_attack': 'Add flash loan protection mechanisms',
            'integer_overflow': 'Use SafeMath or Solidity 0.8+ built-in overflow protection'
        }
        
        for vuln_type in vuln_types:
            if vuln_type in type_recommendations:
                recommendations.append(f"🔧 {type_recommendations[vuln_type]}")
        
        # General recommendations
        if len(vulnerabilities) > 3:
            recommendations.append("📋 Consider comprehensive security audit by professional firm")
        
        recommendations.append("✅ Re-scan after implementing fixes to verify resolution")
        
        return recommendations
    
    def _generate_directory_summary(self, scan_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary for directory scan"""
        
        total_files = len(scan_results)
        files_with_vulnerabilities = len([r for r in scan_results if r.get('total_found', 0) > 0])
        total_vulnerabilities = sum(r.get('total_found', 0) for r in scan_results)
        
        # Aggregate severity counts
        severity_totals = {}
        for result in scan_results:
            for vuln in result.get('vulnerabilities', []):
                severity = vuln.get('severity', 'Unknown')
                severity_totals[severity] = severity_totals.get(severity, 0) + 1
        
        return {
            'total_files': total_files,
            'files_with_vulnerabilities': files_with_vulnerabilities,
            'total_vulnerabilities': total_vulnerabilities,
            'severity_distribution': severity_totals,
            'security_score': max(0, 100 - (total_vulnerabilities * 10))  # Simple scoring
        }
    
    async def _feed_scan_results(self, contract_code: str, contract_path: str, vulnerabilities: List[Dict]):
        """Feed scan results back to learning system"""
        try:
            await self.learning_system.feed_scan_results(contract_code, contract_path, vulnerabilities)
        except Exception as e:
            logger.warning(f"Failed to feed scan results to learning system: {e}")
    
    async def comprehensive_scan(self, contract_code: str, contract_path: str = None) -> Dict[str, Any]:
        """
        Comprehensive scan using all advanced capabilities
        """
        
        if not self.is_initialized:
            await self.initialize()
        
        start_time = time.time()
        
        try:
            # Generate contract hash
            contract_hash = hashlib.sha256(contract_code.encode()).hexdigest()[:16]
            
            # 1. Basic vulnerability detection
            basic_vulnerabilities = await self.vulnerability_detector.detect_vulnerabilities(
                contract_code, 
                contract_path
            )
            
            # 2. Semantic analysis
            semantic_analysis = {}
            if self.config.get('enable_semantic_analysis', True):
                semantic_analysis = self.vulnerability_detector.semantic_analyzer.analyze_contract(contract_code)
            
            # 3. DeFi-specific analysis
            defi_vulnerabilities = []
            if self.config.get('enable_defi_analysis', True):
                defi_vulnerabilities = self.vulnerability_detector.defi_analyzer.analyze_defi_vulnerabilities(contract_code)
            
            # 4. Advanced ML predictions
            ml_predictions = []
            if self.config.get('enable_advanced_ml', True) and self.learning_system.advanced_ml:
                ml_predictions = self.learning_system.advanced_ml.predict_vulnerability(contract_code)
            
            # 5. Exploit simulation for high-confidence vulnerabilities
            enhanced_vulnerabilities = []
            for vuln in basic_vulnerabilities:
                if (vuln.get('confidence', 0) > 0.8 and 
                    self.config.get('enable_exploit_simulation', True)):
                    enhanced_vuln = await self.vulnerability_detector.exploit_simulator.validate_vulnerability(
                        vuln, contract_code
                    )
                    enhanced_vulnerabilities.append(enhanced_vuln)
                else:
                    enhanced_vulnerabilities.append(vuln)
            
            # 6. Combine all results
            all_vulnerabilities = enhanced_vulnerabilities.copy()
            
            # Add DeFi vulnerabilities
            for defi_vuln in defi_vulnerabilities:
                all_vulnerabilities.append({
                    'id': f"DEFI-{len(all_vulnerabilities)+1:03d}",
                    'type': defi_vuln.type,
                    'severity': defi_vuln.severity,
                    'confidence': defi_vuln.confidence,
                    'description': defi_vuln.description,
                    'source': 'defi_analyzer',
                    'attack_vector': defi_vuln.attack_vector,
                    'economic_impact': defi_vuln.economic_impact,
                    'remediation': defi_vuln.remediation,
                    'real_world_examples': defi_vuln.real_world_examples
                })
            
            # Add ML predictions
            for ml_pred in ml_predictions:
                all_vulnerabilities.append({
                    'id': f"ML-{len(all_vulnerabilities)+1:03d}",
                    'type': ml_pred.vulnerability_type,
                    'severity': ml_pred.severity,
                    'confidence': ml_pred.confidence,
                    'description': ml_pred.explanation,
                    'source': 'advanced_ml',
                    'features_used': ml_pred.features_used
                })
            
            # 7. Filter and deduplicate
            filtered_vulnerabilities = self._filter_and_deduplicate(all_vulnerabilities)
            
            scan_time = time.time() - start_time
            
            # 8. Prepare comprehensive result
            comprehensive_result = {
                'success': True,
                'scan_time': scan_time,
                'contract_hash': contract_hash,
                'total_vulnerabilities': len(filtered_vulnerabilities),
                'vulnerabilities': filtered_vulnerabilities,
                'semantic_analysis': semantic_analysis,
                'defi_analysis': {
                    'total_defi_vulnerabilities': len(defi_vulnerabilities),
                    'defi_vulnerabilities': defi_vulnerabilities
                },
                'ml_analysis': {
                    'total_ml_predictions': len(ml_predictions),
                    'ml_predictions': ml_predictions
                },
                'statistics': {
                    'critical_count': len([v for v in filtered_vulnerabilities if v.get('severity') == 'Critical']),
                    'high_count': len([v for v in filtered_vulnerabilities if v.get('severity') == 'High']),
                    'medium_count': len([v for v in filtered_vulnerabilities if v.get('severity') == 'Medium']),
                    'low_count': len([v for v in filtered_vulnerabilities if v.get('severity') == 'Low']),
                    'average_confidence': sum(v.get('confidence', 0) for v in filtered_vulnerabilities) / max(len(filtered_vulnerabilities), 1)
                },
                'scan_configuration': {
                    'exploit_simulation_enabled': self.config.get('enable_exploit_simulation', True),
                    'semantic_analysis_enabled': self.config.get('enable_semantic_analysis', True),
                    'defi_analysis_enabled': self.config.get('enable_defi_analysis', True),
                    'advanced_ml_enabled': self.config.get('enable_advanced_ml', True)
                }
            }
            
            return comprehensive_result
            
        except Exception as e:
            logger.error(f"Comprehensive scan failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'scan_time': time.time() - start_time,
                'contract_hash': contract_hash if 'contract_hash' in locals() else None
            }
    
    def _filter_and_deduplicate(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter and deduplicate vulnerabilities"""
        
        # Filter by confidence threshold
        filtered = [
            vuln for vuln in vulnerabilities 
            if vuln.get('confidence', 0) >= self.config['confidence_threshold']
        ]
        
        # Filter by severity if specified
        if self.config['severity_filter']:
            severity_order = {'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1}
            min_severity = severity_order.get(self.config['severity_filter'], 0)
            
            filtered = [
                vuln for vuln in filtered
                if severity_order.get(vuln.get('severity', 'Low'), 1) >= min_severity
            ]
        
        # Deduplicate based on type and location
        seen = set()
        deduplicated = []
        
        for vuln in filtered:
            key = (vuln.get('type', ''), vuln.get('line_number', ''), vuln.get('file_path', ''))
            if key not in seen:
                seen.add(key)
                deduplicated.append(vuln)
        
        return deduplicated
    
    async def generate_report(self, scan_results: Dict[str, Any], output_path: str, format: str = 'html') -> str:
        """Generate enterprise report"""
        
        # Update reporter config
        self.reporter.config.format = format
        
        # Generate report
        report_path = self.reporter.generate_report(scan_results, output_path)
        
        logger.info(f"✅ Report generated: {report_path}")
        return report_path

# Export main function for console script
# main_cli = main