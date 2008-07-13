all: epydoc

epydoc:
	epydoc --html -o apidoc -v --graph all --no-private --exclude="__pkginfo__" --exclude="setup" -n "Logilab Indexer Module" ..

clean:
	rm -f *.html
	rm -rf apidoc
