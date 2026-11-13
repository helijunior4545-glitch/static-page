# Studio Contact — Django

Model ContactMessage, formulário público com CSRF e caixa de entrada para equipe.
Usa exclusivamente PostgreSQL via DATABASE_URL. Não contém credenciais nem SQLite.
As tabelas da versão anterior com psycopg direto não são apagadas nem importadas.
O novo model usa a tabela contacts_contactmessage.

## Instalação no computador

python3 py.py --install
source .venv/bin/activate

O instalador faz backup dos arquivos substituídos em .installer-backups/.
Defina SECRET_KEY, DATABASE_URL e ALLOWED_HOSTS no ambiente antes de executar Django.
Para HTTP local apenas: DEBUG=true. Não use DEBUG=true na publicação.
O instalador não cria banco, usuário nem executa migrations.

## Studio

Aplicação web; raiz do repositório; build vazio; porta 8000; health check /healthz.
Inicialização: python py.py
A imagem aprovada precisa conter Django 5.2, psycopg 3.3.2 e gunicorn 23.
requirements.txt não é instalado automaticamente pelo runtime offline.

Variáveis obrigatórias:
- SECRET_KEY: valor aleatório secreto, gerado e armazenado nas variáveis do app.
- DATABASE_URL: fornecida pelo provisionamento exclusivo do Studio.
- ALLOWED_HOSTS: hostname público do app, sem https://, separado por vírgula se necessário.
- CSRF_TRUSTED_ORIGINS: origem HTTPS pública completa do app.
- TRUST_PROXY_HTTPS=true apenas com proxy confiável que substitua X-Forwarded-Proto.

## Migrações e equipe

A migração contacts/migrations/0001_initial.py já está versionada.
Preparação do banco (no runtime, depois do provisionamento): python manage.py migrate --noinput
Criação da conta da aplicação: python manage.py createsuperuser
Essa conta só administra este app; não é o superuser da plataforma LojasNova.
Também é possível criar uma conta is_staff sem privilégios de superuser.
Não versionar senhas, dumps, .env ou .venv.

Comandos adicionais: python py.py check / python py.py migrate --noinput
Desenvolvimento: python py.py runserver 127.0.0.1:8000
Testes (banco exclusivo de testes): python manage.py test contacts
O servidor padrão usa Gunicorn, escuta em 0.0.0.0 e não executa migrations sozinho.
O painel ainda precisa oferecer a etapa de migrate e criação segura da primeira conta.
Antes de tráfego público amplo, configurar rate limiting do login e antispam no proxy.
