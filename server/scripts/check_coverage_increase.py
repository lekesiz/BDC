#!/usr/bin/env python3
"""Check if coverage has increased between two coverage.xml files."""
import sys
import xml.etree.ElementTree as ET
from typing import Tuple


def parse_coverage(xml_file: str) -> Tuple[float, dict]:
    """Parse coverage XML file and return coverage percentage and details."""
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Get overall line rate
        line_rate = float(root.get('line-rate', 0)) * 100
        
        # Get package-level coverage
        packages = {}
        for package in root.findall('.//package'):
            package_name = package.get('name')
            package_line_rate = float(package.get('line-rate', 0)) * 100
            packages[package_name] = package_line_rate
        
        return line_rate, packages
    except Exception as e:
        print(f"Error parsing {xml_file}: {e}")
        return 0.0, {}


def main():
    """Main function to compare coverage."""
    if len(sys.argv) != 3:
        print("Usage: python check_coverage_increase.py <base_coverage.xml> <current_coverage.xml>")
        sys.exit(1)
    
    base_file = sys.argv[1]
    current_file = sys.argv[2]
    
    base_coverage, base_packages = parse_coverage(base_file)
    current_coverage, current_packages = parse_coverage(current_file)
    
    print(f"\n{'='*60}")
    print("COVERAGE COMPARISON")
    print(f"{'='*60}")
    print(f"Base coverage:    {base_coverage:.2f}%")
    print(f"Current coverage: {current_coverage:.2f}%")
    print(f"Difference:       {current_coverage - base_coverage:+.2f}%")
    
    # Check if coverage increased
    if current_coverage < base_coverage:
        print("\n❌ COVERAGE DECREASED!")
        print("This PR must increase or maintain test coverage.")
        
        # Show which packages decreased
        print(f"\n{'='*60}")
        print("PACKAGES WITH DECREASED COVERAGE:")
        print(f"{'='*60}")
        
        for package, current_rate in current_packages.items():
            base_rate = base_packages.get(package, 0)
            if current_rate < base_rate:
                print(f"{package}: {base_rate:.2f}% → {current_rate:.2f}% ({current_rate - base_rate:+.2f}%)")
        
        sys.exit(1)
    
    elif current_coverage == base_coverage:
        print("\n⚠️  Coverage remained the same.")
        print("Consider adding more tests to increase coverage.")
    
    else:
        print("\n✅ Coverage increased!")
        
        # Show which packages improved
        print(f"\n{'='*60}")
        print("PACKAGES WITH INCREASED COVERAGE:")
        print(f"{'='*60}")
        
        for package, current_rate in current_packages.items():
            base_rate = base_packages.get(package, 0)
            if current_rate > base_rate:
                print(f"{package}: {base_rate:.2f}% → {current_rate:.2f}% ({current_rate - base_rate:+.2f}%)")
    
    # Show new packages
    new_packages = set(current_packages.keys()) - set(base_packages.keys())
    if new_packages:
        print(f"\n{'='*60}")
        print("NEW PACKAGES:")
        print(f"{'='*60}")
        for package in new_packages:
            print(f"{package}: {current_packages[package]:.2f}%")
    
    # Show removed packages
    removed_packages = set(base_packages.keys()) - set(current_packages.keys())
    if removed_packages:
        print(f"\n{'='*60}")
        print("REMOVED PACKAGES:")
        print(f"{'='*60}")
        for package in removed_packages:
            print(f"{package}: {base_packages[package]:.2f}%")
    
    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()