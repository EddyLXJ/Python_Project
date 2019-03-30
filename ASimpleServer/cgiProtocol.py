from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import subprocess

# class base_case(object):
#     '''Parent for case handlers.'''

#     def handle_file(self, handler, full_path):
#         try:
#             with open(full_path, 'rb') as reader:
#                 content = reader.read()
#             handler.send_content(content)
#         except IOError as msg:
#             msg = "'{0}' cannot be read: {1}".format(full_path, msg)
#             handler.handle_error(msg)
    
#     def index_path(self, handler):
#         return os.path.join(handler.full_path, 'index.html')
    
#     def test(self, handler):
#         assert False, 'Not implemented.'

#     def act(self, handler):
#         assert False, 'Not implemented.'
    
# class case_existing_file(base_case):
#     def test(self, handler):
#         return os.path.isfile(handler.full_path)
    
#     def act(self, handler):
#         self.handle_file(handler, handler.full_path)
class case_cgi_file(object):
    def test(self, handler):
        return os.path.isfile(handler.full_path) and handler.full_path.endswith('.py')
    def act(self, handler):
        handler.run_cgi(handler.full_path)


class case_no_file(object):
    '''File or directory does not exise.'''
    def test(self, handler):
        return not os.path.exists(handler.full_path)
    def act(self, handler):
        raise Exception("'{0}' not found".format(handler.path))

class case_existion_file(object):
    '''File exists'''
    def test(self, handler):
        return os.path.isfile(handler.full_path)
    def act(self, handler):
        handler.handle_file(handler.full_path) 

class case_always_fail(object):
    '''Base case if nothing else worded'''

    def test(self, handler):
        return True
    
    def act(self, handler):
        raise Exception("Unknown object '{0}'".format(handler.path))

class case_directory_index_file(object):
    '''Serve index.html page for a directory.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')
    
    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))
    
    def act(self, handler):
        handler.handle_file(self.index_path(handler))

class case_directory_no_index_file(object):
    '''Serve listing for a directory without an index.html page.'''

    def index_path(self, handler):
        return os.path.join(handler.full_path, 'index.html')

    def test(self, handler):
        return os.path.isdir(handler.full_path) and os.path.isfile(self.index_path(handler))

    def act(self, handler):
        print('act')
        handler.list_dir(handler.full_path)

class RequestHandler(BaseHTTPRequestHandler):
    '''
    If the requested path maps to a file, that file is server
    If anything goes wrong, an error page is contructed.
    '''

    Cases = [
        case_cgi_file(),
        case_directory_no_index_file(),
        case_directory_index_file(),
        case_no_file(),
            case_existion_file(),
            
            case_always_fail()
            ]

    def do_GET(self):
        try:
            # Figure out what exactly is being requested
            self.full_path = os.getcwd() + self.path
            
            # Figure out how to handle if.
            for case in self.Cases:
                handler = case
                if handler.test(self):
                    print(handler)
                    handler.act(self)
                    break

        # Handle errors
        except Exception as msg:
            print(msg)
            self.handle_error(msg)

    def handle_file(self, full_path):
        try:
            with open(full_path, 'rb') as reader:
                content = reader.read()
            print(content)
            self.send_content_nob(content)
        except IOError as msg:
            msg = "'{0}' cannot be read: {1}".format(self.path, msg)
            self.handle_error(msg)

    Error_Page = '''
    <html>
    <body>
    <h1>Error accessing {path}</h1>
    <p>{msg}</p>
    </body>
    </html>
    '''

    Listing_Page = '''
    <html>
    <body>
    <ul>
    {0}
    </ul>
    </body>
    </html>
    '''
    # Handle unknow objects
    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg = msg)
        self.send_content(content, 404)

    # Send actual content
    def send_content(self, content, status = 200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content.encode())

    # Send actual content
    def send_content_nob(self, content, status = 200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def list_dir(self, full_path):
        try:
            entries = os.listdir(full_path)
            bullets = ['<li>{0}</li>'.format(e) for e in entries if not e.startswith('.')]
            page = self.Listing_Page.format('\n'.join(bullets))
            self.send_content(page)
        except OSError as msg:
            msg = "'{0}' cannot be listed: {1}".format(self.path, msg)
            self.handle_error(msg)

    def run_cgi(self, full_path):
        cmd = "python3 " + full_path
        child_stdin = os.popen(cmd)
        
        data = child_stdin.read()
        
        self.send_content(data)

if __name__ == '__main__':
    serverAdderss = ('', 8080)
    server = HTTPServer(serverAdderss, RequestHandler)
    server.serve_forever()

