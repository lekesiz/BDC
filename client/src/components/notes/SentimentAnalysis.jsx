import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
  Grid,
  Paper,
  Chip,
  IconButton,
  Tooltip,
  Button,
  LinearProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel
} from '@mui/material';
import {
  EmotionHappy,
  EmotionNeutral,
  EmotionSad,
  TrendingUp,
  TrendingDown,
  Analytics,
  CalendarMonth,
  Psychology,
  Timeline,
  CompareArrows,
  Refresh
} from '@mui/icons-material';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';
import { useSnackbar } from 'notistack';
import api from '../../services/api';

const sentimentColors = {
  positive: '#4CAF50',
  neutral: '#FFC107',
  negative: '#F44336',
  mixed: '#9C27B0'
};

const sentimentIcons = {
  positive: <EmotionHappy />,
  neutral: <EmotionNeutral />,
  negative: <EmotionSad />
};

const getScoreColor = (score) => {
  if (score > 0.3) return sentimentColors.positive;
  if (score < -0.3) return sentimentColors.negative;
  return sentimentColors.neutral;
};

const SentimentAnalysis = ({ noteId, beneficiaryId, noteContent }) => {
  const [sentimentData, setSentimentData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('overview');
  const [timeRange, setTimeRange] = useState('month');
  const [comparison, setComparison] = useState(null);
  const { enqueueSnackbar } = useSnackbar();

  const fetchSentimentData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/api/notes/${noteId}/analysis`, {
        params: { analysis_type: 'sentiment' }
      });
      setSentimentData(response.data);
      enqueueSnackbar('Sentiment analizi başarıyla yüklendi', { variant: 'success' });
    } catch (err) {
      setError('Sentiment analizi yüklenemedi');
      enqueueSnackbar('Sentiment analizi hatası', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const fetchHistoricalData = async () => {
    try {
      const response = await api.get(`/api/beneficiaries/${beneficiaryId}/sentiment-history`, {
        params: { time_range: timeRange }
      });
      setComparison(response.data);
    } catch (err) {
      enqueueSnackbar('Geçmiş veri yüklenemedi', { variant: 'error' });
    }
  };

  useEffect(() => {
    if (noteId) {
      fetchSentimentData();
    }
  }, [noteId]);

  useEffect(() => {
    if (beneficiaryId && viewMode === 'timeline') {
      fetchHistoricalData();
    }
  }, [beneficiaryId, viewMode, timeRange]);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!sentimentData) return null;

  const { sentiment } = sentimentData;

  const overallSentimentChart = {
    labels: ['Pozitif', 'Nötr', 'Negatif'],
    datasets: [{
      data: [
        sentiment.positive_percentage,
        sentiment.neutral_percentage,
        sentiment.negative_percentage
      ],
      backgroundColor: [
        sentimentColors.positive,
        sentimentColors.neutral,
        sentimentColors.negative
      ],
      borderWidth: 0
    }]
  };

  const emotionRadarChart = sentiment.emotions && {
    labels: Object.keys(sentiment.emotions),
    datasets: [{
      label: 'Duygu Yoğunluğu',
      data: Object.values(sentiment.emotions),
      backgroundColor: 'rgba(63, 81, 181, 0.2)',
      borderColor: '#3F51B5',
      pointBackgroundColor: '#3F51B5',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: '#3F51B5'
    }]
  };

  const sentenceSentimentChart = sentiment.sentence_sentiments && {
    labels: sentiment.sentence_sentiments.map((_, idx) => `Cümle ${idx + 1}`),
    datasets: [{
      label: 'Sentiment Skoru',
      data: sentiment.sentence_sentiments.map(s => s.score),
      backgroundColor: sentiment.sentence_sentiments.map(s => getScoreColor(s.score)),
      borderWidth: 0
    }]
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Box sx={{ fontSize: 60, color: getScoreColor(sentiment.score) }}>
            {sentiment.score > 0.3 ? sentimentIcons.positive :
             sentiment.score < -0.3 ? sentimentIcons.negative :
             sentimentIcons.neutral}
          </Box>
          <Typography variant="h6" gutterBottom>
            Genel Duygu
          </Typography>
          <Typography variant="h4" sx={{ fontWeight: 'bold', color: getScoreColor(sentiment.score) }}>
            {sentiment.overall_sentiment}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Skor: {sentiment.score.toFixed(3)}
          </Typography>
        </Paper>
      </Grid>

      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Duygu Dağılımı
          </Typography>
          <Box sx={{ height: 200 }}>
            <Doughnut 
              data={overallSentimentChart}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom'
                  }
                }
              }}
            />
          </Box>
        </Paper>
      </Grid>

      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Duygusal Güven
          </Typography>
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Analiz Güvenilirliği
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={sentiment.confidence * 100}
              sx={{ 
                height: 10, 
                borderRadius: 5,
                backgroundColor: '#e0e0e0'
              }}
            />
            <Typography variant="body2" align="right" sx={{ mt: 0.5 }}>
              %{Math.round(sentiment.confidence * 100)}
            </Typography>
          </Box>
          
          {sentiment.subjectivity !== undefined && (
            <Box>
              <Typography variant="body2" color="text.secondary">
                Öznel/Nesnel
              </Typography>
              <LinearProgress 
                variant="determinate" 
                value={sentiment.subjectivity * 100}
                sx={{ 
                  height: 10, 
                  borderRadius: 5,
                  backgroundColor: '#e0e0e0'
                }}
              />
              <Typography variant="body2" align="right" sx={{ mt: 0.5 }}>
                %{Math.round(sentiment.subjectivity * 100)} Öznel
              </Typography>
            </Box>
          )}
        </Paper>
      </Grid>

      {sentiment.key_phrases && sentiment.key_phrases.length > 0 && (
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Anahtar İfadeler
            </Typography>
            <Box sx={{ mt: 2 }}>
              {sentiment.key_phrases.map((phrase, idx) => (
                <Chip
                  key={idx}
                  label={phrase.text}
                  sx={{ 
                    m: 0.5,
                    backgroundColor: getScoreColor(phrase.sentiment),
                    color: 'white'
                  }}
                  icon={
                    <Box sx={{ color: 'white' }}>
                      {phrase.sentiment > 0.3 ? sentimentIcons.positive :
                       phrase.sentiment < -0.3 ? sentimentIcons.negative :
                       sentimentIcons.neutral}
                    </Box>
                  }
                />
              ))}
            </Box>
          </Paper>
        </Grid>
      )}

      {sentiment.ai_insights && (
        <Grid item xs={12}>
          <Paper sx={{ p: 3, backgroundColor: '#f5f5f5' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Psychology sx={{ mr: 1, color: '#3F51B5' }} />
              <Typography variant="h6">
                AI İçgörüleri
              </Typography>
            </Box>
            <Typography variant="body1" paragraph>
              {sentiment.ai_insights.emotional_state}
            </Typography>
            {sentiment.ai_insights.recommendations && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Öneriler:
                </Typography>
                <ul>
                  {sentiment.ai_insights.recommendations.map((rec, idx) => (
                    <li key={idx}>
                      <Typography variant="body2">{rec}</Typography>
                    </li>
                  ))}
                </ul>
              </Box>
            )}
          </Paper>
        </Grid>
      )}
    </Grid>
  );

  const renderDetailed = () => (
    <Grid container spacing={3}>
      {sentiment.emotions && (
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Duygu Analizi
            </Typography>
            <Box sx={{ height: 300 }}>
              <Radar
                data={emotionRadarChart}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    r: {
                      beginAtZero: true,
                      max: 1
                    }
                  }
                }}
              />
            </Box>
          </Paper>
        </Grid>
      )}

      {sentiment.sentence_sentiments && (
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Cümle Bazlı Analiz
            </Typography>
            <Box sx={{ height: 300 }}>
              <Bar
                data={sentenceSentimentChart}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      max: 1,
                      min: -1
                    }
                  },
                  plugins: {
                    legend: {
                      display: false
                    }
                  }
                }}
              />
            </Box>
          </Paper>
        </Grid>
      )}

      {sentiment.sentence_sentiments && (
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Metin Analizi
            </Typography>
            {sentiment.sentence_sentiments.map((sent, idx) => (
              <Box key={idx} sx={{ mb: 2, p: 2, backgroundColor: '#f9f9f9', borderRadius: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Box sx={{ color: getScoreColor(sent.score), mr: 1 }}>
                    {sent.score > 0.3 ? sentimentIcons.positive :
                     sent.score < -0.3 ? sentimentIcons.negative :
                     sentimentIcons.neutral}
                  </Box>
                  <Typography variant="subtitle2">
                    Cümle {idx + 1} - Skor: {sent.score.toFixed(3)}
                  </Typography>
                </Box>
                <Typography variant="body2">
                  {sent.text}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      )}
    </Grid>
  );

  const renderTimeline = () => (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Paper sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h6">
              Duygu Durum Trendi
            </Typography>
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Zaman Aralığı</InputLabel>
              <Select
                value={timeRange}
                onChange={(e) => setTimeRange(e.target.value)}
              >
                <MenuItem value="week">Son 1 Hafta</MenuItem>
                <MenuItem value="month">Son 1 Ay</MenuItem>
                <MenuItem value="quarter">Son 3 Ay</MenuItem>
                <MenuItem value="year">Son 1 Yıl</MenuItem>
              </Select>
            </FormControl>
          </Box>

          {comparison && comparison.timeline && (
            <Box sx={{ height: 400 }}>
              <Line
                data={{
                  labels: comparison.timeline.map(point => 
                    new Date(point.date).toLocaleDateString('tr-TR')
                  ),
                  datasets: [{
                    label: 'Sentiment Skoru',
                    data: comparison.timeline.map(point => point.score),
                    borderColor: '#3F51B5',
                    backgroundColor: 'rgba(63, 81, 181, 0.1)',
                    tension: 0.4,
                    fill: true
                  }]
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                      min: -1,
                      max: 1
                    }
                  },
                  plugins: {
                    legend: {
                      display: false
                    }
                  }
                }}
              />
            </Box>
          )}

          {comparison && comparison.summary && (
            <Grid container spacing={2} sx={{ mt: 3 }}>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Ortalama Skor
                  </Typography>
                  <Typography variant="h4" sx={{ color: getScoreColor(comparison.summary.average_score) }}>
                    {comparison.summary.average_score.toFixed(3)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    En Pozitif
                  </Typography>
                  <Typography variant="h4" sx={{ color: sentimentColors.positive }}>
                    {comparison.summary.highest_score.toFixed(3)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    En Negatif
                  </Typography>
                  <Typography variant="h4" sx={{ color: sentimentColors.negative }}>
                    {comparison.summary.lowest_score.toFixed(3)}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} md={3}>
                <Box sx={{ textAlign: 'center' }}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Trend
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    {comparison.summary.trend > 0 ? 
                      <TrendingUp sx={{ color: sentimentColors.positive, fontSize: 40 }} /> :
                      <TrendingDown sx={{ color: sentimentColors.negative, fontSize: 40 }} />
                    }
                  </Box>
                </Box>
              </Grid>
            </Grid>
          )}
        </Paper>
      </Grid>
    </Grid>
  );

  const renderView = () => {
    switch (viewMode) {
      case 'overview':
        return renderOverview();
      case 'detailed':
        return renderDetailed();
      case 'timeline':
        return renderTimeline();
      default:
        return renderOverview();
    }
  };

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" component="h2">
            Duygu Analizi
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Button
              variant={viewMode === 'overview' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('overview')}
              startIcon={<Analytics />}
              size="small"
            >
              Genel Bakış
            </Button>
            <Button
              variant={viewMode === 'detailed' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('detailed')}
              startIcon={<Psychology />}
              size="small"
            >
              Detaylı
            </Button>
            <Button
              variant={viewMode === 'timeline' ? 'contained' : 'outlined'}
              onClick={() => setViewMode('timeline')}
              startIcon={<Timeline />}
              size="small"
            >
              Zaman Çizgisi
            </Button>
            <Tooltip title="Yenile">
              <IconButton onClick={fetchSentimentData} size="small">
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {renderView()}
      </CardContent>
    </Card>
  );
};

export default SentimentAnalysis;