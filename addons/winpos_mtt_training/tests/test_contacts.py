from odoo.tests.common import TransactionCase


class TestContact(TransactionCase):

    def setUp(self):
        super(TestContact, self).setUp()
        self.Contact = self.env['winpos_mtt_training.contact']

    def test_create_contact(self):
        contact = self.Contact.create({
            'name': 'Alice',
            'email': 'Alice@gmail.com',
            'phone': '0123456789',
            'age': 25
        })
        self.assertEqual(contact.name, 'Alice')
        self.assertEqual(contact.email, 'Alice@gmail.com')
        self.assertEqual(contact.phone, '0123456789')
        self.assertEqual(contact.age, 25)

    def test_is_adult(self):
        contact1 = self.Contact.create({'name': 'Bob', 'age': 26})
        contact2 = self.Contact.create({'name': 'Charlie', 'age': 16})
        contact3 = self.Contact.create({'name': 'David'})

        self.assertTrue(contact1.is_adult())
        self.assertFalse(contact2.is_adult())
        self.assertFalse(contact3.is_adult())

    def test_contact_info(self):
        contact = self.Contact.create(
            {'name': 'Eva', 'email': 'Eva@gmail.com'})
        self.assertEqual(contact.contact_info(), 'Eva - Eva@gmail.com - N/A')

        contact2 = self.Contact.create({'name': 'Bob'})
        self.assertEqual(contact2.contact_info(), 'Bob - N/A - N/A')
