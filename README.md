# Studio Contact — Django, Docker e PostgreSQL externo

## Gerar o projeto

Coloque py.py na raiz do static-page e execute:

python3 py.py --write-only

Cria models, formulário, login da equipe, migração versionada, Dockerfile,
compose.yaml e compose.studio.yaml. Arquivos substituídos ganham backup em
.installer-backups/. Não instala Docker, não cria banco e não executa migrations.
`--install` também prepara .venv e instala requirements para desenvolvimento.
Não usar --install como comando de inicialização.

## Modo gerenciado do Studio LojasNova (fluxo atual)

Versionar os arquivos gerados e usar Aplicação web / perfil Django, raiz do repo,
start `python py.py`, porta 8000, health /healthz e marcar migrate antes de iniciar.
O painel injeta DATABASE_URL após provisionar banco exclusivo e verificar a rede.
SECRET_KEY é gerada pelo painel e as variáveis HTTPS podem ser ajustadas ali.
O Dockerfile/Compose do repositório não são executados por esse modo gerenciado.

## Docker ou Coolify administrado diretamente

Requer Docker com Compose v2 no computador/servidor. Para preparar configuração
local sem exibir a chave, execute `python3 py.py --configure-docker`.
Depois edite `.env` e preencha DATABASE_URL com o banco EXCLUSIVO da aplicação.
Nunca use a conexão administrativa do cluster nem o banco interno da LojasNova.
Não compartilhe .env e não o versione.

Para teste com banco externo acessível pela rede Docker:

docker compose up --build -d
docker compose logs -f app

Abra http://localhost:8088. No servidor, a porta fica em loopback; use proxy HTTPS
ou túnel SSH. Para domínio público no Coolify, associe o domínio ao serviço app,
porta interna 8000. Ajuste ALLOWED_HOSTS (hostname) e CSRF_TRUSTED_ORIGINS (origem
HTTPS) no gerenciador de variáveis. TRUST_PROXY_HTTPS=true somente com proxy
confiável que substitua X-Forwarded-Proto. Segredos são só de runtime, não build args.

No servidor Studio, a opção abaixo conecta à rede exclusiva JÁ preparada pelo
agente e usa o perfil seccomp instalado no host:

docker compose -f compose.yaml -f compose.studio.yaml up --build -d

Isso é uma alternativa administrativa de teste. Não iniciar outro app no mesmo
domínio controlado pelo Studio nem confundir com o modo gerenciado. Este override
não cria redes, não libera firewall e não conecta à rede compartilhada do banco.
O Compose base de desenvolvimento não impõe o firewall de saída do Studio.

A imagem instala Django 5.2.19, psycopg[binary] 3.3.2 e Gunicorn 23.0.0.
Em produção, construir em builder isolado e publicar uma imagem por digest; a base
python:3.13-slim deste Dockerfile de teste pode receber atualizações entre builds.
O app roda com UID 10001, código somente leitura, tmpfs, limite 512 MiB/0,5 CPU,
capabilities removidas e sem portas públicas diretas no Compose.

## Migrations, dados e equipe

O entrypoint Docker aplica `python manage.py migrate --noinput`, com timeout de
180 segundos e lock PostgreSQL, antes de iniciar Gunicorn. Falha impede o start.
Health só retorna 200 quando a tabela do model existe e pode ser consultada.
`makemigrations` é de desenvolvimento: 0001_initial.py já está incluída.
Reiniciar não apaga dados. Rollback de código não desfaz migrations nem dados.
As tabelas do backend Python antigo não são apagadas/importadas automaticamente.

A caixa de entrada fica em /equipe/, exige usuário is_staff do próprio app.
Criação administrativa, no modo Docker direto:

docker compose exec app python manage.py createsuperuser

É uma conta deste Django, não da plataforma LojasNova. No modo gerenciado, criar
essa primeira conta exige um fluxo administrativo separado, ainda não incluído
no painel. Não há senha padrão nem criação de superuser automática.

## Validação

1. Enviar mensagem pelo formulário e anotar protocolo.
2. Entrar em /equipe/ e conferir registro.
3. Reiniciar container e conferir protocolo novamente.
4. Testar /healthz.

Testes usam PostgreSQL descartável: `python manage.py test contacts`.
Backups, retenção de dados, rate limiting e antispam devem ser configurados na
infraestrutura antes de abrir a aplicação a tráfego amplo.
