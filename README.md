# 🚀 Automotizador de Login - Sistema Inteligente v2.0

[![Versão](https://img.shields.io/badge/Versão-2.0-brightgreen.svg)](https://github.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Licença](https://img.shields.io/badge/Licença-MIT-green.svg)](LICENSE)

**Sistema profissional de automação de login com validação avançada e interface intuitiva.**

---

## 📁 Estrutura do Projeto

```
automatizador-login/
├── 📂 config/           # Configurações e dependências
│   ├── config.ini       # Configurações do usuário
│   ├── config_exemplo.ini # Template de configuração
│   └── requirements.txt # Dependências Python
├── 📂 docs/            # Documentação completa
│   ├── README.md       # Esta documentação
│   └── ...             # Guias e manuais
├── 📂 scripts/         # Scripts de execução e instalação
│   ├── executar.bat    # Inicializador principal (Windows)
│   ├── executar.ps1    # Inicializador PowerShell
│   └── install.bat     # Instalador de dependências
├── 📂 src/             # Código fonte principal
│   ├── __init__.py     # Pacote Python
│   ├── gui.py          # Interface gráfica profissional
│   ├── login_automator.py # Motor de automação inteligente
│   ├── run.py          # Inicializador da interface
│   └── ...             # Outros módulos
├── 📂 tests/           # Testes automatizados
└── 📂 logs/            # Arquivos de log
    └── automator.log   # Logs de execução
```

---

## 🎯 Funcionalidades Principais

### ✅ **Sistema de Validação Avançada**
- Análise completa de páginas web
- Detecção inteligente de elementos HTML
- Validação de estruturas e compatibilidade
- Análise de palavras-chave de login

### ✅ **Detecção Inteligente de Campos**
- **5 estratégias diferentes** de detecção automática
- Suporte a diferentes layouts de formulários
- Fallback robusto para casos complexos
- Adaptação automática a sites variados

### ✅ **Fluxo de 8 Fases Estruturado**
1. **Validação inicial** das configurações
2. **Configuração profissional** do navegador
3. **Acesso controlado** à página de login
4. **Validação completa** da página carregada
5. **Detecção inteligente** dos campos
6. **Preenchimento automático** do formulário
7. **Submissão profissional** do formulário
8. **Verificação de sucesso** com indicadores

### ✅ **Modo Híbrido Adaptativo**
- Detecção automática de falhas parciais
- Execução inteligente do possível
- Orientação clara para conclusão manual
- Controle de tempo otimizado

### ✅ **Agendamento Automático**
- Baseado no horário do sistema local
- Execução periódica programada
- Monitoramento em tempo real
- Logs detalhados de cada execução

---

## 🚀 Instalação Rápida

### **Pré-requisitos**
- Windows 10/11
- Python 3.11+ (instalado em `C:\Python311`)

### **Instalação Automática**
```bash
# 1. Executar instalador
scripts/install.bat

# 2. Configurar sistema
executar.bat
```

### **Instalação Manual**
```bash
# 1. Instalar Python
winget install --id Python.Python.3.11 --location "C:\Python311"

# 2. Instalar dependências
C:\Python311\python.exe -m pip install -r config/requirements.txt

# 3. Configurar e executar
executar.bat
```

---

## 🎮 Como Usar

### **1. Configuração Inicial**
```bash
executar.bat
```
- Configure URL, e-mail e senha
- Teste a configuração
- Mapeie campos automaticamente

### **2. Teste do Sistema**
- **Testar Configuração**: Valida dados inseridos
- **Executar Login**: Teste completo automatizado
- **Analisar Resultados**: Ver logs detalhados

### **3. Agendamento Automático**
- Configure horários desejados
- Inicie o agendador automático
- Monitore execuções em tempo real

---

## 🏗️ Arquitetura Técnica

### **Camadas do Sistema**
```
🎨 Interface (gui.py)
   ├── Interface gráfica profissional
   ├── Feedback visual em tempo real
   └── Controles intuitivos

🧠 Lógica de Negócios (login_automator.py)
   ├── Motor de automação inteligente
   ├── Validação avançada de páginas
   └── Detecção multi-estratégia

💾 Persistência (config/, logs/)
   ├── Configurações estruturadas
   ├── Logs com timestamps
   └── Histórico de execuções
```

### **Fluxo de Funcionamento**
```
Configuração → Validação → Detecção → Execução → Verificação
     ↓           ↓         ↓         ↓          ↓
   Interface → Análise → Campos → Login → Sucesso/Falha
```

---

## 📊 Características Técnicas

| Recurso | Status | Descrição |
|---------|--------|-----------|
| **Interface Gráfica** | ✅ Completa | Tkinter profissional com 2 painéis |
| **Validação Avançada** | ✅ Implementada | Análise completa de páginas HTML |
| **Detecção Inteligente** | ✅ 5 Estratégias | Múltiplos métodos de busca |
| **Modo Híbrido** | ✅ Adaptativo | Fallback inteligente |
| **Agendamento** | ✅ Automático | Baseado em horário do sistema |
| **Logs Estruturados** | ✅ Profissionais | Níveis e timestamps |
| **Documentação** | ✅ Completa | Guias e manuais técnicos |

---

## 🔧 Configuração Avançada

### **Arquivo config.ini**
```ini
[SITE]
url = https://exemplo.com/login
email_field_selector = input[type="email"]
password_field_selector = input[type="password"]
login_button_selector = button[type="submit"]

[CREDENTIALS]
email = seu@email.com
password = sua_senha

[SETTINGS]
headless = false
wait_timeout = 10
```

### **Seletores CSS Suportados**
- `input[type="email"]` - Campo de e-mail
- `input[type="password"]` - Campo de senha
- `button[type="submit"]` - Botão de submit
- `input[name="usuario"]` - Campo por nome
- `.btn-login` - Classe específica

---

## 🐛 Solução de Problemas

### **Problemas Comuns**

**❌ "Python não encontrado"**
```bash
# Instalar Python no local correto
winget install --id Python.Python.3.11 --location "C:\Python311"
```

**❌ "Módulo não encontrado"**
```bash
# Instalar dependências
scripts/install.bat
```

**❌ "Campo não detectado"**
- Use o botão "Mapear Campos"
- Verifique se a página carregou completamente
- Teste com diferentes URLs

### **Logs de Debug**
- Arquivo: `logs/automator.log`
- Níveis: INFO, WARNING, ERROR
- Timestamps completos

---

## 📈 Desenvolvimento

### **Estrutura de Código**
- **Módulos bem organizados** em pacotes Python
- **Documentação técnica** completa (docstrings)
- **Tratamento robusto** de exceções
- **Padrões de codificação** consistentes

### **Testes**
```bash
# Executar testes
python -m pytest tests/
```

### **Contribuição**
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 🤝 Suporte

- **Documentação**: Pasta `docs/`
- **Exemplos**: Arquivo `docs/EXEMPLO_PRATICO.txt`
- **Logs**: Arquivo `logs/automator.log`

---

## 🎯 Próximos Passos

- [ ] Suporte a múltiplos navegadores
- [ ] Interface web responsiva
- [ ] API REST para integração
- [ ] Suporte a CAPTCHA
- [ ] Dashboard de monitoramento

---

## 📞 Contato

**Sistema Automatizado de Login**
- Versão: 2.0.0
- Data: Dezembro 2025
- Status: ✅ **PRODUÇÃO**

---

**🚀 Sistema pronto para automação profissional de login!**
