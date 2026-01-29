from django.test import TestCase, Client
from django.urls import reverse
from .models import Room, Customer, Payment, BoardingHouseUser
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


class TransferCustomerTest(TestCase):
    def setUp(self):
        # Create Admin User
        self.user = BoardingHouseUser.objects.create_superuser(username='admin', password='password', role='Admin')
        self.client = Client()
        self.client.login(username='admin', password='password')

        # Create Rooms
        self.room_cheap = Room.objects.create(
            room_number='101',
            room_type='Bed Spacer',
            price=Decimal('1000.00'),
            capacity=2,
            status='Available'
        )
        self.room_expensive = Room.objects.create(
            room_number='202',
            room_type='Single',
            price=Decimal('1500.00'),
            capacity=1,
            status='Available'
        )
        self.room_vacant = Room.objects.create(
            room_number='303',
            room_type='Single',
            price=Decimal('1500.00'),
            capacity=1,
            status='Available'
        )

        # Create Customer
        self.customer = Customer.objects.create(
            name='John Doe',
            room=self.room_cheap,
            due_date=timezone.localdate(),
            status='Active'
        )

    def test_transfer_upgrade_adjustment(self):
        # Customer pays for the cheap room
        Payment.objects.create(
            customer=self.customer,
            due_date=self.customer.due_date,
            amount=self.room_cheap.price,
            amount_received=self.room_cheap.price,
            is_paid=True
        )

        # Transfer to expensive room
        response = self.client.post(reverse('transfer_customer', args=[self.customer.pk]), {
            'new_room': self.room_expensive.pk
        })

        self.assertEqual(response.status_code, 302)

        # Reload customer
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.room, self.room_expensive)

        # Check for adjustment payment
        payments = Payment.objects.filter(customer=self.customer, due_date=self.customer.due_date)
        total_paid = sum(p.amount_received for p in payments)
        self.assertEqual(total_paid, self.room_expensive.price)

        adjustment = payments.filter(remarks__startswith="Transfer Adjustment").first()
        self.assertIsNotNone(adjustment)
        self.assertEqual(adjustment.amount_received, Decimal('500.00'))

    def test_transfer_downgrade_credit(self):
        # Setup: Customer in expensive room, fully paid
        self.customer.room = self.room_expensive
        self.customer.save()

        Payment.objects.create(
            customer=self.customer,
            due_date=self.customer.due_date,
            amount=self.room_expensive.price,
            amount_received=self.room_expensive.price,
            is_paid=True
        )

        # Transfer to cheap room
        response = self.client.post(reverse('transfer_customer', args=[self.customer.pk]), {
            'new_room': self.room_cheap.pk
        })

        self.assertEqual(response.status_code, 302)

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.room, self.room_cheap)

        # Check for credit payment in NEXT month
        from dateutil.relativedelta import relativedelta
        next_due = self.customer.due_date + relativedelta(months=1)

        credit_payment = Payment.objects.filter(customer=self.customer, due_date=next_due).first()
        self.assertIsNotNone(credit_payment)
        self.assertEqual(credit_payment.amount_received, Decimal('500.00'))
        self.assertTrue(credit_payment.remarks.startswith("Transfer Credit"))

        # Ensure current cycle is still considered fully paid (balance 0)
        # Note: balance logic is in the view, but we can check the data
        current_payments = Payment.objects.filter(customer=self.customer, due_date=self.customer.due_date)
        total_paid_current = sum(p.amount_received for p in current_payments)
        # Total paid is still 1500, price is 1000. Balance is 0.
        self.assertEqual(total_paid_current, Decimal('1500.00'))


class PaymentCycleTest(TestCase):
    def setUp(self):
        self.user = BoardingHouseUser.objects.create_superuser(username='admin', password='password', role='Admin')
        self.client = Client()
        self.client.login(username='admin', password='password')

        self.room = Room.objects.create(
            room_number='401',
            room_type='Single',
            price=Decimal('1000.00'),
            capacity=1,
            status='Available'
        )

        self.customer = Customer.objects.create(
            name='Alice',
            room=self.room,
            due_date=timezone.localdate(),
            status='Active'
        )

    def test_partial_then_full_payment_advances_cycle_once(self):
        today = timezone.localdate()

        # First partial payment
        response1 = self.client.post(reverse('process_payment'), {
            'customer_id': self.customer.pk,
            'payment_id': '',
            'amount_received': '400.00',
            'change_amount': '0.00',
            'remarks': 'first partial',
        })
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()
        self.assertTrue(data1.get('success'))

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.due_date, today)

        # Second payment completes the cycle
        response2 = self.client.post(reverse('process_payment'), {
            'customer_id': self.customer.pk,
            'payment_id': '',
            'amount_received': '600.00',
            'change_amount': '0.00',
            'remarks': 'second partial',
        })
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertTrue(data2.get('success'))

        from dateutil.relativedelta import relativedelta

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.due_date, today + relativedelta(months=1))

        # Ensure total applied to the original cycle equals the room price
        payments = Payment.objects.filter(customer=self.customer, due_date=today, is_paid=True)
        total_applied = sum(p.amount_received for p in payments)
        self.assertEqual(total_applied, self.room.price)

    def test_over_cash_is_treated_as_change_not_prepayment(self):
        today = timezone.localdate()

        response = self.client.post(reverse('process_payment'), {
            'customer_id': self.customer.pk,
            'payment_id': '',
            'amount_received': '1200.00',
            'change_amount': '0.00',
            'remarks': 'over cash',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data.get('success'))

        from dateutil.relativedelta import relativedelta

        # Due date should advance by one month
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.due_date, today + relativedelta(months=1))

        # Payment record for the original cycle should only apply the room price
        payment = Payment.objects.filter(customer=self.customer, due_date=today, is_paid=True).first()
        self.assertIsNotNone(payment)
        self.assertEqual(payment.amount_received, self.room.price)
        # Change should be the extra cash
        self.assertEqual(payment.change_amount, Decimal('200.00'))

    def test_reject_payment_when_cycle_already_fully_paid(self):
        today = timezone.localdate()

        # Manually mark the current cycle as fully paid without advancing due_date
        Payment.objects.create(
            customer=self.customer,
            due_date=self.customer.due_date,
            amount=self.room.price,
            amount_received=self.room.price,
            is_paid=True
        )

        response = self.client.post(reverse('process_payment'), {
            'customer_id': self.customer.pk,
            'payment_id': '',
            'amount_received': '500.00',
            'change_amount': '0.00',
            'remarks': 'attempt prepayment',
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertFalse(data.get('success'))
        self.assertIn('already fully paid', data.get('error', ''))
