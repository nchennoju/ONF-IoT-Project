# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server

PAGE_OLD="""\
<html>
<head>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<center><img src="stream.mjpg" width="640" height="480"></center>
</body>
</html>
"""

PAGE="""\
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Vision Pi</title>
    <link href="https://fonts.googleapis.com/css?family=Montserrat" rel="stylesheet">
    <style>

		/*General */
		html{    
		  background:#000;
		  background-size: cover;
		  height:100%;
		}
		body
		{
			font-family: 'Montserrat', Arial, Helvetica, sans-serif;
		}

		#form-main{
			width:100%;
			float:left;
			padding-top:0px;
		}

		#form-div {
			background-color:rgba(72,72,72,0.4);
			/*padding-left:35px;
			padding-right:35px;*/
			padding-top:35px;
			padding-bottom:10px;
			
		  	margin-top:20px;
		  	margin-bottom: 20px;
			margin-left: 10%;
			margin-right: auto;
			width: 80%;
		  	border-radius: 7px;
		  
		}

		#form-div img {
			display:block; margin: 0 auto
		}



		/*Styles for small screens*/
		@media  only screen and (max-width: 580px) {
			#form-div{
				margin-left: 3%;
				margin-right: 3%;
				width: 88%;
				padding-left: 3%;
				padding-right: 3%;
			}

			#form-div img{
				width: 420px;
			}
		}

	</style>


</head>
  <body >
      <div class="container">
        <div id="form-main">
  <div id="form-div">

    <form class="montform" id="reused_form">
      <h1 style="text-align: center; color: #fff;">Vision Pi - Stream</h1>
      <img src="stream.mjpg" width="640" height="480" style="">
    </form>
    
    <a href="https://www.public.asu.edu/~nchennoj/" target="_blank">
    	<button style="text-align: center; color: #787878; font-size: 12px; border: #5e5e5e solid 1px; cursor:pointer; background-color: #000; margin-top:5%; margin-left: 30%; margin-right: auto; width: 40%;" >Designed by Nitish C.</button>
    </a>


    </div>
    </div>
    </div>
      

      
  </body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()
