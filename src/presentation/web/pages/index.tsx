import { useState, useEffect } from 'react'
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  Box,
  Chip,
  LinearProgress,
  Alert
} from '@mui/material'
import {
  PlayArrow,
  Add,
  Analytics,
  Settings,
  CheckCircle,
  Error,
  Pending
} from '@mui/icons-material'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import axios from 'axios'
import toast from 'react-hot-toast'

// API base URL - em produção viria de env
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Types
interface Task {
  id: string
  name: string
  status: string
  success_rate: number
  created_at: string
}

interface HealthStatus {
  status: string
  services: Record<string, string>
  timestamp: string
}

export default function Dashboard() {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null)
  const queryClient = useQueryClient()

  // Queries
  const { data: tasks, isLoading: tasksLoading, error: tasksError } = useQuery<Task[]>(
    'tasks',
    async () => {
      const response = await axios.get(`${API_BASE}/tasks`)
      return response.data
    },
    {
      refetchInterval: 5000, // Atualiza a cada 5 segundos
    }
  )

  const { data: health, isLoading: healthLoading } = useQuery<HealthStatus>(
    'health',
    async () => {
      const response = await axios.get(`${API_BASE}/health`)
      return response.data
    },
    {
      refetchInterval: 30000, // Atualiza a cada 30 segundos
    }
  )

  // Mutations
  const executeTaskMutation = useMutation(
    async (taskId: string) => {
      const response = await axios.post(`${API_BASE}/tasks/${taskId}/execute`)
      return response.data
    },
    {
      onSuccess: (data) => {
        toast.success(`Tarefa executada: ${data.message}`)
        queryClient.invalidateQueries('tasks')
      },
      onError: (error: any) => {
        toast.error(`Erro na execução: ${error.response?.data?.detail || error.message}`)
      },
    }
  )

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle color="success" />
      case 'failed':
        return <Error color="error" />
      case 'running':
        return <Pending color="warning" />
      default:
        return <Pending color="default" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'error'
      case 'running':
        return 'warning'
      default:
        return 'default'
    }
  }

  const handleExecuteTask = async (task: Task) => {
    if (task.status === 'running') {
      toast.error('Tarefa já está em execução')
      return
    }

    executeTaskMutation.mutate(task.id)
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom>
          Automator Web IA v7.0
        </Typography>
        <Typography variant="h6" color="text.secondary">
          Dashboard de Controle e Monitoramento
        </Typography>
      </Box>

      {/* Health Status */}
      {health && (
        <Alert
          severity={health.status === 'healthy' ? 'success' : health.status === 'degraded' ? 'warning' : 'error'}
          sx={{ mb: 3 }}
        >
          <Typography variant="body2">
            Status do Sistema: {health.status.toUpperCase()}
            {health.services && (
              <span> | Serviços: {Object.entries(health.services).map(([service, status]) =>
                `${service}: ${status}`
              ).join(', ')}</span>
            )}
          </Typography>
        </Alert>
      )}

      {/* Quick Actions */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Ações Rápidas
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Button
                  variant="contained"
                  startIcon={<Add />}
                  fullWidth
                >
                  Nova Tarefa
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Analytics />}
                  fullWidth
                >
                  Análise de Página
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<Settings />}
                  fullWidth
                >
                  Configurações
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Estatísticas do Sistema
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="primary">
                    {tasks?.length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total de Tarefas
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="success.main">
                    {tasks?.filter(t => t.status === 'completed').length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Concluídas
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="warning.main">
                    {tasks?.filter(t => t.status === 'running').length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Em Execução
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="h4" color="error.main">
                    {tasks?.filter(t => t.status === 'failed').length || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Com Falha
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tasks List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Tarefas de Automação
          </Typography>

          {tasksLoading && <LinearProgress sx={{ mb: 2 }} />}

          {tasksError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              Erro ao carregar tarefas: {tasksError.message}
            </Alert>
          )}

          {!tasksLoading && tasks && tasks.length === 0 && (
            <Alert severity="info">
              Nenhuma tarefa encontrada. Clique em "Nova Tarefa" para começar.
            </Alert>
          )}

          <Grid container spacing={2}>
            {tasks?.map((task) => (
              <Grid item xs={12} md={6} lg={4} key={task.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                      {getStatusIcon(task.status)}
                      <Typography variant="h6" sx={{ ml: 1 }}>
                        {task.name}
                      </Typography>
                    </Box>

                    <Box sx={{ mb: 2 }}>
                      <Chip
                        label={task.status}
                        color={getStatusColor(task.status)}
                        size="small"
                      />
                    </Box>

                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Taxa de Sucesso: {task.success_rate.toFixed(1)}%
                    </Typography>

                    <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                      Criado em: {new Date(task.created_at).toLocaleString()}
                    </Typography>

                    <Button
                      variant="contained"
                      startIcon={<PlayArrow />}
                      fullWidth
                      onClick={() => handleExecuteTask(task)}
                      disabled={task.status === 'running' || executeTaskMutation.isLoading}
                    >
                      {task.status === 'running' ? 'Executando...' : 'Executar'}
                    </Button>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>
    </Container>
  )
}
