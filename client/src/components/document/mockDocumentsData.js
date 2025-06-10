// TODO: i18n - processed
import { addDays, subDays } from 'date-fns';
// Generate dates
import { useTranslation } from "react-i18next";const today = new Date();
const yesterday = subDays(today, 1);
const lastWeek = subDays(today, 7);
const twoWeeksAgo = subDays(today, 14);
const nextWeek = addDays(today, 7);
// Mock folders data
export const mockFolders = [
{
  id: 1,
  name: 'Training Materials',
  parent_id: null,
  created_at: twoWeeksAgo.toISOString(),
  updated_at: yesterday.toISOString(),
  owner_id: 1,
  owner_name: 'Sarah Johnson',
  document_count: 5
},
{
  id: 2,
  name: 'Beneficiary Documents',
  parent_id: null,
  created_at: lastWeek.toISOString(),
  updated_at: today.toISOString(),
  owner_id: 1,
  owner_name: 'Sarah Johnson',
  document_count: 3
},
{
  id: 3,
  name: 'Reference Documents',
  parent_id: null,
  created_at: lastWeek.toISOString(),
  updated_at: lastWeek.toISOString(),
  owner_id: 2,
  owner_name: 'Michael Chen',
  document_count: 2
},
{
  id: 4,
  name: 'Technical Courses',
  parent_id: 1,
  created_at: lastWeek.toISOString(),
  updated_at: yesterday.toISOString(),
  owner_id: 1,
  owner_name: 'Sarah Johnson',
  document_count: 2
},
{
  id: 5,
  name: 'Soft Skills',
  parent_id: 1,
  created_at: lastWeek.toISOString(),
  updated_at: today.toISOString(),
  owner_id: 3,
  owner_name: 'Emily Davis',
  document_count: 3
}];

// Mock documents data
export const mockDocuments = [
{
  id: 1,
  name: 'Beneficiary Handbook.pdf',
  description: 'Complete guide for beneficiaries including program details and resources',
  folder_id: null,
  folder_name: null,
  mime_type: 'application/pdf',
  size: 2541653, // ~2.5MB
  created_at: twoWeeksAgo.toISOString(),
  updated_at: twoWeeksAgo.toISOString(),
  owner_id: 1,
  owner_name: 'Sarah Johnson',
  is_starred: true,
  version: 1,
  is_shared: true
},
{
  id: 2,
  name: 'Programming Fundamentals.pdf',
  description: 'Course materials for the programming fundamentals module',
  folder_id: 4,
  folder_name: 'Technical Courses',
  mime_type: 'application/pdf',
  size: 4823145, // ~4.8MB
  created_at: lastWeek.toISOString(),
  updated_at: yesterday.toISOString(),
  owner_id: 2,
  owner_name: 'Michael Chen',
  is_starred: false,
  version: 2,
  is_shared: true
},
{
  id: 3,
  name: 'Communication Skills Workshop.pptx',
  description: 'Presentation slides for the communication skills workshop',
  folder_id: 5,
  folder_name: 'Soft Skills',
  mime_type: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  size: 3571846, // ~3.5MB
  created_at: lastWeek.toISOString(),
  updated_at: lastWeek.toISOString(),
  owner_id: 3,
  owner_name: 'Emily Davis',
  is_starred: true,
  version: 1,
  is_shared: false
},
{
  id: 4,
  name: 'Web Development Roadmap.png',
  description: 'Visual roadmap for web development career path',
  folder_id: 4,
  folder_name: 'Technical Courses',
  mime_type: 'image/png',
  size: 1248576, // ~1.2MB
  created_at: yesterday.toISOString(),
  updated_at: yesterday.toISOString(),
  owner_id: 2,
  owner_name: 'Michael Chen',
  is_starred: false,
  version: 1,
  is_shared: true
},
{
  id: 5,
  name: 'Beneficiary Progress Tracker.xlsx',
  description: 'Excel template for tracking beneficiary progress through the program',
  folder_id: 2,
  folder_name: 'Beneficiary Documents',
  mime_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  size: 867245, // ~0.8MB
  created_at: twoWeeksAgo.toISOString(),
  updated_at: yesterday.toISOString(),
  owner_id: 1,
  owner_name: 'Sarah Johnson',
  is_starred: true,
  version: 3,
  is_shared: true
},
{
  id: 6,
  name: 'Interview Preparation Guide.docx',
  description: 'Guide for preparing beneficiaries for job interviews',
  folder_id: 5,
  folder_name: 'Soft Skills',
  mime_type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  size: 1645721, // ~1.6MB
  created_at: lastWeek.toISOString(),
  updated_at: lastWeek.toISOString(),
  owner_id: 3,
  owner_name: 'Emily Davis',
  is_starred: false,
  version: 1,
  is_shared: false
},
{
  id: 7,
  name: 'Program Overview.mp4',
  description: 'Video overview of the beneficiary development program',
  folder_id: null,
  folder_name: null,
  mime_type: 'video/mp4',
  size: 25673421, // ~25MB
  created_at: twoWeeksAgo.toISOString(),
  updated_at: twoWeeksAgo.toISOString(),
  owner_id: 1,
  owner_name: 'Sarah Johnson',
  is_starred: false,
  version: 1,
  is_shared: true
},
{
  id: 8,
  name: 'Trainer Guidelines.pdf',
  description: 'Guidelines and best practices for trainers',
  folder_id: null,
  folder_name: null,
  mime_type: 'application/pdf',
  size: 1892634, // ~1.8MB
  created_at: yesterday.toISOString(),
  updated_at: yesterday.toISOString(),
  owner_id: 1,
  owner_name: 'Sarah Johnson',
  is_starred: true,
  version: 1,
  is_shared: false
},
{
  id: 9,
  name: 'Beneficiary Assessment Form.pdf',
  description: 'Standard form for assessing beneficiary progress',
  folder_id: 2,
  folder_name: 'Beneficiary Documents',
  mime_type: 'application/pdf',
  size: 958762, // ~0.9MB
  created_at: twoWeeksAgo.toISOString(),
  updated_at: today.toISOString(),
  owner_id: 2,
  owner_name: 'Michael Chen',
  is_starred: false,
  version: 2,
  is_shared: true
},
{
  id: 10,
  name: 'Program Resources.zip',
  description: 'Collection of resources and templates for the program',
  folder_id: 3,
  folder_name: 'Reference Documents',
  mime_type: 'application/zip',
  size: 15784632, // ~15MB
  created_at: lastWeek.toISOString(),
  updated_at: lastWeek.toISOString(),
  owner_id: 3,
  owner_name: 'Emily Davis',
  is_starred: false,
  version: 1,
  is_shared: false
}];

// Mock document versions
export const mockDocumentVersions = {
  // Document ID 2 (Programming Fundamentals.pdf) has 2 versions
  2: [
  {
    id: 3,
    document_id: 2,
    version: 2,
    size: 4823145,
    created_at: yesterday.toISOString(),
    user_id: 2,
    user_name: 'Michael Chen',
    change_type: 'Updated content with new exercises'
  },
  {
    id: 2,
    document_id: 2,
    version: 1,
    size: 4256789,
    created_at: lastWeek.toISOString(),
    user_id: 2,
    user_name: 'Michael Chen',
    change_type: 'Initial upload'
  }],

  // Document ID 5 (Beneficiary Progress Tracker.xlsx) has 3 versions
  5: [
  {
    id: 7,
    document_id: 5,
    version: 3,
    size: 867245,
    created_at: yesterday.toISOString(),
    user_id: 1,
    user_name: 'Sarah Johnson',
    change_type: 'Added new tracking metrics'
  },
  {
    id: 6,
    document_id: 5,
    version: 2,
    size: 812456,
    created_at: lastWeek.toISOString(),
    user_id: 1,
    user_name: 'Sarah Johnson',
    change_type: 'Fixed calculation formulas'
  },
  {
    id: 5,
    document_id: 5,
    version: 1,
    size: 789123,
    created_at: twoWeeksAgo.toISOString(),
    user_id: 1,
    user_name: 'Sarah Johnson',
    change_type: 'Initial upload'
  }],

  // Document ID 9 (Beneficiary Assessment Form.pdf) has 2 versions
  9: [
  {
    id: 10,
    document_id: 9,
    version: 2,
    size: 958762,
    created_at: today.toISOString(),
    user_id: 2,
    user_name: 'Michael Chen',
    change_type: 'Updated form fields'
  },
  {
    id: 9,
    document_id: 9,
    version: 1,
    size: 912345,
    created_at: twoWeeksAgo.toISOString(),
    user_id: 2,
    user_name: 'Michael Chen',
    change_type: 'Initial upload'
  }]

};
// Mock comments data
export const mockComments = {
  // Comments for document ID 1
  1: [
  {
    id: 1,
    document_id: 1,
    user_id: 2,
    user_name: 'Michael Chen',
    content: 'Great handbook! We should update the contact information on page 5.',
    created_at: yesterday.toISOString()
  },
  {
    id: 2,
    document_id: 1,
    user_id: 3,
    user_name: 'Emily Davis',
    content: 'I agree with Michael. Also, can we add a section about the new mentorship program?',
    created_at: yesterday.toISOString()
  }],

  // Comments for document ID 3
  3: [
  {
    id: 3,
    document_id: 3,
    user_id: 1,
    user_name: 'Sarah Johnson',
    content: 'This workshop has been very effective with the latest cohort. We should schedule it again next month.',
    created_at: yesterday.toISOString()
  }],

  // Comments for document ID 5
  5: [
  {
    id: 4,
    document_id: 5,
    user_id: 2,
    user_name: 'Michael Chen',
    content: 'The new metrics are very helpful. Can we add a visualization tab?',
    created_at: today.toISOString()
  },
  {
    id: 5,
    document_id: 5,
    user_id: 3,
    user_name: 'Emily Davis',
    content: 'I noticed a small issue with the calculation in cell G15. It should include the workshop attendance.',
    created_at: today.toISOString()
  }]

};
// Mock shared users data
export const mockSharedUsers = {
  // Users with whom document ID 1 is shared
  1: [
  {
    id: 2,
    name: 'Michael Chen',
    email: 'michael.chen@example.com',
    access_type: 'edit',
    shared_at: lastWeek.toISOString()
  },
  {
    id: 3,
    name: 'Emily Davis',
    email: 'emily.davis@example.com',
    access_type: 'view',
    shared_at: lastWeek.toISOString()
  }],

  // Users with whom document ID 2 is shared
  2: [
  {
    id: 1,
    name: 'Sarah Johnson',
    email: 'sarah.johnson@example.com',
    access_type: 'view',
    shared_at: lastWeek.toISOString()
  },
  {
    id: 3,
    name: 'Emily Davis',
    email: 'emily.davis@example.com',
    access_type: 'view',
    shared_at: lastWeek.toISOString()
  }],

  // Users with whom document ID 5 is shared
  5: [
  {
    id: 2,
    name: 'Michael Chen',
    email: 'michael.chen@example.com',
    access_type: 'edit',
    shared_at: twoWeeksAgo.toISOString()
  },
  {
    id: 3,
    name: 'Emily Davis',
    email: 'emily.davis@example.com',
    access_type: 'edit',
    shared_at: twoWeeksAgo.toISOString()
  }]

};
// Mock API functions
export const fetchDocuments = (folderId = null) => {
  const folderDocuments = folderId ?
  mockDocuments.filter((doc) => doc.folder_id === parseInt(folderId)) :
  mockDocuments.filter((doc) => doc.folder_id === null);
  const foldersList = folderId ?
  mockFolders.filter((folder) => folder.parent_id === parseInt(folderId)) :
  mockFolders.filter((folder) => folder.parent_id === null);
  return {
    status: 200,
    data: {
      documents: folderDocuments,
      folders: foldersList
    }
  };
};
export const fetchDocument = (id) => {
  const document = mockDocuments.find((doc) => doc.id === parseInt(id));
  if (!document) {
    return {
      status: 404,
      data: { message: 'Document not found' }
    };
  }
  return {
    status: 200,
    data: document
  };
};
export const fetchFolder = (id) => {
  const folder = mockFolders.find((folder) => folder.id === parseInt(id));
  if (!folder) {
    return {
      status: 404,
      data: { message: 'Folder not found' }
    };
  }
  // Build the folder path
  const buildPath = (folderId) => {
    const pathFolder = mockFolders.find((f) => f.id === folderId);
    if (!pathFolder) return [];
    if (pathFolder.parent_id) {
      return [...buildPath(pathFolder.parent_id), { id: pathFolder.id, name: pathFolder.name }];
    }
    return [{ id: pathFolder.id, name: pathFolder.name }];
  };
  const path = folder.parent_id ? buildPath(folder.parent_id) : [];
  return {
    status: 200,
    data: {
      ...folder,
      path
    }
  };
};
export const fetchDocumentVersions = (id) => {
  const versions = mockDocumentVersions[id] || [];
  if (versions.length === 0) {
    // If no specific versions are defined, create a default version
    const document = mockDocuments.find((doc) => doc.id === parseInt(id));
    if (document) {
      versions.push({
        id: 1000 + parseInt(id),
        document_id: parseInt(id),
        version: 1,
        size: document.size,
        created_at: document.created_at,
        user_id: document.owner_id,
        user_name: document.owner_name,
        change_type: 'Initial upload'
      });
    }
  }
  return {
    status: 200,
    data: versions
  };
};
export const fetchDocumentComments = (id) => {
  const comments = mockComments[id] || [];
  return {
    status: 200,
    data: comments
  };
};
export const addDocumentComment = (id, data) => {
  const newComment = {
    id: Math.floor(Math.random() * 1000) + 100, // Generate a random ID
    document_id: parseInt(id),
    user_id: 1, // Current user ID
    user_name: 'You', // Current user name
    content: data.content,
    created_at: new Date().toISOString()
  };
  return {
    status: 201,
    data: newComment
  };
};
export const fetchDocumentSharing = (id) => {
  const sharedUsers = mockSharedUsers[id] || [];
  const shareLink = sharedUsers.length > 0 ?
  `https://bdc-app.example.com/share/${id}/${Math.random().toString(36).substring(2, 10)}` :
  '';
  return {
    status: 200,
    data: {
      shared_users: sharedUsers,
      share_link: shareLink
    }
  };
};
export const generateShareLink = (id) => {
  return {
    status: 200,
    data: {
      share_link: `https://bdc-app.example.com/share/${id}/${Math.random().toString(36).substring(2, 15)}`
    }
  };
};
export const shareDocument = (id, data) => {
  return {
    status: 200,
    data: {
      message: 'Document shared successfully',
      shared_with: data.user_ids.length
    }
  };
};
export const shareMultipleDocuments = (data) => {
  return {
    status: 200,
    data: {
      message: 'Documents shared successfully',
      document_count: data.document_ids.length,
      shared_with: data.user_ids.length
    }
  };
};
export const updateDocument = (id, data) => {
  return {
    status: 200,
    data: {
      id: parseInt(id),
      ...data,
      updated_at: new Date().toISOString()
    }
  };
};
export const deleteDocument = (id) => {
  return {
    status: 204,
    data: null
  };
};
export const uploadDocument = (data) => {
  const newId = Math.floor(Math.random() * 1000) + 100;
  return {
    status: 201,
    data: {
      id: newId,
      name: data.name || 'Uploaded Document',
      description: data.description || '',
      folder_id: data.folder_id || null,
      mime_type: 'application/pdf', // Assumed default
      size: 1024000, // 1MB default
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      owner_id: 1, // Current user ID
      owner_name: 'You', // Current user name
      is_starred: false,
      version: 1,
      is_shared: false
    }
  };
};
export const createFolder = (data) => {
  const newId = Math.floor(Math.random() * 1000) + 100;
  return {
    status: 201,
    data: {
      id: newId,
      name: data.name,
      parent_id: data.parent_id || null,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      owner_id: 1, // Current user ID
      owner_name: 'You', // Current user name
      document_count: 0
    }
  };
};
export const searchUsers = (query) => {
  const users = [
  { id: 1, name: 'Sarah Johnson', email: 'sarah.johnson@example.com' },
  { id: 2, name: 'Michael Chen', email: 'michael.chen@example.com' },
  { id: 3, name: 'Emily Davis', email: 'emily.davis@example.com' },
  { id: 4, name: 'Robert Wilson', email: 'robert.wilson@example.com' },
  { id: 5, name: 'Jennifer Lopez', email: 'jennifer.lopez@example.com' }];

  const results = users.filter((user) =>
  user.name.toLowerCase().includes(query.toLowerCase()) ||
  user.email.toLowerCase().includes(query.toLowerCase())
  );
  return {
    status: 200,
    data: results
  };
};
export const fetchMultipleDocuments = (ids) => {
  const documents = mockDocuments.filter((doc) => ids.includes(doc.id.toString()));
  return {
    status: 200,
    data: documents
  };
};