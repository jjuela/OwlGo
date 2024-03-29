"""added reports

Revision ID: 5619e413423f
Revises: 
Create Date: 2023-12-05 21:30:01.447461

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '5619e413423f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user__report',
    sa.Column('report_id', sa.Integer(), nullable=False),
    sa.Column('reporter_id', sa.Integer(), nullable=False),
    sa.Column('reported_user_id', sa.Integer(), nullable=False),
    sa.Column('report_text', sa.Text(), nullable=True),
    sa.Column('report_timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['reported_user_id'], ['user.user_id'], ),
    sa.ForeignKeyConstraint(['reporter_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('report_id')
    )
    op.create_table('ride__passenger',
    sa.Column('ride_id', sa.Integer(), nullable=False),
    sa.Column('passenger_id', sa.Integer(), nullable=False),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('is_driver', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['passenger_id'], ['user.user_id'], ),
    sa.ForeignKeyConstraint(['ride_id'], ['ride.ride_id'], ),
    sa.PrimaryKeyConstraint('ride_id', 'passenger_id')
    )
    op.create_table('ride__report',
    sa.Column('report_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('ride_id', sa.Integer(), nullable=False),
    sa.Column('report_text', sa.Text(), nullable=True),
    sa.Column('report_timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['ride.ride_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('report_id')
    )
    op.create_table('ride__request',
    sa.Column('ride_id', sa.Integer(), nullable=False),
    sa.Column('passenger_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('role', sa.String(length=10), nullable=True),
    sa.Column('commute_days', sa.String(length=50), nullable=True),
    sa.Column('accessibility', sa.String(length=100), nullable=True),
    sa.Column('custom_message', sa.String(length=500), nullable=True),
    sa.Column('requested_stops', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['passenger_id'], ['user.user_id'], ),
    sa.ForeignKeyConstraint(['ride_id'], ['ride.ride_id'], ),
    sa.PrimaryKeyConstraint('ride_id', 'passenger_id')
    )
    op.drop_table('post')
    op.drop_table('ride_report')
    op.drop_table('user_report')
    op.drop_table('ride_passenger')
    op.drop_table('ride_request')
    with op.batch_alter_table('announcement', schema=None) as batch_op:
        batch_op.drop_column('announcement_date')

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.alter_column('recipient_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.create_foreign_key(None, 'user', ['recipient_id'], ['user_id'])

    with op.batch_alter_table('rating', schema=None) as batch_op:
        batch_op.alter_column('recipient_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.alter_column('cleanliness',
               existing_type=mysql.TINYINT(unsigned=True),
               type_=sa.SmallInteger(),
               existing_nullable=True)
        batch_op.alter_column('punctuality',
               existing_type=mysql.TINYINT(unsigned=True),
               type_=sa.SmallInteger(),
               existing_nullable=True)
        batch_op.alter_column('safety',
               existing_type=mysql.TINYINT(unsigned=True),
               type_=sa.SmallInteger(),
               existing_nullable=True)
        batch_op.alter_column('communication',
               existing_type=mysql.TINYINT(unsigned=True),
               type_=sa.SmallInteger(),
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'user', ['recipient_id'], ['user_id'])

    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.alter_column('recipient_id',
               existing_type=mysql.INTEGER(),
               nullable=False)
        batch_op.create_foreign_key(None, 'user', ['recipient_id'], ['user_id'])

    with op.batch_alter_table('ride', schema=None) as batch_op:
        batch_op.drop_column('end_date')
        batch_op.drop_column('start_date')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ride', schema=None) as batch_op:
        batch_op.add_column(sa.Column('start_date', sa.DATE(), nullable=True))
        batch_op.add_column(sa.Column('end_date', sa.DATE(), nullable=True))

    with op.batch_alter_table('review', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('recipient_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    with op.batch_alter_table('rating', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('communication',
               existing_type=sa.SmallInteger(),
               type_=mysql.TINYINT(unsigned=True),
               existing_nullable=True)
        batch_op.alter_column('safety',
               existing_type=sa.SmallInteger(),
               type_=mysql.TINYINT(unsigned=True),
               existing_nullable=True)
        batch_op.alter_column('punctuality',
               existing_type=sa.SmallInteger(),
               type_=mysql.TINYINT(unsigned=True),
               existing_nullable=True)
        batch_op.alter_column('cleanliness',
               existing_type=sa.SmallInteger(),
               type_=mysql.TINYINT(unsigned=True),
               existing_nullable=True)
        batch_op.alter_column('recipient_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    with op.batch_alter_table('message', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('recipient_id',
               existing_type=mysql.INTEGER(),
               nullable=True)

    with op.batch_alter_table('announcement', schema=None) as batch_op:
        batch_op.add_column(sa.Column('announcement_date', mysql.DATETIME(), nullable=True))

    op.create_table('ride_request',
    sa.Column('ride_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('passenger_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('timestamp', mysql.DATETIME(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.Column('role', mysql.VARCHAR(length=10), nullable=True),
    sa.Column('commute_days', mysql.VARCHAR(length=50), nullable=True),
    sa.Column('accessibility', mysql.VARCHAR(length=100), nullable=True),
    sa.Column('custom_message', mysql.VARCHAR(length=500), nullable=True),
    sa.Column('requested_stops', mysql.VARCHAR(length=100), nullable=True),
    sa.ForeignKeyConstraint(['passenger_id'], ['user.user_id'], name='ride_request_ibfk_2'),
    sa.ForeignKeyConstraint(['ride_id'], ['ride.ride_id'], name='ride_request_ibfk_1'),
    sa.PrimaryKeyConstraint('ride_id', 'passenger_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('ride_passenger',
    sa.Column('ride_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('passenger_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('confirmed', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.Column('is_driver', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['passenger_id'], ['user.user_id'], name='ride_passenger_ibfk_2'),
    sa.ForeignKeyConstraint(['ride_id'], ['ride.ride_id'], name='ride_passenger_ibfk_1'),
    sa.PrimaryKeyConstraint('ride_id', 'passenger_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('user_report',
    sa.Column('report_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('reporter_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('reported_user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('report_text', mysql.TEXT(), nullable=True),
    sa.Column('report_timestamp', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['reported_user_id'], ['user.user_id'], name='user_report_ibfk_2'),
    sa.ForeignKeyConstraint(['reporter_id'], ['user.user_id'], name='user_report_ibfk_1'),
    sa.PrimaryKeyConstraint('report_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('ride_report',
    sa.Column('report_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('ride_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('report_text', mysql.TEXT(), nullable=True),
    sa.Column('report_timestamp', mysql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['ride.ride_id'], name='ride_report_ibfk_2'),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='ride_report_ibfk_1'),
    sa.PrimaryKeyConstraint('report_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('post',
    sa.Column('post_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('ride_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('post_text', mysql.TEXT(), nullable=True),
    sa.Column('post_date', mysql.DATETIME(), nullable=True),
    sa.ForeignKeyConstraint(['ride_id'], ['ride.ride_id'], name='post_ibfk_2'),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='post_ibfk_1'),
    sa.PrimaryKeyConstraint('post_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('ride__request')
    op.drop_table('ride__report')
    op.drop_table('ride__passenger')
    op.drop_table('user__report')
    # ### end Alembic commands ###
