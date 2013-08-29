import os

html_files = []

def retrieve_doc_files():
	for r, d, files in os.walk("."):
	    for file in files:
	    	absfilepath = os.path.abspath(os.path.join(r,file))
	        if file.endswith(".html") and "htmldocs" not in absfilepath :
				html_files.append(absfilepath)
				print("[info] Adding => {}".format(file))
	totalfiles = len(html_files)
	print("[info] Found {} file{}".format(totalfiles, "s" if totalfiles > 1 or totalfiles == 0 else ""))

def copy_doc_files():
	import shutil
	if not os.path.exists("htmldocs"):
		os.mkdir("htmldocs")
		print("[info] Creating folder...")
	destination = "htmldocs"
	for file in html_files:
		basename = os.path.basename(file)
		shutil.copyfile(file, "htmldocs/{}".format(basename))
		print("[info] Copying {}...".format(basename))

def start_server():
	from http.server import HTTPServer, CGIHTTPRequestHandler
	os.chdir("htmldocs")
	httpd = HTTPServer(("localhost", 8080), CGIHTTPRequestHandler)
	print("[info] Server started. Send SIGING to stop")
	httpd.serve_forever()

if __name__ == "__main__":
	import sys
	args = sys.argv
	if len(args) > 1 and args[1] == "startserver":
		if sys.version_info.major > 3:
			start_server()
		else:
			print("[info] To start the server python >3 is required. Meanwhile, use python -m SimpleHTTPServer :P")
	# use => python docs.py startserver
	retrieve_doc_files()
	copy_doc_files()
	
