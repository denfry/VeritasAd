"""migrate result fields to JSONB, add ad_segments / logo_embedding and GIN index

Revision ID: 013
Revises: 012
Create Date: 2026-06-07

Aligns the schema with the thesis (sec. 3.5):
- analyses result fields -> JSONB
- new analyses.ad_segments JSONB column (temporal NMS output)
- custom_brands.aliases -> TEXT[]; new custom_brands.logo_embedding FLOAT[]
- GIN index on analyses.detected_brands for fast containment queries

All schema changes are PostgreSQL-specific. On SQLite (local development) the
columns already exist as JSON via metadata.create_all / runtime sync, so this
migration is a no-op there.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "013"
down_revision = "012"
branch_labels = None
depends_on = None


# analyses columns that hold JSON documents and should become JSONB.
_JSON_COLUMNS = [
    "detected_brands",
    "detected_keywords",
    "disclosure_markers",
    "cta_matches",
    "commercial_urls",
    "erids",
    "promo_codes",
]


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        # SQLite/dev: ad_segments is added by _sync_sqlite_analysis_columns().
        return

    # 1. Convert existing JSON result fields to JSONB.
    for column in _JSON_COLUMNS:
        op.execute(
            f'ALTER TABLE analyses ALTER COLUMN {column} TYPE jsonb '
            f'USING {column}::jsonb'
        )

    # 2. New temporal-NMS output column.
    op.add_column(
        "analyses",
        sa.Column("ad_segments", postgresql.JSONB(), nullable=True),
    )

    # 3. GIN index on detected_brands for containment / key lookups.
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_analyses_detected_brands_gin "
        "ON analyses USING gin (detected_brands)"
    )

    # 4. custom_brands.aliases JSON -> TEXT[].
    op.execute(
        "ALTER TABLE custom_brands ALTER COLUMN aliases TYPE text[] USING ("
        "CASE WHEN aliases IS NULL THEN NULL "
        "ELSE ARRAY(SELECT jsonb_array_elements_text(aliases::jsonb)) END)"
    )

    # 5. New 512-dim CLIP logo embedding column.
    op.add_column(
        "custom_brands",
        sa.Column(
            "logo_embedding",
            postgresql.ARRAY(sa.Float()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    op.drop_column("custom_brands", "logo_embedding")
    op.execute(
        "ALTER TABLE custom_brands ALTER COLUMN aliases TYPE jsonb USING to_jsonb(aliases)"
    )
    op.execute("DROP INDEX IF EXISTS ix_analyses_detected_brands_gin")
    op.drop_column("analyses", "ad_segments")
    for column in _JSON_COLUMNS:
        op.execute(
            f'ALTER TABLE analyses ALTER COLUMN {column} TYPE json '
            f'USING {column}::json'
        )
