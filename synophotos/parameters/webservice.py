
ENTRY_URL = '{url}/webapi/entry.cgi'

# potential additional fields (taken from web session) are:
# "action": external_login
# "enable_syno_token": "yes"
# "logintype": "local"
# "enable_device_token": "no"
# "rememberme": "0"
# "session": webui

LOGIN_PARAMS = {
	'api': 'SYNO.API.Auth',
	'version': 7,
	'method': 'login',
	'account': None, # needs to be filled
	'passwd': None, # needs to be filled
  'otp_code': '', # empty string when not using 2FA
}

LOGIN_MFA = {
	'api': 'SYNO.API.Auth',
	'version': 7,
	'method': 'login',
	'enable_syno_token': 'no',
	# ik_message: None,
	'account': None,
	'passwd': None,
	'otp_code': 999999,
	# 'enable_device_token': 'no',
	# 'timezone': '+01:00',
	'rememberme': 1,
}
