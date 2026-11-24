import sys
from os.path import abspath, dirname
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ajout de la racine du projet dans sys.path pour importer app
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from app.core.config import settings
from app.models import Base

# Configuration du logging Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Injection dynamique de l'URL de base de données depuis les variables d'environnement
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Métadonnées cibles pour la génération automatique de schémas
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Exécution des migrations en mode 'offline' (sans connexion active)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Exécution des migrations en mode 'online' (avec connexion à la base)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
