import React from 'react';
import { Box, Container, Typography, Breadcrumbs, Link, Chip } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import NavigateNextIcon from '@mui/icons-material/NavigateNext';
import HomeIcon from '@mui/icons-material/Home';
import AssessmentIcon from '@mui/icons-material/Assessment';
import ReportsDashboard from '../../components/reports/ReportsDashboard';
import { useAuth } from '../../contexts/AuthContext';

const ReportsPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  return (
    <Box sx={{ backgroundColor: '#f5f5f5', minHeight: '100vh', py: 3 }}>
      <Container maxWidth="xl">
        {/* Breadcrumbs */}
        <Breadcrumbs
          separator={<NavigateNextIcon fontSize="small" />}
          sx={{ mb: 3 }}
        >
          <Link
            underline="hover"
            sx={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}
            color="inherit"
            onClick={() => navigate('/')}
          >
            <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Home
          </Link>
          <Typography
            sx={{ display: 'flex', alignItems: 'center' }}
            color="text.primary"
          >
            <AssessmentIcon sx={{ mr: 0.5 }} fontSize="inherit" />
            Reports
          </Typography>
        </Breadcrumbs>

        {/* Page Header */}
        <Box sx={{ mb: 4 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Typography variant="h4" component="h1" sx={{ fontWeight: 600 }}>
              Reports & Analytics
            </Typography>
            {user?.role === 'admin' && (
              <Chip
                label="Admin Access"
                color="primary"
                size="small"
                sx={{ ml: 2 }}
              />
            )}
          </Box>
          <Typography variant="body1" color="text.secondary">
            Generate, schedule, and manage comprehensive reports for your organization
          </Typography>
        </Box>

        {/* Reports Dashboard */}
        <ReportsDashboard />
      </Container>
    </Box>
  );
};

export default ReportsPage;