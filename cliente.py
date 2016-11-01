# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore, uic
from xmlrpc.client import ServerProxy

MainWindowUI, MainWindowBase = uic.loadUiType("cliente.ui")


class Cliente(MainWindowUI, MainWindowBase):
	def __init__( self ):
		super( Cliente, self ).__init__()
		uic.loadUi( 'cliente.ui', self )
		self.setupUi(self)
		self.espera = 0
		self.timer = QtCore.QTimer( self )
		self.timer.timeout.connect( self.estado_juego )
		self.timer.start(self.espera)
		self.servidor = None
		self.snake = False
		self.redimensionar()
		self.poner_lienzo_celdas()
		self.clickers()
		self.tabla.setSelectionMode( QtGui.QTableWidget.NoSelection )


	def conexion( self ):
		url = self.url.text()
		puerto = self.puerto.value()

		self.servidor = ServerProxy( "http://"+url+":"+str(puerto) )
		#self.servidor = ServerProxy( "http://127.0.0.1:8000" )


	def conectar_con_ping( self ):
		self.ping_pong.setText("Pinging...")
		
		try:
			self.conexion()
			pong = self.serv.ping()
			print(pong)
			self.ping_pong.setText("¡Pong!")
		except:
			self.ping_pong.setText("No pong :(")

	def conectar_con_yo_juego( self ):
		if self.servidor is None :
			return

		datos = self.servidor.yo_juego()
		self.id.setValue(datos["id"])
		self.color.setValue(datos["color"])
		#desabilita la entrada de datos en esos input (lool)
		self.id.configure(state="disabled")
		self.color.configure(state="disabled")
		self.snake = True

	def conectar_con_cambia_direccion( self, teclita ):
		id = self.id.text()

		if teclita == QtCore.Qt.Key_Up:
			direccion = 0
		if teclita == QtCore.Qt.Key_Down:
			direccion = 2
		if teclita == QtCore.Qt.Key_Left:
			direccion = 3
		if teclita == QtCore.Qt.Key_Right:
			direccion = 1

		self.servidor.cambia_direccion( id, direccion )


	def eventFilter( self, source, event ):
		if event.type() == QtCore.QEvent.KeyPress and source is self.tabla :
			teclita = event.key()
			self.conectar_con_cambia_direccion(teclita)


	def estado_juego( self ):
		if self.servidor is None or not self.snake:
			return

		self.tabla.installEventFilter(self)
		datos = self.servidor.estado_del_juego()
		self.cambio_espera(datos["espera"])
		columnas = datos["tamX"]
		filas = datos["tamY"]
		snakes = datos["viboras"]

		self.cambio_numero_celdas(filas,columnas)

		for snake in snakes:
			R = snake["color"]["r"]
			G = snake["color"]["g"]
			B = snake["color"]["b"]
			for cachito_snake in snake["camino"]:
				tabla.item( cachito_snake_bb[0], cachito_snake[1] ).setBackground( QtGui.QColor( R, G, B ) )


	def cambio_espera( self, espera ):
		if self.espera != espera:
			self.espera = espera
			self.timer.setInterval(espera)


	def redimensionar(self):
		self.tabla.verticalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
		self.tabla.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)


	def poner_lienzo_celdas( self ):
		self.tabla.setSelectionMode(QtGui.QTableWidget.NoSelection)
		for i in range( self.tabla.rowCount() ) :
			for j in range( self.tabla.columnCount() ) :
				self.tabla.setItem( i, j, QtGui.QTableWidgetItem() )
				self.tabla.item( i, j ).setBackground( QtGui.QColor( 0, 0, 0 ) )


	def cambio_numero_celdas( self, filas, columnas ):
		self.tabla.setRowCount(filas)
		self.tabla.setColumnCount(columnas)
		self.poner_lienzo_celdas()
		self.redimensionar()


	def clickers( self ):
		self.ping_pong.clicked.connect( self.conectar_con_ping )
		self.participar.clicked.connect( self.conectar_con_yo_juego )


app = QtGui.QApplication(sys.argv)
window = Cliente()
window.show()
sys.exit(app.exec_())
