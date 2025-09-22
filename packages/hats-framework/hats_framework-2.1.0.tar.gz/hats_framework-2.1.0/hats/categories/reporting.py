"""
Reporting category implementation for HATS framework.
Handles report generation and output formatting.
"""

import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..utils.logger import get_logger


class ReportingCategory:
    """Handles report generation in various formats."""
    
    def __init__(self):
        """Initialize the reporting category."""
        self.logger = get_logger(__name__)
        self.category = "reporting"
    
    def generate_html_report(self, scan_results: Dict, template: str = "default") -> str:
        """
        Generate HTML report from scan results.
        
        Args:
            scan_results (Dict): Scan results data
            template (str): Report template to use
            
        Returns:
            str: HTML report content
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>HATS Security Assessment Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; }}
                .critical {{ background-color: #e74c3c; color: white; }}
                .high {{ background-color: #e67e22; color: white; }}
                .medium {{ background-color: #f39c12; color: white; }}
                .low {{ background-color: #27ae60; color: white; }}
                .info {{ background-color: #3498db; color: white; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>HATS Security Assessment Report</h1>
                <p>Generated on: {timestamp}</p>
            </div>
        """
        
        # Executive Summary
        html_content += self._generate_executive_summary_html(scan_results)
        
        # Detailed Findings
        html_content += self._generate_findings_html(scan_results)
        
        # Network Discovery
        if 'network_scan' in scan_results:
            html_content += self._generate_network_scan_html(scan_results['network_scan'])
        
        # Vulnerability Details
        if 'vulnerabilities' in scan_results:
            html_content += self._generate_vulnerabilities_html(scan_results['vulnerabilities'])
        
        html_content += """
        </body>
        </html>
        """
        
        return html_content
    
    def generate_json_report(self, scan_results: Dict) -> str:
        """
        Generate JSON report from scan results.
        
        Args:
            scan_results (Dict): Scan results data
            
        Returns:
            str: JSON report content
        """
        report_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'tool': 'HATS',
                'version': '1.0.0'
            },
            'summary': self._generate_summary_stats(scan_results),
            'results': scan_results
        }
        
        return json.dumps(report_data, indent=2, default=str)
    
    def generate_xml_report(self, scan_results: Dict) -> str:
        """
        Generate XML report from scan results.
        
        Args:
            scan_results (Dict): Scan results data
            
        Returns:
            str: XML report content
        """
        root = ET.Element("hats_report")
        
        # Metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "generated_at").text = datetime.now().isoformat()
        ET.SubElement(metadata, "tool").text = "HATS"
        ET.SubElement(metadata, "version").text = "1.0.0"
        
        # Summary
        summary = ET.SubElement(root, "summary")
        stats = self._generate_summary_stats(scan_results)
        for key, value in stats.items():
            ET.SubElement(summary, key).text = str(value)
        
        # Results
        results = ET.SubElement(root, "results")
        self._dict_to_xml(scan_results, results)
        
        return ET.tostring(root, encoding='unicode')
    
    def generate_csv_report(self, scan_results: Dict, report_type: str = "vulnerabilities") -> str:
        """
        Generate CSV report from scan results.
        
        Args:
            scan_results (Dict): Scan results data
            report_type (str): Type of CSV report to generate
            
        Returns:
            str: CSV report content
        """
        if report_type == "vulnerabilities":
            return self._generate_vulnerabilities_csv(scan_results)
        elif report_type == "hosts":
            return self._generate_hosts_csv(scan_results)
        elif report_type == "ports":
            return self._generate_ports_csv(scan_results)
        else:
            return "Report type not supported"
    
    def _generate_executive_summary_html(self, scan_results: Dict) -> str:
        """Generate executive summary section."""
        stats = self._generate_summary_stats(scan_results)
        
        return f"""
        <div class="section">
            <h2>Executive Summary</h2>
            <p>This report contains the results of a security assessment conducted using HATS.</p>
            <ul>
                <li>Hosts Discovered: {stats.get('hosts_discovered', 0)}</li>
                <li>Open Ports: {stats.get('open_ports', 0)}</li>
                <li>Vulnerabilities Found: {stats.get('vulnerabilities_found', 0)}</li>
                <li>Critical Issues: {stats.get('critical_issues', 0)}</li>
            </ul>
        </div>
        """
    
    def _generate_findings_html(self, scan_results: Dict) -> str:
        """Generate findings summary section."""
        return """
        <div class="section">
            <h2>Key Findings</h2>
            <p>The following critical and high-severity issues were identified:</p>
            <!-- Findings content would be generated based on actual results -->
        </div>
        """
    
    def _generate_network_scan_html(self, network_data: Dict) -> str:
        """Generate network scan results section."""
        hosts = network_data.get('hosts', [])
        
        html = """
        <div class="section">
            <h2>Network Discovery Results</h2>
            <table>
                <tr>
                    <th>Host</th>
                    <th>Status</th>
                    <th>Open Ports</th>
                </tr>
        """
        
        for host in hosts:
            html += f"""
                <tr>
                    <td>{host.get('ip', 'Unknown')}</td>
                    <td>{host.get('status', 'Unknown')}</td>
                    <td>{', '.join(map(str, host.get('ports', [])))}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html
    
    def _generate_vulnerabilities_html(self, vuln_data: List) -> str:
        """Generate vulnerabilities section."""
        html = """
        <div class="section">
            <h2>Vulnerability Details</h2>
            <table>
                <tr>
                    <th>Severity</th>
                    <th>Title</th>
                    <th>Host</th>
                    <th>Port</th>
                    <th>Description</th>
                </tr>
        """
        
        for vuln in vuln_data:
            severity_class = vuln.get('severity', 'info').lower()
            html += f"""
                <tr>
                    <td class="{severity_class}">{vuln.get('severity', 'Unknown')}</td>
                    <td>{vuln.get('title', 'Unknown')}</td>
                    <td>{vuln.get('host', 'Unknown')}</td>
                    <td>{vuln.get('port', 'N/A')}</td>
                    <td>{vuln.get('description', 'No description available')}</td>
                </tr>
            """
        
        html += """
            </table>
        </div>
        """
        
        return html
    
    def _generate_summary_stats(self, scan_results: Dict) -> Dict:
        """Generate summary statistics."""
        stats = {
            'hosts_discovered': 0,
            'open_ports': 0,
            'vulnerabilities_found': 0,
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0
        }
        
        # Count hosts
        if 'network_scan' in scan_results:
            stats['hosts_discovered'] = len(scan_results['network_scan'].get('hosts', []))
        
        # Count vulnerabilities by severity
        if 'vulnerabilities' in scan_results:
            for vuln in scan_results['vulnerabilities']:
                stats['vulnerabilities_found'] += 1
                severity = vuln.get('severity', '').lower()
                if severity == 'critical':
                    stats['critical_issues'] += 1
                elif severity == 'high':
                    stats['high_issues'] += 1
                elif severity == 'medium':
                    stats['medium_issues'] += 1
                elif severity == 'low':
                    stats['low_issues'] += 1
        
        return stats
    
    def _generate_vulnerabilities_csv(self, scan_results: Dict) -> str:
        """Generate CSV for vulnerabilities."""
        csv_content = "Severity,Title,Host,Port,Description\n"
        
        vulnerabilities = scan_results.get('vulnerabilities', [])
        for vuln in vulnerabilities:
            csv_content += f'"{vuln.get("severity", "")}","{vuln.get("title", "")}","{vuln.get("host", "")}","{vuln.get("port", "")}","{vuln.get("description", "")}"\n'
        
        return csv_content
    
    def _generate_hosts_csv(self, scan_results: Dict) -> str:
        """Generate CSV for discovered hosts."""
        csv_content = "IP Address,Status,Open Ports,OS Detection\n"
        
        if 'network_scan' in scan_results:
            hosts = scan_results['network_scan'].get('hosts', [])
            for host in hosts:
                ports = ','.join(map(str, host.get('ports', [])))
                csv_content += f'"{host.get("ip", "")}","{host.get("status", "")}","{ports}","{host.get("os", "")}"\n'
        
        return csv_content
    
    def _generate_ports_csv(self, scan_results: Dict) -> str:
        """Generate CSV for open ports."""
        csv_content = "Host,Port,Protocol,Service,State\n"
        
        if 'network_scan' in scan_results and 'open_ports' in scan_results['network_scan']:
            for port_info in scan_results['network_scan']['open_ports']:
                csv_content += f'"{port_info.get("host", "")}","{port_info.get("port", "")}","{port_info.get("protocol", "")}","{port_info.get("service", "")}","open"\n'
        
        return csv_content
    
    def _dict_to_xml(self, data: Any, parent: ET.Element):
        """Convert dictionary to XML elements."""
        if isinstance(data, dict):
            for key, value in data.items():
                element = ET.SubElement(parent, str(key))
                self._dict_to_xml(value, element)
        elif isinstance(data, list):
            for item in data:
                element = ET.SubElement(parent, "item")
                self._dict_to_xml(item, element)
        else:
            parent.text = str(data)
