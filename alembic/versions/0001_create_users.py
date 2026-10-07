"""HU05-T03-API: crear users conforme al diccionario de datos."""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_users"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("nombre", sa.String(120), nullable=False),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("rol", sa.String(13), nullable=False),
        sa.Column("activo", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
        sa.UniqueConstraint("correo", name="uq_users_correo"),
        sa.CheckConstraint("length(btrim(nombre)) > 0", name=op.f("ck_users_nombre_no_vacio")),
        sa.CheckConstraint("length(btrim(correo)) > 0", name=op.f("ck_users_correo_no_vacio")),
        sa.CheckConstraint("correo = lower(btrim(correo))", name=op.f("ck_users_correo_normalizado")),
        sa.CheckConstraint("length(btrim(password_hash)) > 0", name=op.f("ck_users_hash_no_vacio")),
        sa.CheckConstraint("rol IN ('CIUDADANO', 'VOLUNTARIO', 'ENTIDAD', 'ADMINISTRADOR')", name=op.f("ck_users_rol_valido")),
    )


def downgrade():
    op.drop_table("users")
