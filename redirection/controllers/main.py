from odoo import http
from odoo.http import request
from odoo.exceptions import UserError
from odoo.addons.pos_self_order.controllers.orders import PosSelfOrderController


import ipaddress
import logging

_logger = logging.getLogger(__name__)

class OnyxRouting(http.Controller):

    def _is_menu_domain(self):
        return request.httprequest.host.startswith("menu.onyx-cafe.com")

    # Root redirect
    @http.route('/', type='http', auth='public', website=True, priority=1000)
    def root_redirect(self, **kwargs):
        if self._is_menu_domain():
            return request.redirect('/pos-self/1')
        return None

class OnyxOrderSecurity(PosSelfOrderController):

    def _is_internal(self):
        # Get real client IP (Cloudflare first, fallback to direct)
        ip = request.httprequest.headers.get("CF-Connecting-IP") or request.httprequest.remote_addr

        _logger.warning("Client IP detected: %s", ip)

        if not ip:
            return False

        try:
            ip_obj = ipaddress.ip_address(ip)

            # 🔧 Adjust networks if needed
            allowed_networks = [
                "185.217.184.0/24",  # public WiFi
                "192.168.1.0/24"            
            ]

            return any(ip_obj in ipaddress.ip_network(net) for net in allowed_networks)

        except ValueError:
            return False

    @http.route(
        "/pos-self-order/process-order/<device_type>/",
        auth="public",
        type="jsonrpc",
        website=True,
        csrf=False
    )
    def process_order(self, order, access_token, table_identifier, device_type):

        # 🔒 BLOCK outside WiFi
        if not self._is_internal():
            # return {
            #     "error": "Ordering is only available inside Onyx Cafe WiFi ☕"
            # }
            raise UserError("Ordering is only available inside Onyx Cafe WiFi ☕")

        # ✅ Allow normal behavior
        return super().process_order(order, access_token, table_identifier, device_type)