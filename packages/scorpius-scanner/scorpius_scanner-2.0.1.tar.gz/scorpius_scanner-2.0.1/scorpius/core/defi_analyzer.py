#!/usr/bin/env python3
"""
Scorpius DeFi Analyzer
Advanced DeFi-specific vulnerability detection and analysis
"""

import re
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DeFiVulnerability:
    """DeFi-specific vulnerability representation"""
    type: str
    severity: str
    confidence: float
    description: str
    attack_vector: str
    economic_impact: str
    remediation: str
    real_world_examples: List[str]

class DeFiAnalyzer:
    """
    Advanced DeFi-specific vulnerability analyzer
    """
    
    def __init__(self):
        self.defi_patterns = self._init_defi_patterns()
        self.attack_vectors = self._init_attack_vectors()
        self.economic_models = self._init_economic_models()
        
    def _init_defi_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize DeFi-specific vulnerability patterns"""
        
        return {
            'flash_loan_attack': {
                'patterns': [
                    r'flashLoan\s*\(',
                    r'flash.*loan',
                    r'borrow.*repay',
                    r'instant.*borrow'
                ],
                'context_patterns': [
                    r'price.*manipulat',
                    r'arbitrage.*profit',
                    r'atomic.*transaction',
                    r'profit.*calculation'
                ],
                'severity': 'Critical',
                'confidence': 0.92,
                'economic_impact': 'High',
                'attack_vector': 'Flash loan manipulation for profit extraction',
                'real_examples': [
                    'Harvest Finance ($34M)',
                    'Cream Finance ($130M)',
                    'PancakeBunny ($45M)',
                    'bZx Protocol ($8M)'
                ]
            },
            
            'oracle_manipulation': {
                'patterns': [
                    r'\.getPrice\s*\(',
                    r'\.latestAnswer\s*\(',
                    r'getReserves\s*\(',
                    r'oracle\.\w+\s*\(',
                    r'chainlink.*price',
                    r'spot.*price'
                ],
                'context_patterns': [
                    r'single.*source',
                    r'manipulat.*price',
                    r'(?!TWAP|average|median)',
                    r'flash.*loan.*price',
                    r'arbitrage.*price'
                ],
                'severity': 'Critical',
                'confidence': 0.90,
                'economic_impact': 'Very High',
                'attack_vector': 'Oracle price manipulation for economic gain',
                'real_examples': [
                    'Synthetix ($37M)',
                    'bZx Protocol ($1M)',
                    'Harvest Finance ($34M)',
                    'Mango Markets ($100M)'
                ]
            },
            
            'governance_attack': {
                'patterns': [
                    r'vote.*token',
                    r'proposal.*execute',
                    r'governance.*token',
                    r'voting.*power',
                    r'timelock.*execute',
                    r'admin.*proposal'
                ],
                'context_patterns': [
                    r'governance.*manipulat',
                    r'voting.*exploit',
                    r'timelock.*bypass',
                    r'proposal.*attack'
                ],
                'severity': 'Critical',
                'confidence': 0.88,
                'economic_impact': 'Extreme',
                'attack_vector': 'Governance system manipulation',
                'real_examples': [
                    'Beanstalk ($182M)',
                    'Tornado Cash (Governance takeover)',
                    'MakerDAO (Governance attack)',
                    'Compound (Proposal attack)'
                ]
            },
            
            'liquidity_mining_exploit': {
                'patterns': [
                    r'reward.*token',
                    r'liquidity.*mining',
                    r'staking.*reward',
                    r'yield.*farm',
                    r'reward.*distribution'
                ],
                'context_patterns': [
                    r'inflate.*reward',
                    r'manipulat.*reward',
                    r'gaming.*system',
                    r'fake.*liquidity'
                ],
                'severity': 'High',
                'confidence': 0.85,
                'economic_impact': 'Medium',
                'attack_vector': 'Liquidity mining system exploitation',
                'real_examples': [
                    'SushiSwap (Reward manipulation)',
                    'Compound (Reward farming)',
                    'Yearn Finance (Vault gaming)'
                ]
            },
            
            'amm_manipulation': {
                'patterns': [
                    r'addLiquidity\s*\(',
                    r'removeLiquidity\s*\(',
                    r'getAmountsOut\s*\(',
                    r'getAmountsIn\s*\(',
                    r'swapExactTokensForTokens',
                    r'swapTokensForExactTokens'
                ],
                'context_patterns': [
                    r'price.*impact',
                    r'manipulat.*reserve',
                    r'flash.*swap',
                    r'arbitrage.*profit'
                ],
                'severity': 'High',
                'confidence': 0.87,
                'economic_impact': 'Medium',
                'attack_vector': 'AMM price manipulation',
                'real_examples': [
                    'Uniswap V2 (Price manipulation)',
                    'SushiSwap (Reserve manipulation)',
                    'PancakeSwap (Flash swap attacks)'
                ]
            },
            
            'bridge_vulnerability': {
                'patterns': [
                    r'bridge.*deposit',
                    r'bridge.*withdraw',
                    r'cross.*chain',
                    r'multi.*chain',
                    r'lock.*mint',
                    r'burn.*unlock'
                ],
                'context_patterns': [
                    r'signature.*verification',
                    r'validator.*consensus',
                    r'relay.*attack',
                    r'validator.*bribe'
                ],
                'severity': 'Critical',
                'confidence': 0.91,
                'economic_impact': 'Extreme',
                'attack_vector': 'Cross-chain bridge exploitation',
                'real_examples': [
                    'Ronin Bridge ($625M)',
                    'Wormhole ($325M)',
                    'Nomad Bridge ($190M)',
                    'Poly Network ($611M)'
                ]
            },
            
            'yield_farming_exploit': {
                'patterns': [
                    r'yield.*farm',
                    r'farming.*reward',
                    r'compound.*interest',
                    r'auto.*compound',
                    r'vault.*strategy'
                ],
                'context_patterns': [
                    r'strategy.*exploit',
                    r'vault.*manipulat',
                    r'reward.*gaming',
                    r'compound.*attack'
                ],
                'severity': 'High',
                'confidence': 0.83,
                'economic_impact': 'Medium',
                'attack_vector': 'Yield farming strategy exploitation',
                'real_examples': [
                    'Yearn Finance (Vault exploits)',
                    'Harvest Finance (Strategy gaming)',
                    'Compound (Interest rate manipulation)'
                ]
            },
            
            'mev_exploitation': {
                'patterns': [
                    r'frontrun',
                    r'backrun',
                    r'sandwich.*attack',
                    r'arbitrage.*bot',
                    r'maximal.*extractable.*value'
                ],
                'context_patterns': [
                    r'mev.*extraction',
                    r'priority.*fee',
                    r'gas.*price.*manipulation',
                    r'block.*space.*auction'
                ],
                'severity': 'Medium',
                'confidence': 0.75,
                'economic_impact': 'Low',
                'attack_vector': 'MEV extraction through transaction ordering',
                'real_examples': [
                    'Uniswap (Sandwich attacks)',
                    'SushiSwap (Front-running)',
                    'Various DEXs (MEV bots)'
                ]
            }
        }
    
    def _init_attack_vectors(self) -> Dict[str, Dict[str, Any]]:
        """Initialize DeFi attack vectors"""
        
        return {
            'flash_loan_arbitrage': {
                'description': 'Use flash loans to manipulate prices and extract profit',
                'steps': [
                    'Borrow large amount via flash loan',
                    'Manipulate price through large trade',
                    'Execute profitable transaction',
                    'Repay flash loan with profit'
                ],
                'profit_potential': 'Very High',
                'complexity': 'Medium'
            },
            
            'oracle_price_manipulation': {
                'description': 'Manipulate oracle prices for economic gain',
                'steps': [
                    'Identify single-source oracle',
                    'Execute large trade to move price',
                    'Trigger liquidation or arbitrage',
                    'Profit from price difference'
                ],
                'profit_potential': 'Extreme',
                'complexity': 'Low'
            },
            
            'governance_takeover': {
                'description': 'Take control of governance system',
                'steps': [
                    'Accumulate governance tokens',
                    'Submit malicious proposal',
                    'Execute proposal to extract value',
                    'Exit with stolen funds'
                ],
                'profit_potential': 'Extreme',
                'complexity': 'High'
            },
            
            'bridge_exploitation': {
                'description': 'Exploit cross-chain bridge vulnerabilities',
                'steps': [
                    'Identify bridge vulnerability',
                    'Manipulate validator consensus',
                    'Mint tokens on target chain',
                    'Withdraw real assets'
                ],
                'profit_potential': 'Extreme',
                'complexity': 'Very High'
            }
        }
    
    def _init_economic_models(self) -> Dict[str, Dict[str, Any]]:
        """Initialize DeFi economic models"""
        
        return {
            'liquidity_pools': {
                'description': 'Automated Market Maker liquidity pools',
                'risks': ['Impermanent loss', 'Price manipulation', 'Liquidity draining'],
                'vulnerabilities': ['AMM manipulation', 'Flash loan attacks', 'Oracle manipulation']
            },
            
            'lending_protocols': {
                'description': 'Decentralized lending and borrowing',
                'risks': ['Liquidation cascades', 'Oracle manipulation', 'Collateral exploitation'],
                'vulnerabilities': ['Flash loan liquidation', 'Oracle price manipulation', 'Collateral gaming']
            },
            
            'yield_farming': {
                'description': 'Automated yield optimization',
                'risks': ['Smart contract bugs', 'Strategy exploitation', 'Reward manipulation'],
                'vulnerabilities': ['Vault exploits', 'Strategy gaming', 'Reward inflation']
            },
            
            'governance_systems': {
                'description': 'Decentralized governance mechanisms',
                'risks': ['Governance attacks', 'Voting manipulation', 'Proposal exploitation'],
                'vulnerabilities': ['Governance takeover', 'Voting power manipulation', 'Malicious proposals']
            },
            
            'cross_chain_bridges': {
                'description': 'Cross-chain asset transfers',
                'risks': ['Validator attacks', 'Signature forgery', 'Consensus manipulation'],
                'vulnerabilities': ['Bridge exploitation', 'Validator bribery', 'Relay attacks']
            }
        }
    
    def analyze_defi_vulnerabilities(self, contract_code: str) -> List[DeFiVulnerability]:
        """Analyze DeFi-specific vulnerabilities"""
        
        vulnerabilities = []
        
        for vuln_type, pattern_data in self.defi_patterns.items():
            vuln = self._check_defi_vulnerability(contract_code, vuln_type, pattern_data)
            if vuln:
                vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _check_defi_vulnerability(self, contract_code: str, vuln_type: str, pattern_data: Dict[str, Any]) -> Optional[DeFiVulnerability]:
        """Check for specific DeFi vulnerability"""
        
        # Check primary patterns
        primary_matches = 0
        for pattern in pattern_data['patterns']:
            if re.search(pattern, contract_code, re.IGNORECASE):
                primary_matches += 1
        
        # Check context patterns
        context_matches = 0
        for pattern in pattern_data.get('context_patterns', []):
            if re.search(pattern, contract_code, re.IGNORECASE):
                context_matches += 1
        
        # Calculate confidence based on matches
        if primary_matches > 0:
            confidence = pattern_data['confidence']
            
            # Boost confidence for context matches
            if context_matches > 0:
                confidence = min(1.0, confidence + 0.05 * context_matches)
            
            # Boost confidence for multiple primary matches
            if primary_matches > 1:
                confidence = min(1.0, confidence + 0.03 * (primary_matches - 1))
            
            return DeFiVulnerability(
                type=vuln_type,
                severity=pattern_data['severity'],
                confidence=confidence,
                description=self._get_defi_description(vuln_type),
                attack_vector=pattern_data['attack_vector'],
                economic_impact=pattern_data['economic_impact'],
                remediation=self._get_defi_remediation(vuln_type),
                real_world_examples=pattern_data['real_examples']
            )
        
        return None
    
    def _get_defi_description(self, vuln_type: str) -> str:
        """Get DeFi vulnerability description"""
        
        descriptions = {
            'flash_loan_attack': 'Flash loan attack allowing instant borrowing for price manipulation and profit extraction',
            'oracle_manipulation': 'Oracle price manipulation vulnerability allowing attackers to influence prices for economic gain',
            'governance_attack': 'Governance system vulnerability allowing manipulation of protocol decisions',
            'liquidity_mining_exploit': 'Liquidity mining system exploitation for unfair reward extraction',
            'amm_manipulation': 'Automated Market Maker manipulation for price impact and profit',
            'bridge_vulnerability': 'Cross-chain bridge vulnerability allowing asset theft across chains',
            'yield_farming_exploit': 'Yield farming strategy exploitation for unfair reward extraction',
            'mev_exploitation': 'Maximal Extractable Value exploitation through transaction ordering'
        }
        
        return descriptions.get(vuln_type, f'DeFi-specific vulnerability: {vuln_type}')
    
    def _get_defi_remediation(self, vuln_type: str) -> str:
        """Get DeFi vulnerability remediation"""
        
        remediations = {
            'flash_loan_attack': 'Implement TWAP oracles, add slippage protection, use time-weighted prices',
            'oracle_manipulation': 'Use multiple oracle sources, implement TWAP, add price deviation checks',
            'governance_attack': 'Implement timelock delays, require multiple signatures, add governance thresholds',
            'liquidity_mining_exploit': 'Add anti-gaming mechanisms, implement fair reward distribution',
            'amm_manipulation': 'Add price impact limits, implement TWAP, use oracle price validation',
            'bridge_vulnerability': 'Implement multi-signature validation, add time delays, use multiple validators',
            'yield_farming_exploit': 'Add strategy validation, implement fair reward mechanisms',
            'mev_exploitation': 'Use MEV protection, implement fair ordering, add anti-frontrunning measures'
        }
        
        return remediations.get(vuln_type, 'Implement appropriate security measures for this vulnerability type')
    
    def analyze_economic_impact(self, vulnerability: DeFiVulnerability, contract_code: str) -> Dict[str, Any]:
        """Analyze economic impact of DeFi vulnerability"""
        
        impact_analysis = {
            'potential_loss': self._estimate_potential_loss(vulnerability, contract_code),
            'attack_complexity': self._assess_attack_complexity(vulnerability),
            'profit_potential': self._assess_profit_potential(vulnerability),
            'liquidity_impact': self._assess_liquidity_impact(vulnerability, contract_code),
            'market_impact': self._assess_market_impact(vulnerability)
        }
        
        return impact_analysis
    
    def _estimate_potential_loss(self, vulnerability: DeFiVulnerability, contract_code: str) -> str:
        """Estimate potential financial loss"""
        
        # Analyze contract for value indicators
        value_indicators = re.findall(r'(?:totalValueLocked|TVL|totalSupply|balanceOf)', contract_code, re.IGNORECASE)
        
        if vulnerability.type in ['flash_loan_attack', 'oracle_manipulation']:
            if len(value_indicators) > 0:
                return 'High ($10M - $100M)'
            else:
                return 'Medium ($1M - $10M)'
        elif vulnerability.type in ['governance_attack', 'bridge_vulnerability']:
            return 'Extreme ($100M+)'
        else:
            return 'Medium ($1M - $10M)'
    
    def _assess_attack_complexity(self, vulnerability: DeFiVulnerability) -> str:
        """Assess attack complexity"""
        
        complexity_map = {
            'flash_loan_attack': 'Medium',
            'oracle_manipulation': 'Low',
            'governance_attack': 'High',
            'bridge_vulnerability': 'Very High',
            'liquidity_mining_exploit': 'Medium',
            'amm_manipulation': 'Low',
            'yield_farming_exploit': 'Medium',
            'mev_exploitation': 'Low'
        }
        
        return complexity_map.get(vulnerability.type, 'Medium')
    
    def _assess_profit_potential(self, vulnerability: DeFiVulnerability) -> str:
        """Assess profit potential for attacker"""
        
        profit_map = {
            'flash_loan_attack': 'Very High',
            'oracle_manipulation': 'Extreme',
            'governance_attack': 'Extreme',
            'bridge_vulnerability': 'Extreme',
            'liquidity_mining_exploit': 'Medium',
            'amm_manipulation': 'Medium',
            'yield_farming_exploit': 'Medium',
            'mev_exploitation': 'Low'
        }
        
        return profit_map.get(vulnerability.type, 'Medium')
    
    def _assess_liquidity_impact(self, vulnerability: DeFiVulnerability, contract_code: str) -> str:
        """Assess impact on protocol liquidity"""
        
        if vulnerability.type in ['flash_loan_attack', 'oracle_manipulation']:
            return 'High - Can drain significant liquidity'
        elif vulnerability.type in ['governance_attack', 'bridge_vulnerability']:
            return 'Extreme - Can drain all protocol funds'
        else:
            return 'Medium - Moderate liquidity impact'
    
    def _assess_market_impact(self, vulnerability: DeFiVulnerability) -> str:
        """Assess broader market impact"""
        
        if vulnerability.type in ['governance_attack', 'bridge_vulnerability']:
            return 'Extreme - Can cause market-wide panic'
        elif vulnerability.type in ['oracle_manipulation']:
            return 'High - Can affect multiple protocols'
        else:
            return 'Medium - Localized impact'
