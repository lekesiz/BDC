import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/modal';
import { Dialog, DialogHeader, DialogTitle, DialogDescription, DialogContent, DialogFooter } from '@/components/ui/dialog';
import { Table, TableHeader, TableBody, TableRow, TableCell } from '@/components/ui/table';
import { Tabs, TabsList, TabTrigger, TabContent } from '@/components/ui/tabs';
import { Dropdown, DropdownItem, DropdownDivider } from '@/components/ui/dropdown';
import AccessibleSelect from '@/components/ui/accessible-select';
import AccessibleForm from '@/components/forms/AccessibleForm';
import { useToast } from '@/components/ui/toast';
import { announceToScreenReader } from '@/utils/accessibility';
/**
 * Example component demonstrating accessibility features
 * This serves as a reference for implementing accessible components
 */
const AccessibilityExample = () => {
  const [modalOpen, setModalOpen] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState('');
  const [formData, setFormData] = useState({});
  const { toast } = useToast();
  // Example data
  const tableData = [
    { id: 1, name: 'John Doe', email: 'john@example.com', role: 'Admin' },
    { id: 2, name: 'Jane Smith', email: 'jane@example.com', role: 'User' },
    { id: 3, name: 'Bob Johnson', email: 'bob@example.com', role: 'User' },
  ];
  const selectOptions = [
    { value: 'option1', label: 'Option 1' },
    { value: 'option2', label: 'Option 2' },
    { value: 'option3', label: 'Option 3', disabled: true },
    { value: 'option4', label: 'Option 4' },
  ];
  const handleFormSubmit = async (data) => {
    setFormData(data);
    toast({
      type: 'success',
      title: 'Form Submitted',
      message: 'Your form has been submitted successfully.',
    });
    announceToScreenReader('Form submitted successfully');
  };
  const handleAction = (action) => {
    toast({
      type: 'info',
      title: 'Action Performed',
      message: `You selected: ${action}`,
    });
  };
  return (
    <div className="p-6 space-y-8">
      <header>
        <h1 className="text-3xl font-bold mb-2">Accessibility Example</h1>
        <p className="text-gray-600">
          This page demonstrates various accessible components with proper ARIA attributes,
          keyboard navigation, and screen reader support.
        </p>
      </header>
      {/* Section: Buttons and Inputs */}
      <section aria-labelledby="buttons-heading">
        <h2 id="buttons-heading" className="text-2xl font-semibold mb-4">
          Buttons and Inputs
        </h2>
        <div className="space-y-4">
          <div className="flex gap-4">
            <Button onClick={() => setModalOpen(true)} aria-label="Open modal dialog">
              Open Modal
            </Button>
            <Button 
              variant="secondary" 
              onClick={() => setDialogOpen(true)}
              aria-label="Open confirmation dialog"
            >
              Open Dialog
            </Button>
            <Button 
              variant="outline" 
              isLoading 
              loadingText="Processing..."
              aria-label="Loading button example"
            >
              Loading State
            </Button>
          </div>
          <div className="max-w-md">
            <Input
              label="Example Input"
              placeholder="Enter some text"
              helpText="This is an accessible input with help text"
              required
              aria-describedby="input-help"
            />
          </div>
        </div>
      </section>
      {/* Section: Select and Dropdown */}
      <section aria-labelledby="select-heading">
        <h2 id="select-heading" className="text-2xl font-semibold mb-4">
          Select and Dropdown
        </h2>
        <div className="flex gap-8">
          <div className="w-64">
            <AccessibleSelect
              label="Choose an option"
              options={selectOptions}
              value={selectedValue}
              onValueChange={setSelectedValue}
              placeholder="Select an option"
              required
            />
          </div>
          <Dropdown
            trigger={
              <Button variant="outline" aria-label="Actions menu">
                Actions Menu
              </Button>
            }
            aria-label="Actions dropdown menu"
          >
            <DropdownItem onClick={() => handleAction('Edit')}>Edit</DropdownItem>
            <DropdownItem onClick={() => handleAction('Duplicate')}>Duplicate</DropdownItem>
            <DropdownDivider />
            <DropdownItem onClick={() => handleAction('Delete')} disabled>
              Delete (Disabled)
            </DropdownItem>
          </Dropdown>
        </div>
      </section>
      {/* Section: Tabs */}
      <section aria-labelledby="tabs-heading">
        <h2 id="tabs-heading" className="text-2xl font-semibold mb-4">
          Accessible Tabs
        </h2>
        <Tabs defaultValue="tab1" className="w-full">
          <TabsList>
            <TabTrigger value="tab1">Tab 1</TabTrigger>
            <TabTrigger value="tab2">Tab 2</TabTrigger>
            <TabTrigger value="tab3" disabled>Tab 3 (Disabled)</TabTrigger>
          </TabsList>
          <TabContent value="tab1">
            <p>Content for Tab 1. Use arrow keys to navigate between tabs.</p>
          </TabContent>
          <TabContent value="tab2">
            <p>Content for Tab 2. Tabs are fully keyboard accessible.</p>
          </TabContent>
        </Tabs>
      </section>
      {/* Section: Table */}
      <section aria-labelledby="table-heading">
        <h2 id="table-heading" className="text-2xl font-semibold mb-4">
          Accessible Table
        </h2>
        <Table aria-label="User data table" caption="List of registered users">
          <TableHeader>
            <TableRow>
              <TableCell isHeader scope="col">Name</TableCell>
              <TableCell isHeader scope="col">Email</TableCell>
              <TableCell isHeader scope="col">Role</TableCell>
              <TableCell isHeader scope="col">Actions</TableCell>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tableData.map((row) => (
              <TableRow key={row.id}>
                <TableCell>{row.name}</TableCell>
                <TableCell>{row.email}</TableCell>
                <TableCell>{row.role}</TableCell>
                <TableCell>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    aria-label={`Edit ${row.name}`}
                    onClick={() => handleAction(`Edit ${row.name}`)}
                  >
                    Edit
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </section>
      {/* Section: Form */}
      <section aria-labelledby="form-heading">
        <h2 id="form-heading" className="text-2xl font-semibold mb-4">
          Accessible Form
        </h2>
        <div className="max-w-lg">
          <AccessibleForm
            formTitle="Contact Form"
            onSubmit={handleFormSubmit}
            submitButtonText="Submit Form"
          />
        </div>
      </section>
      {/* Modal Example */}
      <Modal
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        title="Accessible Modal"
        size="md"
        closeOnEscape
        closeOnOutsideClick
        initialFocus="[data-focus]"
      >
        <div className="space-y-4">
          <p>
            This modal demonstrates focus management, keyboard navigation, and
            screen reader announcements.
          </p>
          <Input
            label="Modal Input"
            placeholder="Type something..."
            data-focus
          />
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => {
              setModalOpen(false);
              announceToScreenReader('Modal action completed');
            }}>
              Confirm
            </Button>
          </div>
        </div>
      </Modal>
      {/* Dialog Example */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogHeader>
          <DialogTitle>Confirmation Dialog</DialogTitle>
          <DialogDescription>
            Are you sure you want to perform this action? This dialog is fully accessible.
          </DialogDescription>
        </DialogHeader>
        <DialogContent>
          <p>This action cannot be undone.</p>
        </DialogContent>
        <DialogFooter>
          <Button variant="outline" onClick={() => setDialogOpen(false)}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={() => {
            setDialogOpen(false);
            handleAction('Confirmed');
          }}>
            Confirm
          </Button>
        </DialogFooter>
      </Dialog>
      {/* Keyboard Navigation Instructions */}
      <section aria-labelledby="instructions-heading" className="bg-gray-50 p-6 rounded-lg">
        <h2 id="instructions-heading" className="text-xl font-semibold mb-4">
          Keyboard Navigation Instructions
        </h2>
        <ul className="space-y-2 text-sm">
          <li>• <kbd>Tab</kbd> - Navigate forward through interactive elements</li>
          <li>• <kbd>Shift + Tab</kbd> - Navigate backward</li>
          <li>• <kbd>Enter</kbd> or <kbd>Space</kbd> - Activate buttons and links</li>
          <li>• <kbd>Arrow Keys</kbd> - Navigate within dropdowns, tabs, and selects</li>
          <li>• <kbd>Escape</kbd> - Close modals, dialogs, and dropdowns</li>
          <li>• <kbd>Home/End</kbd> - Jump to first/last item in lists</li>
        </ul>
      </section>
    </div>
  );
};
export default AccessibilityExample;