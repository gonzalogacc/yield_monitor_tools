########################################################################
##Filtro de puntos extremos de monitores por ventana movil##############
########################################################################

##Formula de calculo de la distancia
##D=TERM1/COS(ARCTAN(TERM2 X TERM3))
##TERM1=111.08956 X (DL + 0.000001)
##TERM2=COS(L1 + (DL/2))
##TERM3=(DG + 0.000001)/(DL + 0.000001)
##D=111.08956 X (DL + 0.000001)/COS(ARCTAN(COS(L1 + (DL/2)) X (DG + 0.000001)/(DL + 0.000001)))

########################################################################################################################
## Configuraciones 
##
## Lotes de sol de mayo quedaron muy bien con 40 metros de distancia y el limite inferior como el 0.55*promedio !!!
## esta es la configuracion mejorcita, ojo que puede borrar demasiados puntos en algunos lotes!!

import csv, time, os, math
try:
	from osgeo import ogr
except:
	import ogr


## ---------------------------------> Configuracion <-------------------------------------------------------------------
##
##
ventana_metros=25
proporcion=0.4
proporcion_arriba=0.75 ## --> esta funciona al reves que la anterior porque se suma al promedio para obtener el limite superior si es grande una mayor proporcion del promedio se sumara al promedio
columna=2
pasada=1
directorio='/home/lart/Escritorio/Rasters_monit/Pasadas'
directorio_salida='/home/lart/Escritorio/Rasters_monit/filtrados'
##
##----------------------------------------------------------------------------------------------------------------------



os.chdir(directorio)


class shapetools:
	def __init__(self):
		shapetools.rto=[]
		shapetools.xp=[]
		shapetools.yp=[]
		shapetools.i=0
		shapetools.listafinal=[]
	listafinal=[]
	def shape_a_lista(self,archivo,col_rto,col_pasada):
		""" Ventana: tamanio de la ventana en metros
			Proporcion: proporcion de la media que va a eliminar """
		drive=ogr.GetDriverByName('ESRI shapefile')
		shape=drive.Open(archivo,0)
		numero_capas=shape.GetLayerCount()
		print numero_capas
		capa_shape=shape.GetLayer()
		print capa_shape.GetFeatureCount()
		feat_capa=capa_shape.GetNextFeature()
		while feat_capa:
			georef=feat_capa.GetGeometryRef()
			x=georef.GetX()
			y=georef.GetY()
			di=feat_capa.GetField(col_rto)
			pasada=feat_capa.GetField(col_pasada)
			shapetools.rto.append(di)
			shapetools.yp.append(y)
			shapetools.xp.append([x,shapetools.i,pasada])
			shapetools.i+=1
			feat_capa=capa_shape.GetNextFeature()
			##feat_capa.Destroy()
		##self.capa_shape.Destroy()
		shapetools.xp.sort()
		
	def filtro(self,ventana,proporcion,proporcion_arriba):
		##define la equivalencia en grados y metros para la latitud del lote
		DL=1    		##1 grado de delta de longitud y en latitud 
		DG=1	
		L1=shapetools.xp[len(shapetools.xp)/2][1]	##ubica el lote en la latitud
		metro=111.08956*(DL+0.000001)/math.cos(math.atan(math.cos(L1+(DL/2))*(DG+0.000001)/(DL+0.000001)))
		grad=1/metro/1000   ##grados por metro
		## tamano de la ventana (en metros)
		tv=ventana 
		vent=grad*tv

		print '-->',time.clock()
		## Posicion del punto en la lista ordenada
		cont=0
		for x in shapetools.xp:
			templist=[]
			sumatoria=0
			size_n=0
			size_n_abajo=0
			size_n_arriba=0
			punto_central=shapetools.xp[cont][0]
			ventana_limite_x_inferior=punto_central-vent
			ventana_limite_x_superior=punto_central+vent
			ventana_limite_y_inferior=shapetools.yp[shapetools.xp[cont][1]]-vent
			ventana_limite_y_superior=shapetools.yp[shapetools.xp[cont][1]]+vent
			pasada_punto=[shapetools.xp[cont][2]]
			## busca los menores que estan mas arriba en el indice de la lista ordenada
			cont_abajo=cont
			while shapetools.xp[cont_abajo][0]<ventana_limite_x_superior and cont_abajo<len(shapetools.xp)-1:
				if shapetools.yp[shapetools.xp[cont_abajo][1]]>ventana_limite_y_inferior and shapetools.yp[shapetools.xp[cont_abajo][1]]<ventana_limite_y_superior and shapetools.xp[cont_abajo][2] != pasada_punto:
					sumatoria=sumatoria+shapetools.rto[cont_abajo]
					##print 'hit'
					size_n_abajo=size_n_abajo+1
				cont_abajo=cont_abajo+1
				
			
			## busca los mayores del rango que estan en los menores indices de la lista
			cont_arriba=cont
			while shapetools.xp[cont_arriba][0]>ventana_limite_x_inferior and cont_arriba>0:
				if shapetools.yp[shapetools.xp[cont_arriba][1]]>ventana_limite_y_inferior and shapetools.yp[shapetools.xp[cont_arriba][1]]<ventana_limite_y_superior and shapetools.xp[cont_arriba][2] != pasada_punto:
					sumatoria=sumatoria+shapetools.rto[cont_arriba]
					##print 'hit_arr'
					size_n_arriba=size_n_arriba+1
				cont_arriba=cont_arriba-1
			
			size_n=size_n_abajo+size_n_arriba
			
			promedio=sumatoria/float(size_n)
			##print promedio
			##comparacion, desicion y append
			if shapetools.rto[shapetools.xp[cont][1]]>promedio*proporcion and shapetools.rto[shapetools.xp[cont][1]]<(promedio+promedio*proporcion_arriba):
				shapetools.listafinal.append([shapetools.xp[cont][0],shapetools.yp[shapetools.xp[cont][1]],shapetools.rto[shapetools.xp[cont][1]]])
			cont=cont+1
			
		print 'Fin -->', (time.clock())

		print 'El archivo original tenia--> ', len(shapetools.xp),'registros'
		print 'El nuevo archivo tiene--> ', len(shapetools.listafinal),'registros'

	def escritura_shape(self,nombre_archivo_salida):
		## crea el shape 
		driver=ogr.GetDriverByName('ESRI shapefile')
		datasource=driver.CreateDataSource(nombre_archivo_salida)
		capa_shape=datasource.CreateLayer(nombre_archivo_salida,geom_type=ogr.wkbPoint)
		
		##definir los campos que va a tener el shape
		campo_x=ogr.FieldDefn()
		campo_x.SetName('long')
		campo_x.SetType(ogr.OFTReal)
		campo_x.SetWidth(10)
		campo_x.SetPrecision(10)
		capa_shape.CreateField(campo_x)
		
		campo_y=ogr.FieldDefn()
		campo_y.SetName('lat')
		campo_y.SetType(ogr.OFTReal)
		campo_y.SetWidth(10)
		campo_y.SetPrecision(10)
		capa_shape.CreateField(campo_y)
		
		campo_rto=ogr.FieldDefn()
		campo_rto.SetName('Rto')
		campo_rto.SetType(ogr.OFTReal)
		campo_rto.SetWidth(10)
		campo_rto.SetPrecision(10)
		capa_shape.CreateField(campo_rto)
		
		feature=ogr.Feature(capa_shape.GetLayerDefn())
		for i in shapetools.listafinal:
			long_x=i[0]
			lat_y=i[1]
			rto=i[2]
			
			wkt="POINT(" + str(long_x) + " " + str(lat_y) + ")"
			point=ogr.CreateGeometryFromWkt(wkt)
			
			##set geometry
			feature.SetGeometryDirectly(point)
			
			## set attributes
			feature.SetField('long',long_x)
			feature.SetField('lat',lat_y)
			feature.SetField('Rto',rto)
			
			capa_shape.CreateFeature(feature)
			
######################################################################################################################		


lista_entrada=[]
for archivo in os.listdir(directorio):
        if archivo[-4:]=='.shp':
                lista_entrada.append(archivo)

print lista_entrada


cont_lote_lista=0
for i in lista_entrada:
	i3=directorio_salida+'/'+i[:-4]+"f_40m.shp"
	print i
	obj_temp=shapetools()
	obj_temp.shape_a_lista(i,columna,pasada)
	obj_temp.filtro(ventana_metros,proporcion,proporcion_arriba)
	obj_temp.escritura_shape(i3)
	cont_lote_lista+=1

##archivo='4sj2010_pasadas.shp'
##archivo_salida='zzzz_'+archivo
##monit=shapetools()
##monit.shape_a_lista(archivo,2,1)
##monit.filtro(40,0.55)
##monit.escritura_shape(archivo_salida)
