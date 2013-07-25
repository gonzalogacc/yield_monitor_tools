########################################################################
## Por ahora este filtro agrega las pasadas al shape para seguir procesando con 
## el Filtro_monitores_con_pasada.py
########################################################################


	
from osgeo import ogr
from pylab import *
import matplotlib.pyplot as plt
import math,os
from numpy import *



class monitor():
	def __init__(self,archivo,col_rto):
		""" cuando se crea la instancia monitor hay que llamarla con el nombre 
		del archivo y la columna donde esta el rendimiento """
		
		self.archivo=archivo
		self.archivo_salida=directorio_salida+'/'+archivo[:-4]+'_pasadas.shp'
		self.columna_rto=col_rto
		
		def crear_shape(self,archivo):
			""" Crea un shape vacio al que despues se le va a agregar la informacion"""
			driver_entrada=ogr.GetDriverByName('ESRI shapefile')
			shape_entrada=driver_entrada.Open(archivo)
			capa_entrada=shape_entrada.GetLayer()
					
			archivo_salida=self.archivo_salida
					
			driver=ogr.GetDriverByName('ESRI shapefile')	
			shape_salida=driver.CreateDataSource(archivo_salida)
			
			capa_salida=shape_salida.CreateLayer(archivo_salida)
			
			for feature in range(capa_entrada.GetFeatureCount()-1):
				capa_salida.CreateFeature(capa_entrada.GetFeature(feature).Clone())

			shape_entrada.Destroy()
		try:
			crear_shape(self,self.archivo)
		except:
			print "el archivo ya se creo y solo se agregara una columna"
	
	
	def escribir_campo(self,nombre_campo,lista_campo,type=ogr.OFTReal,precision=5):
		""" toma una lista de una sola dimension y la escribe en el shape de salida como una nueva columna """
		driver_entrada=ogr.GetDriverByName('ESRI shapefile')
		shape_entrada=driver_entrada.Open(self.archivo_salida, update=True)
		capa_shape=shape_entrada.GetLayer()		
		
		campo=ogr.FieldDefn()
		campo.SetName(str(nombre_campo))
		campo.SetType(type)
		campo.SetWidth(precision)
		campo.SetPrecision(precision)
		
		capa_shape.CreateField(campo)
		
		for feature in range(capa_shape.GetFeatureCount()):
			feature_salida=capa_shape.GetFeature(feature)
			feature_salida.SetField(str(nombre_campo),lista_campo[feature])
			capa_shape.SetFeature(feature_salida)	

		
				
	def shape_a_lista(self,archivo,col_rto):
		""" abre el shape y lo devuelve como una lista de tipo [[x,y,rto],[x,y,rto],...,[x,y,rto]]"""
		rto=[]
		coords=[]
		drive=ogr.GetDriverByName('ESRI shapefile')
		shape=drive.Open(archivo,0)
		numero_capas=shape.GetLayerCount()
		##print numero_capas
		capa_shape=shape.GetLayer()
		##print capa_shape.GetFeatureCount()
		feat_capa=capa_shape.GetNextFeature()
		i=0
		while feat_capa:
			georef=feat_capa.GetGeometryRef()
			x=georef.GetX()
			y=georef.GetY()

			rto=feat_capa.GetField(col_rto)
			coords.append([x,y,rto])
			i+=1
			feat_capa=capa_shape.GetNextFeature()

		return coords
	
	

	
	def pasadas(self,escribir="no"):
		""" separa las pasadas basandose en la direccion y la guarda en una columna nueva """
		
		coords=self.shape_a_lista(self.archivo,self.columna_rto)
		limite_inf=-0.00007
		limite_sup=0.00007
		
		n_pasada=0
		
		lista_pasadasx=[]
		lista_rto=[]
		
		for i in range(len(coords)):
			if i<2:
				##lista_pasadas.append([coords[i][0],coords[i][1],coords[i][2],0,0])
				lista_pasadasx.append(0)
				pass
			else:
				derivada_x=(coords[i][0]-coords[i-1][0])-(coords[i-1][0]-coords[i-2][0])
				derivada_y=(coords[i][1]-coords[i-1][1])-(coords[i-1][1]-coords[i-2][1])
				derivada_rto=(coords[i][2]-coords[i-1][2])-(coords[i-1][2]-coords[i-2][2])
				
				if derivada_x<limite_inf or derivada_x>limite_sup or derivada_y<limite_inf or derivada_y>limite_sup:
					n_pasada+=1
				
				lista_pasadasx.append(n_pasada)
			lista_rto.append(coords[i][2])

	
		if escribir=="si":
			self.escribir_campo("pasadas",lista_pasadasx)
			self.escribir_campo("rto",lista_rto)
	
	def distancia(self,escribir="no"):
		""" separa las pasadas basadas en la distancia al punto inicial y lo pone como una columna """
		## Falta agregarle que ponga las pasadas en una lista para filtrarlas!!! en el pasadas de arriba esta hecho
		coords=self.shape_a_lista(self.archivo,self.columna_rto)
		lista_dist=[]
	
		punto_inicial=coords[0]
	
		for punto in range(len(coords)):
			if punto<2:
				distancia=0
			else:					
				distancia=math.sqrt((coords[punto][0]-punto_inicial[0])**2+(coords[punto][1]-punto_inicial[1])**2)
				dist_antes=math.sqrt((coords[punto-1][0]-punto_inicial[0])**2+(coords[punto-1][1]-punto_inicial[1])**2)
				dist_mas_antes=math.sqrt((coords[punto-2][0]-punto_inicial[0])**2+(coords[punto-2][1]-punto_inicial[1])**2)
				
				
				derivada=distancia-dist_antes
				lista_dist.append(distancia)
				##print derivada
		
		lista_derivada2=[]
		for punt2 in range(len(lista_dist)):
			derivada2=lista_dist[punt2]-lista_dist[punt2-1]
			if derivada2<0:
				lista_derivada2.append(0)
			else:
				lista_derivada2.append(1)
				
		pasada=0
		lista_pasada=[]
		for i in range(len(lista_derivada2)):
			actual=lista_derivada2[i]
			anterior=lista_derivada2[i-1]
			mas_anterior=lista_derivada2[i-2]
			if anterior==actual:## and actual==mas_anterior:
				lista_pasada.append(pasada)
			else:
				pasada=pasada+1
				lista_pasada.append(pasada)
				
				
		##return lista_pasada
		for cv in lsita_pasada:
			print cv
				
		if escribir=="si":
			self.escribir_campo("distancia",lista_pasada)
			##return lista_pasada

def col_rto(archivo):
	driver=ogr.GetDriverByName('ESRI Shapefile')
	monitor=driver.Open(archivo)
	
	ds=monitor.GetLayer()
	
	feature=ds.GetNextFeature()
	
	## Agarra los indices de los campos que quiero usar
	lista_columnas=['Masa']
	for ff in range(feature.GetFieldCount()):
		if feature.GetFieldDefnRef(ff).GetNameRef()[:4] in lista_columnas:
			return feature.GetFieldIndex(feature.GetFieldDefnRef(ff).GetNameRef())
	

	
## -------------------------> Configuracion para usarlo en directorio<--------------------------------------------------
##
##
columna=16
directorio='/home/lart/Escritorio/Rasters_monit/PedidosRaster1'
directorio_salida='/home/lart/Escritorio/Rasters_monit/Pasadas'
##
##----------------------------------------------------------------------------------------------------------------------

os.chdir(directorio)

lista_entrada=[]
for archivo in os.listdir(directorio):
        if archivo[-4:]=='.shp':
                lista_entrada.append(archivo)

print lista_entrada


cont_lote_lista=0
for i in lista_entrada:
	print i
	##columna=col_rto(i)
	##print columna
	mon=monitor(i,columna)
	mon.pasadas("si")
