import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useToast } from '../../hooks/useToast';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Card } from '../../components/ui/card';
import { Checkbox } from '../../components/ui/checkbox';
import { Badge } from '../../components/ui/badge';
import {
  Loader2,
  Search,
  ArrowLeft,
  UserPlus,
  UserMinus,
  Users
} from 'lucide-react';
const AssignBeneficiariesPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [program, setProgram] = useState(null);
  const [beneficiaries, setBeneficiaries] = useState([]);
  const [selectedBeneficiaries, setSelectedBeneficiaries] = useState(new Set());
  const [searchTerm, setSearchTerm] = useState('');
  const [filterEnrolled, setFilterEnrolled] = useState(false);
  useEffect(() => {
    fetchProgramDetails();
    fetchBeneficiaries();
  }, [id]);
  const fetchProgramDetails = async () => {
    try {
      const res = await fetch(`/api/programs/${id}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch program');
      const data = await res.json();
      setProgram(data);
    } catch (error) {
      console.error('Error fetching program:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch program details',
        variant: 'destructive'
      });
    }
  };
  const fetchBeneficiaries = async () => {
    try {
      const res = await fetch('/api/beneficiaries', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!res.ok) throw new Error('Failed to fetch beneficiaries');
      const data = await res.json();
      // Fetch enrolled beneficiaries for this program
      const enrolledRes = await fetch(`/api/programs/${id}/beneficiaries`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      const enrolledData = await enrolledRes.json();
      const enrolledIds = new Set(enrolledData.map(b => b.id));
      // Mark beneficiaries as enrolled
      const beneficiariesWithEnrollment = data.map(beneficiary => ({
        ...beneficiary,
        isEnrolled: enrolledIds.has(beneficiary.id)
      }));
      setBeneficiaries(beneficiariesWithEnrollment);
      setSelectedBeneficiaries(enrolledIds);
    } catch (error) {
      console.error('Error fetching beneficiaries:', error);
      toast({
        title: 'Error',
        description: 'Failed to fetch beneficiaries',
        variant: 'destructive'
      });
    } finally {
      setLoading(false);
    }
  };
  const handleSelectBeneficiary = (beneficiaryId) => {
    const newSelection = new Set(selectedBeneficiaries);
    if (newSelection.has(beneficiaryId)) {
      newSelection.delete(beneficiaryId);
    } else {
      newSelection.add(beneficiaryId);
    }
    setSelectedBeneficiaries(newSelection);
  };
  const handleSelectAll = () => {
    if (selectedBeneficiaries.size === filteredBeneficiaries.length) {
      setSelectedBeneficiaries(new Set());
    } else {
      const allIds = new Set(filteredBeneficiaries.map(b => b.id));
      setSelectedBeneficiaries(allIds);
    }
  };
  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await fetch(`/api/programs/${id}/beneficiaries`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          beneficiary_ids: Array.from(selectedBeneficiaries)
        })
      });
      if (!res.ok) throw new Error('Failed to update assignments');
      toast({
        title: 'Success',
        description: 'Beneficiary assignments updated successfully'
      });
      navigate(`/programs/${id}`);
    } catch (error) {
      console.error('Error saving assignments:', error);
      toast({
        title: 'Error',
        description: 'Failed to update assignments',
        variant: 'destructive'
      });
    } finally {
      setSaving(false);
    }
  };
  const filteredBeneficiaries = beneficiaries.filter(beneficiary => {
    const matchesSearch = beneficiary.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         beneficiary.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = !filterEnrolled || beneficiary.isEnrolled;
    return matchesSearch && matchesFilter;
  });
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate(`/programs/${id}`)}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <h1 className="text-2xl font-bold text-gray-900">
          Assign Beneficiaries to {program?.name}
        </h1>
      </div>
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
                <Input
                  type="text"
                  placeholder="Search beneficiaries..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-9 w-64"
                />
              </div>
              <label className="flex items-center gap-2">
                <Checkbox
                  checked={filterEnrolled}
                  onCheckedChange={setFilterEnrolled}
                />
                <span className="text-sm">Show enrolled only</span>
              </label>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">
                {selectedBeneficiaries.size} of {filteredBeneficiaries.length} selected
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleSelectAll}
              >
                {selectedBeneficiaries.size === filteredBeneficiaries.length ? 'Deselect All' : 'Select All'}
              </Button>
            </div>
          </div>
          <div className="border rounded-lg divide-y max-h-[500px] overflow-y-auto">
            {filteredBeneficiaries.length === 0 ? (
              <div className="p-8 text-center text-gray-500">
                <Users className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p>No beneficiaries found</p>
              </div>
            ) : (
              filteredBeneficiaries.map((beneficiary) => (
                <div
                  key={beneficiary.id}
                  className={`p-4 flex items-center justify-between hover:bg-gray-50 cursor-pointer ${
                    selectedBeneficiaries.has(beneficiary.id) ? 'bg-blue-50' : ''
                  }`}
                  onClick={() => handleSelectBeneficiary(beneficiary.id)}
                >
                  <div className="flex items-center gap-3">
                    <Checkbox
                      checked={selectedBeneficiaries.has(beneficiary.id)}
                      onChange={() => {}}
                    />
                    <div>
                      <p className="font-medium text-gray-900">{beneficiary.full_name}</p>
                      <p className="text-sm text-gray-500">{beneficiary.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {beneficiary.isEnrolled && (
                      <Badge variant="outline" className="text-green-700">
                        Enrolled
                      </Badge>
                    )}
                    {beneficiary.status && (
                      <Badge variant="secondary">
                        {beneficiary.status}
                      </Badge>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
          <div className="flex items-center justify-between pt-4">
            <div className="text-sm text-gray-600">
              <p>Current enrollment: {program?.enrolled_count || 0} / {program?.max_participants}</p>
              <p>Selected for enrollment: {selectedBeneficiaries.size}</p>
            </div>
            <div className="flex gap-3">
              <Button
                variant="outline"
                onClick={() => navigate(`/programs/${id}`)}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Save Assignments
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
export default AssignBeneficiariesPage;