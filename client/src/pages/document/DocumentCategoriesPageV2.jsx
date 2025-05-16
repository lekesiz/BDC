import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaFolder, FaEdit, FaTrash, FaPlus, FaTimes, FaCheck, FaSort, FaSearch } from 'react-icons/fa';
import { toast } from 'react-toastify';

const DocumentCategoriesPageV2 = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);
  const [filteredCategories, setFilteredCategories] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    parent_id: null,
    color: '#3B82F6',
    icon: 'folder',
    permissions: {
      view: ['all'],
      upload: ['trainer', 'admin'],
      delete: ['admin']
    }
  });
  const [sortConfig, setSortConfig] = useState({ key: 'name', direction: 'asc' });
  const [selectedCategories, setSelectedCategories] = useState([]);
  const [bulkAction, setBulkAction] = useState('');

  const icons = [
    'folder', 'file', 'document', 'archive', 'book', 'briefcase',
    'clipboard', 'database', 'envelope', 'image', 'video', 'music'
  ];

  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
    '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#14B8A6'
  ];

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    filterCategories();
  }, [searchTerm, categories]);

  const fetchCategories = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/documents/categories');
      setCategories(response.data);
    } catch (error) {
      toast.error('Kategoriler yüklenemedi');
    } finally {
      setLoading(false);
    }
  };

  const filterCategories = () => {
    let filtered = categories;
    
    if (searchTerm) {
      filtered = filtered.filter(cat => 
        cat.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        cat.description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];
      
      if (sortConfig.direction === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    setFilteredCategories(filtered);
  };

  const handleSort = (key) => {
    setSortConfig({
      key,
      direction: sortConfig.key === key && sortConfig.direction === 'asc' ? 'desc' : 'asc'
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingCategory) {
        await axios.put(`/api/documents/categories/${editingCategory.id}`, formData);
        toast.success('Kategori güncellendi');
      } else {
        await axios.post('/api/documents/categories', formData);
        toast.success('Kategori oluşturuldu');
      }
      
      fetchCategories();
      handleCloseModal();
    } catch (error) {
      toast.error('İşlem başarısız');
    }
  };

  const handleEdit = (category) => {
    setEditingCategory(category);
    setFormData({
      name: category.name,
      description: category.description || '',
      parent_id: category.parent_id,
      color: category.color || '#3B82F6',
      icon: category.icon || 'folder',
      permissions: category.permissions || {
        view: ['all'],
        upload: ['trainer', 'admin'],
        delete: ['admin']
      }
    });
    setShowModal(true);
  };

  const handleDelete = async (categoryId) => {
    if (window.confirm('Bu kategoriyi silmek istediğinizden emin misiniz?')) {
      try {
        await axios.delete(`/api/documents/categories/${categoryId}`);
        toast.success('Kategori silindi');
        fetchCategories();
      } catch (error) {
        toast.error('Silme işlemi başarısız');
      }
    }
  };

  const handleBulkAction = async () => {
    if (!bulkAction || selectedCategories.length === 0) return;

    try {
      if (bulkAction === 'delete') {
        await axios.post('/api/documents/categories/bulk-delete', {
          category_ids: selectedCategories
        });
        toast.success(`${selectedCategories.length} kategori silindi`);
      }
      
      setSelectedCategories([]);
      setBulkAction('');
      fetchCategories();
    } catch (error) {
      toast.error('Toplu işlem başarısız');
    }
  };

  const handleSelectCategory = (categoryId) => {
    if (selectedCategories.includes(categoryId)) {
      setSelectedCategories(selectedCategories.filter(id => id !== categoryId));
    } else {
      setSelectedCategories([...selectedCategories, categoryId]);
    }
  };

  const handleSelectAll = () => {
    if (selectedCategories.length === filteredCategories.length) {
      setSelectedCategories([]);
    } else {
      setSelectedCategories(filteredCategories.map(cat => cat.id));
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingCategory(null);
    setFormData({
      name: '',
      description: '',
      parent_id: null,
      color: '#3B82F6',
      icon: 'folder',
      permissions: {
        view: ['all'],
        upload: ['trainer', 'admin'],
        delete: ['admin']
      }
    });
  };

  const renderCategoryTree = (categories, parentId = null, level = 0) => {
    return categories
      .filter(cat => cat.parent_id === parentId)
      .map(category => (
        <div key={category.id}>
          <div
            className={`flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg ${
              selectedCategories.includes(category.id) ? 'bg-blue-50' : ''
            }`}
            style={{ paddingLeft: `${level * 20 + 12}px` }}
          >
            <div className="flex items-center flex-1">
              <input
                type="checkbox"
                checked={selectedCategories.includes(category.id)}
                onChange={() => handleSelectCategory(category.id)}
                className="mr-3"
              />
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mr-3"
                style={{ backgroundColor: category.color + '20' }}
              >
                <FaFolder style={{ color: category.color }} />
              </div>
              <div>
                <h3 className="font-medium">{category.name}</h3>
                {category.description && (
                  <p className="text-sm text-gray-600">{category.description}</p>
                )}
                <div className="flex items-center text-xs text-gray-500 mt-1">
                  <span>{category.document_count} doküman</span>
                  {category.subcategory_count > 0 && (
                    <span className="ml-3">{category.subcategory_count} alt kategori</span>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleEdit(category)}
                className="text-blue-500 hover:text-blue-600"
              >
                <FaEdit />
              </button>
              <button
                onClick={() => handleDelete(category.id)}
                className="text-red-500 hover:text-red-600"
              >
                <FaTrash />
              </button>
            </div>
          </div>
          {renderCategoryTree(categories, category.id, level + 1)}
        </div>
      ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => navigate('/documents')}
            className="text-gray-600 hover:text-gray-800 mb-4"
          >
            ← Dokümanlara Geri Dön
          </button>
          <h1 className="text-2xl font-bold">Kategori Yönetimi</h1>
          <p className="text-gray-600">Doküman kategorilerini düzenleyin ve yönetin</p>
        </div>

        {/* Actions Bar */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowModal(true)}
                className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 flex items-center"
              >
                <FaPlus className="mr-2" />
                Yeni Kategori
              </button>
              
              {selectedCategories.length > 0 && (
                <div className="flex items-center space-x-2">
                  <select
                    value={bulkAction}
                    onChange={(e) => setBulkAction(e.target.value)}
                    className="px-3 py-2 border rounded"
                  >
                    <option value="">Toplu İşlem</option>
                    <option value="delete">Sil</option>
                  </select>
                  <button
                    onClick={handleBulkAction}
                    className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
                  >
                    Uygula
                  </button>
                </div>
              )}
            </div>

            <div className="relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Kategori ara..."
                className="pl-10 pr-4 py-2 border rounded-lg w-full md:w-64"
              />
              <FaSearch className="absolute left-3 top-3 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Categories List */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="p-4 border-b">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={selectedCategories.length === filteredCategories.length && filteredCategories.length > 0}
                onChange={handleSelectAll}
                className="mr-3"
              />
              <button
                onClick={() => handleSort('name')}
                className="flex items-center text-sm text-gray-600 hover:text-gray-800"
              >
                Kategori Adı
                <FaSort className="ml-1" />
              </button>
            </div>
          </div>

          <div className="p-4">
            {filteredCategories.length > 0 ? (
              renderCategoryTree(filteredCategories)
            ) : (
              <div className="text-center py-8">
                <FaFolder className="text-5xl text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">
                  {searchTerm ? 'Arama kriterlerine uygun kategori bulunamadı' : 'Henüz kategori eklenmemiş'}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Create/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-lg font-semibold">
                {editingCategory ? 'Kategori Düzenle' : 'Yeni Kategori'}
              </h3>
              <button
                onClick={handleCloseModal}
                className="text-gray-500 hover:text-gray-700"
              >
                <FaTimes />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Kategori Adı</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Açıklama</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows="3"
                />
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Üst Kategori</label>
                <select
                  value={formData.parent_id || ''}
                  onChange={(e) => setFormData({ ...formData, parent_id: e.target.value || null })}
                  className="w-full px-3 py-2 border rounded-lg"
                >
                  <option value="">Ana Kategori</option>
                  {categories
                    .filter(cat => cat.id !== editingCategory?.id)
                    .map(cat => (
                      <option key={cat.id} value={cat.id}>
                        {cat.name}
                      </option>
                    ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Renk</label>
                  <div className="grid grid-cols-5 gap-2">
                    {colors.map(color => (
                      <button
                        key={color}
                        type="button"
                        onClick={() => setFormData({ ...formData, color })}
                        className={`w-10 h-10 rounded-lg ${
                          formData.color === color ? 'ring-2 ring-offset-2 ring-blue-500' : ''
                        }`}
                        style={{ backgroundColor: color }}
                      />
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">İkon</label>
                  <select
                    value={formData.icon}
                    onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
                    className="w-full px-3 py-2 border rounded-lg"
                  >
                    {icons.map(icon => (
                      <option key={icon} value={icon}>{icon}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">İzinler</label>
                <div className="space-y-2">
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.permissions.view.includes('all')}
                        onChange={(e) => {
                          const permissions = { ...formData.permissions };
                          if (e.target.checked) {
                            permissions.view = ['all'];
                          } else {
                            permissions.view = [];
                          }
                          setFormData({ ...formData, permissions });
                        }}
                        className="mr-2"
                      />
                      Herkes görüntüleyebilir
                    </label>
                  </div>
                  <div>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={formData.permissions.upload.includes('trainer')}
                        onChange={(e) => {
                          const permissions = { ...formData.permissions };
                          if (e.target.checked) {
                            permissions.upload = [...permissions.upload, 'trainer'];
                          } else {
                            permissions.upload = permissions.upload.filter(r => r !== 'trainer');
                          }
                          setFormData({ ...formData, permissions });
                        }}
                        className="mr-2"
                      />
                      Eğitmenler yükleyebilir
                    </label>
                  </div>
                </div>
              </div>

              <div className="flex justify-end space-x-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  İptal
                </button>
                <button
                  type="submit"
                  className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600"
                >
                  {editingCategory ? 'Güncelle' : 'Oluştur'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentCategoriesPageV2;