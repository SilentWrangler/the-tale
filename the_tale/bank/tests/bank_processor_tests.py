# coding: utf-8
import mock

from dext.settings import settings

from common.utils import testcase

from bank.tests.helpers import BankTestsMixin

from bank.conf import bank_settings

from bank.workers.environment import workers_environment as bank_workers_environment


class BankTests(testcase.TestCase, BankTestsMixin):

    def setUp(self):
        super(BankTests, self).setUp()

        bank_workers_environment.deinitialize()
        bank_workers_environment.initialize()

        settings[bank_settings.SETTINGS_ALLOWED_KEY] = 'allowed'

        self.worker = bank_workers_environment.bank_processor

    def test_initialize__reset_invoices(self):
        with mock.patch('bank.prototypes.InvoicePrototype.reset_all') as reset_all:
            self.worker.initialize()

        self.assertEqual(reset_all.call_count, 1)

    @mock.patch('bank.conf.bank_settings.ENABLE_BANK', False)
    @mock.patch('bank.conf.bank_settings.BANK_PROCESSOR_SLEEP_TIME', 0)
    def test_run__turn_off_by_configs(self):
        invoice = self.create_invoice()
        self.worker.process_freeze_invoice()
        invoice.reload()
        self.assertTrue(invoice.state._is_REQUESTED)

    @mock.patch('bank.conf.bank_settings.BANK_PROCESSOR_SLEEP_TIME', 0)
    def test_freeze_invoice__turn_off_by_settings(self):
        del settings[bank_settings.SETTINGS_ALLOWED_KEY]
        invoice = self.create_invoice()
        self.worker.process_freeze_invoice()
        invoice.reload()
        self.assertTrue(invoice.state._is_REQUESTED)

    def test_freeze_invoice__no_invoice(self):
        self.worker.process_freeze_invoice()

    def test_freeze_invoice(self):
        invoice = self.create_invoice()
        self.worker.process_freeze_invoice()
        invoice.reload()
        self.assertTrue(invoice.state._is_FROZEN)

    def test_confirm_invoice(self):
        invoice = self.create_invoice()
        self.worker.process_freeze_invoice()
        self.worker.process_confirm_invoice(invoice.id)
        invoice.reload()
        self.assertTrue(invoice.state._is_CONFIRMED)

    def test_cancel_invoice(self):
        invoice = self.create_invoice()
        self.worker.process_freeze_invoice()
        self.worker.process_cancel_invoice(invoice.id)
        invoice.reload()
        self.assertTrue(invoice.state._is_CANCELED)