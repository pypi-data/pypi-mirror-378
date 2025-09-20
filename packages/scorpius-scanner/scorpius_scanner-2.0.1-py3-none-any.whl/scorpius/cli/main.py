#!/usr/bin/env python3
"""
Scorpius CLI - Main Command Interface
Professional CLI for the world's strongest smart contract scanner
"""

import click
import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import logging

from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.syntax import Syntax

# Import our ASCII art (package-friendly)
try:
    from scorpius_ascii import print_header, print_version_info, print_quick_start
except ImportError:
    # Fallback if ASCII art module not available
    def print_header(style="compact", console=None):
        if console:
            console.print("[bold blue]SCORPIUS Scanner 2.0.1 - Smart Contract Security Analysis[/bold blue]")
    
    def print_version_info(version, console=None):
        if console:
            console.print(f"[bold green]Version: {version}[/bold green]")
    
    def print_quick_start(console=None):
        if console:
            console.print("[bold yellow]Quick Start: scorpius scan contract.sol[/bold yellow]")

# Import core functionality
from ..core.scanner import ScorpiusScanner
from ..core.learning_system import LearningSystem

console = Console()

@click.group(invoke_without_command=True)
@click.option('--version', '-v', is_flag=True, help='Show version information')
@click.option('--quiet', '-q', is_flag=True, help='Suppress header output')
@click.pass_context
def cli(ctx, version, quiet):
    """
    SCORPIUS - Smart Contract Security Scanner
    
    AI-powered vulnerability detection with continuous learning capabilities.
    """
    
    # Show header unless quiet mode
    if not quiet and not version:
        print_header("compact", console)
    
    if version:
        print_version_info("2.0.1", console)
        return
    
    # Show help if no command provided
    if ctx.invoked_subcommand is None:
        if not quiet:
            print_quick_start(console)
        else:
            click.echo(ctx.get_help())

@cli.command()
@click.argument('target', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file for results')
@click.option('--format', '-f', type=click.Choice(['json', 'csv', 'sarif', 'html']), 
              default='json', help='Output format')
@click.option('--report', '-r', type=click.Choice(['pdf', 'html', 'markdown']), 
              help='Generate detailed report')
@click.option('--severity', '-s', type=click.Choice(['Critical', 'High', 'Medium', 'Low']), 
              help='Minimum severity level to report')
@click.option('--confidence', '-c', type=float, default=0.5, 
              help='Minimum confidence threshold (0.0-1.0)')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
@click.option('--recursive', '-R', is_flag=True, help='Scan directories recursively')
@click.option('--comprehensive', is_flag=True, help='Use comprehensive scan with all advanced features')
@click.option('--exploit-simulation', is_flag=True, default=True, help='Enable exploit simulation')
@click.option('--semantic-analysis', is_flag=True, default=True, help='Enable semantic analysis')
@click.option('--defi-analysis', is_flag=True, default=True, help='Enable DeFi-specific analysis')
@click.option('--advanced-ml', is_flag=True, default=True, help='Enable advanced ML models')
def scan(target, output, format, report, severity, confidence, verbose, recursive, comprehensive, exploit_simulation, semantic_analysis, defi_analysis, advanced_ml):
    """
    Scan smart contracts for vulnerabilities
    
    TARGET can be a single contract file or directory containing contracts.
    
    Examples:
        scorpius scan contract.sol
        scorpius scan contracts/ --report pdf
        scorpius scan contracts/ --format json --output results.json
        scorpius scan . --recursive --severity High
    """
    
    async def run_scan():
        target_path = Path(target)
        
        if verbose:
            console.print(f"Scanning: {target_path}", style="blue")
            console.print(f"Format: {format}, Confidence: {confidence}", style="dim")
        
        # Configure scanner
        config = {
            'confidence_threshold': confidence,
            'severity_filter': severity,
            'enable_learning': True,
            'enable_exploit_simulation': exploit_simulation,
            'enable_semantic_analysis': semantic_analysis,
            'enable_defi_analysis': defi_analysis,
            'enable_advanced_ml': advanced_ml
        }
        
        # Initialize scanner
        scanner = ScorpiusScanner(config)
        await scanner.initialize()
        
        # Find contract files
        contract_files = []
        if target_path.is_file():
            if target_path.suffix == '.sol':
                contract_files = [target_path]
            else:
                console.print("Error: File must be a Solidity contract (.sol)", style="red")
                return
        else:
            # Directory scanning
            pattern = "**/*.sol" if recursive else "*.sol"
            contract_files = list(target_path.glob(pattern))
        
        if not contract_files:
            console.print("Error: No Solidity contracts found", style="red")
            return
        
        console.print(f"Found {len(contract_files)} contract(s) to scan", style="green")
        
        # Scan contracts with progress bar
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            task = progress.add_task("Scanning contracts...", total=len(contract_files))
            
            for contract_file in contract_files:
                try:
                    # Read contract
                    with open(contract_file, 'r', encoding='utf-8') as f:
                        contract_code = f.read()
                    
                    # Scan contract
                    if comprehensive:
                        scan_result = await scanner.comprehensive_scan(contract_code, str(contract_file))
                    else:
                        scan_result = await scanner.scan_contract(contract_code, str(contract_file))
                    
                    # Filter by confidence and severity
                    filtered_vulnerabilities = []
                    for vuln in scan_result.get('vulnerabilities', []):
                        if vuln.get('confidence', 0) >= confidence:
                            if not severity or vuln.get('severity') == severity:
                                filtered_vulnerabilities.append(vuln)
                    
                    result = {
                        'file': str(contract_file),
                        'scan_time': scan_result.get('scan_time', 0),
                        'vulnerabilities': filtered_vulnerabilities,
                        'total_found': len(filtered_vulnerabilities),
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    results.append(result)
                    
                    progress.update(task, advance=1, 
                                  description=f"Scanned {contract_file.name} - {len(filtered_vulnerabilities)} vulnerabilities")
                
                except Exception as e:
                    console.print(f"❌ Failed to scan {contract_file}: {e}", style="red")
                    progress.update(task, advance=1)
        
        # Display results
        await display_scan_results(results, format, output, report, verbose)
    
    asyncio.run(run_scan())

async def display_scan_results(results: List[dict], format: str, output: Optional[str], 
                              report: Optional[str], verbose: bool):
    """Display scan results in requested format"""
    
    total_vulnerabilities = sum(r['total_found'] for r in results)
    total_files = len(results)
    
    # Summary
    console.print(f"\nScan Complete!", style="bold green")
    console.print(f"   Files scanned: {total_files}")
    console.print(f"   Vulnerabilities found: {total_vulnerabilities}")
    
    if total_vulnerabilities == 0:
        console.print("No vulnerabilities found. Contracts appear secure.", style="green")
        return
    
    # Detailed results
    if verbose or total_vulnerabilities > 0:
        table = Table(title="Vulnerability Summary")
        table.add_column("File", style="cyan")
        table.add_column("Vulnerabilities", justify="right", style="red")
        table.add_column("Highest Severity", style="yellow")
        table.add_column("Scan Time", justify="right", style="green")
        
        for result in results:
            if result['total_found'] > 0:
                highest_severity = "Low"
                for vuln in result['vulnerabilities']:
                    if vuln.get('severity') in ['Critical', 'High']:
                        highest_severity = vuln['severity']
                        break
                
                table.add_row(
                    Path(result['file']).name,
                    str(result['total_found']),
                    highest_severity,
                    f"{result['scan_time']:.3f}s"
                )
        
        console.print(table)
        
        # Detailed vulnerability list
        if verbose:
            for result in results:
                if result['vulnerabilities']:
                    console.print(f"\n📄 {Path(result['file']).name}:", style="bold")
                    
                    for i, vuln in enumerate(result['vulnerabilities'], 1):
                        severity_style = {
                            'Critical': 'bold red',
                            'High': 'red', 
                            'Medium': 'yellow',
                            'Low': 'green'
                        }.get(vuln.get('severity', 'Unknown'), 'white')
                        
                        console.print(f"   {i}. [{severity_style}]{vuln.get('severity', 'Unknown')}[/{severity_style}] "
                                    f"{vuln.get('type', 'Unknown')} "
                                    f"(Confidence: {vuln.get('confidence', 0):.2f})")
                        
                        if vuln.get('description'):
                            console.print(f"      💡 {vuln['description'][:100]}...", style="dim")
    
    # Save output
    if output:
        await save_results(results, output, format)
    
    # Generate report
    if report:
        await generate_report(results, report)

async def save_results(results: List[dict], output: str, format: str):
    """Save results in specified format"""
    
    output_path = Path(output)
    
    try:
        if format == 'json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
        
        elif format == 'csv':
            import pandas as pd
            
            # Flatten results for CSV
            rows = []
            for result in results:
                for vuln in result['vulnerabilities']:
                    rows.append({
                        'file': result['file'],
                        'vulnerability_type': vuln.get('type'),
                        'severity': vuln.get('severity'),
                        'confidence': vuln.get('confidence'),
                        'description': vuln.get('description', ''),
                        'scan_time': result['scan_time']
                    })
            
            df = pd.DataFrame(rows)
            df.to_csv(output_path, index=False)
        
        elif format == 'sarif':
            # Generate SARIF 2.1.0 format
            sarif_output = {
                "version": "2.1.0",
                "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
                "runs": [{
                    "tool": {
                        "driver": {
                            "name": "Scorpius Scanner",
                            "version": "1.0.0",
                            "informationUri": "https://github.com/scorpius-security/scorpius-scanner"
                        }
                    },
                    "results": []
                }]
            }
            
            for result in results:
                for vuln in result['vulnerabilities']:
                    sarif_result = {
                        "ruleId": vuln.get('type', 'unknown'),
                        "level": vuln.get('severity', 'warning').lower(),
                        "message": {
                            "text": vuln.get('description', 'Vulnerability detected')
                        },
                        "locations": [{
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": result['file']
                                }
                            }
                        }],
                        "properties": {
                            "confidence": vuln.get('confidence', 0),
                            "scanTime": result['scan_time']
                        }
                    }
                    sarif_output["runs"][0]["results"].append(sarif_result)
            
            with open(output_path, 'w') as f:
                json.dump(sarif_output, f, indent=2)
        
        console.print(f"💾 Results saved to: {output_path}", style="green")
        
    except Exception as e:
        console.print(f"❌ Failed to save results: {e}", style="red")

async def generate_report(results: List[dict], report_type: str):
    """Generate detailed report"""
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = Path(f"scorpius_report_{timestamp}.{report_type}")
    
    try:
        if report_type == 'pdf':
            await generate_pdf_report(results, report_file)
        elif report_type == 'html':
            await generate_html_report(results, report_file)
        elif report_type == 'markdown':
            await generate_markdown_report(results, report_file)
        
        console.print(f"📄 Report generated: {report_file}", style="green")
        
    except Exception as e:
        console.print(f"❌ Failed to generate report: {e}", style="red")

async def generate_pdf_report(results: List[dict], output_file: Path):
    """Generate PDF report"""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        
        doc = SimpleDocTemplate(str(output_file), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title = Paragraph("Scorpius Security Scan Report", styles['Title'])
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Summary
        total_vulns = sum(r['total_found'] for r in results)
        summary = f"""
        Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        Files Scanned: {len(results)}
        Total Vulnerabilities: {total_vulns}
        Scanner: Scorpius v1.0.0
        """
        
        story.append(Paragraph(summary, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Detailed results
        for result in results:
            if result['vulnerabilities']:
                file_title = Paragraph(f"File: {Path(result['file']).name}", styles['Heading2'])
                story.append(file_title)
                
                for vuln in result['vulnerabilities']:
                    vuln_text = f"""
                    Type: {vuln.get('type', 'Unknown')}
                    Severity: {vuln.get('severity', 'Unknown')}
                    Confidence: {vuln.get('confidence', 0):.2f}
                    Description: {vuln.get('description', 'No description')}
                    """
                    story.append(Paragraph(vuln_text, styles['Normal']))
                    story.append(Spacer(1, 6))
        
        doc.build(story)
        
    except ImportError:
        console.print("❌ PDF generation requires: pip install reportlab", style="red")

async def generate_html_report(results: List[dict], output_file: Path):
    """Generate HTML report"""
    
    total_vulns = sum(r['total_found'] for r in results)
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Scorpius Security Scan Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 40px; background: #0a0a0a; color: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #00e5ff, #5bffea); color: #000; padding: 20px; border-radius: 10px; margin-bottom: 30px; }}
        .summary {{ background: #1a1a1a; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #00e5ff; }}
        .file-section {{ background: #1a1a1a; padding: 15px; border-radius: 8px; margin-bottom: 15px; }}
        .vulnerability {{ background: #2a2a2a; padding: 10px; margin: 10px 0; border-radius: 5px; border-left: 3px solid #ff4444; }}
        .critical {{ border-left-color: #ff0000; }}
        .high {{ border-left-color: #ff6600; }}
        .medium {{ border-left-color: #ffaa00; }}
        .low {{ border-left-color: #00ff00; }}
        .confidence {{ float: right; background: #333; padding: 2px 8px; border-radius: 3px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🦂 Scorpius Security Scan Report</h1>
        <p>World's Strongest Smart Contract Security Scanner</p>
    </div>
    
    <div class="summary">
        <h2>📊 Scan Summary</h2>
        <p><strong>Scan Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Files Scanned:</strong> {len(results)}</p>
        <p><strong>Total Vulnerabilities:</strong> {total_vulns}</p>
        <p><strong>Scanner Version:</strong> Scorpius v1.0.0</p>
    </div>
"""
    
    for result in results:
        if result['vulnerabilities']:
            html_content += f"""
    <div class="file-section">
        <h3>📄 {Path(result['file']).name}</h3>
        <p><strong>Scan Time:</strong> {result['scan_time']:.3f}s</p>
        <p><strong>Vulnerabilities Found:</strong> {result['total_found']}</p>
"""
            
            for vuln in result['vulnerabilities']:
                severity_class = vuln.get('severity', 'unknown').lower()
                html_content += f"""
        <div class="vulnerability {severity_class}">
            <div class="confidence">{vuln.get('confidence', 0):.2f}</div>
            <h4>{vuln.get('type', 'Unknown')} - {vuln.get('severity', 'Unknown')}</h4>
            <p>{vuln.get('description', 'No description available')}</p>
        </div>
"""
            
            html_content += "</div>"
    
    html_content += """
    <div class="summary">
        <h2>🛡️ Powered by Scorpius</h2>
        <p>This report was generated by Scorpius, the world's strongest smart contract security scanner.</p>
        <p>🧠 AI-Powered • 🎯 100% Precision • ⚡ Lightning Fast • 🆓 Open Source</p>
    </div>
</body>
</html>
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

async def generate_markdown_report(results: List[dict], output_file: Path):
    """Generate Markdown report"""
    
    total_vulns = sum(r['total_found'] for r in results)
    
    markdown_content = f"""# 🦂 Scorpius Security Scan Report

**World's Strongest Smart Contract Security Scanner**

## 📊 Scan Summary

- **Scan Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Files Scanned**: {len(results)}
- **Total Vulnerabilities**: {total_vulns}
- **Scanner Version**: Scorpius v1.0.0

## 🔍 Detailed Results

"""
    
    for result in results:
        if result['vulnerabilities']:
            markdown_content += f"""### 📄 {Path(result['file']).name}

**Scan Time**: {result['scan_time']:.3f}s  
**Vulnerabilities Found**: {result['total_found']}

"""
            
            for i, vuln in enumerate(result['vulnerabilities'], 1):
                severity_emoji = {
                    'Critical': '🔴',
                    'High': '🟠', 
                    'Medium': '🟡',
                    'Low': '🟢'
                }.get(vuln.get('severity'), '⚪')
                
                markdown_content += f"""#### {i}. {severity_emoji} {vuln.get('type', 'Unknown')} - {vuln.get('severity', 'Unknown')}

**Confidence**: {vuln.get('confidence', 0):.2f}  
**Description**: {vuln.get('description', 'No description available')}

"""
    
    markdown_content += """---

🛡️ **Powered by Scorpius** - World's Strongest Smart Contract Security Scanner  
🧠 AI-Powered • 🎯 100% Precision • ⚡ Lightning Fast • 🆓 Open Source
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

@cli.command()
@click.option('--data', '-d', type=click.Path(exists=True), help='Training data file (CSV/JSON)')
@click.option('--source', '-s', help='Audit source name')
@click.option('--continuous', '-c', is_flag=True, help='Continuous learning mode')
def train(data, source, continuous):
    """
    Train the scanner on new audit data
    
    Examples:
        scorpius train --data new_audits.csv
        scorpius train --source "My Security Firm"
        scorpius train --continuous
    """
    
    async def run_training():
        console.print("🤖 Training Scorpius on new audit data...", style="blue")
        
        learning_system = LearningSystem()
        await learning_system.initialize()
        
        if data:
            result = await learning_system.train_from_file(data, source)
            
            if result['success']:
                console.print(f"✅ Training completed successfully!", style="green")
                console.print(f"   • New patterns learned: {result['patterns_learned']}")
                console.print(f"   • Training accuracy: {result['accuracy']:.3f}")
            else:
                console.print(f"❌ Training failed: {result['error']}", style="red")
        
        elif continuous:
            console.print("🔄 Starting continuous learning mode...", style="blue")
            console.print("Press Ctrl+C to stop")
            
            try:
                await learning_system.continuous_learning()
            except KeyboardInterrupt:
                console.print("\n⏹️ Continuous learning stopped", style="yellow")
        
        else:
            console.print("❌ Please specify --data file or --continuous mode", style="red")
    
    asyncio.run(run_training())

@cli.command()
@click.option('--export', '-e', help='Export patterns to file')
@click.option('--format', '-f', type=click.Choice(['json', 'csv']), default='json')
@click.option('--min-confidence', default=0.7, help='Minimum confidence threshold')
def patterns(export, format, min_confidence):
    """
    Manage learned vulnerability patterns
    
    Examples:
        scorpius patterns --export scanner_rules.json
        scorpius patterns --format csv --min-confidence 0.8
    """
    
    async def run_patterns():
        learning_system = LearningSystem()
        await learning_system.initialize()
        
        stats = await learning_system.get_statistics()
        
        console.print("📋 Learned Vulnerability Patterns", style="bold")
        console.print(f"   • Total patterns: {stats['total_patterns']}")
        console.print(f"   • Vulnerability types: {stats['unique_vulnerability_types']}")
        
        if export:
            result = await learning_system.export_patterns(export, format, min_confidence)
            if result['success']:
                console.print(f"✅ Patterns exported to: {export}", style="green")
                console.print(f"   • Exported patterns: {result['pattern_count']}")
            else:
                console.print(f"❌ Export failed: {result['error']}", style="red")
    
    asyncio.run(run_patterns())

@cli.command()
@click.option('--host', default='0.0.0.0', help='API host')
@click.option('--port', default=8000, help='API port')
@click.option('--reload', is_flag=True, help='Auto-reload on changes')
def api(host, port, reload):
    """
    Start the Scorpius REST API server
    
    Examples:
        scorpius api
        scorpius api --port 9000
        scorpius api --host localhost --reload
    """
    
    try:
        import uvicorn
        from ..api.server import app
        
        console.print(f"🌐 Starting Scorpius API server...", style="blue")
        console.print(f"   • Host: {host}")
        console.print(f"   • Port: {port}")
        console.print(f"   • Docs: http://{host}:{port}/docs")
        
        uvicorn.run(
            "scorpius.api.server:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
        
    except ImportError:
        console.print("❌ API server requires: pip install scorpius-scanner[api]", style="red")

@cli.command()
def stats():
    """
    Show scanner statistics and performance metrics
    """
    
    async def show_stats():
        learning_system = LearningSystem()
        await learning_system.initialize()
        
        stats = await learning_system.get_statistics()
        
        # Create statistics table
        table = Table(title="Scorpius Scanner Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Total Contracts Learned", f"{stats.get('total_contracts', 0):,}")
        table.add_row("Vulnerability Patterns", f"{stats.get('total_patterns', 0):,}")
        table.add_row("Unique Vulnerability Types", str(stats.get('unique_vulnerability_types', 0)))
        table.add_row("Training Accuracy", f"{stats.get('training_accuracy', 0.0):.3f}")
        table.add_row("System Status", "Trained" if stats.get('is_trained') else "Not Trained")
        
        console.print(table)
        
        if stats.get('pattern_breakdown'):
            console.print("\n🎯 Top Vulnerability Patterns:", style="bold")
            sorted_patterns = sorted(stats['pattern_breakdown'].items(), key=lambda x: x[1], reverse=True)
            for pattern, count in sorted_patterns[:10]:
                console.print(f"   • {pattern}: {count} occurrences")
    
    asyncio.run(show_stats())

@cli.command()
@click.argument('code_file', type=click.Path(exists=True))
def predict(code_file):
    """
    Predict vulnerabilities for a specific code snippet
    
    Examples:
        scorpius predict contract.sol
        scorpius predict vulnerable_function.sol
    """
    
    async def run_prediction():
        try:
            with open(code_file, 'r', encoding='utf-8') as f:
                code = f.read()
            
            scanner = ScorpiusScanner()
            await scanner.initialize()
            
            console.print(f"🔮 Analyzing {Path(code_file).name}...", style="blue")
            
            prediction = await scanner.predict_vulnerability(code)
            
            # Display prediction results
            console.print("\n📊 Vulnerability Prediction Results", style="bold")
            
            prediction_panel = f"""
🎯 Predicted Type: {prediction.get('predicted_type', 'unknown')}
🚨 Predicted Severity: {prediction.get('predicted_severity', 'Unknown')}
📊 Confidence Score: {prediction.get('confidence', 0.0):.3f}
💡 Recommendation: {prediction.get('recommendation', 'No recommendation')}
🔍 Similar Patterns: {prediction.get('similar_patterns', 0)}
"""
            
            console.print(Panel(
                prediction_panel.strip(),
                title="Prediction Results",
                border_style="green" if prediction.get('confidence', 0) > 0.7 else "yellow"
            ))
            
        except Exception as e:
            console.print(f"❌ Prediction failed: {e}", style="red")
    
    asyncio.run(run_prediction())

@cli.command()
def version():
    """
    Show detailed version information
    """
    print_version_info("2.0.1", console)

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n👋 Goodbye!", style="yellow")
    except Exception as e:
        console.print(f"❌ Unexpected error: {e}", style="red")
        sys.exit(1)

def main():
    """Main entry point for the scorpius command"""
    cli()

if __name__ == "__main__":
    main()