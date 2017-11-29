
from common.crypto import AESCipher

company = 'ytml'
company_username = 'ytmladmin'
company_password = ''
"""
`company_xxx` variable will be modified when user logged in, and reset
when logged out, is accessible to all other modules across the application
"""

crypto = AESCipher()
"""
`crypto` variable is an instance for AESCipher
"""
