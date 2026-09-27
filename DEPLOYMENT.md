# 🚀 Deployment Vercel + Supabase

Guia completo para fazer deploy do Muse Studio ERP.

## **PASSO 1: Configurar Supabase (PostgreSQL)**

### 1.1 Criar conta no Supabase
1. Vai para https://supabase.com
2. Clica em **Sign Up**
3. Registra com GitHub (recomendado)

### 1.2 Criar novo projeto
1. Clica em **New Project**
2. Nome: `muse-studio-erp`
3. Database Password: salva em lugar seguro
4. Region: escolhe mais próxima

### 1.3 Obter Connection String
1. Vai para **Settings** → **Database**
2. Copia a **Connection String** (modo URI)
3. Substitui `[YOUR-PASSWORD]` com a senha do database

Exemplo:
```
postgresql://postgres:[PASSWORD]@[HOST].supabase.co:5432/postgres?sslmode=require
```

---

## **PASSO 2: Configurar Vercel**

### 2.1 Conectar GitHub
1. Vai para https://vercel.com
2. Clica em **New Project**
3. Importa o repositório GitHub

### 2.2 Configurar Environment Variables
Na tela de configuração, adiciona:

| Variável | Valor |
|----------|-------|
| `DATABASE_URL` | Connection string do Supabase |
| `SECRET_KEY` | Gera uma chave segura (mínimo 32 caracteres) |
| `FLASK_ENV` | `production` |

Para gerar SECRET_KEY segura:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 2.3 Deploy
1. Clica em **Deploy**
2. Aguarda o build completar
3. Copia a URL do deploy

---

## **PASSO 3: Verificar Deploy**

Acessa a URL do Vercel:
```
https://seu-projeto.vercel.app/admin
```

Login:
- **Usuario:** admin
- **Contraseña:** admin123

---

## **PASSO 4: Inicializar Banco de Dados**

Se o banco vem vazio, acessa a URL com `/init`:
```
https://seu-projeto.vercel.app/init
```

Isso vai criar todas as tabelas.

---

## **Variáveis de Ambiente Necessárias**

```env
# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/postgres?sslmode=require

# Flask Security
SECRET_KEY=seu-chave-secreta-aqui-minimo-32-caracteres

# Environment
FLASK_ENV=production
PORT=5000
```

---

## **Troubleshooting**

### ❌ "Connection refused"
- Verifica se o DATABASE_URL está correto
- Verifica se Supabase foi criar o projeto
- Aguarda alguns minutos (Supabase pode estar iniciando)

### ❌ "Table does not exist"
- Acessa `/init` para criar as tabelas
- Ou executa migrations se tiver

### ❌ "SECRET_KEY is missing"
- Adiciona SECRET_KEY na aba Environment Variables do Vercel

### ❌ Static files não carregam
- Verifica se `/static` folder existe no repositório
- Pode ser que precise fazer force push

---

## **Arquivos Importantes**

- `vercel.json` - Configuração do Vercel
- `wsgi.py` - Entry point para Vercel
- `.env.example` - Exemplo de variáveis
- `requirements.txt` - Dependências

---

## **Próximos Passos**

1. ✅ Deploy para Vercel
2. ✅ Conectar Supabase
3. ✅ Teste o login
4. ✅ Carregue dados (opcional)
5. ✅ Configure domínio customizado (opcional)

---

**Sucesso! 🎉**

Se tiver problemas, verifica os logs no Vercel Dashboard.
