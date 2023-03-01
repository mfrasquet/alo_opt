# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import random
import numpy as np
import pandas as pd

#INPUTS INICIALES
#num_op = [1,2,3,4] #numero operarios
jornada_ini = 8 #HOD Hour of day comienzo jornada
jornada_end = 18 #HOD Hour of day final jornada

coste_hora = 10 # euros/hora
goal = 4 #Objetivo de producción 

num_max_steps = 480 #número máximo horas en la simulación
superficie_libre_ini=10000
superficie_libre = superficie_libre_ini



class Componente:
    """
    Define un componente 
    """
    def __init__(self, id, name, inv,area,hijos = []):
        self.id = id
        self.name = name
        self.inv = inv
        self.inv_acum_h = []
        self.hijos = hijos
        self.area = area

class Tarea:
    """
    Define una tarea
    """
    def __init__(self, id,name,componente,horas_min,coste,ritmo,ayudantes_req = 0):
        self.id = id
        self.componente = componente
        self.name = name
        self.horas_min = horas_min
        self.coste = coste
        self.ritmo = ritmo
        self.ayudantes_req = ayudantes_req


class Operario:
    """
    Define un operario
    """
    def __init__(self, id,name,tarea):
        self.id = id
        self.proceso = 0
        self.name=name
        self.tarea = tarea
        self.coste_acum = 0
        self.tarea_anterior = tarea
        self.ayudando_a = None
        
        self.proceso_h = []
        self.tarea_h = []
        self.coste_acum_h = []
        self.ayudando_a_h = []

# ### PROBLEMA COMPLEJO

# comp_0 = Componente(0,'ala',0,10)
# comp_1 = Componente(1,'centro',0,10)
# comp_2 = Componente(2,'espejo',0,10)
# comp_3 = Componente(3,'tracking',0,10)
# comp_4 = Componente(4,'semieje',0,10,[{'comp':comp_0,'unid_req':2},{'comp':comp_1,'unid_req':1}])
# comp_5 = Componente(5,'eje',0,10,[{'comp':comp_2,'unid_req':4},{'comp':comp_4,'unid_req':2}])
# comp_6 = Componente(6,'modulo',0,10,[{'comp':comp_5,'unid_req':3},{'comp':comp_3,'unid_req':4}])

# componentes = [comp_0,comp_1,comp_2,comp_3,comp_4,comp_5,comp_6]

# ocio = Tarea(0,'ocio',[],0,0,0)
# tarea_1 = Tarea(1,'alas',[comp_0],1,10,1)
# tarea_2 = Tarea(2,'centros',[comp_1],1,10,1)
# tarea_3 = Tarea(3,'espejos',[comp_2],1,10,1)
# tarea_4 = Tarea(4,'tracking',[comp_3],1,10,1)
# tarea_5 = Tarea(5,'ejes',[comp_4,comp_5],1,10,1)
# tarea_6 = Tarea(6,'modulo',[comp_6],1,10,1,1)

# tareas = [tarea_1,tarea_2,tarea_3,tarea_4,tarea_5,tarea_6]

# op_0 = Operario(0,'ruben',ocio)
# op_1 = Operario(1,'yeray',ocio)
# op_2 = Operario(2,'miguel',ocio)
# operarios = [op_0,op_1,op_2]

## PROBLEMA SIMPLE

comp_3 = Componente(3,'tracking',0,10)
comp_5 = Componente(5,'eje',0,10)
comp_6 = Componente(6,'modulo',0,10,[{'comp':comp_5,'unid_req':3},{'comp':comp_3,'unid_req':4}])

componentes = [comp_3,comp_5,comp_6]

ocio = Tarea(0,'ocio',[],0,0,0)
tarea_4 = Tarea(4,'tracking',[comp_3],1,10,1)
tarea_5 = Tarea(5,'ejes',[comp_5],1,10,1)
tarea_6 = Tarea(6,'modulo',[comp_6],1,10,1,1)

tareas = [tarea_4,tarea_5,tarea_6]

op_0 = Operario(0,'ruben',ocio)
op_1 = Operario(1,'yeray',ocio)
op_2 = Operario(2,'miguel',ocio)

operarios = [op_0,op_1,op_2]

### --------------------------


zeros = np.zeros(num_max_steps)

dict_pandas ={'hora_dia':zeros,'jornada':zeros}
for op in operarios:
    dict_pandas.update({op.name+'_tarea':zeros,op.name+'_proceso':zeros,op.name+'_ayudando':zeros,op.name+'_coste':zeros,op.name+'_tar_ant':zeros})

for comp in componentes:
    dict_pandas.update({comp.name:zeros})

dict_pandas.update({'superf':zeros})

data = pd.DataFrame(dict_pandas)
### -----------------------------


def check_area(tarea,superficie_libre):
    """
    Verifica que hay espacio suficiente
    """
    return tarea.componente[0].area * tarea.ritmo < superficie_libre

def check_hours(tarea,hora_dia,jornada_end):
    """
    Verifica que suficientes horas disponibles para las horas mínimas de tarea
    """
    return tarea.horas_min + hora_dia <= jornada_end

def check_horario(hora_dia,jornada_ini,jornada_end):
    """
    Verifica que estoy en la jornada laboral
    """
    return hora_dia >= jornada_ini and hora_dia <jornada_end

def check_ayudantes(tarea,operarios):
    return tarea.ayudantes_req < sum(1 for op in operarios if op.proceso == 0)

def check_inventario(tarea):
    grupo_comp_tarea = tarea.componente
    for c in tarea.componente:
        for h in c.hijos:
            if h['comp'] in grupo_comp_tarea:
                pass
            else:
                if h['comp'].inv < h['unid_req'] * tarea.ritmo:
                    return False
    return True

def operario_bloqueado(op):
    op.proceso_h.append(op.proceso)
    calculo_coste(op,hora_dia)
    op.tarea_h.append('ocio')
    op.ayudando_a_h.append('')
    return

def calculo_coste(op,hora_dia):
    # Calculo el coste de trabajo de los operarios
    if op.tarea_anterior != op.tarea:
        if hora_dia == jornada_ini:
            op.coste_acum_h.append(coste_hora)
        else: 
            op.coste_acum_h.append(coste_hora*1.1) #Aumento del coste por cambio de tarea
    else:
        op.coste_acum_h.append(coste_hora)
    return

def operario_trabajando_nueva_tarea(op,superficie_libre):
    if op.ayudando_a == None: #Soy el operario principal de la tarea, los ayudantes no modifican inventario ni superficie
        for comp in op.tarea.componente:
            
            comp.inv +=op.tarea.ritmo #Modifico inventario de cada componentes de la tarea
            superficie_libre -= comp.area * op.tarea.ritmo #Reduzco la superficie libre ya que un nuevo componente ha sido fabricado
            
            # Actualizo los hijos
            for hijo in comp.hijos:
                hijo['comp'].inv -=hijo['unid_req'] * op.tarea.ritmo  # Reduzco el inventario de los hijos del componente al haber sido utilizados
                superficie_libre += hijo['comp'].area * hijo['unid_req'] * op.tarea.ritmo  # Aumento la superficie libre ya que los hijos de ese componente han sido utilizados
    
    op.proceso_h.append(op.proceso)
    op.ayudando_a_h.append('')
    calculo_coste(op,hora_dia)

        
    
    data.loc[i,op.name+'_tar_ant'] = op.tarea_anterior.name 
    data.loc[i,op.name+'_coste'] = op.coste_acum
    

    op.tarea_anterior = op.tarea
    
   
    return

def operario_sigue_en_tarea(op):
    op.proceso_h.append(op.proceso)
    calculo_coste(op,hora_dia)
    
    #Registro en el dataframe

    data.loc[i,op.name+'_tar_ant'] = op.tarea_anterior.name


    op.tarea_anterior = op.tarea

    data.loc[i,op.name+'_coste'] = op.coste_acum
    return

hora_dia=0
i=0
while i < num_max_steps and comp_6.inv < goal:
    data.loc[i,'hora_dia'] = hora_dia
    if check_horario(hora_dia,jornada_ini,jornada_end):
        data.loc[i,'jornada'] = 'dentro'
        
        #Los operarios seleccionan la tarea en la que trabajar
        for op in operarios:
            if op.proceso == 0:
                
                # Estrategias de seleccion de tarea
                
                tarea_activa = random.choice(tareas)
                
                # ---------------------------------
                
                data.loc[i,op.name+'_tarea'] = tarea_activa.name
                if check_area(tarea_activa,superficie_libre):
                    if check_hours(tarea_activa,hora_dia,jornada_end):
                        if check_inventario(tarea_activa):
                            if check_ayudantes(tarea_activa,operarios):
                                op.tarea = tarea_activa
                                op.tarea_h.append(tarea_activa.name)
                                op.proceso = tarea_activa.horas_min
                                data.loc[i,op.name+'_proceso'] = op.proceso
                                if op.tarea.ayudantes_req > 0:
                                    # El operario busca otro operario libre para que le ayude
                                    ayudante = operarios[[i for i in range(len(operarios)) if operarios[i].proceso == 0][0]]
                                    #El operario le dice al primer operario libre que le ayude en su tarea
                                    ayudante.ayudando_a = op
                                    ayudante.ayudando_a_h.append(op.name)
                                    ayudante.tarea = tarea_activa
                                    ayudante.tarea_h.append(tarea_activa.name)
                                    ayudante.proceso = tarea_activa.horas_min
                                    #Registro en dataframe
                                    data.loc[i,ayudante.name+'_ayudando'] = op.name
                                    data.loc[i,ayudante.name+'_proceso'] = ayudante.proceso
                                    data.loc[i,ayudante.name+'_tarea'] = ayudante.tarea.name
        

                if op.proceso > 0:
                    operario_trabajando_nueva_tarea(op,superficie_libre)
                else:
                    operario_bloqueado(op)
                    
            else: #Operario continua con la tarea (de más de 1h)
                operario_sigue_en_tarea(op)
        
        
        #Todos los operarios terminan la hora de trabajo
        for op in operarios:
            op.proceso = max(0,op.proceso -1)
            #Si la tarea ha terminado, reseteo las variables
            if op.proceso == 0:
               op.ayudando_a = None
            
    else:
        for op in operarios:
            op.ayudando_a_h.append('')
            op.proceso_h.append(0)
            op.coste_acum_h.append(0)
            op.tarea_h.append('ocio')
        data.loc[i,'jornada'] = 'fuera'




    # Alimento el dataframe
    for comp in componentes:
        comp.inv_acum_h.append(comp.inv)
        data.loc[i,comp.name] = comp.inv    
    
    data.loc[i,'superf'] = superficie_libre    
    
    
    hora_dia+=1
    i+=1
    if hora_dia == 24:
        hora_dia = 0


#### Results
superficie_ocupada = superficie_libre_ini - min(data[data['superf'] > 1]['superf'])
coste_operarios = sum(op.coste_acum for op in operarios)
semanas_totales = i/7

print("\n --- RESULTADOS ---\n superficie ocupada:",
      superficie_ocupada," m2 \n coste operarios: ",
      coste_operarios, " € \n semanas totales: ",
      round(semanas_totales,2))
