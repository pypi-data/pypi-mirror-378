# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
CORE Office - datasync triggers
"""

import sqlalchemy as sa

from rattail.app import GenericHandler
from rattail_corepos.datasync.corepos import make_changes_table


class CoreTriggerHandler(GenericHandler):
    """
    Handler to install and show status of CORE DB triggers, for use
    with Rattail DataSync.
    """
    supported_triggers = [
        'custdata',
        'meminfo',
        'employees',
        'departments',
        'subdepts',
        'vendors',
        'products',
        'vendorItems',
    ]

    def show_status(self, op_session, table_name):
        """
        Show trigger status for an ``office_op`` database.
        """
        print()
        print("database")
        # nb. use repr() to hide password
        print(f"url: {repr(op_session.bind.url)}")
        exists = self.database_exists(op_session)
        print(f"exists: {exists}")
        if not exists:
            return # nothing more to test
        print()

        print("changes table")
        print(f"name: {table_name}")
        table = self.make_changes_table(table_name)
        exists = self.changes_table_exists(op_session, table)
        print(f"exists: {exists}")
        if exists:
            records = op_session.execute(table.select())
            print(f"records: {len(records.fetchall())}")
        print()

        for trigger in self.supported_triggers:
            print(f"triggers for {trigger}")
            
            create = f'record_{trigger}_create'
            exists = self.trigger_exists(op_session, create)
            print(f"{create:40s} exists: {exists}")

            update = f'record_{trigger}_update'
            exists = self.trigger_exists(op_session, update)
            print(f"{update:40s} exists: {exists}")

            delete = f'record_{trigger}_delete'
            exists = self.trigger_exists(op_session, delete)
            print(f"{delete:40s} exists: {exists}")

            print()

    def database_exists(self, op_session):
        corepos = self.app.get_corepos_handler()
        op_model = corepos.get_model_office_op()
        try:
            # just query a basic table, if things are normal then we're good
            op_session.query(op_model.Department).count()
        except sa.exc.ProgrammingError:
            return False
        return True

    def trigger_exists(self, op_session, trigger):
        dbname = op_session.bind.url.database
        sql = sa.text(f"""
        SHOW TRIGGERS FROM `{dbname}` WHERE `Trigger` = :trigger
        """)
        result = op_session.execute(sql, {'trigger': trigger})
        if result.fetchone():
            return True
        return False

    def changes_table_exists(self, op_session, table):
        if isinstance(table, str):
            table = self.make_changes_table(table)
        try:
            op_session.execute(table.select())
        except sa.exc.ProgrammingError:
            return False
        return True

    def make_changes_table(self, table_name):
        metadata = sa.MetaData()
        table = make_changes_table(table_name, metadata)
        return table

    def install_all(self, op_session, table_name, dry_run=False):
        self.install_changes_table(op_session, table_name, dry_run=dry_run)
        self.install_triggers(op_session, table_name, dry_run=dry_run)

    def install_changes_table(self, op_session, table_name, dry_run=False):
        print()
        print("installing changes table...")
        print(f"{table_name}: ", end='')

        table = self.make_changes_table(table_name)
        if self.changes_table_exists(op_session, table):
            print("already exists")
            print()
            return

        if not dry_run:
            table.create(op_session.bind)
        print("done")
        print()

    def install_triggers(self, op_session, table_name, dry_run=False):
        print("installing triggers...")

        for trigger in self.supported_triggers:
            if not dry_run:
                self.drop_triggers(op_session, trigger)

                meth = getattr(self, f'create_triggers_{trigger}')
                meth(op_session, table_name)

        print("done")
        print()

    def uninstall_all(self, op_session, table_name, dry_run=False):
        self.uninstall_changes_table(op_session, table_name, dry_run=dry_run)
        self.uninstall_triggers(op_session, dry_run=dry_run)

    def uninstall_changes_table(self, op_session, table_name, dry_run=False):
        print()
        print("uninstalling changes table...")

        table = self.make_changes_table(table_name)
        if not self.changes_table_exists(op_session, table):
            print("table does not exist")
            print()
            return

        if not dry_run:
            # TODO: why does this drop() method just hang forever?
            #table.drop(op_session.bind)
            op_session.execute(sa.text(f"DROP TABLE {table_name}"))
        print("done")
        print()

    def uninstall_triggers(self, op_session, dry_run=False):
        print("uninstalling triggers...")

        for trigger in self.supported_triggers:
            if not dry_run:
                self.drop_triggers(op_session, trigger)

        print("done")
        print()

    def create_triggers_custdata(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_custdata_create
        AFTER INSERT ON custdata
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Member', CONVERT(NEW.CardNo, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_custdata_update
        AFTER UPDATE ON custdata
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Member', CONVERT(NEW.CardNo, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_custdata_delete
        AFTER DELETE ON custdata
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Member', CONVERT(OLD.CardNo, CHAR), 1);
        """))

    def create_triggers_meminfo(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_meminfo_create
        AFTER INSERT ON meminfo
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Member', CONVERT(NEW.card_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_meminfo_update
        AFTER UPDATE ON meminfo
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Member', CONVERT(NEW.card_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_meminfo_delete
        AFTER DELETE ON meminfo
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Member', CONVERT(OLD.card_no, CHAR), 1);
        """))

    def create_triggers_employees(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_employees_create
        AFTER INSERT ON employees
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Employee', CONVERT(NEW.emp_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_employees_update
        AFTER UPDATE ON employees
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Employee', CONVERT(NEW.emp_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_employees_delete
        AFTER DELETE ON employees
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Employee', CONVERT(OLD.emp_no, CHAR), 1);
        """))

    def create_triggers_departments(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_departments_create
        AFTER INSERT ON departments
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Department', CONVERT(NEW.dept_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_departments_update
        AFTER UPDATE ON departments
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Department', CONVERT(NEW.dept_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_departments_delete
        AFTER DELETE ON departments
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Department', CONVERT(OLD.dept_no, CHAR), 1);
        """))

    def create_triggers_subdepts(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_subdepts_create
        AFTER INSERT ON subdepts
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Subdepartment', CONVERT(NEW.subdept_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_subdepts_update
        AFTER UPDATE ON subdepts
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Subdepartment', CONVERT(NEW.subdept_no, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_subdepts_delete
        AFTER DELETE ON subdepts
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Subdepartment', CONVERT(OLD.subdept_no, CHAR), 1);
        """))

    def create_triggers_vendors(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_vendors_create
        AFTER INSERT ON vendors
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Vendor', CONVERT(NEW.vendorID, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_vendors_update
        AFTER UPDATE ON vendors
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Vendor', CONVERT(NEW.vendorID, CHAR), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_vendors_delete
        AFTER DELETE ON vendors
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Vendor', CONVERT(OLD.vendorID, CHAR), 1);
        """))

    def create_triggers_products(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_products_create
        AFTER INSERT ON products
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Product', NEW.upc, 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_products_update
        AFTER UPDATE ON products
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Product', NEW.upc, 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_products_delete
        AFTER DELETE ON products
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('Product', OLD.upc, 1);
        """))

    def create_triggers_vendorItems(self, op_session, changes_table):

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_vendorItems_create
        AFTER INSERT ON vendorItems
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('VendorItem', CONCAT_WS('|', NEW.sku, CONVERT(NEW.vendorID, CHAR)), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_vendorItems_update
        AFTER UPDATE ON vendorItems
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('VendorItem', CONCAT_WS('|', NEW.sku, CONVERT(NEW.vendorID, CHAR)), 0);
        """))

        op_session.execute(sa.text(f"""
        CREATE TRIGGER record_vendorItems_delete
        AFTER DELETE ON vendorItems
        FOR EACH ROW INSERT INTO {changes_table} (object_type, object_key, deleted) VALUES ('VendorItem', CONCAT_WS('|', OLD.sku, CONVERT(OLD.vendorID, CHAR)), 1);
        """))

    def drop_triggers(self, op_session, trigger):

        op_session.execute(sa.text(f"""
        DROP TRIGGER IF EXISTS record_{trigger}_create;
        """))

        op_session.execute(sa.text(f"""
        DROP TRIGGER IF EXISTS record_{trigger}_update;
        """))

        op_session.execute(sa.text(f"""
        DROP TRIGGER IF EXISTS record_{trigger}_delete;
        """))
