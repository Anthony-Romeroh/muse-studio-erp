# 🚀 Instruções de Deploy - Muse Studio ERP

## Opções de Deploy Gratuito

### 1️⃣ **Render.com** (Recomendado - Gratuito com pausa automática)
**Passo a passo:**

1. Acesse https://render.com
2. Sign up com sua conta GitHub
3. Clique em "New" → "Web Service"
4. Conecte seu repositório `muse-studio-erp`
5. Preencha:
   - **Name**: `muse-studio-erp`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Deploy automático ao fazer push para `main`

**Link gerado**: `https://seu-projeto.onrender.com`

---

### 2️⃣ **Railway.app** (Gratuito - $5/mês de crédito)
**Passo a passo:**

1. Acesse https://railway.app
2. Sign up com GitHub
3. Clique em "New Project" → "Deploy from GitHub repo"
4. Selecione `muse-studio-erp`
5. Railway detecta automaticamente (Python Flask)
6. Configurar variável `PORT=8000`

**Link gerado**: `https://seu-projeto-nome.railway.app`

---

### 3️⃣ **Heroku** (Gratuito, precisa reativar)
⚠️ *Nota: Heroku descontinuou plano free em 2022, mas você pode usar alternativas acima*

---

## 📋 Arquivos Necessários (Já Adicionados)

✅ `Procfile` - Define como rodar a aplicação  
✅ `runtime.txt` - Especifica versão Python  
✅ `.github/workflows/deploy.yml` - Automação CI/CD  

---

## 🔐 Variáveis de Ambiente

Se seu app usar `.env`, configure no painel da plataforma:

```
SECRET_KEY=sua_chave_secreta
DATABASE_URL=postgresql://seu-db
```

---

## ✅ Checklist Antes do Deploy

- [x] `requirements.txt` atualizado
- [x] `app.py` com `if __name__ == '__main__'`
- [x] Banco de dados configurado (SQLite local ou externa)
- [x] Git atualizado com `git push origin main`

---

## 🧪 Testar Localmente

```bash
pip install gunicorn
gunicorn app:app
```

Abra: http://localhost:8000/admin

---

## 📞 Suporte

Qualquer dúvida, acesse:
- Render: https://render.com/docs
- Railway: https://docs.railway.app
- Muse Studio: https://github.com/Anthony-Romeroh/muse-studio-erp
