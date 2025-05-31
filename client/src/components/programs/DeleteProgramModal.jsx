import { Dialog, DialogTrigger, DialogContent, DialogTitle } from '@radix-ui/react-dialog'
import { useState } from 'react'
import { Button } from '@/components/ui/button'
import axios from 'axios'

const DeleteProgramModal = ({ programId, onDeleted }) => {
  const [open, setOpen] = useState(false)
  const handleDelete = async () => {
    await axios.delete(`/api/programs/${programId}`)
    onDeleted?.()
    setOpen(false)
  }
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="destructive">Delete</Button>
      </DialogTrigger>
      <DialogContent className="p-6 bg-white rounded shadow-xl">
        <DialogTitle className="text-lg font-semibold mb-4">Delete Program?</DialogTitle>
        <p className="mb-6 text-sm text-gray-700">This action cannot be undone.</p>
        <div className="flex gap-3 justify-end">
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button variant="destructive" onClick={handleDelete}>Delete</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
export default DeleteProgramModal 