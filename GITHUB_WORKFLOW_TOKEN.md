# 🔧 ИНСТРУКЦИЯ: Добавление workflow scope к GitHub токену

## 🎯 Проблема:
GitHub требует специального **workflow scope** для изменения файлов в `.github/workflows/`

---

## ✅ Вариант 1: Обновить существующий токен (быстрее)

### Шаги:
1. **Зайдите на GitHub.com**
2. **Перейдите:** Click профиль (右上角) → Settings
3. **В меню слева:** Developer settings → Personal access tokens → Tokens (classic)
4. **Найдите ваш токен** в списке
5. **Click:** Редактировать (Edit)
6. **Добавьте галочку:** ✅ `workflow` (в разделе "repo")
7. **Click:** Update token

---

## ✅ Вариант 2: Создать новый токен (если не помните старый)

### Шаги:
1. **GitHub.com** → Profile → Settings
2. **Developer settings** → Personal access tokens → Tokens (classic)
3. **Click:** Generate new token (classic)
4. **Note:** Aurion OS Deployment
5. **Expiration:** 90 days (или No expiration)
6. **Выберите scopes:**
   - ✅ `repo` (все подпункты)
   - ✅ `workflow` (ВАЖНО!)
   - ✅ `read:org`
   - ✅ `user:email`
7. **Click:** Generate token
8. **Скопируйте токен** (показывается только один раз!)

---

## 🔄 После получения токена:

### Обновите токен локально:
```bash
# Mac/Linux
git remote set-url origin https://ВАШ_ТОКЕН@github.com/rooseve1t/aurion-backend.git

# Или используйте credential helper
git config --global credential.helper cache
git push origin main  # введите токен как пароль
```

### Для macOS Keychain:
```bash
# Удалить старый токен из Keychain
security delete-internet-password -s github.com -a rooseve1t

# Затем push с новым токеном
git push origin main
# Введите логин: rooseve1t
# Введите пароль: ВАШ_НОВЫЙ_ТОКЕН
```

---

## 🌐 Альтернатива: Загрузить через Web-интерфейс

Если не хотите возиться с токенами:

1. **Зайдите:** https://github.com/rooseve1t/aurion-backend
2. **Перейдите:** .github/workflows/ (создайте папки если нужно)
3. **Click:** Add file → Upload files
4. **Выберите файл:** `deploy.yml` с вашего компьютера
5. **Commit message:** "Add deployment workflow"
6. **Click:** Commit changes

---

## 📝 Содержимое файла deploy.yml (если нужно создать заново):

```yaml
name: Deploy Aurion OS

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python test_comprehensive.py
    
    - name: Deploy to production
      if: github.ref == 'refs/heads/main'
      run: |
        echo "🚀 Deploying Aurion OS..."
        # Добавьте команды деплоя
```

---

## ⚡ Быстрый фикс прямо сейчас:

**Через GitHub Web:**
1. Откройте: https://github.com/rooseve1t/aurion-backend/tree/main/.github/workflows
2. Нажмите **"Add file"** → **"Create new file"**
3. Имя файла: `deploy.yml`
4. Скопируйте содержимое выше
5. **Commit new file**

---

## ✅ Проверка после обновления токена:

```bash
cd /Users/natalacernikova/Downloads/aurion-stage13/aurion-backend
git push origin main
```

Должно работать без ошибок!

---

**Сэр, рекомендую Вариант 1 (обновить токен) - это быстрее всего! 🚀**
