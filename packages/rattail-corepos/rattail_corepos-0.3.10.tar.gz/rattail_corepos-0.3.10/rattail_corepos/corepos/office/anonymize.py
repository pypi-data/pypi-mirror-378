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
CORE Office - data anonymization
"""

import random

from rattail.app import GenericHandler
from rattail.db.util import finalize_session
from rattail_corepos.corepos.office.util import get_blueline_template, make_blueline


class Anonymizer(GenericHandler):
    """
    Make anonymous (randomize) all customer names etc.
    """

    def anonymize_all(self, dbkey=None, dry_run=False, progress=None):
        # nb. these must be installed with:
        #   pip install names us zipcodes
        import names
        import us
        import zipcodes

        self.all_zipcodes = zipcodes.list_all()

        core_handler = self.app.get_corepos_handler()
        op_session = core_handler.make_session_office_op(dbkey=dbkey)
        op_model = core_handler.get_model_office_op()

        states = [state.abbr for state in us.states.STATES]

        # custdata
        customers = op_session.query(op_model.CustomerClassic)\
                              .order_by(op_model.CustomerClassic.card_number,
                                        op_model.CustomerClassic.person_number)\
                              .all()
        blueline_template = get_blueline_template(self.config)
        customers_by_card_number = {}

        def anon_custdata(customer, i):
            customer.first_name = names.get_first_name()
            customer.last_name = names.get_last_name()
            customer.blue_line = make_blueline(self.config, customer,
                                               template=blueline_template)
            customers_by_card_number.setdefault(customer.card_number, []).append(customer)

        self.app.progress_loop(anon_custdata, customers, progress,
                               message="Anonymizing custdata")

        # meminfo
        members = op_session.query(op_model.MemberInfo).all()

        def anon_meminfo(member, i):
            if member.first_name:
                member.first_name = names.get_first_name()
            if member.last_name:
                member.last_name = names.get_last_name()
            if member.other_first_name:
                member.other_first_name = names.get_first_name()
            if member.other_last_name:
                member.other_last_name = names.get_last_name()

            member.street = '123 Main St.'
            member.city = 'Anytown'
            member.state = random.choice(states)
            member.zip = self.random_zipcode()
            member.phone = self.random_phone()

            customers = customers_by_card_number.get(member.card_number)
            if customers:
                customer = customers[0]
                member.email = f'{customer.first_name}_{customer.last_name}@mailinator.com'\
                      .lower()
            else:
                member.email = self.random_email()

            member.notes.clear()

        self.app.progress_loop(anon_meminfo, members, progress,
                               message="Anonymizing meminfo")

        # Customers
        customers = op_session.query(op_model.Customer).all()

        def del_customer(customer, i):
            op_session.delete(customer)

        self.app.progress_loop(del_customer, customers, progress,
                               message="Deleting from Customers")

        # CustomerAccounts
        accounts = op_session.query(op_model.CustomerAccount).all()

        def del_account(account, i):
            op_session.delete(account)

        self.app.progress_loop(del_account, accounts, progress,
                               message="Deleting from CustomerAccounts")

        # employees
        employees = op_session.query(op_model.Employee).all()

        def anon_employee(employee, i):
            employee.first_name = names.get_first_name()
            employee.last_name = names.get_last_name()

        self.app.progress_loop(anon_employee, employees, progress,
                               message="Anonymizing employees")

        # Users
        users = op_session.query(op_model.User).all()

        def anon_user(user, i):
            user.real_name = names.get_full_name()

        self.app.progress_loop(anon_user, users, progress,
                               message="Anonymizing users")

        finalize_session(op_session, dry_run=dry_run)

    def random_phone(self):
        digits = [random.choice('0123456789')
                  for i in range(10)]
        return self.app.format_phone_number(''.join(digits))

    def random_email(self):
        import names
        name = names.get_full_name()
        name = name.replace(' ', '_')
        return f'{name}@mailinator.com'.lower()

    def random_zipcode(self):
        return random.choice(self.all_zipcodes)['zip_code']
