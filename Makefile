MODULES=techwatch
HTML_DIR=epydoc
NAME=techwatch

doc: doc-html

doc-html:
	epydoc -v --html -o ${HTML_DIR} --name ${NAME} --redundant-details --no-private ${MODULES}

check:
	epydoc --no-private --no-imports --check ${MODULES}

clean:
	-rm -rf ${HTML_DIR} ${PDF_DIR}

