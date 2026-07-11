from odoo import http
from odoo.http import request
import json
from odoo.addons.hb_jwt.controllers.main import (
    _param,
    _encode_jwt,
    _json_error,
    _json_success,
    _refresh_ttl_days,
    _hash_token,
    _new_refresh_token_string,
    _client_fingerprint,
    JwtApiController
)
from odoo.addons.hb_jwt.controllers.helpers import POST_PARAMS

class PickbazarJwtApiController(JwtApiController):

    @http.route(["/api/auth/login", "/api/token"], **POST_PARAMS)
    def api_login(self, **kwargs):
        params = json.loads(request.httprequest.data or "{}") or {}
        login = (params.get("login") or params.get("email") or "").strip()
        password = params.get("password") or ""
        db = request.env.cr.dbname

        if not login or not password:
            return _json_error("login and password are required")
        try:
            user = request.session.authenticate(db, {'login': login, 'password': password, 'type': 'password'})
            uid = user.get('uid')

            access_token = _encode_jwt(uid, login)

            # Issue refresh token (opaque, stored hashed)
            raw_refresh = _new_refresh_token_string()
            ua, ip = _client_fingerprint()
            request.env["jwt.refresh.token"].create_token(
                request.env["res.users"].sudo().browse(uid),
                _hash_token(raw_refresh),
                _refresh_ttl_days(),
                ua=ua, ip=ip,
            )

            result = {
                "token": access_token,
                "permissions": ["customer"],
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": int(_param("jwt.ttl_seconds", "1296000")),
                "refresh_token": raw_refresh,
                "refresh_expires_in_days": _refresh_ttl_days(),
                "user": {"id": uid, "login": login},
            }
            return _json_success(result)
        except Exception as e:
            if type(e) == http.AccessDenied:
                return _json_error("Invalid credentials")
            return _json_error(str(e))
