# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.exceptions import UserError


class WooCommerceError(UserError):
    pass


class MissingParentsError(UserError):
    pass
