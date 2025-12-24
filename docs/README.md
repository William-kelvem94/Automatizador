# Automatizador de Login

Este programa automatiza o processo de login em sites web, executando logins em horários específicos configurados pelo usuário.

## Funcionalidades

- ✅ Mapeamento automático dos campos de login
- ✅ Agendamento baseado no horário do computador
- ✅ Execução automática em horários configurados
- ✅ Logs detalhados das operações
- ✅ Interface interativa e linha de comando

## Requisitos

- Python 3.7+
- Google Chrome instalado
- Conexão com internet

## Instalação

### Instalação Automática (Recomendado)

1. **Instalar Python no disco C:**
```bash
winget install --id Python.Python.3.11 --location "C:\Python311"
```

2. **Executar o instalador:**
```bash
install.bat
```

### Instalação Manual

1. Instale Python 3.9+ do site oficial: https://www.python.org/downloads/

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `config.ini` com suas informações:
   - URL do site de login
   - Seletor CSS dos campos (ou use o mapeamento automático)
   - Credenciais de login
   - Horários desejados

## Configuração

Edite o arquivo `config.ini`:

```ini
[SITE]
url = https://exemplo.com/login
email_field_selector = #email
password_field_selector = #password
login_button_selector = .btn-login

[CREDENTIALS]
email = seu_email@exemplo.com
password = sua_senha

[SCHEDULE]
# Horários no formato HH:MM (24h), separados por vírgula
horarios = 08:00, 12:00, 18:00, 22:00

[SETTINGS]
# Executar em modo headless (sem interface gráfica)
headless = false
# Tempo de espera em segundos
wait_timeout = 10
```

## 🎮 Como Usar - Super Fácil!

### 🚀 Método Mais Fácil: Interface Gráfica

1. **Clique duplo** no arquivo `executar.bat`
2. **Aguarde** a janela abrir (leva alguns segundos)
3. **Configure** na aba "⚙️ Configuração":
   - 🌐 URL do site de login
   - 📧 Seu e-mail
   - 🔒 Sua senha (oculta na tela)
   - ⏰ Horários desejados (ex: 08:00, 12:00, 18:00, 22:00)
4. **Clique** "💾 Salvar Configuração"
5. **Teste** na aba "🧪 Teste" - veja o navegador abrir e fazer login!
6. **Agende** na aba "⏰ Agendamento" para execuções automáticas

### ✨ Funcionalidades da Interface:

#### ⚙️ Aba Configuração
- **Campos visuais** para todas as configurações
- **Validação automática** dos horários (HH:MM)
- **Mapeamento automático** dos campos do site
- **Salvamento automático** das configurações

#### 🧪 Aba Teste
- **Teste real** - abre Chrome e executa login completo
- **Logs em tempo real** do processo
- **Verificação visual** se funcionou ou não

#### ⏰ Aba Agendamento
- **Controle total** do agendador (iniciar/parar/reiniciar)
- **Status visual** (🟢 executando 🔴 parado)
- **Logs detalhados** de todas as execuções
- **Próxima execução** mostrada

### 🎯 Execução Super Fácil (Interface Gráfica)

**Basta executar:**
```bash
executar.bat
```

**ou**

**Clique duplo no arquivo `executar.bat`**

---

### ✨ O Que Acontece:

1. **Uma janela bonita se abre** com interface gráfica completa
2. **3 abas principais:**
   - **⚙️ Configuração** - Configure URL, email, senha e horários
   - **🧪 Teste** - Teste o login e veja o navegador abrir
   - **⏰ Agendamento** - Configure execuções automáticas

3. **Funcionalidades:**
   - ✅ **Interface intuitiva** - Tudo visual e fácil
   - ✅ **Navegador real** - Abre Chrome e faz login de verdade
   - ✅ **Configuração salva** - Não precisa reconfigurar sempre
   - ✅ **Logs em tempo real** - Veja exatamente o que está acontecendo
   - ✅ **Agendamento automático** - Executa nos horários programados

---

### 🔧 Comandos Avançados (Opcional)

Para usuários avançados, ainda existem os comandos de linha:

```bash
executar.bat --map        # Mapear campos automaticamente
executar.bat --test       # Testar login via linha de comando
executar.bat --schedule   # Agendador via linha de comando
```

### Execução Direta

```bash
C:\Python311\python.exe main.py --help
```

### Mapeamento Automático dos Campos

Se você não sabe os seletores CSS dos campos, use o mapeamento automático:

```bash
executar.bat --map
```

Ou através do menu interativo - opção 2.

### Teste de Login

Para testar se o login funciona:

```bash
executar.bat --test
```

Ou através do menu interativo - opção 3.

### Agendamento Automático

Para iniciar o agendador que executará logins nos horários configurados:

```bash
executar.bat --schedule
```

Ou através do menu interativo - opção 4.

O programa ficará executando em segundo plano. Use Ctrl+C para parar.

## Comandos Disponíveis

### Menu Interativo (executar.bat)
- `executar.bat` - Menu completo com 6 opções
- Opção 1: Configurar login (URL, email, senha, horários)
- Opção 2: Mapear campos automaticamente
- Opção 3: Testar login único
- Opção 4: Iniciar agendador automático
- Opção 5: Ver configurações atuais
- Opção 6: Sair

### Comandos Diretos
- `executar.bat --map` - Mapear campos automaticamente
- `executar.bat --test` - Testar login único
- `executar.bat --schedule` - Iniciar agendador automático

### Linha de Comando
- `C:\Python311\python.exe main.py --help` - Ver ajuda
- `C:\Python311\python.exe main.py --config config.ini` - Usar arquivo específico

## Logs

Os logs são salvos no arquivo `automator.log` com informações detalhadas sobre:
- Tentativas de login
- Sucessos e falhas
- Horários de execução
- Erros encontrados

---

## 📁 Arquivos Importantes

### 🎯 Arquivos Essenciais (Comece Aqui!)
- **`executar.bat`** - **CLIQUE AQUI PRIMEIRO!** Abre a interface gráfica completa
- **`EXEMPLO_PRATICO.txt`** - **LEIA ISTO!** Guia passo-a-passo completo
- **`PRONTO_PARA_TESTAR.txt`** - **STATUS ATUAL** do projeto

### 💻 Interface Gráfica Avançada
- **`gui.py`** - Interface inteligente com validação avançada
- **Funcionalidades:**
  - 🔍 Análise completa da página
  - 🎯 Detecção automática de campos
  - 🧪 Teste inteligente de login
  - ⏰ Agendamento automático

### ⚙️ Core com Validação Avançada
- **`login_automator.py`** - Motor inteligente com validação completa
- **Recursos:**
  - ✅ Validação de página antes do login
  - 🎯 Detecção inteligente de campos
  - 🔄 Modo híbrido automático
  - 📊 Análise detalhada de elementos

### 📦 Instalação e Dependências
- **`install.bat`** - Instalação automática completa
- **`requirements.txt`** - Todas as bibliotecas necessárias

### 🔧 Configurações e Utilitários
- **`config.ini`** - Suas configurações salvas automaticamente
- **`config_exemplo.ini`** - Exemplos de configuração
- **`inspecionar_site.py`** - Ferramenta de análise de página
- **`teste_login.py`** - Teste direto do automatizador

### 📊 Logs e Documentação
- **`automator.log`** - Logs detalhados de todas as operações
- **`VALIDACAO_AVANCADA.md`** - **NOVO!** Documentação das validações
- **`README.md`** - Esta documentação completa

## Segurança

⚠️ **IMPORTANTE:**
- Suas credenciais são armazenadas em texto plano no `config.ini`
- Mantenha este arquivo seguro e não o compartilhe
- Considere usar variáveis de ambiente para credenciais em produção

## Resolução de Problemas

### Problemas Comuns:

1. **Driver do Chrome não encontrado**: O webdriver-manager deve instalar automaticamente
2. **Campos não encontrados**: Use a opção `--map` para mapeamento automático
3. **Login falhando**: Verifique os seletores CSS e credenciais
4. **Horários não funcionando**: Certifique-se do formato HH:MM correto

### Logs de Debug:

Verifique o arquivo `automator.log` para detalhes sobre erros.

## Exemplo de Uso Completo

1. Configure o `config.ini` com a URL do site
2. Execute mapeamento: `python main.py --map`
3. Teste o login: `python main.py --test`
4. Configure os horários desejados
5. Inicie o agendador: `python main.py --schedule`

O programa agora executará logins automaticamente nos horários configurados!
