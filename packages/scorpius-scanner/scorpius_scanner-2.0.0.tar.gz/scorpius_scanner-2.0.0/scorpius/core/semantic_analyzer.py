#!/usr/bin/env python3
"""
Scorpius Semantic Analyzer
Advanced semantic analysis using AST parsing and control flow analysis
"""

import ast
import re
from typing import Dict, List, Any, Optional, Set, Tuple
import networkx as nx
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ASTNode:
    """AST node representation"""
    node_type: str
    value: Any
    children: List['ASTNode']
    line_number: int
    source_code: str

@dataclass
class ControlFlowNode:
    """Control flow graph node"""
    node_id: str
    node_type: str
    statement: str
    line_number: int
    variables: Set[str]
    function_calls: Set[str]

class SemanticAnalyzer:
    """
    Advanced semantic analysis for Solidity contracts
    """
    
    def __init__(self):
        self.cfg_graph = nx.DiGraph()
        self.data_flow_graph = nx.DiGraph()
        self.function_dependencies = {}
        self.state_variables = {}
        self.function_signatures = {}
        
    def analyze_contract(self, contract_code: str) -> Dict[str, Any]:
        """Perform comprehensive semantic analysis"""
        
        analysis_result = {
            'ast_analysis': self._parse_ast(contract_code),
            'control_flow_analysis': self._analyze_control_flow(contract_code),
            'data_flow_analysis': self._analyze_data_flow(contract_code),
            'function_dependencies': self._analyze_function_dependencies(contract_code),
            'variable_analysis': self._analyze_variables(contract_code),
            'call_graph': self._build_call_graph(contract_code),
            'complexity_metrics': self._calculate_complexity_metrics(contract_code)
        }
        
        return analysis_result
    
    def _parse_ast(self, contract_code: str) -> Dict[str, Any]:
        """Parse Solidity contract to AST-like structure"""
        
        # Extract key contract elements
        contract_match = re.search(r'contract\s+(\w+)\s*\{([^}]+)\}', contract_code, re.DOTALL)
        if not contract_match:
            return {'error': 'No contract found'}
        
        contract_name = contract_match.group(1)
        contract_body = contract_match.group(2)
        
        # Extract functions
        functions = []
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*(?:external|public|internal|private)?\s*(?:view|pure|payable)?\s*(?:returns\s*\([^)]*\))?\s*\{([^}]+)\}'
        
        for match in re.finditer(function_pattern, contract_body, re.DOTALL):
            function_name = match.group(1)
            function_body = match.group(2)
            
            functions.append({
                'name': function_name,
                'body': function_body,
                'line_number': contract_code[:match.start()].count('\n') + 1,
                'statements': self._extract_statements(function_body)
            })
        
        # Extract state variables
        state_vars = []
        var_pattern = r'(?:mapping|uint256|address|bool|string|bytes)\s+\w+\s+(\w+)(?:;|=\s*[^;]+;)'
        
        for match in re.finditer(var_pattern, contract_body):
            state_vars.append({
                'name': match.group(1),
                'type': match.group(0).split()[0],
                'line_number': contract_code[:match.start()].count('\n') + 1
            })
        
        return {
            'contract_name': contract_name,
            'functions': functions,
            'state_variables': state_vars,
            'total_lines': contract_code.count('\n') + 1
        }
    
    def _extract_statements(self, function_body: str) -> List[Dict[str, Any]]:
        """Extract individual statements from function body"""
        
        statements = []
        lines = function_body.strip().split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            statement_type = self._classify_statement(line)
            statements.append({
                'content': line,
                'type': statement_type,
                'line_number': i + 1
            })
        
        return statements
    
    def _classify_statement(self, statement: str) -> str:
        """Classify statement type"""
        
        if 'require(' in statement or 'assert(' in statement:
            return 'assertion'
        elif 'if(' in statement:
            return 'conditional'
        elif 'for(' in statement or 'while(' in statement:
            return 'loop'
        elif '.call(' in statement or '.delegatecall(' in statement:
            return 'external_call'
        elif 'transfer(' in statement or 'send(' in statement:
            return 'transfer'
        elif '=' in statement and not '==' in statement:
            return 'assignment'
        elif 'return' in statement:
            return 'return'
        else:
            return 'other'
    
    def _analyze_control_flow(self, contract_code: str) -> Dict[str, Any]:
        """Analyze control flow patterns"""
        
        cfg_nodes = []
        cfg_edges = []
        
        # Extract functions for CFG analysis
        functions = re.findall(r'function\s+\w+\s*\([^)]*\)\s*(?:external|public|internal|private)?\s*(?:view|pure|payable)?\s*(?:returns\s*\([^)]*\))?\s*\{([^}]+)\}', contract_code, re.DOTALL)
        
        for func_idx, function_body in enumerate(functions):
            statements = self._extract_statements(function_body)
            
            for i, stmt in enumerate(statements):
                node_id = f"func_{func_idx}_stmt_{i}"
                
                cfg_nodes.append({
                    'id': node_id,
                    'type': stmt['type'],
                    'statement': stmt['content'],
                    'line_number': stmt['line_number']
                })
                
                # Add edges based on control flow
                if i < len(statements) - 1:
                    cfg_edges.append((node_id, f"func_{func_idx}_stmt_{i+1}"))
                
                # Handle conditional branches
                if stmt['type'] == 'conditional':
                    # Add edge to next statement (false branch)
                    if i < len(statements) - 1:
                        cfg_edges.append((node_id, f"func_{func_idx}_stmt_{i+1}"))
        
        return {
            'nodes': cfg_nodes,
            'edges': cfg_edges,
            'complexity': len(cfg_nodes),
            'branching_points': len([n for n in cfg_nodes if n['type'] == 'conditional'])
        }
    
    def _analyze_data_flow(self, contract_code: str) -> Dict[str, Any]:
        """Analyze data flow patterns"""
        
        data_flows = []
        
        # Extract variable assignments and usages
        assignments = re.findall(r'(\w+)\s*=\s*([^;]+);', contract_code)
        
        for var, value in assignments:
            data_flows.append({
                'variable': var,
                'assigned_value': value,
                'type': 'assignment',
                'taint_sources': self._find_taint_sources(value),
                'taint_sinks': self._find_taint_sinks(value)
            })
        
        # Extract function calls with parameters
        function_calls = re.findall(r'(\w+)\s*\(([^)]*)\)', contract_code)
        
        for func, params in function_calls:
            data_flows.append({
                'function': func,
                'parameters': params,
                'type': 'function_call',
                'taint_analysis': self._analyze_function_taint(func, params)
            })
        
        return {
            'data_flows': data_flows,
            'taint_sources': self._extract_taint_sources(contract_code),
            'taint_sinks': self._extract_taint_sinks(contract_code),
            'sensitive_operations': self._find_sensitive_operations(contract_code)
        }
    
    def _find_taint_sources(self, expression: str) -> List[str]:
        """Find taint sources in expression"""
        
        taint_sources = []
        
        # msg.sender, msg.value, tx.origin, block.timestamp
        if re.search(r'(msg\.sender|msg\.value|tx\.origin|block\.timestamp)', expression):
            taint_sources.append('user_input')
        
        # External contract calls
        if re.search(r'\.call\(|\.delegatecall\(', expression):
            taint_sources.append('external_call')
        
        # Storage reads
        if re.search(r'storage\[|balances\[', expression):
            taint_sources.append('storage_read')
        
        return taint_sources
    
    def _find_taint_sinks(self, expression: str) -> List[str]:
        """Find taint sinks in expression"""
        
        taint_sinks = []
        
        # External calls
        if re.search(r'\.call\(|\.delegatecall\(|\.transfer\(', expression):
            taint_sinks.append('external_call')
        
        # Storage writes
        if re.search(r'storage\[.*\]\s*=|balances\[.*\]\s*=', expression):
            taint_sinks.append('storage_write')
        
        # Self-destruct
        if 'selfdestruct' in expression:
            taint_sinks.append('selfdestruct')
        
        return taint_sinks
    
    def _analyze_function_taint(self, func: str, params: str) -> Dict[str, Any]:
        """Analyze function taint"""
        
        return {
            'taint_sources': self._find_taint_sources(params),
            'taint_sinks': self._find_taint_sinks(params)
        }
    
    def _extract_taint_sources(self, contract_code: str) -> List[Dict[str, Any]]:
        """Extract all taint sources from contract"""
        
        sources = []
        
        # User inputs
        user_inputs = re.findall(r'(msg\.sender|msg\.value|tx\.origin|block\.timestamp)', contract_code)
        for inp in user_inputs:
            sources.append({
                'type': 'user_input',
                'source': inp,
                'severity': 'high'
            })
        
        # External calls
        external_calls = re.findall(r'(\w+)\.call\(|(\w+)\.delegatecall\(', contract_code)
        for call in external_calls:
            sources.append({
                'type': 'external_call',
                'source': call[0] or call[1],
                'severity': 'critical'
            })
        
        return sources
    
    def _extract_taint_sinks(self, contract_code: str) -> List[Dict[str, Any]]:
        """Extract all taint sinks from contract"""
        
        sinks = []
        
        # External calls
        external_calls = re.findall(r'(\w+)\.call\(|(\w+)\.delegatecall\(|(\w+)\.transfer\(', contract_code)
        for call in external_calls:
            sinks.append({
                'type': 'external_call',
                'sink': call[0] or call[1] or call[2],
                'severity': 'critical'
            })
        
        # Storage writes
        storage_writes = re.findall(r'(storage\[[^\]]+\]|balances\[[^\]]+\])\s*=', contract_code)
        for write in storage_writes:
            sinks.append({
                'type': 'storage_write',
                'sink': write,
                'severity': 'high'
            })
        
        return sinks
    
    def _find_sensitive_operations(self, contract_code: str) -> List[Dict[str, Any]]:
        """Find sensitive operations in contract"""
        
        sensitive_ops = []
        
        # Critical operations
        critical_patterns = [
            (r'selfdestruct\s*\(', 'selfdestruct', 'critical'),
            (r'\.delegatecall\s*\(', 'delegatecall', 'critical'),
            (r'\.call\s*\{.*value.*\}\s*\(', 'external_call_with_value', 'critical'),
            (r'assembly\s*\{', 'inline_assembly', 'high'),
            (r'create2\s*\(', 'create2', 'high'),
            (r'\.transfer\s*\(', 'transfer', 'medium')
        ]
        
        for pattern, op_type, severity in critical_patterns:
            matches = re.finditer(pattern, contract_code)
            for match in matches:
                sensitive_ops.append({
                    'type': op_type,
                    'severity': severity,
                    'line_number': contract_code[:match.start()].count('\n') + 1,
                    'code': match.group(0)
                })
        
        return sensitive_ops
    
    def _analyze_function_dependencies(self, contract_code: str) -> Dict[str, Any]:
        """Analyze function dependencies and call relationships"""
        
        dependencies = {}
        
        # Extract function definitions
        functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)', contract_code)
        
        for func in functions:
            # Find function calls within this function
            func_pattern = rf'function\s+{func}\s*\([^)]*\)\s*(?:external|public|internal|private)?\s*(?:view|pure|payable)?\s*(?:returns\s*\([^)]*\))?\s*\{{([^}}]+)\}}'
            func_match = re.search(func_pattern, contract_code, re.DOTALL)
            
            if func_match:
                func_body = func_match.group(1)
                called_functions = re.findall(r'(\w+)\s*\(', func_body)
                
                dependencies[func] = {
                    'calls': [f for f in called_functions if f in functions],
                    'external_calls': [f for f in called_functions if f not in functions],
                    'complexity': len(func_body.split('\n'))
                }
        
        return dependencies
    
    def _analyze_variables(self, contract_code: str) -> Dict[str, Any]:
        """Analyze variable usage and relationships"""
        
        variables = {}
        
        # State variables
        state_vars = re.findall(r'(?:mapping|uint256|address|bool|string|bytes)\s+(\w+)', contract_code)
        
        for var in state_vars:
            # Find all usages of this variable
            usages = re.findall(rf'{var}\s*(?:\[|\s*=|\.)', contract_code)
            
            variables[var] = {
                'type': 'state_variable',
                'usages': len(usages),
                'read_usages': len(re.findall(rf'{var}(?!\s*=)', contract_code)),
                'write_usages': len(re.findall(rf'{var}\s*=', contract_code))
            }
        
        return variables
    
    def _build_call_graph(self, contract_code: str) -> Dict[str, Any]:
        """Build function call graph"""
        
        call_graph = {
            'nodes': [],
            'edges': []
        }
        
        # Extract all functions
        functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)', contract_code)
        
        for func in functions:
            call_graph['nodes'].append({
                'id': func,
                'type': 'function'
            })
        
        # Extract function calls
        for func in functions:
            func_pattern = rf'function\s+{func}\s*\([^)]*\)\s*(?:external|public|internal|private)?\s*(?:view|pure|payable)?\s*(?:returns\s*\([^)]*\))?\s*\{{([^}}]+)\}}'
            func_match = re.search(func_pattern, contract_code, re.DOTALL)
            
            if func_match:
                func_body = func_match.group(1)
                called_functions = re.findall(r'(\w+)\s*\(', func_body)
                
                for called_func in called_functions:
                    if called_func in functions:
                        call_graph['edges'].append({
                            'from': func,
                            'to': called_func
                        })
        
        return call_graph
    
    def _calculate_complexity_metrics(self, contract_code: str) -> Dict[str, Any]:
        """Calculate complexity metrics"""
        
        # Cyclomatic complexity
        conditions = len(re.findall(r'\b(if|while|for|case)\b', contract_code))
        complexity = conditions + 1
        
        # Function count
        function_count = len(re.findall(r'function\s+\w+', contract_code))
        
        # Line count
        line_count = len(contract_code.split('\n'))
        
        # Statement count
        statement_count = len(re.findall(r';', contract_code))
        
        return {
            'cyclomatic_complexity': complexity,
            'function_count': function_count,
            'line_count': line_count,
            'statement_count': statement_count,
            'average_function_length': line_count / max(function_count, 1),
            'complexity_score': min(10, complexity / max(function_count, 1) * 10)
        }
