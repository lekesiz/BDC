#!/usr/bin/env python3
"""
BDC Project Checklist Manager
Manages the project development checklist with progress tracking
"""

import os
import re
import json
from datetime import datetime
from typing import Dict, List, Tuple

class ChecklistManager:
    def __init__(self, checklist_file='PROJECT_CHECKLIST.md'):
        self.checklist_file = checklist_file
        self.progress_file = 'PROJECT_PROGRESS.json'
        self.sections = {}
        self.load_checklist()
        self.load_progress()
    
    def load_checklist(self):
        """Load and parse the markdown checklist"""
        if not os.path.exists(self.checklist_file):
            print(f"Checklist file {self.checklist_file} not found!")
            return
        
        with open(self.checklist_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_section = None
        section_pattern = re.compile(r'^## (.+)$', re.MULTILINE)
        item_pattern = re.compile(r'^- \[([ x])\] (.+)$', re.MULTILINE)
        
        sections = section_pattern.split(content)[1:]
        
        for i in range(0, len(sections), 2):
            section_name = sections[i].strip()
            section_content = sections[i + 1] if i + 1 < len(sections) else ""
            
            items = []
            for match in item_pattern.finditer(section_content):
                status = match.group(1) == 'x'
                task = match.group(2)
                items.append({
                    'task': task,
                    'completed': status,
                    'original_status': status
                })
            
            self.sections[section_name] = items
    
    def load_progress(self):
        """Load progress data from JSON file"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r') as f:
                self.progress_data = json.load(f)
        else:
            self.progress_data = {
                'last_updated': datetime.now().isoformat(),
                'total_tasks': 0,
                'completed_tasks': 0,
                'completion_percentage': 0,
                'history': []
            }
    
    def save_progress(self):
        """Save progress data to JSON file"""
        self.calculate_progress()
        with open(self.progress_file, 'w') as f:
            json.dump(self.progress_data, f, indent=2)
    
    def calculate_progress(self):
        """Calculate overall progress"""
        total = 0
        completed = 0
        
        for section, items in self.sections.items():
            for item in items:
                total += 1
                if item['completed']:
                    completed += 1
        
        self.progress_data['total_tasks'] = total
        self.progress_data['completed_tasks'] = completed
        self.progress_data['completion_percentage'] = round((completed / total * 100) if total > 0 else 0, 2)
        self.progress_data['last_updated'] = datetime.now().isoformat()
    
    def update_checklist_file(self):
        """Update the markdown file with current status"""
        with open(self.checklist_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update progress percentage
        progress_pattern = r'\*\*Progress:\*\* \d+% Complete'
        progress_replacement = f'**Progress:** {self.progress_data["completion_percentage"]}% Complete'
        content = re.sub(progress_pattern, progress_replacement, content)
        
        # Update last updated date
        date_pattern = r'\*\*Last Updated:\*\* \d{4}-\d{2}-\d{2}'
        date_replacement = f'**Last Updated:** {datetime.now().strftime("%Y-%m-%d")}'
        content = re.sub(date_pattern, date_replacement, content)
        
        # Update task statuses
        for section, items in self.sections.items():
            for item in items:
                old_pattern = f"- \\[{'x' if item['original_status'] else ' '}\\] {re.escape(item['task'])}"
                new_pattern = f"- [{'x' if item['completed'] else ' '}] {item['task']}"
                content = re.sub(old_pattern, new_pattern, content)
        
        with open(self.checklist_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def display_progress(self):
        """Display current progress"""
        print("\n" + "="*50)
        print("BDC PROJECT PROGRESS")
        print("="*50)
        
        for section, items in self.sections.items():
            if not section.startswith('✅'):
                continue
                
            completed = sum(1 for item in items if item['completed'])
            total = len(items)
            percentage = round((completed / total * 100) if total > 0 else 0, 1)
            
            print(f"\n{section}")
            print(f"Progress: {completed}/{total} ({percentage}%)")
            print("─" * 30)
            
            for item in items:
                status = "✓" if item['completed'] else "○"
                print(f"{status} {item['task']}")
        
        print("\n" + "="*50)
        print(f"OVERALL PROGRESS: {self.progress_data['completed_tasks']}/{self.progress_data['total_tasks']} ({self.progress_data['completion_percentage']}%)")
        print("="*50)
    
    def toggle_task(self, section_name: str, task_index: int):
        """Toggle a task's completion status"""
        if section_name in self.sections and 0 <= task_index < len(self.sections[section_name]):
            task = self.sections[section_name][task_index]
            task['completed'] = not task['completed']
            
            # Add to history
            self.progress_data['history'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'completed' if task['completed'] else 'uncompleted',
                'section': section_name,
                'task': task['task']
            })
            
            self.save_progress()
            self.update_checklist_file()
            print(f"Task {'completed' if task['completed'] else 'uncompleted'}: {task['task']}")
        else:
            print("Invalid section or task index")
    
    def search_tasks(self, keyword: str):
        """Search for tasks containing keyword"""
        results = []
        for section, items in self.sections.items():
            for i, item in enumerate(items):
                if keyword.lower() in item['task'].lower():
                    results.append((section, i, item))
        
        return results
    
    def list_sections(self):
        """List all sections"""
        for i, section in enumerate(self.sections.keys()):
            print(f"{i}: {section}")
    
    def list_tasks(self, section_name: str):
        """List tasks in a section"""
        if section_name in self.sections:
            print(f"\nTasks in {section_name}:")
            for i, item in enumerate(self.sections[section_name]):
                status = "✓" if item['completed'] else "○"
                print(f"{i}: {status} {item['task']}")
        else:
            print(f"Section '{section_name}' not found")
    
    def add_task(self, section_name: str, task_description: str):
        """Add a new task to a section"""
        if section_name in self.sections:
            self.sections[section_name].append({
                'task': task_description,
                'completed': False,
                'original_status': False
            })
            
            # Add to history
            self.progress_data['history'].append({
                'timestamp': datetime.now().isoformat(),
                'action': 'added',
                'section': section_name,
                'task': task_description
            })
            
            self.save_progress()
            self.update_checklist_file()
            print(f"Task added: {task_description}")
        else:
            print(f"Section '{section_name}' not found")
    
    def generate_report(self):
        """Generate a progress report"""
        report = f"""
# BDC Project Progress Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overall Progress
- Total Tasks: {self.progress_data['total_tasks']}
- Completed Tasks: {self.progress_data['completed_tasks']}
- Completion: {self.progress_data['completion_percentage']}%

## Section Breakdown
"""
        
        for section, items in self.sections.items():
            if not section.startswith('✅'):
                continue
                
            completed = sum(1 for item in items if item['completed'])
            total = len(items)
            percentage = round((completed / total * 100) if total > 0 else 0, 1)
            
            report += f"\n### {section}\n"
            report += f"Progress: {completed}/{total} ({percentage}%)\n\n"
            
            # Pending tasks
            pending = [item for item in items if not item['completed']]
            if pending:
                report += "**Pending Tasks:**\n"
                for item in pending[:5]:  # Show first 5 pending
                    report += f"- {item['task']}\n"
                if len(pending) > 5:
                    report += f"- ... and {len(pending) - 5} more\n"
                report += "\n"
        
        # Recent activity
        report += "\n## Recent Activity\n"
        recent = self.progress_data.get('history', [])[-10:]
        for entry in reversed(recent):
            timestamp = datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')
            report += f"- {timestamp}: {entry['action']} - {entry['task']}\n"
        
        return report


def main():
    """Interactive CLI for checklist management"""
    manager = ChecklistManager()
    
    while True:
        print("\n" + "="*50)
        print("BDC PROJECT CHECKLIST MANAGER")
        print("="*50)
        print("1. Display Progress")
        print("2. List Sections")
        print("3. List Tasks in Section")
        print("4. Toggle Task Completion")
        print("5. Search Tasks")
        print("6. Add New Task")
        print("7. Generate Report")
        print("8. Update Check by Task Search")
        print("9. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            manager.display_progress()
        
        elif choice == '2':
            print("\nSections:")
            manager.list_sections()
        
        elif choice == '3':
            manager.list_sections()
            section_idx = int(input("\nEnter section number: "))
            sections = list(manager.sections.keys())
            if 0 <= section_idx < len(sections):
                manager.list_tasks(sections[section_idx])
            else:
                print("Invalid section number")
        
        elif choice == '4':
            manager.list_sections()
            section_idx = int(input("\nEnter section number: "))
            sections = list(manager.sections.keys())
            if 0 <= section_idx < len(sections):
                section_name = sections[section_idx]
                manager.list_tasks(section_name)
                task_idx = int(input("\nEnter task number: "))
                manager.toggle_task(section_name, task_idx)
            else:
                print("Invalid section number")
        
        elif choice == '5':
            keyword = input("\nEnter search keyword: ")
            results = manager.search_tasks(keyword)
            if results:
                print(f"\nFound {len(results)} results:")
                for i, (section, idx, item) in enumerate(results):
                    status = "✓" if item['completed'] else "○"
                    print(f"{i}: [{section}] {status} {item['task']}")
            else:
                print("No results found")
        
        elif choice == '6':
            manager.list_sections()
            section_idx = int(input("\nEnter section number: "))
            sections = list(manager.sections.keys())
            if 0 <= section_idx < len(sections):
                task_desc = input("Enter task description: ")
                manager.add_task(sections[section_idx], task_desc)
            else:
                print("Invalid section number")
        
        elif choice == '7':
            report = manager.generate_report()
            print(report)
            save = input("\nSave report to file? (y/n): ")
            if save.lower() == 'y':
                filename = f"progress_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(filename, 'w') as f:
                    f.write(report)
                print(f"Report saved to {filename}")
        
        elif choice == '8':
            keyword = input("\nEnter search keyword: ")
            results = manager.search_tasks(keyword)
            if results:
                print(f"\nFound {len(results)} results:")
                for i, (section, idx, item) in enumerate(results):
                    status = "✓" if item['completed'] else "○"
                    print(f"{i}: [{section}] {status} {item['task']}")
                
                result_idx = int(input("\nEnter result number to toggle: "))
                if 0 <= result_idx < len(results):
                    section, task_idx, _ = results[result_idx]
                    manager.toggle_task(section, task_idx)
                else:
                    print("Invalid result number")
            else:
                print("No results found")
        
        elif choice == '9':
            print("\nExiting...")
            break
        
        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()