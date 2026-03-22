from odoo import models, api
import logging

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _process_order(self, order, existing_order):
        """Detect ONLY newly added items (correct logic)."""

        _logger.info("Processing order %s (existing: %s)", order, existing_order)

        # -------------------------
        # BEFORE: capture old quantities
        # -------------------------
        old_quantities = {}

        if existing_order:
            for line in existing_order.lines:
                old_quantities[line.product_id.id] = line.qty

        # -------------------------
        # Process order
        # -------------------------
        res = super()._process_order(order, existing_order)

        pos_order = self.browse(res)

        if pos_order.source != 'mobile':
            return res

        # -------------------------
        # Table (safe here)
        # -------------------------
        table = pos_order.self_ordering_table_id or pos_order.table_id

        if not table:
            _logger.warning("No table found after _process_order for order %s", pos_order.id)
            return res

        table_num = table.table_number or table.name

        # -------------------------
        # AFTER: detect changes
        # -------------------------
        changed_items = []

        for line in pos_order.lines:
            product_id = line.product_id.id
            old_qty = old_quantities.get(product_id, 0)

            if line.qty > old_qty:
                added_qty = line.qty - old_qty

                changed_items.append({
                    'product': line.product_id.display_name,
                    'quantity': added_qty,
                    'price_unit': line.price_unit,
                    'total': added_qty * line.price_unit,
                })

        # -------------------------
        # Skip if nothing new
        # -------------------------
        if not changed_items:
            return res

        _logger.info("New items detected: %s", changed_items)

        # -------------------------
        # Build message
        # -------------------------
        message = "🔔 New Self Order\n"
        message += f"Table {table_num}:\n\n"

        for item in changed_items:
            message += f"{int(item['quantity'])}x {item['product']}\n"

        _logger.info(message)

        # -------------------------
        # Send notification
        # -------------------------
        self.env['bus.bus']._sendone(
            'pos_order_notification',
            'new_self_order',
            {
                'message': message,
                'order_id': pos_order.id,
                'items': changed_items,
                'type': 'new_self_order',
            }
        )

        return res
    # -------------------------
    # Helpers
    # -------------------------

    def _get_table(self, order):
        """Always fetch fresh table from DB (avoid cache issues)."""

        fresh_order = self.env['pos.order'].sudo().browse(order.id)

        if fresh_order.self_ordering_table_id:
            return fresh_order.self_ordering_table_id

        if fresh_order.table_id:
            return fresh_order.table_id

        return None

    def _get_table_number(self, order):
        table = self._get_table(order)

        if table:
            return table.table_number or table.name

        return None

    def _prepare_items(self, order_lines):
        return [{
            'product': line.product_id.display_name,
            'quantity': line.qty,
            'price_unit': line.price_unit,
            'total': line.price_subtotal,
        } for line in order_lines]

    def _merge_items(self, items):
        merged = {}

        for item in items:
            name = item['product']

            if name in merged:
                merged[name]['quantity'] += item['quantity']
                merged[name]['total'] += item['total']
            else:
                merged[name] = item.copy()

        return list(merged.values())

    def _send_self_order_notification(self, order, items, table_num):
        message = "🔔 New Self Order\n"
        message += f"Table {table_num}:\n\n"

        for item in items:
            message += f"{int(item['quantity'])} x {item['product']}\n"

        _logger.info(message)

        self.env['bus.bus']._sendone(
            'pos_order_notification',
            'new_self_order',
            {
                'message': message,
                'order_id': order.id,
                'items': items,
                'type': 'new_self_order'
            }
        )

    # -------------------------
    # WRITE
    # -------------------------

    def write(self, vals):

        previous_quantities = {
            order.id: {line.id: line.qty for line in order.lines}
            for order in self
        }

        res = super().write(vals)

        for order in self:

            if order.source != 'mobile':
                continue

            changed_items = []
            old_quantities = previous_quantities.get(order.id, {})

            for line in order.lines:
                old_qty = old_quantities.get(line.id, 0)

                if line.qty > old_qty:
                    added_qty = line.qty - old_qty

                    changed_items.append({
                        'product': line.product_id.display_name,
                        'quantity': added_qty,
                        'price_unit': line.price_unit,
                        'total': added_qty * line.price_unit,
                    })

            if not changed_items:
                continue

            # 🔥 Try to get table
            table = order.self_ordering_table_id or order.table_id

            # ❌ If missing → force refresh AFTER commit
            if not table:
                self.env.cr.commit()  # 🔥 force DB sync

                fresh_order = self.env['pos.order'].sudo().browse(order.id)
                table = fresh_order.self_ordering_table_id or fresh_order.table_id

            if not table:
                _logger.warning("Still no table after retry for order %s", order.id)
                continue

            table_num = table.table_number or table.name

            _logger.info("Additional items ordered: %s", changed_items)

            self._send_self_order_notification(order, changed_items, table_num)

        return res