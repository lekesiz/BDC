// TODO: i18n - processed
import { Dialog, DialogTrigger, DialogContent, DialogTitle } from '@radix-ui/react-dialog';
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import axios from 'axios';import { useTranslation } from "react-i18next";
const DeleteProgramModal = ({ programId, onDeleted }) => {const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const handleDelete = async () => {
    await axios.delete(`/api/programs/${programId}`);
    onDeleted?.();
    setOpen(false);
  };
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button size="sm" variant="destructive">{t("components.delete")}</Button>
      </DialogTrigger>
      <DialogContent className="p-6 bg-white rounded shadow-xl">
        <DialogTitle className="text-lg font-semibold mb-4">{t("components.delete_program")}</DialogTitle>
        <p className="mb-6 text-sm text-gray-700">{t("components.this_action_cannot_be_undone")}</p>
        <div className="flex gap-3 justify-end">
          <Button variant="outline" onClick={() => setOpen(false)}>{t("components.cancel")}</Button>
          <Button variant="destructive" onClick={handleDelete}>{t("components.delete")}</Button>
        </div>
      </DialogContent>
    </Dialog>);

};
export default DeleteProgramModal;