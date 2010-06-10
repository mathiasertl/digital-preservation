=== Documentation ===

=== Requirements ===
This script is written in pure python 3. You must have python 3 installed in
order to run this script. 

The script detects file-formats either using the unix command-line tool file[1]
or FITS[2], which is based on the Java programming language. You must have at
least one of the tools available, but file is highly recommended (for speed).

Other then that, the tool requires epydoc[3] if you want to generate
Javadoc-style documentation. The documentation can be generated with the
Makefile and will be located in the directory epydoc/.

[1] http://en.wikipedia.org/wiki/File_%28command%29
[2] http://code.google.com/p/fits/
[3] http://epydoc.sourceforge.net

=== Running the script ===
The script can be run with no command-line parameters, but supports may
different parameters to customize behaviour. Please start watcher.py with --help
for a list of command-line options:
	./watcher.py --help

Usually you have to give at least the --to parameter (if you want to receive
notifications). So a typical invocation might look like:
	./watcher.py --max-depth 2 --to=e0326788@student.tuwien.ac.at \
		--smtp-relay=mgate.chello.at --seed=http://vowi.fsinf.at

=== Command-line parameters ===
The --help parameter gives a complete list of all parameters. This section
describes some parameters in more details:

  --database-backend
  	Specify a database backend. This is a dummy option and anything other
	than "sqlite" will result in an error.
  --from/--to
  	Specify the from/to address that notifications are sent to. Note that
	by default, the script sends messages to *me*, so please give your
	address at least for the To: field.
  --smtp-server
  	The script does not implement its own SMTP-server. You have to give it
	on the command-line. The default is mr.tuwien.ac.at, which works inside
	the network of the Vienna University of Technology. Generally, you have
	to use the SMTP-server of your network provider, e.g. if your provider
	is UPC, you should try mgate.chello.at.

=== Detection using FITS ===
If you want to use FITS, you must have a FITS installation configured. You must
also set the environment variable FITS_PATH to the path of your FITS-
installation. So if you extracted FITS in your home directory, run the script
like this:
	FITS_PATH=/home/user/fits-0.3.2 ./watcher.py

FITS acts as a meta-tool which consults many different tools to reach a
conclusion. If the tools disagree, a conflict is reported. My solution will take
whatever the majority of the tools concluded.

Note that FITS takes quite some time to run - it is *much* slower than the
file-backend.

