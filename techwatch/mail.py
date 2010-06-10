"""
Mail an alert to the user.
"""

from techwatch import options
import smtplib

def send( message ):
	"""
	Very simple method to send a notification.
	"""

	frm = options.get( 'from' )
	to = options.get( 'to' )
	server = smtplib.SMTP( options.get( 'smtp_server' ) )
	headers = """From: %s
To: %s
Subject: Technology Watch notification""" %(frm, to)
	message = headers + "\n\n" + message
	server.sendmail( frm, to, message )
	server.quit()
