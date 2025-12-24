# 📁 LEGACY - Versões Anteriores (v6.x/v7.x)

Este diretório contém arquivos e documentação das versões anteriores do Automator Web IA que **não fazem parte** da arquitetura enterprise v8.0.

## 📋 Conteúdo

### 📖 Documentação (docs/)
- `EXEMPLO_PRATICO.txt` - Guia prático da versão anterior
- `INSTRUCOES_RAPIDAS.txt` - Instruções básicas
- `INSTRUCOES_TESTE.md` - Guia de testes
- `PRONTO_PARA_TESTAR.txt` - Status de prontidão

### ⚙️ Configuração (config/)
- `config_exemplo.ini` - Exemplo de configuração INI
- `config.ini` - Arquivo de configuração real (com credenciais - NÃO USAR)

### 🛠️ Scripts (scripts/)
- `install.bat` - Script de instalação para Windows
- `executar.ps1` - Script PowerShell para execução

## ⚠️ Importante

**Estes arquivos são LEGACY e não devem ser usados na versão 8.0 enterprise.**

### Diferenças Principais:
- **v6.x/v7.x**: Interface gráfica baseada em Tkinter/CustomTkinter com abas
- **v8.0**: Arquitetura enterprise com APIs REST/GraphQL, microservices, Kubernetes

### Funcionalidades Removidas:
- Interface gráfica desktop com abas
- Configuração via arquivos INI
- Scripts de instalação simples
- Dependência de interface visual

### Funcionalidades Adicionadas na v8.0:
- APIs REST e GraphQL enterprise
- Microservices architecture
- Kubernetes deployment
- Monitoring avançado (Prometheus/Grafana)
- Security enterprise (RBAC, encryption, audit)
- AI orchestration multi-model
- Auto-scaling e high availability

## 🔄 Migração

Para migrar de v7.x para v8.0:

1. **Backup**: Faça backup dos dados importantes
2. **Configuração**: Migre configurações INI para Pydantic models
3. **Deployment**: Use Docker Compose ou Kubernetes
4. **APIs**: Use as novas APIs REST/GraphQL
5. **Monitoring**: Configure Prometheus/Grafana

## 📞 Suporte

Para suporte com versões legacy, consulte a documentação específica de cada versão ou entre em contato com o time de desenvolvimento.

---

**🚀 Recomendamos fortemente a migração para a versão 8.0 enterprise para obter todas as funcionalidades avançadas e suporte de produção.**
