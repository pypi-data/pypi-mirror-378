"""add ldap bind user

Peek Plugin Database Migration Script

Revision ID: b78f1d04341a
Revises: bc55dc1de80a
Create Date: 2025-09-07 15:12:30.515528

"""

# revision identifiers, used by Alembic.
revision = "b78f1d04341a"
down_revision = "bc55dc1de80a"
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade():
    # Add service account credentials for email lookups
    op.add_column(
        "LdapSetting",
        sa.Column("ldapServiceUsername", sa.String(), nullable=True),
        schema="core_user",
    )
    op.add_column(
        "LdapSetting",
        sa.Column("ldapServicePassword", sa.String(), nullable=True),
        schema="core_user",
    )

    # Add email authentication setting
    op.add_column(
        "LdapSetting",
        sa.Column(
            "allowEmailLogin", sa.Boolean(), nullable=False, server_default="0"
        ),
        schema="core_user",
    )


def downgrade():
    op.drop_column("LdapSetting", "allowEmailLogin", schema="core_user")
    op.drop_column("LdapSetting", "ldapServicePassword", schema="core_user")
    op.drop_column("LdapSetting", "ldapServiceUsername", schema="core_user")
