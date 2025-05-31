#!/usr/bin/env python
"""Test all frontend pages systematically."""

import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Read the test token
with open('/tmp/bdc_test_token.txt', 'r') as f:
    TEST_TOKEN = f.read().strip()

# List of all pages to test
PAGES_TO_TEST = [
    # Dashboard
    {'path': '/dashboard', 'name': 'Dashboard'},
    
    # Beneficiaries
    {'path': '/beneficiaries', 'name': 'Beneficiaries List'},
    {'path': '/beneficiaries/create', 'name': 'Create Beneficiary'},
    
    # Programs
    {'path': '/programs', 'name': 'Programs List'},
    {'path': '/programs/create', 'name': 'Create Program'},
    
    # Evaluations
    {'path': '/evaluations', 'name': 'Evaluations'},
    {'path': '/evaluations/templates', 'name': 'Evaluation Templates'},
    {'path': '/evaluations/create', 'name': 'Create Evaluation'},
    
    # Calendar
    {'path': '/calendar', 'name': 'Calendar'},
    {'path': '/appointments', 'name': 'Appointments'},
    
    # Documents
    {'path': '/documents', 'name': 'Documents'},
    {'path': '/documents/upload', 'name': 'Upload Document'},
    {'path': '/documents/templates', 'name': 'Document Templates'},
    
    # Messages
    {'path': '/messages', 'name': 'Messages'},
    {'path': '/notifications', 'name': 'Notifications'},
    
    # Analytics
    {'path': '/analytics', 'name': 'Analytics Dashboard'},
    {'path': '/analytics/beneficiaries', 'name': 'Beneficiary Analytics'},
    {'path': '/analytics/programs', 'name': 'Program Analytics'},
    {'path': '/analytics/performance', 'name': 'Performance Analytics'},
    
    # Reports
    {'path': '/reports', 'name': 'Reports'},
    {'path': '/reports/create', 'name': 'Create Report'},
    {'path': '/reports/scheduled', 'name': 'Scheduled Reports'},
    
    # Settings
    {'path': '/settings', 'name': 'Settings'},
    {'path': '/settings/profile', 'name': 'Profile Settings'},
    {'path': '/settings/security', 'name': 'Security Settings'},
    {'path': '/settings/notifications', 'name': 'Notification Settings'},
    {'path': '/settings/ai', 'name': 'AI Settings'},
    
    # Admin Pages
    {'path': '/admin/users', 'name': 'Admin - Users'},
    {'path': '/admin/tenants', 'name': 'Admin - Tenants'},
    {'path': '/admin/system', 'name': 'Admin - System'},
    {'path': '/admin/audit', 'name': 'Admin - Audit Logs'},
    
    # AI Features
    {'path': '/ai/assistant', 'name': 'AI Assistant'},
    {'path': '/ai/insights', 'name': 'AI Insights'},
    {'path': '/ai/recommendations', 'name': 'AI Recommendations'},
    
    # Integrations
    {'path': '/integrations', 'name': 'Integrations'},
    {'path': '/integrations/configure', 'name': 'Configure Integrations'},
    
    # Compliance
    {'path': '/compliance', 'name': 'Compliance Dashboard'},
    {'path': '/compliance/audits', 'name': 'Compliance Audits'},
    {'path': '/compliance/certifications', 'name': 'Certifications'},
    
    # Portal
    {'path': '/portal', 'name': 'Portal Dashboard'},
    {'path': '/portal/courses', 'name': 'Portal Courses'},
    {'path': '/portal/progress', 'name': 'Portal Progress'},
    {'path': '/portal/resources', 'name': 'Portal Resources'},
    {'path': '/portal/achievements', 'name': 'Portal Achievements'},
    {'path': '/portal/skills', 'name': 'Portal Skills'}
]

def test_page_manual(page_info):
    """Manually check if a page loads without using Selenium."""
    base_url = 'http://localhost:5173'
    full_url = base_url + page_info['path']
    
    print(f"\n{'='*60}")
    print(f"Testing: {page_info['name']}")
    print(f"URL: {full_url}")
    print(f"{'='*60}")
    
    result = {
        'name': page_info['name'],
        'path': page_info['path'],
        'status': 'untested',
        'issues': []
    }
    
    # For manual testing, just print instructions
    print("\nPlease manually navigate to this URL in your browser")
    print("and check for the following:")
    print("1. Page loads without errors")
    print("2. No infinite loading spinners")
    print("3. No console errors (check DevTools)")
    print("4. Content displays properly")
    print("\nPress Enter when ready to continue to next page...")
    input()
    
    # Ask for result
    while True:
        status = input("Result (p=pass, w=warning, f=fail): ").lower()
        if status in ['p', 'w', 'f']:
            break
        print("Please enter p, w, or f")
    
    result['status'] = {
        'p': 'passed',
        'w': 'warning', 
        'f': 'failed'
    }[status]
    
    if status in ['w', 'f']:
        issue = input("Brief description of issue: ")
        result['issues'].append(issue)
    
    return result

def main():
    """Run all tests."""
    print("🚀 BDC Frontend Manual Testing Tool")
    print("=" * 60)
    print(f"Total pages to test: {len(PAGES_TO_TEST)}")
    print("\nBefore starting:")
    print("1. Make sure you're logged in as admin@bdc.com")
    print("2. Open browser DevTools Console to watch for errors")
    print("3. Have the browser window visible")
    print("\nAlternatively, run this in browser console to set token:")
    print(f"localStorage.setItem('access_token', '{TEST_TOKEN}');")
    print("window.location.reload();")
    print("\nPress Enter to start testing...")
    input()
    
    results = []
    
    for i, page in enumerate(PAGES_TO_TEST):
        print(f"\n[{i+1}/{len(PAGES_TO_TEST)}]", end='')
        result = test_page_manual(page)
        results.append(result)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = [r for r in results if r['status'] == 'passed']
    warnings = [r for r in results if r['status'] == 'warning']
    failed = [r for r in results if r['status'] == 'failed']
    
    print(f"✅ Passed: {len(passed)}/{len(results)}")
    print(f"⚠️  Warnings: {len(warnings)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    
    if warnings:
        print("\n⚠️  Pages with warnings:")
        for r in warnings:
            print(f"  - {r['name']}: {', '.join(r['issues'])}")
    
    if failed:
        print("\n❌ Failed pages:")
        for r in failed:
            print(f"  - {r['name']}: {', '.join(r['issues'])}")
    
    # Save results
    import json
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\nResults saved to test_results.json")

if __name__ == '__main__':
    main()