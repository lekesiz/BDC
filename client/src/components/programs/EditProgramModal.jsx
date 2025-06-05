import { Dialog, DialogTrigger, DialogContent, DialogTitle } from '@radix-ui/react-dialog'
import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import axios from 'axios'
const EditProgramModal = ({ program, onUpdated }) => {
  const [open, setOpen] = useState(false)
  const [formData, setFormData] = useState({
    name: program.name,
    description: program.description || '',
    category: program.category || '',
    level: program.level || '',
    status: program.status || 'draft',
    duration: program.duration || 0,
    max_participants: program.max_participants || 0,
    objectives: program.objectives || '',
    requirements: program.requirements || ''
  })
  useEffect(() => {
    if (program) {
      setFormData({
        name: program.name,
        description: program.description || '',
        category: program.category || '',
        level: program.level || '',
        status: program.status || 'draft',
        duration: program.duration || 0,
        max_participants: program.max_participants || 0,
        objectives: program.objectives || '',
        requirements: program.requirements || ''
      })
    }
  }, [program])
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }
  const handleSave = async () => {
    try {
      await axios.put(`/api/programs/${program.id}`, formData)
      onUpdated?.()
      setOpen(false)
    } catch (error) {
      console.error('Error updating program:', error)
    }
  }
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="outline">Edit</Button>
      </DialogTrigger>
      <DialogContent className="p-6 bg-white rounded shadow-xl">
        <DialogTitle className="text-lg font-semibold mb-4">Edit Program</DialogTitle>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Name</label>
            <input 
              name="name"
              className="border p-2 w-full rounded"
              value={formData.name} 
              onChange={handleChange} 
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Description</label>
            <textarea 
              name="description"
              className="border p-2 w-full rounded"
              value={formData.description} 
              onChange={handleChange}
              rows={3} 
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Category</label>
              <input 
                name="category"
                className="border p-2 w-full rounded"
                value={formData.category} 
                onChange={handleChange} 
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Level</label>
              <select 
                name="level"
                className="border p-2 w-full rounded"
                value={formData.level} 
                onChange={handleChange}
              >
                <option value="">Select level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Status</label>
              <select 
                name="status"
                className="border p-2 w-full rounded"
                value={formData.status} 
                onChange={handleChange}
              >
                <option value="draft">Draft</option>
                <option value="published">Published</option>
                <option value="active">Active</option>
                <option value="archived">Archived</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Duration (weeks)</label>
              <input 
                name="duration"
                type="number"
                className="border p-2 w-full rounded"
                value={formData.duration} 
                onChange={handleChange} 
                min={0}
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Max Participants</label>
            <input 
              name="max_participants"
              type="number"
              className="border p-2 w-full rounded"
              value={formData.max_participants} 
              onChange={handleChange} 
              min={0}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Learning Objectives</label>
            <textarea 
              name="objectives"
              className="border p-2 w-full rounded"
              value={formData.objectives} 
              onChange={handleChange}
              rows={2} 
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Prerequisites</label>
            <textarea 
              name="requirements"
              className="border p-2 w-full rounded"
              value={formData.requirements} 
              onChange={handleChange}
              rows={2} 
            />
          </div>
        </div>
        <div className="flex gap-3 justify-end mt-6">
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSave}>Save Changes</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};
export default EditProgramModal; 