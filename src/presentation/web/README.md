# Automator Web UI

Interface Web React/Next.js para o Automatizador IA v7.0

## 🚀 Funcionalidades

- **Dashboard Interativo**: Monitoramento em tempo real das tarefas
- **Gerenciamento de Tarefas**: Criar, executar e monitorar automações
- **Análise Visual**: Gráficos e métricas de performance
- **Workflow Designer**: Interface visual para criar fluxos de automação
- **Real-time Updates**: Notificações em tempo real via WebSocket

## 🛠️ Tecnologias

- **Next.js 14**: React Framework
- **TypeScript**: Type Safety
- **Material-UI**: Componentes UI
- **React Query**: State Management
- **Tailwind CSS**: Styling
- **React Flow**: Workflow Designer
- **Socket.io**: Real-time Communication

## 📦 Instalação

```bash
# Instalar dependências
npm install

# Ou com yarn
yarn install
```

## 🚀 Execução

```bash
# Desenvolvimento
npm run dev

# Build para produção
npm run build

# Executar em produção
npm start
```

## 🔧 Configuração

### Variáveis de Ambiente (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### API Endpoints

A aplicação se conecta com a API FastAPI em `http://localhost:8000` por padrão.

## 📁 Estrutura

```
web/
├── pages/              # Páginas Next.js
│   ├── _app.tsx       # App principal
│   ├── index.tsx      # Dashboard
│   └── api/           # API Routes (se necessário)
├── components/        # Componentes reutilizáveis
├── hooks/            # Custom hooks
├── lib/              # Utilitários
├── styles/           # CSS global
└── types/            # TypeScript types
```

## 🎨 UI/UX

### Tema Dark
- Paleta de cores profissional
- Design system consistente
- Componentes acessíveis
- Responsividade mobile-first

### Dashboard
- Métricas em tempo real
- Status visual das tarefas
- Gráficos de performance
- Notificações toast

## 🔌 APIs Utilizadas

### REST API
- `GET /tasks` - Listar tarefas
- `POST /tasks` - Criar tarefa
- `POST /tasks/{id}/execute` - Executar tarefa
- `POST /analyze` - Analisar página

### WebSocket
- Conexão real-time para atualizações
- Notificações de execução
- Status de tarefas

## 🧪 Desenvolvimento

```bash
# Type checking
npm run type-check

# Linting
npm run lint

# Testes (quando implementados)
npm test
```

## 🚀 Deploy

### Vercel (Recomendado)
```bash
npm i -g vercel
vercel --prod
```

### Docker
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 📱 Mobile Support

A aplicação é responsiva e funciona em:
- Desktop (Chrome, Firefox, Safari, Edge)
- Tablet (iOS, Android)
- Mobile (Progressive Web App)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.
