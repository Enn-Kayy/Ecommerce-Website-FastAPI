from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from typing import Union, Sequence

# revision identifiers, used by Alembic.
revision: str = 'de7f908db0f8'
down_revision: Union[str, Sequence[str], None] = '8bc46270e940'
branch_labels = None
depends_on = None

def upgrade():
    # ✅ Rename order_id → id if exists (safe for Postgres)
    with op.batch_alter_table('orders', schema=None) as batch_op:
        batch_op.alter_column('order_id', new_column_name='id')

    # ✅ Add missing columns if not exist
    op.add_column('orders', sa.Column('total_amount', sa.Numeric(), server_default='0'))
    op.add_column('orders', sa.Column('status', sa.String(), server_default='pending'))
    op.add_column('orders', sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()))

    # ✅ Fix order_items FK
    with op.batch_alter_table('order_items', schema=None) as batch_op:
        batch_op.drop_constraint('order_items_order_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'order_items_order_id_fkey',
            'orders',
            ['order_id'],
            ['id'],
            ondelete="CASCADE"
        )


def downgrade():
    pass
