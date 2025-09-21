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
CORE POS (API) -> Rattail data importing
"""

import datetime
import decimal
import logging
from collections import OrderedDict

import sqlalchemy as sa
from sqlalchemy import orm

from rattail import importing
from rattail.db.util import normalize_full_name
from rattail_corepos import importing as corepos_importing
from rattail_corepos.corepos.util import get_core_members


log = logging.getLogger(__name__)


class FromCOREPOSToRattail(importing.ToRattailHandler):
    """
    Import handler for data coming from a CORE POS API.
    """
    host_key = 'corepos_api'
    generic_host_title = "CORE Office (API)"
    host_title = "CORE-POS (API)"
    safe_for_web_app = True

    def get_importers(self):
        importers = OrderedDict()
        importers['Customer'] = CustomerImporter
        importers['CustomerShopper'] = CustomerShopperImporter
        importers['MembershipType'] = MembershipTypeImporter
        importers['Member'] = MemberImporter
        importers['Employee'] = EmployeeImporter
        importers['Store'] = StoreImporter
        importers['Department'] = DepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Vendor'] = VendorImporter
        importers['Product'] = ProductImporter
        importers['ProductCost'] = ProductCostImporter
        importers['ProductMovement'] = ProductMovementImporter
        return importers

    def get_default_keys(self):
        keys = super().get_default_keys()

        if 'ProductMovement' in keys:
            keys.remove('ProductMovement')
        return keys

    def get_core_members(self, api, progress=None):
        if not hasattr(self, 'cached_core_members'):
            self.cached_core_members = get_core_members(
                self.config, api, progress=progress)
        return self.cached_core_members


class FromCOREPOSAPI(importing.Importer):
    """
    Base class for all CORE POS API data importers.
    """

    def setup(self):
        super().setup()

        self.establish_api()

        self.ignore_new_members = self.should_ignore_new_members()

    def datasync_setup(self):
        super().datasync_setup()

        self.establish_api()

    def establish_api(self):
        self.api = self.app.get_corepos_handler().make_webapi()

    def should_ignore_new_members(self):
        if hasattr(self, 'ignore_new_members'):
            return self.ignore_new_members

        return self.config.getbool('rattail_corepos',
                                   'importing_ignore_new_members',
                                   default=False)

    def get_core_members(self):
        members = self.handler.get_core_members(self.api, progress=self.progress)

        # maybe ignore NEW MEMBER accounts
        if self.should_ignore_new_members():
            members = [member for member in members
                       if not self.is_new_member(member)]

        return members

    def is_new_member(self, member):
        """
        Convenience method to check if the given member represents a
        "NEW MEMBER" record in CORE-POS, and hence it should be
        ignored for the import.
        """
        customers = member['customers']
        if customers:
            customer = customers[0]
            if (not customer['firstName']
                and customer['lastName'] == 'NEW MEMBER'):
                return True
        return False


class CustomerImporter(FromCOREPOSAPI, corepos_importing.model.CustomerImporter):
    """
    Importer for customer data from CORE POS API.
    """
    key = 'corepos_card_number'
    supported_fields = [
        'corepos_card_number',
        'corepos_account_id',
        'number',
        'name',
        # 'account_holder_first_name',
        # 'account_holder_last_name',
        'address_street',
        'address_street2',
        'address_city',
        'address_state',
        'address_zipcode',
    ]

    def get_host_objects(self):
        return self.get_core_members()

    def normalize_host_object(self, member):
        card_number = int(member['cardNo'])

        # figure out the "account holder" customer for the member.  note that
        # we only use this to determine the `Customer.name` in Rattail
        customers = member['customers']
        account_holders = [customer for customer in customers
                           if customer['accountHolder']]
        if account_holders:
            if len(account_holders) > 1:
                log.warning("member %s has %s account holders in CORE: %s",
                            member['cardNo'], len(account_holders), member)
            customer = account_holders[0]
        elif customers:
            if len(customers) > 1:
                log.warning("member %s has %s customers but no account holders: %s",
                            member['cardNo'], len(customers), member)
            customer = customers[0]
        else:
            raise NotImplementedError("TODO: how to handle member with no customers?")

        data = {
            'corepos_card_number': card_number,
            'corepos_account_id': int(member['customerAccountID']),
            'number': card_number,
            'name': normalize_full_name(customer['firstName'],
                                        customer['lastName']),

            # 'account_holder_first_name': customer['firstName'],
            # 'account_holder_last_name': customer['lastName'],
            'address_street': member['addressFirstLine'] or None,
            'address_street2': member['addressSecondLine'] or None,
            'address_city': member['city'] or None,
            'address_state': member['state'] or None,
            'address_zipcode': member['zip'] or None,
        }

        return data


class CustomerShopperImporter(FromCOREPOSAPI, corepos_importing.model.CustomerShopperImporter):
    """
    Importer for customer shopper data from CORE POS API.
    """
    key = ('customer_uuid', 'shopper_number')
    supported_fields = [
        'customer_uuid',
        'shopper_number',
        'corepos_customer_id',
        'first_name',
        'last_name',
        'display_name',
        'active',
        'phone_number',
        'phone_number_2',
        'email_address',
        'account_holder',
    ]

    def setup(self):
        super().setup()
        model = self.model

        self.maxlen_phone_number = self.get_maxlen_phone_number()

        self.customers_by_card_number = self.app.cache_model(
            self.session,
            model.Customer,
            key='corepos_card_number',
            query_options=[orm.joinedload(model.Customer._corepos)])

    def get_maxlen_phone_number(self):
        if hasattr(self, 'maxlen_phone_number'):
            return self.maxlen_phone_number

        model = self.model
        return self.app.maxlen(model.PhoneNumber.number)

    def get_host_objects(self):

        # first get all member data from CORE API
        members = self.get_core_members()
        normalized = []

        # then collect all the "shopper" records
        def normalize(member, i):
            normalized.extend(self.get_shoppers_for_member(member))

        self.progress_loop(normalize, members,
                           message="Collecting Person data from CORE")
        return normalized

    def get_customer_by_card_number(self, card_number):
        if hasattr(self, 'customers_by_card_number'):
            return self.customers_by_card_number.get(card_number)

        model = self.model
        try:
            return self.session.query(model.Customer)\
                               .join(model.CoreCustomer)\
                               .filter(model.CoreCustomer.corepos_card_number == card_number)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def get_shoppers_for_member(self, member):
        """
        Return a list of shopper info dicts associated with the given
        member info dict (latter having come from the CORE API).
        """
        customers = member['customers']
        shoppers = []

        # make sure account holder is listed first
        account_holder = None
        secondary = False
        mixedup = False
        for customer in customers:
            if customer['accountHolder'] and not secondary:
                account_holder = customer
            elif not customer['accountHolder']:
                secondary = True
            elif customer['accountHolder'] and secondary:
                mixedup = True
        if mixedup:
            raise NotImplementedError("TODO: should re-sort the customers list for member {}".format(member['cardNo']))

        for i, customer in enumerate(customers, 1):
            shopper = dict(customer)
            shopper['card_number'] = member['cardNo']
            shopper['shopper_number'] = i
            shoppers.append(shopper)

        return shoppers

    def normalize_host_object(self, shopper):
        card_number = shopper['card_number']

        customer = self.get_customer_by_card_number(card_number)
        if not customer:
            log.warning("Rattail customer not found for CardNo %s: %s",
                        card_number, shopper)
            return

        data = {
            'customer_uuid': customer.uuid,
            'shopper_number': shopper['shopper_number'],
            'corepos_customer_id': int(shopper['customerID']),

            'first_name': shopper['firstName'],
            'last_name': shopper['lastName'],
            'display_name': normalize_full_name(shopper['firstName'],
                                                shopper['lastName']),

            # TODO: can a CORE shopper be *not* active?
            'active': True,

            'phone_number': shopper['phone'] or None,
            'phone_number_2': shopper['altPhone'] or None,

            'email_address': shopper['email'] or None,
            'account_holder': bool(shopper['accountHolder']),
        }

        # truncate phone number data if needed
        maxlen_phone_number = self.get_maxlen_phone_number()
        if data['phone_number'] and len(data['phone_number']) > maxlen_phone_number:
            log.warning("phone_number is too long (%s chars), "
                        "will truncate to %s chars: %s",
                        len(data['phone_number']),
                        maxlen_phone_number,
                        data['phone_number'])
            data['phone_number'] = data['phone_number'][:maxlen_phone_number]
        if data['phone_number_2'] and len(data['phone_number_2']) > maxlen_phone_number:
            log.warning("phone_number_2 is too long (%s chars), "
                        "will truncate to %s chars: %s",
                        len(data['phone_number_2']),
                        maxlen_phone_number,
                        data['phone_number_2'])
            data['phone_number_2'] = data['phone_number_2'][:maxlen_phone_number]

        # swap 1st and 2nd phone numbers if only latter has value
        self.prioritize_2(data, 'phone_number')

        return data


class EmployeeImporter(FromCOREPOSAPI, corepos_importing.model.EmployeeImporter):
    """
    Importer for employee data from CORE POS API.
    """
    key = 'corepos_number'
    supported_fields = [
        'corepos_number',
        'id',
        'first_name',
        'last_name',
        'full_name',
        'status',
    ]

    def get_host_objects(self):
        return self.api.get_employees()

    def normalize_host_object(self, employee):
        return {
            'corepos_number': int(employee['emp_no']),
            'id': int(employee['emp_no']),
            'first_name': employee['FirstName'],
            'last_name': employee['LastName'],
            'full_name': normalize_full_name(employee['FirstName'], employee['LastName']),
            'status': self.enum.EMPLOYEE_STATUS_CURRENT if employee['EmpActive'] == '1' else self.enum.EMPLOYEE_STATUS_FORMER,
        }


class StoreImporter(FromCOREPOSAPI, corepos_importing.model.StoreImporter):
    """
    Importer for store data from CORE POS API.
    """
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'id',
        'name',
    ]

    def get_host_objects(self):
        return self.api.get_stores()

    def normalize_host_object(self, store):
        return {
            'corepos_id': int(store['storeID']),
            'id': str(store['storeID']),
            'name': store['description'],
        }


class DepartmentImporter(FromCOREPOSAPI, corepos_importing.model.DepartmentImporter):
    """
    Importer for department data from CORE POS API.
    """
    key = 'corepos_number'
    supported_fields = [
        'corepos_number',
        'number',
        'name',
    ]

    def get_host_objects(self):
        return self.api.get_departments()

    def normalize_host_object(self, department):
        return {
            'corepos_number': int(department['dept_no']),
            'number': int(department['dept_no']),
            'name': department['dept_name'],
        }


class SubdepartmentImporter(FromCOREPOSAPI, corepos_importing.model.SubdepartmentImporter):
    """
    Importer for subdepartment data from CORE POS API.
    """
    key = 'corepos_number'
    supported_fields = [
        'corepos_number',
        'number',
        'name',
        'department_number',
    ]

    def get_host_objects(self):
        return self.api.get_subdepartments()

    def normalize_host_object(self, subdepartment):
        department_number = None
        if 'dept_ID' in subdepartment:
            department_number = int(subdepartment['dept_ID'])

        return {
            'corepos_number': int(subdepartment['subdept_no']),
            'number': int(subdepartment['subdept_no']),
            'name': subdepartment.get('subdept_name'),
            'department_number': department_number,
        }


class VendorImporter(FromCOREPOSAPI, corepos_importing.model.VendorImporter):
    """
    Importer for vendor data from CORE POS API.
    """
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'id',
        'name',
        'abbreviation',
        'special_discount',
        'phone_number',
        'fax_number',
        'email_address',
    ]

    def get_host_objects(self):
        return self.api.get_vendors()

    def normalize_host_object(self, vendor):
        return {
            'corepos_id': int(vendor['vendorID']),
            'id': str(vendor['vendorID']),
            'name': vendor.get('vendorName'),
            'abbreviation': vendor.get('vendorAbbreviation') or None,
            'special_discount': decimal.Decimal(vendor['discountRate']),
            'phone_number': vendor.get('phone') or None,
            'fax_number': vendor.get('fax') or None,
            'email_address': vendor.get('email') or None,
        }


class ProductImporter(FromCOREPOSAPI, corepos_importing.model.ProductImporter):
    """
    Importer for product data from CORE POS API.
    """
    key = 'uuid'
    supported_fields = [
        'uuid',
        'corepos_id',
        'item_id',
        'upc',
        'brand_name',
        'description',
        'unit_size',
        'unit_of_measure',
        'uom_abbreviation',
        'size',
        'weighed',
        'department_number',
        'subdepartment_number',
        'regular_price_price',
        'regular_price_multiple',
        'regular_price_type',
        'food_stampable',
        # 'tax1',
        # 'tax2',
        'case_size',
    ]

    def setup(self):
        super().setup()
        model = self.model

        query = self.session.query(model.Product)\
                            .join(model.CoreProduct)\
                            .filter(model.CoreProduct.corepos_id != None)\
                            .options(orm.joinedload(model.Product._corepos))
        self.core_existing = self.app.cache_model(self.session,
                                                  model.Product,
                                                  key='corepos_id',
                                                  query=query)

        self.vendor_items_by_upc = {}

        def cache(item, i):
            if item.get('upc'):
                self.vendor_items_by_upc.setdefault(item['upc'], []).append(item)

        self.progress_loop(cache, self.api.get_vendor_items(),
                           message="Caching CORE Vendor Items")

    def get_host_objects(self):
        products = OrderedDict()

        def collect(product, i):
            if product.get('upc'):
                if product['upc'] in products:
                    log.warning("duplicate UPC encountered for '%s'; will discard: %s",
                                product['upc'], product)
                else:
                    products[product['upc']] = product

        self.progress_loop(collect, self.api.get_products(),
                           message="Fetching product info from CORE-POS")
        return list(products.values())

    def identify_product(self, corepos_product):
        model = self.app.model
        corepos_id = int(corepos_product['id'])

        if hasattr(self, 'core_existing'):
            product = self.core_existing.get(corepos_id)
            if product:
                return product

        else:
            try:
                return self.session.query(model.Product)\
                                   .join(model.CoreProduct)\
                                   .filter(model.CoreProduct.corepos_id == corepos_id)\
                                   .one()
            except orm.exc.NoResultFound:
                pass

        # at this point we'll search by `Product.item_id` instead
        return self.session.query(model.Product)\
                           .outerjoin(model.CoreProduct)\
                           .filter(model.CoreProduct.corepos_id == None)\
                           .filter(model.Product.item_id == corepos_product['upc'])\
                           .first()

    def identify_product_uuid(self, corepos_product):
        product = self.identify_product(corepos_product)
        if product:
            return product.uuid
        return self.app.make_uuid()

    def get_vendor_items(self, api_product):
        if hasattr(self, 'vendor_items_by_upc'):
            return self.vendor_items_by_upc.get(api_product['upc'])

        return self.api.get_vendor_items(upc=api_product['upc'])

    def normalize_host_object(self, product):
        model = self.model
        if 'upc' not in product:
            log.warning("CORE-POS product has no UPC: %s", product)
            return

        try:
            upc = self.app.make_gpc(product['upc'], calc_check_digit='upc')
        except (TypeError, ValueError):
            log.debug("CORE POS product has invalid UPC: %s", product['upc'])
            if len(self.key) == 1 and self.key[0] == 'upc':
                return
            upc = None

        department_number = None
        if 'department' in product:
            department_number = int(product['department']) or None

        subdepartment_number = None
        if 'subdept' in product:
            subdepartment_number = int(product['subdept']) or None

        price = None
        if product.get('normal_price') is not None:
            price = decimal.Decimal(product['normal_price'])

        data = {
            'uuid': self.identify_product_uuid(product),
            'corepos_id': int(product['id']),
            'item_id': product['upc'],
            'upc': upc,
            'brand_name': product.get('brand') or None,
            'description': product.get('description') or '',

            'department_number': department_number,
            'subdepartment_number': subdepartment_number,

            'weighed': product.get('scale') == '1',
            'food_stampable': None,
            # 'tax1': product['tax'] == '1', # TODO: is this right?
            # 'tax2': product['tax'] == '2', # TODO: is this right?

            'regular_price_price': price,
            'regular_price_multiple': 1 if price is not None else None,
            'regular_price_type': self.enum.PRICE_TYPE_REGULAR if price is not None else None,
        }

        if 'foodstamp' in product:
            data['food_stampable'] = product['foodstamp'] == '1'

        if self.fields_active(self.size_fields):
            size_info = self.normalize_size_info(product)
            data.update({
                'size': size_info['size'],
                'unit_size': size_info['unit_size'],
                'unit_of_measure': size_info['uom_code'],
                'uom_abbreviation': (size_info['uom_abbrev'] or '').strip() or None,
            })

            maxval = self.app.maxval(model.Product.unit_size)
            if data['unit_size'] and data['unit_size'] >= maxval:
                log.warning("unit_size too large (%s) for product %s, will use null instead: %s",
                            data['unit_size'], data['upc'], product)
                data['unit_size'] = None

        if 'case_size' in self.fields:
            case_size = None
            items = self.get_vendor_items(product)
            if items:
                # here we sort by `modified DESC` to get the "deterministic
                # pseudo-default" vendorItems record

                def sortkey(item):
                    modified = item.get('modified')
                    if not modified:
                        return datetime.datetime(1900, 1, 1)
                    dt = datetime.datetime.strptime(modified, '%Y-%m-%d %H:%M:%S')
                    return dt

                items = sorted(items, key=sortkey, reverse=True)
                item = items[0]
                case_size = decimal.Decimal(item['units'])

            data['case_size'] = case_size

        return data


class ProductMovementImporter(FromCOREPOSAPI, corepos_importing.model.ProductImporter):
    """
    Importer for product movement data from CORE POS API.
    """
    key = 'corepos_id'
    supported_fields = [
        'corepos_id',
        'last_sold',
    ]
    allow_create = False
    allow_delete = False

    def get_host_objects(self):
        return self.api.get_products()

    def normalize_host_object(self, product):

        last_sold = None
        if 'last_sold' in product:
            last_sold = datetime.datetime.strptime(product['last_sold'], '%Y-%m-%d %H:%M:%S')
            last_sold = self.app.localtime(last_sold)
            last_sold = self.app.make_utc(last_sold)

        return {
            'corepos_id': int(product['id']),
            'last_sold': last_sold,
        }


class ProductCostImporter(FromCOREPOSAPI, corepos_importing.model.ProductCostImporter):
    """
    Importer for product cost data from CORE POS API.
    """
    key = ('corepos_vendor_id', 'corepos_sku')
    supported_fields = [
        'corepos_vendor_id',
        'corepos_sku',
        'product_uuid',
        'vendor_uuid',
        'code',
        'case_size',
        'case_cost',
        'unit_cost',
        'preferred',
    ]

    def setup(self):
        super().setup()
        model = self.app.model

        query = self.session.query(model.Vendor)\
                            .join(model.CoreVendor)\
                            .filter(model.CoreVendor.corepos_id != None)
        self.vendors = self.app.cache_model(self.session,
                                            model.Vendor,
                                            query=query,
                                            key='corepos_id')

        self.corepos_products = {}

        def cache(product, i):
            if 'upc' in product:
                self.corepos_products[product['upc']] = product

        self.progress_loop(cache, self.api.get_products(),
                           message="Caching Products from CORE-POS API")

        self.products_by_item_id = self.app.cache_model(self.session,
                                                        model.Product,
                                                        key='item_id')

    def should_warn_for_missing_vendor_id(self):
        return self.config.getbool('rattail.importing.corepos.vendor_items.warn_for_missing_vendor_id',
                                   default=True)

    def get_host_objects(self):

        # first we will cache API products by upc
        products = OrderedDict()

        def cache(product, i):
            if product.get('upc'):
                products[product['upc']] = product

        self.progress_loop(cache, self.api.get_products(),
                           message="Caching product data from CORE")

        # next we cache API vendor items, also by upc
        vendor_items = {}
        warn_for_missing_vendor_id = self.should_warn_for_missing_vendor_id()

        def cache(item, i):
            if not item.get('upc'):
                log.warning("CORE vendor item has no upc: %s", item)
                return
            if item['vendorID'] == '0':
                logger = log.warning if warn_for_missing_vendor_id else log.debug
                logger("CORE vendor item has no vendorID: %s", item)
                return
            vendor_items.setdefault(item['upc'], []).append(item)

        self.progress_loop(cache, self.api.get_vendor_items(),
                           message="Caching vendor item data from CORE")

        # now we must "sort" the vendor items for each upc.  to do
        # this we just ensure the item for default vendor is first

        def organize(upc, i):
            product = products.get(upc)
            if not product:
                return          # product not found

            vendor_id = product['default_vendor_id']
            if not vendor_id:
                return          # product has no default vendor

            items = vendor_items[upc]
            self.sort_these_vendor_items(items, vendor_id)

        self.progress_loop(organize, list(vendor_items),
                           message="Sorting items by default vendor")

        # keep the vendor item cache for reference later
        self.api_vendor_items = vendor_items

        # host objects are the API products (in original sequence)
        return list(products.values())

    def get_vendor(self, item):
        corepos_id = int(item['vendorID'])

        if hasattr(self, 'vendors'):
            return self.vendors.get(corepos_id)

        model = self.app.model
        try:
            return self.session.query(model.Vendor)\
                               .join(model.CoreVendor)\
                               .filter(model.CoreVendor.corepos_id == corepos_id)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def get_corepos_product(self, item):
        if hasattr(self, 'corepos_products'):
            return self.corepos_products.get(item['upc'])

        return self.api.get_product(item['upc'])

    def get_product(self, item):
        item_id = item.get('upc')
        if not item_id:
            return

        if hasattr(self, 'products_by_item_id'):
            return self.products_by_item_id.get(item_id)

        model = self.model
        try:
            return self.session.query(model.Product)\
                               .filter(model.Product.item_id == item_id)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def normalize_host_data(self, host_objects=None):

        # TODO: this all seems a bit hacky but works for now..
        # could even be we don't need this method?

        if host_objects is None:
            host_objects = self.get_host_objects()
        normalized = []
        self.sorted_vendor_items = {}

        def normalize(product, i):
            if not product.get('upc'):
                log.warning("product has no upc: %s", product)
                return
            items = self.sort_vendor_items(product)
            self.sorted_vendor_items[product['upc']] = items
            for item in items:
                data = self.normalize_host_object(item)
                if data:
                    normalized.append(data)

        self.progress_loop(normalize, host_objects,
                           message=f"Reading Product data from {self.host_system_title}")
        return normalized

    def normalize_host_object(self, item):
        vendor = self.get_vendor(item)
        if not vendor:
            log.warning("CORE POS vendor not found for item: %s", item)
            return

        product = self.get_product(item)
        if not product:
            # just debug logging since this is a common scenario; the
            # CORE table is for items "available from vendor" but not
            # necssarily items carried by store
            log.debug("product not found for CORE vendor item: %s", item)
            return

        core_product = self.get_corepos_product(item)
        # if not product:
        #     log.warning("CORE POS product not found for item: %s", item)
        #     return

        case_size = decimal.Decimal(item['units'])
        unit_cost = item.get('cost')
        if unit_cost is not None:
            unit_cost = decimal.Decimal(unit_cost)
        case_cost = None
        if unit_cost is not None:
            case_cost = unit_cost * case_size

        data = {
            'corepos_vendor_id': int(item['vendorID']),
            'corepos_sku': item['sku'],
            'product_uuid': product.uuid,
            'vendor_uuid': vendor.uuid,
            'code': (item['sku'] or '').strip() or None,
            'case_size': case_size,
            'case_cost': case_cost,
            'unit_cost': unit_cost,
        }

        if self.fields_active(['preference', 'preferred']):
            items = self.get_sorted_vendor_items(item)
            i = items.index(item)
            data['preference'] = i + 1
            data['preferred'] = i == 0

        return data

    def get_sorted_vendor_items(self, item):
        if hasattr(self, 'sorted_vendor_items'):
            return self.sorted_vendor_items.get(item['upc'])

        product = self.api.get_product(item['upc'])
        return self.sort_vendor_items(product)

    def sort_vendor_items(self, product):

        # TODO: this all seems a bit hacky but works for now..

        if not product.get('upc'):
            return []

        if hasattr(self, 'api_vendor_items'):
            return self.api_vendor_items.get(product['upc'], [])

        # nb. remaining logic is for real-time datasync.  here we
        # do not have a cache of vendor items so must fetch what
        # we need from API.  unfortunately we must (?) fetch *all*
        # vendor items and then filter locally
        items = [item
                 for item in self.api.get_vendor_items()
                 if item.get('upc') == product['upc']]

        vendor_id = product['default_vendor_id']
        self.sort_these_vendor_items(items, vendor_id)
        return items

    def sort_these_vendor_items(self, items, default_vendor_id):
        for item in items:
            if item['vendorID'] == default_vendor_id:
                # found the default vendor item
                i = items.index(item)
                if i != 0:
                    # it was not first; make it so
                    items.pop(i)
                    items.insert(0, item)
                break


class MembershipTypeImporter(FromCOREPOSAPI, importing.model.MembershipTypeImporter):
    """
    Imports membership type data from CORE-POS API
    """
    key = 'number'
    supported_fields = [
        'number',
        'name',
    ]

    def get_host_objects(self):
        return self.api.get_member_types()

    def normalize_host_object(self, memtype):
        return {
            'number': int(memtype['memtype']),
            'name': memtype['memDesc'],
        }


class MemberImporter(FromCOREPOSAPI, corepos_importing.model.MemberImporter):
    """
    Importer for member data from CORE POS API.
    """
    key = 'corepos_card_number'
    supported_fields = [
        'number',
        'corepos_account_id',
        'corepos_card_number',
        'customer_uuid',
        'person_uuid',
        'person_first_name',
        'person_last_name',
        'membership_type_number',
        'joined',
        'withdrew',
        'active',
    ]

    # TODO: should make this configurable
    member_status_codes = [
        'PC',
        'TERM',
    ]

    # TODO: should make this configurable
    non_member_status_codes = [
        'REG',
        'INACT',
    ]

    def setup(self):
        super().setup()
        model = self.model

        self.customers_by_number = self.app.cache_model(
            self.session,
            model.Customer,
            key='number')

        query = self.session.query(model.Person)\
                            .outerjoin(model.Customer,
                                       model.Customer.account_holder_uuid == model.Person.uuid)\
                            .outerjoin(model.CoreCustomer)\
                            .outerjoin(model.Member,
                                       model.Member.person_uuid == model.Person.uuid)\
                            .outerjoin(model.CoreMember)\
                            .filter(sa.or_(
                                model.CoreCustomer.corepos_card_number != None,
                                model.CoreMember.corepos_card_number != None))\
                            .options(orm.joinedload(model.Person.customer_accounts)\
                                     .joinedload(model.Customer._corepos))
        def card_number(person, normal):
            customer = self.app.get_customer(person)
            if customer and customer.corepos_card_number:
                return customer.corepos_card_number
            member = self.app.get_member(person)
            if member and member.corepos_card_number:
                return member.corepos_card_number
        self.people_by_card_number = self.cache_model(model.Person, query=query,
                                                      key=card_number)

        self.membership_type_number_non_member = self.get_membership_type_number_non_member()

    def get_membership_type_number_non_member(self):
        if hasattr(self, 'membership_type_number_non_member'):
            return self.membership_type_number_non_member

        return self.config.getint('corepos.membership_type.non_member')

    def should_warn_for_unknown_membership_type(self):
        return self.config.getbool('rattail.importing.corepos.warn_for_unknown_membership_type',
                                   default=True)

    def get_host_objects(self):
        return self.get_core_members()

    def get_person(self, card_number):
        if hasattr(self, 'people_by_card_number'):
            return self.people_by_card_number.get(card_number)

        model = self.model

        try:
            return self.session.query(model.Person)\
                               .join(model.Customer,
                                     model.Customer.account_holder_uuid == model.Person.uuid)\
                               .join(model.CoreCustomer)\
                               .filter(model.CoreCustomer.corepos_card_number == card_number)\
                               .one()
        except orm.exc.NoResultFound:
            pass

        try:
            return self.session.query(model.Person)\
                               .join(model.Member,
                                     model.Member.person_uuid == model.Person.uuid)\
                               .join(model.CoreMember)\
                               .filter(model.CoreMember.corepos_card_number == card_number)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def get_customer_by_number(self, number):
        if hasattr(self, 'customers_by_number'):
            return self.customers_by_number.get(number)

        model = self.model
        try:
            return self.session.query(model.Customer)\
                               .filter(model.Customer.number == number)\
                               .one()
        except orm.exc.NoResultFound:
            pass

    def get_corepos_customer(self, corepos_member):
        for customer in corepos_member['customers']:
            if customer['accountHolder']:
                return customer

    def normalize_host_object(self, member):
        card_number = member['cardNo']
        customer = self.get_customer_by_number(card_number)
        person = self.get_person(card_number)

        # TODO: at first i was *skipping* non-member status records,
        # but since CORE sort of assumes all customers are members,
        # probably not worth making the distinction here..?  it is
        # important to import the full member info from CORE, so that
        # we have it to sync back.  therefore can't afford to "skip"
        # any member records here
        memstatus = (member['memberStatus'] or '').upper() or None
        if (memstatus not in self.member_status_codes
            and memstatus not in self.non_member_status_codes):
            log.warning("unexpected status '%s' for member %s: %s",
                        member['memberStatus'], card_number, member)

        joined = None
        if member['startDate'] and member['startDate'] != '0000-00-00 00:00:00':
            joined = datetime.datetime.strptime(member['startDate'],
                                                '%Y-%m-%d %H:%M:%S')
            joined = joined.date()
            if joined == datetime.date(1900, 1, 1):
                joined = None

        withdrew = None
        if (member['endDate']
            and member['endDate'] != '0000-00-00 00:00:00'
            and member['endDate'] != '1900-01-01 00:00:00'):
            withdrew = datetime.datetime.strptime(member['endDate'],
                                                  '%Y-%m-%d %H:%M:%S')
            withdrew = withdrew.date()
            if withdrew == datetime.date(1900, 1, 1):
                withdrew = None

        typeno = int(member['customerTypeID'] or 0)
        memtype = self.get_membership_type_by_number(typeno)
        if not memtype:
            typeno = self.get_membership_type_number_non_member()
            if typeno is not None:
                memtype = self.get_membership_type_by_number(typeno)
                if not memtype:
                    raise ValueError("configured membership type for non-members is invalid!")

            logger = log.warning if self.should_warn_for_unknown_membership_type() else log.debug
            logger("unknown customerTypeID (membership_type_number) '%s' for: %s",
                   member['customerTypeID'], member)
            if typeno is not None:
                log.debug("(will override with membership_type_number: %s)", typeno)

        data = {
            'number': card_number,
            'corepos_account_id': int(member['customerAccountID']),
            'corepos_card_number': card_number,
            'customer_uuid': customer.uuid if customer else None,
            'person_uuid': person.uuid if person else None,
            'person_first_name': None,
            'person_last_name': None,
            'membership_type_number': typeno,
            'joined': joined,
            'withdrew': withdrew,
            'active': not bool(withdrew),
        }

        corepos_customer = self.get_corepos_customer(member)
        if corepos_customer:
            data['person_first_name'] = corepos_customer['firstName']
            data['person_last_name'] = corepos_customer['lastName']

        return data
