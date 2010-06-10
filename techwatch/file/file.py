from subprocess import Popen, PIPE
import os, tempfile

class backend( object ):
	"""
	This format detector backend uses the Unix-tool "file" to detect file
	formats. It is much faster than L{fits}.
	
	@see: L{techwatch.file}
	"""

	def detect( self, data ):
		"""
		Detect the fileformat of the data. This method uses pipes for
		files smaller than 100KB (which is faster, but doesn't work for
		larger files) and creates a temporary file for larger files. 

		@raise RuntimeError: If file returns with an error code.
		@return: The file format detected.
		@see: L{techwatch.file}
		"""
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
		"""
		Detect if the detected fileformat is parseable HTML.

		@return: True if yes, False otherwise.
		@see: L{techwatch.file}
		"""
		if self.format == b'HTML document text':
			return True
		elif self.format == b'UTF-8 Unicode HTML document text, with very long lines':
			return True

		return False

