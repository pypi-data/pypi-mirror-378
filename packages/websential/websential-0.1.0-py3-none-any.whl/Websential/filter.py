payment = [
    "payment", "checkout", "pay", "billing", "invoice", "pricing",
    "subscription", "renewal", "credit_card", "debit_card", "card_payment",
    "payment_gateway", "stripe", "paypal", "apple_pay", "google_pay",
    "bank_transfer", "wire_transfer", "transaction", "charge", "amount",
    "currency", "receipt", "refund", "wallet", "deposit", "withdraw",
    "payout", "secure_payment", "plan_upgrade", "billing_address",
    "checkout_session"
]

oauth = [
    "oauth", "openid", "saml", "federated", "social_login", "provider",
    "login_provider", "third_party_login", "delegated_auth", "external_auth",
    "identity_provider"
]

authz = [
    "security", "authz", "access", "access_level", "role", "roles",
    "permission", "permissions", "admin", "superadmin", "admin_panel",
    "admin_console", "dashboard", "grant_access", "access_rights"
]

verify = [
    "verify", "verification", "validate", "validation", "email_verify",
    "phone_verify", "check_email", "check_code", "confirm", "confirmation",
    "pin", "otp", "2fa", "mfa", "multifactor", "challenge_response",
    "code_sent", "code_input"
]

token = [
    "token", "access_token", "refresh_token", "id_token", "jwt",
    "session_token", "api_key", "secret", "sso", "csrf", "cookie",
    "authorization_token", "bearer", "ttl", "expires_in", "scope_token",
    "token_type"
]

password = [
    "password", "change_password", "update_password", "forgot",
    "forgot_password", "reset", "password_reset", "pin_reset", "recovery",
    "recover", "restore_account", "security_question", "passcode",
    "password_expired"
]

account = [
    "user", "users", "account", "accounts", "profile", "my_account",
    "my_profile", "current_user", "identity", "preferences", "settings",
    "avatar", "timezone", "locale", "user_settings", "personal_data"
]

register = [
    "register", "signup", "sign-up", "sign_up", "enroll", "create_account",
    "start_session", "open_account", "submit_registration", "new_user",
    "accept_invite", "invitation_code", "user_onboarding"
]

auth = [
    "auth", "authenticate", "login", "signin", "sign-in", "sign_in", "logout",
    "signout", "sign-out", "sign_out", "reauthenticate", "session_start",
    "session_end", "login_attempt"
]

keyw = {
    "payment": payment,
    "oauth": oauth,
    "authz": authz,
    "verify": verify,
    "token": token,
    "password": password,
    "account": account,
    "register": register,
    "auth": auth
}

def type(urls, group=''):
    results = []
    search_groups = keyw.values() if group == '' else [keyw.get(group, [])]

    for url in urls:
        for words in search_groups:
            for w in words:
                if w in url:
                    results.append(url)
                    break
            else:
                continue
            break

    return results