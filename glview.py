
import sys

import wx
import wx.glcanvas as glcanvas

from ctypes import *


try:
	from OpenGL.GL import *
	from OpenGL.GLU import *
	from OpenGL.GLUT import *
	haveOpenGL = True
except ImportError:
	haveOpenGL = False

#----------------------------------------------------------------------





class MyCanvasBase(glcanvas.GLCanvas):
	def __init__(self, parent):
		glcanvas.GLCanvas.__init__(self, parent, -1)
		self.init = False
		self.context = glcanvas.GLContext(self)

		self.lastx = self.x = 100
		self.lasty = self.y = 100
		self.size = None

		self.SetBackgroundStyle(wx.BG_STYLE_PAINT)

		self.Bind(wx.EVT_SIZE, self.OnSize)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
		self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
		self.Bind(wx.EVT_MOTION, self.OnMouseMotion)



	def OnSize(self, event):
		wx.CallAfter(self.DoSetViewport)
		event.Skip()


	def DoSetViewport(self):
		size = self.size = self.GetClientSize()
		self.SetCurrent(self.context)
		glViewport(0, 0, size.width, size.height)


	def OnPaint(self, event):
		dc = wx.PaintDC(self)
		self.SetCurrent(self.context)
		if not self.init:
			self.InitGL()
			self.init = True
		self.OnDraw()


	def OnMouseDown(self, evt):
		self.CaptureMouse()
		self.x, self.y = self.lastx, self.lasty = evt.GetPosition()


	def OnMouseUp(self, evt):
		self.ReleaseMouse()


	def OnMouseMotion(self, evt):
		if evt.Dragging() and evt.LeftIsDown():
			self.lastx, self.lasty = self.x, self.y
			self.x, self.y = evt.GetPosition()
			self.Refresh(False)




class CubeCanvas(MyCanvasBase):


	vertices = [
		-1.0,-1.0,-1.0, -1.0,-1.0, 1.0, -1.0, 1.0, 1.0,	 # Left Side
		-1.0,-1.0,-1.0, -1.0, 1.0, 1.0, -1.0, 1.0,-1.0,	 # Left Side
		 1.0, 1.0,-1.0, -1.0,-1.0,-1.0, -1.0, 1.0,-1.0,	 # Back Side
		 1.0,-1.0, 1.0, -1.0,-1.0,-1.0,	 1.0,-1.0,-1.0,	 # Bottom Side
		 1.0, 1.0,-1.0,	 1.0,-1.0,-1.0, -1.0,-1.0,-1.0,	 # Back Side
		 1.0,-1.0, 1.0, -1.0,-1.0, 1.0, -1.0,-1.0,-1.0,	 # Bottom Side
		-1.0, 1.0, 1.0, -1.0,-1.0, 1.0,	 1.0,-1.0, 1.0,	 # Front Side
		 1.0, 1.0, 1.0,	 1.0,-1.0,-1.0,	 1.0, 1.0,-1.0,	 # Right Side
		 1.0,-1.0,-1.0,	 1.0, 1.0, 1.0,	 1.0,-1.0, 1.0,	 # Right Side
		 1.0, 1.0, 1.0,	 1.0, 1.0,-1.0, -1.0, 1.0,-1.0,	 # Top Side
		 1.0, 1.0, 1.0, -1.0, 1.0,-1.0, -1.0, 1.0, 1.0,	 # Top Side
		 1.0, 1.0, 1.0, -1.0, 1.0, 1.0,	 1.0,-1.0, 1.0	 # Front Side
	]

	normals= [ 
		-1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, # Left Side
		-1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, # Left Side
		 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, # Back Side
		 0.0, -1.0, 0.0,0.0, -1.0, 0.0,0.0, -1.0, 0.0, # Bottom Side
		 0.0, 0.0, -1.0,0.0, 0.0, -1.0,0.0, 0.0, -1.0, # Back Side
		 0.0, -1.0, 0.0,0.0, -1.0, 0.0,0.0, -1.0, 0.0, # Bottom Side
		 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, # front Side
		 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, # right Side
		 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, # right Side
		 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, # top Side
		 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, # top Side
		 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0 # front Side
	]
	
	vbo1 = None 
	vbo2 = None

	def createAndCompileShader(self,type,source):
		shader=glCreateShader(type)
		glShaderSource(shader,[source])
		glCompileShader(shader)

		return shader


	def InitGL(self):
	
		vertex_shader= self.createAndCompileShader(GL_VERTEX_SHADER,"""

			out vec4 result;
			vec3 light;
			vec4 color;
			  
			void main(void)
			{
			  light = vec3(0.5,1.5,0.5);
			  color = vec4(0.5,0.5,0.5,0.1);

			  //vec4 V = gl_ModelViewMatrix * gl_Vertex;
			  //vec3 N = gl_NormalMatrix * gl_Normal ;

			  vec3 V = vec3(gl_ModelViewMatrix * gl_Vertex );
			  vec3 N = vec3(gl_ModelViewMatrix * vec4(gl_Normal,0.0));

			  vec3 L = normalize( light - V.xyz );
			  float distance = length( light - V.xyz);

			  //vec3 L = normalize( light - V);
			  //float distance = length( light - V);

			  float diffuse = max(dot(N, L),0.1);

			  diffuse = diffuse * (1.0 /(1.0+(0.8*distance*distance)));

			  result = color * (0.6+diffuse);

			  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
			  
			}
		""")

		fragment_shader= self.createAndCompileShader(GL_FRAGMENT_SHADER,"""

			in vec4 result;

			void main(void)
			{
			  gl_FragColor = result;

			}
		""")
		
		program=glCreateProgram()
		glAttachShader(program,vertex_shader)
		glAttachShader(program,fragment_shader)
		glLinkProgram(program)
		glUseProgram(program)	
		
	
		self.vbo1 = glGenBuffers(1)
		glBindBuffer (GL_ARRAY_BUFFER, self.vbo1)
		glBufferData (GL_ARRAY_BUFFER, len(self.vertices)*4, (c_float*len(self.vertices))(*self.vertices), GL_STATIC_DRAW)
		self.vbo2 = glGenBuffers(1)
		glBindBuffer (GL_ARRAY_BUFFER, self.vbo2)
		glBufferData (GL_ARRAY_BUFFER, len(self.normals)*4, (c_float*len(self.normals))(*self.normals), GL_STATIC_DRAW)
		
	
	
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity()
		gluPerspective(90,1,0.01,1000)
		gluLookAt(1.7,1.7,1.7,0,0,0,0,1,0)

		glEnable(GL_DEPTH_TEST)
		glDepthFunc(GL_LESS)
				
		

	def OnDraw(self):
		
	
		# clear color and depth buffers
		glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
		
		glShadeModel(GL_FLAT)
		glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
		glMatrixMode(GL_MODELVIEW)


		glEnableClientState(GL_VERTEX_ARRAY)
		glEnableClientState(GL_NORMAL_ARRAY)


		glBindBuffer (GL_ARRAY_BUFFER,self.vbo1)
		glVertexPointer (3, GL_FLOAT,0, None)
		
		glBindBuffer (GL_ARRAY_BUFFER,self.vbo2)
		glNormalPointer (GL_FLOAT, 0 ,None)

		n = len(self.vertices)//3
		glDrawArrays (GL_TRIANGLES, 0, n)
		  
		glBindBuffer (GL_ARRAY_BUFFER,0)

		glDisableClientState(GL_NORMAL_ARRAY)
		glDisableClientState(GL_VERTEX_ARRAY)
		
	

		if self.size is None:
			self.size = self.GetClientSize()
		w, h = self.size
		w = max(w, 1.0)
		h = max(h, 1.0)
		xScale = 180.0 / w
		yScale = 180.0 / h
		glRotatef((self.y - self.lasty) * yScale, 1.0, 0.0, 0.0);
		glRotatef((self.x - self.lastx) * xScale, 0.0, 1.0, 0.0);

		self.SwapBuffers()




#----------------------------------------------------------------------


if __name__ == '__main__':
	app = wx.App(False)
	if not haveOpenGL:
		wx.MessageBox('This sample requires the PyOpenGL package.', 'Sorry')
	else:
		frm = wx.Frame(None, title='GLCanvas Sample')
		canvas = CubeCanvas(frm)
		frm.Show()
	app.MainLoop()



#----------------------------------------------------------------------

