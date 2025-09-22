"""
Example script demonstrating how to use HATS to run nmap scans.
"""

import sys
import os

# Add the parent directory to the path so we can import hats
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hats import HATSEngine
from hats.categories.scanning import ScanningCategory


def main():
    """Main function demonstrating nmap usage."""
    print("HATS - Nmap Example")
    print("=" * 40)
    
    # Initialize HATS engine
    engine = HATSEngine()
    scanner = ScanningCategory()
    
    # Target for scanning
    target = "scanme.nmap.org"  # Safe target for testing
    
    print(f"Target: {target}")
    print("-" * 40)
    
    # Example 1: Basic port scan
    print("1. Running basic port scan...")
    try:
        result = engine.execute_tool('nmap', target)
        
        if result['success']:
            print("✓ Scan completed successfully")
            
            # Parse the output
            parsed = scanner.parse_nmap_output(result['output'])
            
            print(f"Hosts discovered: {len(parsed['hosts'])}")
            print(f"Open ports found: {len(parsed['open_ports'])}")
            
            if parsed['open_ports']:
                print("Open ports:")
                for port in parsed['open_ports'][:5]:  # Show first 5 ports
                    print(f"  - {port['port']}/{port['protocol']} ({port['service']})")
        else:
            print(f"✗ Scan failed: {result['error']}")
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print()
    
    # Example 2: Custom port scan
    print("2. Running custom port scan (top 100 ports)...")
    try:
        # Generate custom command
        command = scanner.generate_port_scan_command(
            target=target,
            scan_type='syn',
            ports='1-100',
            timing='T4'
        )
        
        print(f"Command: {' '.join(command)}")
        
        result = engine.execute_tool('nmap', target, {'p': '1-100', 'T': '4'})
        
        if result['success']:
            print("✓ Custom scan completed successfully")
            parsed = scanner.parse_nmap_output(result['output'])
            print(f"Open ports in range 1-100: {len(parsed['open_ports'])}")
        else:
            print(f"✗ Custom scan failed: {result['error']}")
    
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print()
    
    # Example 3: Validate targets
    print("3. Target validation examples...")
    
    test_targets = [
        "192.168.1.1",
        "scanme.nmap.org",
        "192.168.1.0/24",
        "invalid..domain",
        "256.256.256.256"
    ]
    
    for test_target in test_targets:
        is_valid = scanner.validate_target(test_target)
        status = "✓ Valid" if is_valid else "✗ Invalid"
        print(f"  {test_target}: {status}")
    
    print()
    
    # Example 4: Show common ports
    print("4. Common port categories...")
    
    common_ports = scanner.get_common_ports()
    
    for category, ports in common_ports.items():
        if category != 'top_1000':  # Skip the large list
            port_list = ', '.join(map(str, ports[:5]))  # Show first 5
            more = f" (+{len(ports)-5} more)" if len(ports) > 5 else ""
            print(f"  {category}: {port_list}{more}")
    
    print()
    
    # Example 5: Workflow execution
    print("5. Running a workflow...")
    
    workflow = [
        {
            'tool': 'nmap',
            'target': target,
            'options': {'p': '80,443', 'sV': True},
            'stop_on_error': False
        }
    ]
    
    try:
        results = engine.execute_workflow(workflow)
        
        for i, result in enumerate(results, 1):
            status = "✓ Success" if result['success'] else "✗ Failed"
            print(f"  Step {i} ({result['tool']}): {status}")
    
    except Exception as e:
        print(f"✗ Workflow error: {str(e)}")
    
    print()
    print("Example completed!")


if __name__ == "__main__":
    main()
