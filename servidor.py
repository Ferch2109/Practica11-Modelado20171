# -*- coding: utf-8 -*-

import sys, random, uuid
from PyQt4 import QtGui, QtCore, uic
from enum import Enum
from xmlrpc.server import SimpleXMLRPCServer

MainWindowUI, MainWindowBase = uic.loadUiType("servidor.ui")

class Dir(Enum):
	ARRIBA = 0
	ABAJO = 2
	IZQ = 3
	DER = 1

class Estado(Enum):
	EN_MARCHA = 5
	PAUSADO = 6
	REANUDAR = 7
	NINGUNO = 8

class Servidor(QtGui.QMainWindow):

	def __init__(self):
		super( Servidor, self ).__init__()
		uic.loadUi( 'servidor.ui', self )
		self.termina_juego.hide()
		self.estado = Estado.EN_MARCHA
		self.timer = QtCore.QTimer( self )
		self.timer_servidor = QtCore.QTimer( self )
		self.snakes_bebes = []
		self.servidor = None
		self.redimensionar()
		self.poner_lienzo_celdas()
		self.clickers()
		self.tabla.setSelectionMode( QtGui.QTableWidget.NoSelection )
    	#self.principal.setWidgetResizable(True)


	def redimensionar( self ):
		self.tabla.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.tabla.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)


	def poner_lienzo_celdas( self ):
		self.tabla.setSelectionMode(QtGui.QTableWidget.NoSelection)
		for i in range( self.tabla.rowCount() ) :
			for j in range( self.tabla.columnCount() ) :
				self.tabla.setItem( i, j, QtGui.QTableWidgetItem() )
				self.tabla.item( i, j ).setBackground( QtGui.QColor( 0, 0, 0 ) )


	def clickers( self ):
		self.columnas.valueChanged.connect( self.cambio_numero_celdas )
		self.filas.valueChanged.connect( self.cambio_numero_celdas )
		self.espera.valueChanged.connect( self.actualizar_espera )
		self.estado_juego.clicked.connect( self.edo_del_juego )
		self.termina_juego.clicked.connect( self.terminar_juego )
		self.timeout.valueChanged.connect( self.set_timeout )
		self.ping.clicked.connect( self.servidor )


	def edo_del_juego( self ):
		if self.estado == Estado.EN_MARCHA:
			self.iniciar_juego()
			self.estado = Estado.PAUSADO
		elif self.estado == Estado.PAUSADO:
			self.pausar_juego()
			self.estado = Estado.REANUDAR
		else:
			self.reanudar_juego()
			self.estado = Estado.PAUSADO


	def cambio_numero_celdas( self ):
		filas = self.filas.value()
		columnas = self.columnas.value()
		self.tabla.setRowCount(filas)
		self.tabla.setColumnCount(columnas)
		self.poner_lienzo_celdas()
		self.redimensionar()


	def actualizar_espera( self ):
		mili_seg = self.espera.value()
		self.timer.setInterval(mili_seg)


	def iniciar_juego( self ):
		self.termina_juego.show()
		self.estado_juego.setText( "PAUSAR JUEGO" )
		self.snakes_bebes.append(Snake())
		self.dibuja_snakes_bebes()
		self.timer.timeout.connect( self.mueve_snakes )
		self.timer.start( self.espera.value() )
		self.tabla.installEventFilter( self )


	def pausar_juego( self ):
		self.estado_juego.setText( "REANUDAR JUEGO" )
		self.timer.stop()
	

	def reanudar_juego( self ):
		self.estado_juego.setText( "PAUSAR JUEGO" )
		self.timer.start()


	def terminar_juego( self ):
		self.termina_juego.hide()
		self.estado = Estado.EN_MARCHA
		self.estado_juego.setText( "INICIAR JUEGO" )
		self.snakes_bebes = []
		self.timer.stop()
		self.poner_lienzo_celdas()


	def dibuja_snakes_bebes( self ):
		for snake_bb in self.snakes_bebes:
			snake_bb.pintate_de_colores(self.tabla)


	def eventFilter( self, source, event ):
		if event.type() == QtCore.QEvent.KeyPress and source is self.tabla :
			teclita = event.key()

			if teclita == QtCore.Qt.Key_Up and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.ABAJO:
						snake_bb.direccion = Dir.ARRIBA

			if teclita == QtCore.Qt.Key_Down and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.ARRIBA:
						snake_bb.direccion = Dir.ABAJO

			if teclita == QtCore.Qt.Key_Right and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.IZQ:
						snake_bb.direccion = Dir.DER

			if teclita == QtCore.Qt.Key_Left and source is self.tabla:
				for snake_bb in self.snakes_bebes:
					if snake_bb.direccion is not Dir.DER:
						snake_bb.direccion = Dir.IZQ

		return QtGui.QMainWindow.eventFilter( self, source, event )


	def autocanibal_snake( self, snake ):
		for cachito_snake in snake.cuerpo_snake[:len(snake.cuerpo_snake)-2]:
			if snake.cuerpo_snake[-1][0] == cachito_snake[0] and snake.cuerpo_snake[-1][1] == cachito_snake[1]:
				#ponermensajito
				return True
		return False


	def avanza_snakebb( self, snake ):
		if self.autocanibal_snake( snake ):
			self.snakes_bebes.remove( snake )
			self.poner_lienzo_celdas()
			snake_bebesita = Snake()
			self.snakes_bebes.append(snake_bebesita)
		
		self.tabla.item( snake.cuerpo_snake[0][0], snake.cuerpo_snake[0][1] ). setBackground( QtGui.QColor( 0, 0, 0 ) )
		chachito = 0

		for cachito_snake in snake.cuerpo_snake[ :len( snake.cuerpo_snake )-1 ]:
			chachito += 1
			cachito_snake[0] = snake.cuerpo_snake[chachito][0]
			cachito_snake[1] = snake.cuerpo_snake[chachito][1]

		if snake.direccion == Dir.ARRIBA:
			if snake.cuerpo_snake[-1][0] != 0:
				snake.cuerpo_snake[-1][0] -= 1
			else:
				snake.cuerpo_snake[-1][0] = self.tabla.rowCount()-1

		if snake.direccion == Dir.ABAJO:
			if snake.cuerpo_snake[-1][0]+1 < self.tabla.rowCount():
				snake.cuerpo_snake[-1][0] += 1
			else:
				snake.cuerpo_snake[-1][0] = 0

		if snake.direccion == Dir.DER:
			if snake.cuerpo_snake[-1][1]+1 < self.tabla.columnCount():
				snake.cuerpo_snake[-1][1] += 1
			else:
				snake.cuerpo_snake[-1][1] = 0

		if snake.direccion == Dir.IZQ:
			if snake.cuerpo_snake[-1][1] != 0:
				snake.cuerpo_snake[-1][1] -= 1
			else:
				snake.cuerpo_snake[-1][1] = self.tabla.columnCount()-1


	def mueve_snakes( self ):
		for snake_bb in self.snakes_bebes:
			self.avanza_snakebb( snake_bb )

		self.dibuja_snakes_bebes()


	def ping( self ):
		return "¡Pong!"

	
	def yo_juego( self ):
		snake_bebesita = Snake()
		return {'id': snake_bebesita.id, 'color':snake_bebesita.color}


	def busca_snakebb( self, id ):
		for snake in snakes_bebes:
			if snake.id == id:
				return snake
		return None


	def cambia_direccion( self, id_snake, dir_snake ):
		snake_bb = busca_snakebb( id_snake )

		if snake_bb == None:
			return

		snake_bb.direccion = dir_snake
		avanza_snakebb( snake_bb )

	def tupla( self, cuerpo_snake ):
		l = []
		for lista in cuerpo_snake:
			t = tuple(lista)
			l.append(t)
		return l


	def listas_viboras( self ):
		lista = []
		for snake_bb in snakes_bebes:
			 lista.append(
			 	{'id': snake_bb.id, 
			 	'camino': tupla(snake_bb.cuerpo_snake), 
			 	'color': snake_bb.color} )
		return lista


	def estado_del_juego( self ): #Ya habia hecho una que se llamaba asi :'c
		return {'espera': self.espera, 
				'tamX': self.columnas, 
				'tamY': self.filas, 
				'viboras': self.listas_viboras() }


	def peticiones( self ):
		self.servidor.handle_request()

	def servidor(self):
		self.servidor = SimpleXMLRPCServer( ( self.url.text() , 0 ) )
		self.servidor.timeout = 0
		puerto = self.servidor.server_address[1] 
		self.puerto.setValue(puerto)
		self.servidor.register_function(self.ping)
		self.servidor.register_function(self.yo_juego)
		self.servidor.register_function(self.cambia_direccion)
		self.servidor.register_function(self.estado_del_juego)
		self.timer_servidor.connect( self.peticiones )
		self.timer_servidor.start( self.servidor.timeout )


	def set_timeout( self ):
		self.servidor.timeout = self.timeout.valuue()
		self.timer_servidor.setInterval( self.timeout.value() )



class Snake():
	def __init__( self ):
		self.cuerpo_snake = [[0,0],[1,0],[2,0],[3,0],[4,0]]
		self.id = "snakebb:"+str(uuid.uuid4())
		self.tamanio = len( self.cuerpo_snake )
		self.direccion = Dir.ABAJO
		self.R, self.G, self.B = map( int, colores_bonis().split(" ") )
		self.color = {'r': self.R, 'g': self.G, 'b': self.B }


	def pintate_de_colores( self, tabla ):
			for cachito_snake_bb in self.cuerpo_snake:
				tabla.item( cachito_snake_bb[0], cachito_snake_bb[1] ).setBackground( QtGui.QColor( self.R, self.G, self.B ) )

def colores_bonis():
	R=G=B=0
	
	R = random.randint( 10, 255 )
	G = random.randint( 10, 255 )
	B = random.randint( 10, 255 )
	return str(R)+" "+str(G)+" "+str(B)

#SOBRE LA APP :V
app = QtGui.QApplication(sys.argv)
window = Servidor()
window.show()
sys.exit(app.exec_())
