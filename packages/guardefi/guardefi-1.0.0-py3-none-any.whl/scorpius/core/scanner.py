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
            'output_format': 'json'
        }
        
        # Merge with provided config
        self.config = {**self.default_config, **self.config}
    
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

# Export main function for console script
# main_cli = main