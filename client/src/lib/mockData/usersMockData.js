/**
 * Users Mock Data for Demo and Testing
 */

// User roles
export const USER_ROLES = {
  SUPER_ADMIN: 'super_admin',
  TENANT_ADMIN: 'tenant_admin',
  TRAINER: 'trainer',
  STUDENT: 'student',
  TRAINEE: 'trainee'
};

// User status
export const USER_STATUS = {
  ACTIVE: 'active',
  INACTIVE: 'inactive',
  PENDING: 'pending',
  SUSPENDED: 'suspended'
};

// Sample users data
const mockUsers = [
  {
    id: 1,
    email: 'admin@bdc.com',
    username: 'admin',
    firstName: 'System',
    lastName: 'Administrator',
    fullName: 'System Administrator',
    role: USER_ROLES.SUPER_ADMIN,
    status: USER_STATUS.ACTIVE,
    avatar: 'https://i.pravatar.cc/150?u=admin',
    phone: '+90 555 123 4567',
    department: 'IT',
    joinDate: '2024-01-01',
    lastLogin: new Date().toISOString(),
    permissions: [
      'users.view', 'users.create', 'users.edit', 'users.delete',
      'beneficiaries.view', 'beneficiaries.create', 'beneficiaries.edit', 'beneficiaries.delete',
      'programs.view', 'programs.create', 'programs.edit', 'programs.delete',
      'evaluations.view', 'evaluations.create', 'evaluations.edit', 'evaluations.delete',
      'reports.view', 'reports.create', 'settings.manage', 'system.admin'
    ],
    profile: {
      bio: 'System administrator with full access to all features.',
      skills: ['System Administration', 'User Management', 'Security'],
      languages: ['Turkish', 'English'],
      timezone: 'Europe/Istanbul'
    }
  },
  {
    id: 2,
    email: 'tenant@bdc.com',
    username: 'tenant_admin',
    firstName: 'Tenant',
    lastName: 'Admin',
    fullName: 'Tenant Admin',
    role: USER_ROLES.TENANT_ADMIN,
    status: USER_STATUS.ACTIVE,
    avatar: 'https://i.pravatar.cc/150?u=tenant',
    phone: '+90 555 234 5678',
    department: 'Management',
    joinDate: '2024-01-15',
    lastLogin: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    permissions: [
      'beneficiaries.view', 'beneficiaries.create', 'beneficiaries.edit',
      'programs.view', 'programs.create', 'programs.edit',
      'evaluations.view', 'evaluations.create', 'reports.view'
    ],
    profile: {
      bio: 'Tenant administrator managing local operations.',
      skills: ['Management', 'Program Oversight', 'Reporting'],
      languages: ['Turkish', 'English'],
      timezone: 'Europe/Istanbul'
    }
  },
  {
    id: 3,
    email: 'trainer@bdc.com',
    username: 'trainer1',
    firstName: 'Ahmet',
    lastName: 'Yılmaz',
    fullName: 'Ahmet Yılmaz',
    role: USER_ROLES.TRAINER,
    status: USER_STATUS.ACTIVE,
    avatar: 'https://i.pravatar.cc/150?u=trainer1',
    phone: '+90 555 345 6789',
    department: 'Education',
    joinDate: '2024-02-01',
    lastLogin: new Date(Date.now() - 30 * 60 * 1000).toISOString(),
    permissions: [
      'beneficiaries.view', 'beneficiaries.edit',
      'evaluations.view', 'evaluations.create', 'evaluations.grade',
      'programs.view', 'assessments.create'
    ],
    profile: {
      bio: 'Experienced trainer specializing in vocational education.',
      skills: ['Teaching', 'Vocational Training', 'Assessment Design'],
      languages: ['Turkish', 'English'],
      timezone: 'Europe/Istanbul',
      specializations: ['Vocational Skills', 'Digital Literacy', 'Professional Development']
    },
    stats: {
      studentsAssigned: 15,
      completedAssessments: 45,
      averageStudentScore: 82.5,
      coursesCompleted: 8
    }
  },
  {
    id: 4,
    email: 'student@bdc.com',
    username: 'student1',
    firstName: 'Ayşe',
    lastName: 'Demir',
    fullName: 'Ayşe Demir',
    role: USER_ROLES.STUDENT,
    status: USER_STATUS.ACTIVE,
    avatar: 'https://i.pravatar.cc/150?u=student1',
    phone: '+90 555 456 7890',
    department: null,
    joinDate: '2024-03-01',
    lastLogin: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    permissions: [
      'evaluations.view', 'evaluations.take',
      'documents.view', 'profile.edit'
    ],
    profile: {
      bio: 'Active student in the digital skills program.',
      skills: ['Basic Computer Skills', 'Microsoft Office'],
      languages: ['Turkish'],
      timezone: 'Europe/Istanbul'
    },
    studentInfo: {
      program: 'Digital Skills Development',
      enrollmentDate: '2024-03-01',
      progress: 65,
      gpa: 3.2,
      creditsCompleted: 18,
      creditsTotal: 30
    }
  }
];

// Generate additional users
const generateUser = (id, role) => {
  const firstNames = ['Mehmet', 'Fatma', 'Ali', 'Emine', 'Hasan', 'Zeynep', 'İbrahim', 'Hatice', 'Mustafa', 'Ayşe'];
  const lastNames = ['Yılmaz', 'Kaya', 'Demir', 'Şahin', 'Çelik', 'Yıldız', 'Öztürk', 'Arslan', 'Doğan', 'Aslan'];
  
  const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
  const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
  
  const rolePermissions = {
    [USER_ROLES.TRAINER]: [
      'beneficiaries.view', 'beneficiaries.edit',
      'evaluations.view', 'evaluations.create', 'evaluations.grade',
      'programs.view', 'assessments.create'
    ],
    [USER_ROLES.STUDENT]: [
      'evaluations.view', 'evaluations.take',
      'documents.view', 'profile.edit'
    ],
    [USER_ROLES.TRAINEE]: [
      'evaluations.view', 'evaluations.take',
      'documents.view', 'profile.edit'
    ]
  };
  
  return {
    id,
    email: `${firstName.toLowerCase()}.${lastName.toLowerCase()}@example.com`,
    username: `${firstName.toLowerCase()}${id}`,
    firstName,
    lastName,
    fullName: `${firstName} ${lastName}`,
    role,
    status: Math.random() > 0.1 ? USER_STATUS.ACTIVE : USER_STATUS.INACTIVE,
    avatar: `https://i.pravatar.cc/150?u=${id}`,
    phone: `+90 555 ${Math.floor(Math.random() * 900) + 100} ${Math.floor(Math.random() * 9000) + 1000}`,
    department: role === USER_ROLES.TRAINER ? 'Education' : null,
    joinDate: new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28)).toISOString().split('T')[0],
    lastLogin: new Date(Date.now() - Math.floor(Math.random() * 30) * 24 * 60 * 60 * 1000).toISOString(),
    permissions: rolePermissions[role] || [],
    profile: {
      bio: `${role} user in the BDC system.`,
      skills: role === USER_ROLES.TRAINER ? ['Teaching', 'Assessment'] : ['Learning', 'Development'],
      languages: ['Turkish'],
      timezone: 'Europe/Istanbul'
    }
  };
};

// Generate additional users
for (let i = 5; i <= 30; i++) {
  const roles = [USER_ROLES.TRAINER, USER_ROLES.STUDENT, USER_ROLES.TRAINEE];
  const role = roles[Math.floor(Math.random() * roles.length)];
  mockUsers.push(generateUser(i, role));
}

// Export users data
export { mockUsers };

// User statistics
export const userStats = {
  total: mockUsers.length,
  active: mockUsers.filter(u => u.status === USER_STATUS.ACTIVE).length,
  inactive: mockUsers.filter(u => u.status === USER_STATUS.INACTIVE).length,
  byRole: {
    [USER_ROLES.SUPER_ADMIN]: mockUsers.filter(u => u.role === USER_ROLES.SUPER_ADMIN).length,
    [USER_ROLES.TENANT_ADMIN]: mockUsers.filter(u => u.role === USER_ROLES.TENANT_ADMIN).length,
    [USER_ROLES.TRAINER]: mockUsers.filter(u => u.role === USER_ROLES.TRAINER).length,
    [USER_ROLES.STUDENT]: mockUsers.filter(u => u.role === USER_ROLES.STUDENT).length,
    [USER_ROLES.TRAINEE]: mockUsers.filter(u => u.role === USER_ROLES.TRAINEE).length
  },
  recentLogins: mockUsers
    .filter(u => new Date(u.lastLogin) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000))
    .length
};

export default mockUsers;