from subprocess import Popen, PIPE
import os, tempfile


class file( object ):
	def detect( self, data ):
		if len( data ) < 10000:
			cmd = ['file', '-b', '-']
			p = Popen( cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE )
			stdout, stderr = p.communicate( data )
		else:
			# we get a broken pipe somewhere above 120kbyte, So 
			# go over a temporary file. This is slower, but safer.
			fd, name = tempfile.mkstemp()
			f = os.fdopen( fd, 'w+b' )
			f.write( data )
			f.flush()
			f.close()

			cmd = ['file', '-b', name ]
			p = Popen( cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE )
			stdout, stderr = p.communicate()
			os.remove( name )
		
		if p.returncode == 0:
			self.format = stdout.strip()
			return self.format
		else:
			raise RuntimeError( stderr )


	def ishtml( self ):
		if self.format == b'HTML document text':
			return True
		elif self.format == b'UTF-8 Unicode HTML document text, with very long lines':
			return True

		return False

