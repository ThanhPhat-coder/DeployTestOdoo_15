# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase


class TestPMKTandERP(TransactionCase):

    def setUp(self):
        super(TestPMKTandERP, self).setUp()

        # Tạo product
        self.product = self.env['product.product'].create({
            'name': 'Test Product',
            'list_price': 100.0,
            'detailed_type': 'consu',
        })

        # Tạo campaign UTM (dùng cho sale.order)
        self.utm_campaign = self.env['utm.campaign'].create({
            'name': 'UTM Campaign Test',
        })

        # Tạo campaign PMKT (module của bạn)
        self.campaign = self.env['pmkt.campaign'].create({
            'name': 'Test Campaign',
            'budget': 500.0,
        })

        # Tạo customer
        self.partner = self.env['res.partner'].create({
            'name': 'Test Customer',
        })

        # Tạo sale order, gán utm.campaign
        self.sale_order = self.env['sale.order'].create({
            'partner_id': self.partner.id,
            'campaign_id': self.utm_campaign.id,  # ✅ dùng utm.campaign để tránh lỗi FK
        })

    # ---------------------------
    # TEST 1: Campaign budget
    # ---------------------------
    def test_campaign_budget_constraint(self):
        """Kiểm tra budget của campaign không < 0"""
        self.campaign.write({'budget': 1000.0})
        self.assertEqual(
            self.campaign.budget, 1000.0,
            "Budget không được cập nhật đúng"
        )

        # Test logic: budget không thể âm (giả sử bạn có constraint trong model)
        with self.assertRaises(Exception):
            self.campaign.write({'budget': -100.0})

    # ---------------------------
    # TEST 2: Sale Order Confirm
    # ---------------------------
    def test_sale_order_confirm_amount(self):
        """Kiểm tra confirm đơn hàng ERP"""
        self.env['sale.order.line'].create({
            'order_id': self.sale_order.id,
            'product_id': self.product.id,
            'product_uom_qty': 2,
            'price_unit': 100.0,
        })

        self.sale_order.action_confirm()
        self.assertEqual(
            self.sale_order.state, 'sale',
            "Đơn hàng không được confirm"
        )

        total = sum(self.sale_order.order_line.mapped('price_subtotal'))
        self.assertEqual(
            total, 200.0,
            "Tổng tiền không đúng"
        )

    # ---------------------------
    # TEST 3: CRUD Campaign
    # ---------------------------
    def test_campaign_crud(self):
        """Test CRUD cơ bản cho campaign"""
        # Create
        new_campaign = self.env['pmkt.campaign'].create({
            'name': 'CRUD Campaign',
            'budget': 300.0,
        })
        self.assertTrue(new_campaign.id, "Không tạo được campaign")

        # Read
        found = self.env['pmkt.campaign'].search([('name', '=', 'CRUD Campaign')])
        self.assertEqual(found.budget, 300.0, "Không tìm thấy campaign vừa tạo")

        # Update
        found.write({'budget': 400.0})
        self.assertEqual(found.budget, 400.0, "Cập nhật budget không thành công")

        # Delete
        found_id = found.id
        found.unlink()
        check = self.env['pmkt.campaign'].search([('id', '=', found_id)])
        self.assertFalse(check, "Xóa campaign không thành công")
