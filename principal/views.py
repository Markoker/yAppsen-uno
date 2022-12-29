from .models import *
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
import numpy as np
from datetime import datetime, timedelta
import pytz
import json

#region User

def login(rol):
  User = user.objects.get(ROL=rol)
  
  
  User.activo = True
  User.last_login = datetime.now()
  User.save()

def checkLogin(rol):
  User = user.objects.get(ROL=rol)
  
  if User.last_login + timedelta(hours=3) < datetime.now().astimezone(pytz.UTC) or not User.activo:
    User.activo = False
    User.save()
    return False
  else:
    User.last_login = datetime.now()
    User.save()
    return True

def logout(request,rol):
  User = user.objects.get(ROL=rol)
  User.activo = False
  User.save()
  return HttpResponseRedirect(reverse('index'))

#endregion

#region Utility
def round_matrix(matrix):
    rounded_matrix = []
    for i in range(len(matrix)):
        rounded_matrix.append([])
        for j in range(len(matrix[i])):
            if matrix[i][j] == 99:
                rounded_matrix[i].append("--.--")
            else:
              rounded_matrix[i].append("%05.2f" % matrix[i][j])
    return rounded_matrix

def print_pesos(matrix, round=False):
    a = np.array(matrix[:]).T.tolist()
    if round:
        a = round_matrix(a)
    for i in range(len(a)):
        print(a[i])

def weights(a, w=1):
    list = a[:]
    
    pesos_l = []
    for i in range(len(list)):
        pesos_l.append(0) 
        pesos_l[i] += list[i] + list[(i+1)%len(list)]*0.8*w + list[(i+2)%len(list)]*0.4*w + list[(i+3)%len(list)]*0.2*w + list[(i+4)%len(list)]*0.1*w + list[(i+5)%len(list)]*0.05*w + list[(i+6)%len(list)]*0.025*w + list[(i+7)%len(list)]*0.0125*w
        pesos_l[i] += list[(i-1)%len(list)]*0.8*w + list[(i-2)%len(list)]*0.4*w + list[(i-3)%len(list)]*0.2*w + list[(i-4)%len(list)]*0.1*w + list[(i-5)%len(list)]*0.05*w + list[(i-6)%len(list)]*0.025*w + list[(i-7)%len(list)]*0.0125*w
    
    return pesos_l

def gen_horas_estudio(ramo, horario, horas_preferentes, dias_preferentes, horas_inicio, horas_termino):
  #Cantidad de horas del ramo por dia
  horas_diarias = [0,0,0,0,0,0,0]
  print(dias_preferentes)
  
  for i in range(len(horario)):
    for j in range(len(horario[0])):
      if horario[i][j] == ramo:
        horas_diarias[i] += 1
        
  #make a list of list with the hours of the ramo repeated 15 times
  pesos = []
  for i in range(len(horas_diarias)):
    x = horas_diarias[i] - dias_preferentes[i]*0.3
    pesos.append([x for j in range(15)])
    
  horario_num = []
  for i in range(len(horario)):
      horario_num.append([])
      for j in range(len(horario[i])):
          if horario[i][j] != "----":
              horario_num[i].append(1)
          else:
              horario_num[i].append(0)
              
  for i in range(len(pesos)):
        for j in range(len(pesos[i])):
            pesos[i][j] = pesos[i][j] + horario_num[i][j] 
  
  pesos_porfila = pesos[:]
  pesos_porcolumna = np.array(pesos[:]).T.tolist()
  
  for i in range(len(pesos_porfila)):
    pesos_porfila[i] = weights(pesos_porfila[i], 2.4)
    
  for i in range(len(pesos_porcolumna)):
    pesos_porcolumna[i] = weights(pesos_porcolumna[i], 1)
  
  pesos_porcolumna = np.array(pesos_porcolumna[:]).T.tolist()
  
  for i in range(len(pesos)):
        for j in range(len(pesos[i])):
            pesos[i][j] = pesos_porfila[i][j] + pesos_porcolumna[i][j]
            if horario_num[i][j] == 1:
              pesos[i][j] = 99
            if j < horas_inicio[i] or j > horas_termino[i]:
              pesos[i][j] = 99

  minimo = pesos[0][0]
  index_minimo = [0,0]
  for i in range(len(pesos[0])):
      for j in range(len(pesos)):
          if pesos[j][i] < minimo:
            minimo = pesos[j][i] 
            index_minimo = [j,i]

  return index_minimo

def Gen_color(val):  
  # -1 -> 168, 50, 50
  # 0 -> 176, 179, 184
  # 1 -> 50, 168, 82
  
  val = val if val <= 1 else 1
  val = val if val >= -1 else -1
  
  if val < 0:
    r = int((val + 1)*(176 - 168) + 168)
    g = int((val + 1)*(179 - 50) + 50)
    b = int((val + 1)*(184 - 50) + 50)
  else:
    r = int((val)*(50 - 176) + 176)
    g = int((val)*(168 - 179) + 179)
    b = int((val)*(82 - 184) + 184)
  
  ret = "rgb(" + str(r) + "," + str(g) + "," + str(b) + ")"
  
  return ret

def quitarTildes(string):
  print(string)
  chars = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','ñ':'n','Ñ':'N'}
  for char in chars:
    if char in string:
      string = string.replace(char, chars[char])
  print(string+"\n")
  return string
#endregion

#region Pagina principal
def index(request):
  # data = json.load(open("principal/ramos.json", encoding='utf-8'))
  
  # for a in data:
  #     print("sigla:",data[a]['sigla'],
  #           "nombre:",data[a]['nombre'],
  #           "depto:",data[a]['depto'],
  #           "creditos:",data[a]['creditos'],
  #           "hrs_estudio:",data[a]['hrs_estudio'],
  #           "color:",data[a]['color']+"\n")
      
  #     try:
  #       nueva_asignatura = asignaturas(clave_asignatura=data[a]['sigla'],
  #                                     nombre=data[a]['nombre'],
  #                                     depto=data[a]['depto'],
  #                                     creditos=data[a]['creditos'],
  #                                     hrs_estudio=data[a]['hrs_estudio'],
  #                                     color=data[a]['color'])
  #       nueva_asignatura.save()
  #     except:
  #       print("El ramo ya se encuentra en la base de datos"+"\n")
      
        
  template = loader.get_template('index.html')
  return HttpResponse(template.render({}, request))

def iniciarSesion(request):
  if request.method == 'GET':
    template = loader.get_template('login.html')
    return HttpResponse(template.render({}, request))
  else:
    try:
      rol = request.POST['rol'].replace("-", "")
      usuario = user.objects.get(ROL=rol)
        
      if usuario.contrasena == request.POST['contrasena']:
        login(rol)
        if usuario.registro_completo:
          l_tareas = tareas.objects.filter(ROL_id=rol)
          
          for tarea in l_tareas:
            print(tarea.fecha.date())
            print(datetime.now().date())
            if tarea.fecha.date() < datetime.now().date():
              tarea.delete()
          return HttpResponseRedirect(reverse('horario', kwargs={'rol':rol}))
        else:
          return HttpResponseRedirect(reverse('Inscribir_ramos', kwargs={'rol':rol}))
      else:
        template = loader.get_template('login.html')
        return HttpResponse(template.render({'error' : 'El ROL y la contraseña ingresados no coinciden.'}, request))
    except:
      template = loader.get_template('login.html')
      return HttpResponse(template.render({'error' : 'El ROL ingresado no existe.'}, request))
    
def CrearPersona(request):
  nombre = request.POST['nombre']
  apellido = request.POST['apellido']
  ROL = request.POST['ROL'].replace("-", "")
  correo = request.POST['correo']
  contrasena = request.POST['contrasena']  
  contrasena = contrasena.replace("-", "")
  
  if request.POST['contrasena'] == request.POST['c-contrasena']:
    if len(request.POST['contrasena']) >= 8:
      usuario = user(nombre=nombre, apellido=apellido, ROL=ROL, correo=correo, contrasena=contrasena)
      usuario.save()
      horario = horarios(ROL_id=ROL)
      horario.save()
      
      login(ROL)
      return HttpResponseRedirect(reverse('Inscribir_ramos', kwargs={'rol':ROL}))
    else:
      template = loader.get_template('registro.html')
      return HttpResponse(template.render({'error' : 'La contraseña debe contener al menos 8 carácteres'}, request))
  else:
    template = loader.get_template('registro.html')
    return HttpResponse(template.render({'error' : 'Las contraseñas no coinciden'}, request))
    
#endregion

#region Personalizacion de horario
def Inscribir_ramos(request, rol):
  usuario = user.objects.get(ROL=rol)
  at = asignaturasTomadas.objects.filter(ROL=rol)
  Asignaturas = asignaturas.objects.exclude(clave_asignatura='----').order_by('nombre')
    
  context = {'usuario':usuario, 'at':at, 'Asignaturas':Asignaturas}
  template = loader.get_template('inscribir_ramos.html')
  return HttpResponse(template.render(context, request))
  
def inscripcion(request, rol):
  usuario = user.objects.get(ROL=rol)
  Asignaturas = asignaturas.objects.all()

  ramos = request.POST['ramos']
  A_ramos = ramos.split(',')[1:]

  for asignatura in asignaturasTomadas.objects.filter(ROL_id=rol):
    if asignatura.clave_asignatura.clave_asignatura not in A_ramos:
      asignatura.delete()
    if asignatura.clave_asignatura.clave_asignatura in A_ramos:
      A_ramos.remove(asignatura.clave_asignatura.clave_asignatura)

  for ramo in A_ramos:
    asignaturaT = asignaturasTomadas(ROL_id=rol, clave_asignatura_id=ramo, horas_a_dedicar=asignaturas.objects.get(clave_asignatura=ramo).hrs_estudio)
    asignaturaT.save()
 
  return HttpResponseRedirect(reverse('editar_horario', kwargs={'rol':rol}))

def editar_horario(request, rol):
  usuario = user.objects.get(ROL=rol)
  if not checkLogin(rol):
    return HttpResponseRedirect(reverse('Login'))
  
  at = asignaturasTomadas.objects.filter(ROL=rol)
  horario = horarios.objects.get(ROL=rol).horario 
  
  for i in range(len(horario)):
    for j in range(len(horario[i])):
      if horario[i][j] != None:
        horario[i][j] = asignaturas.objects.get(clave_asignatura=horario[i][j])
  
  
  lunes = horario[0]
  martes = horario[1]
  miercoles = horario[2]
  jueves = horario[3]
  viernes = horario[4]
  sabado = horario[5]
  domingo = horario[6]
        
  context = {'usuario': usuario,
             'asignaturasTomadas': at,
             'lunes': lunes,
             'martes': martes,
             'miercoles': miercoles,
             'jueves': jueves,
             'viernes': viernes,
             'sabado': sabado,
             'domingo': domingo}

  template = loader.get_template('horario/editar_horario.html')
  return HttpResponse(template.render(context, request))

def add_horario(request, rol):
  usuario = user.objects.get(ROL=rol)
  
  semana = [request.POST['lunes'],
            request.POST['martes'],
            request.POST['miercoles'],
            request.POST['jueves'],
            request.POST['viernes'],
            request.POST['sabado'],
            request.POST['domingo']]

  for i in range(len(semana)):
    semana[i] = semana[i].split(',')[1:]
  
  horario_G = horarios.objects.get(ROL=rol)
  horario_G.horario = semana
  horario_G.save()
  
  # p_horario = horarios(horario=semana)
  return HttpResponseRedirect(reverse('horasactivas', kwargs={'rol':rol}))

def horasActivas(request, rol):
  usuario = user.objects.get(ROL=rol)
  if not checkLogin(rol):
    return HttpResponseRedirect(reverse('Login'))
  
  at = asignaturasTomadas.objects.filter(ROL=rol)
  
  dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
  horas = horarios.objects.get(ROL=rol).pesos_dia
  
  inicios = horarios.objects.get(ROL=rol).hora_inicio
  terminos = horarios.objects.get(ROL=rol).hora_termino
  
  prioridadDias = zip(dias, horas)
  intervaloDias = zip(dias, inicios, terminos)
  
  bloques = ["8:15am - 9:25am",
             "9:35am - 10:45am",
             "10:55am - 12:05pm",
             "12:15pm - 13:25pm",
             "14:30pm - 15:40pm",
             "15:50pm - 17:00pm",
             "17:10pm - 18:20pm",
             "18:30pm - 19:40pm",
             "19:50pm - 21:00pm",
             "21:10pm - 22:20pm",
             "22:30pm - 23:40pm",
             "23:50pm - 01:00am",
             "1:10am - 02:20am",
             "02:30am - 03:40am",
             "03:50am - 05:00am"]
  
  # make a context with "horas" and the name of the corresponging day
  context = {'usuario': usuario,
             'asignaturasTomadas': at,
             'Prioridades' : prioridadDias,
             'intervalos' : intervaloDias,
             'Bloques' : bloques}
  
  template = loader.get_template('horario/editar_horas.html')
  return HttpResponse(template.render(context, request))
  
def add_horasActivas(request, rol):
  usuario = user.objects.get(ROL=rol)
  at = asignaturasTomadas.objects.filter(ROL=rol)

  for asignatura in at:
    post = request.POST["prioridad" + str(asignatura.clave_asignatura.clave_asignatura)]
    asignatura.horas_a_dedicar = post
    asignatura.save()
  
  semana = [[int(request.POST['inicioLunes']),
            int(request.POST['inicioMartes']),
            int(request.POST['inicioMiercoles']),
            int(request.POST['inicioJueves']),
            int(request.POST['inicioViernes']),
            int(request.POST['inicioSabado']),
            int(request.POST['inicioDomingo'])],
            [int(request.POST['terminoLunes']),
            int(request.POST['terminoMartes']),
            int(request.POST['terminoMiercoles']),
            int(request.POST['terminoJueves']),
            int(request.POST['terminoViernes']),
            int(request.POST['terminoSabado']),
            int(request.POST['terminoDomingo'])]]
  
  prioridad_dias = [int(request.POST['prioridadLunes']),
                    int(request.POST['prioridadMartes']),
                    int(request.POST['prioridadMiercoles']),
                    int(request.POST['prioridadJueves']),
                    int(request.POST['prioridadViernes']),
                    int(request.POST['prioridadSabado']),
                    int(request.POST['prioridadDomingo'])]
  
  horario_G = horarios.objects.get(ROL=rol)
  horario_G.hora_inicio = semana[0]
  horario_G.hora_termino = semana[1]
  horario_G.pesos_dia = prioridad_dias
  horario_G.save()
  
  # p_horario = horarios(horario=semana)
  if usuario.registro_completo == False:
    usuario.registro_completo = True
    usuario.save()
    
  generarHoras(rol)
  return HttpResponseRedirect(reverse('horario', kwargs={'rol':rol}))

def generarHoras(rol):
  ramos = asignaturasTomadas.objects.filter(ROL=rol)
  horario_usuario = horarios.objects.get(ROL=rol)
  
  horario = horario_usuario.horario
  horas_inicio = horario_usuario.hora_inicio
  horas_termino = horario_usuario.hora_termino
  horas_preferentes = horario_usuario.pesos_hora
  dias_preferentes = horario_usuario.pesos_dia
  
  horas_estudio = horario_default()
  
  info_ramos = []
  for i in ramos:
    info_ramos.append([i.clave_asignatura.creditos,
                       i.clave_asignatura.clave_asignatura,
                       i.horas_a_dedicar])
  
  info_ramos.sort()
  info_ramos.reverse()
  
  for ramo in info_ramos:
    while ramo[2] > 0:
      index_minimo = gen_horas_estudio(ramo[1],
                                       horario[:],
                                       horas_preferentes[:],
                                       dias_preferentes[:],
                                       horas_inicio[:],
                                       horas_termino[:])
      horario[index_minimo[0]][index_minimo[1]] = ramo[1]
      horas_estudio[index_minimo[0]][index_minimo[1]] = ramo[1]
      ramo[2] -= 1
      
  horario_final = horarios.objects.get(ROL=rol)
  horario_final.hora_estudio = horas_estudio
  horario_final.save()

#endregion

#region Horario
def horario(request, rol):
  usuario = user.objects.get(ROL=rol)
  if not checkLogin(rol):
    print("Usuario no logeado")
    return HttpResponseRedirect(reverse('Login'))
  
  at = asignaturasTomadas.objects.filter(ROL=rol)
  horas_estudio = horarios.objects.get(ROL=rol).hora_estudio
  clases = horarios.objects.get(ROL=rol).horario
  l_tareas = tareas.objects.filter(ROL=rol).order_by('fecha')[:5]
  
#region Horario
  for i in range(len(horas_estudio)):
    for j in range(len(horas_estudio[i])):
      if horas_estudio[i][j] != "----":
        horas_estudio[i][j] = asignaturas.objects.get(clave_asignatura=horas_estudio[i][j])
      elif clases[i][j] != "----":
        horas_estudio[i][j] = asignaturas.objects.get(clave_asignatura=clases[i][j])
        horas_estudio[i][j].color = horas_estudio[i][j].color + "; filter: saturate(0.05) brightness(1.2);"
      else:
        horas_estudio[i][j] = asignaturas.objects.get(clave_asignatura="----")
  
  lunes = horas_estudio[0]
  martes = horas_estudio[1]
  miercoles = horas_estudio[2]
  jueves = horas_estudio[3]
  viernes = horas_estudio[4]
  sabado = horas_estudio[5]
  domingo = horas_estudio[6]
#endregion
      
  context = {'usuario': usuario,
             'asignaturasTomadas': at,
             'tareas': l_tareas,
             'lunes': lunes,
             'martes': martes,
             'miercoles': miercoles,
             'jueves': jueves,
             'viernes': viernes,
             'sabado': sabado,
             'domingo': domingo}

  template = loader.get_template('horario/horario.html')
  return HttpResponse(template.render(context, request))

def addTarea(request, rol):
  try:
    post_titulo = request.POST['titulo']
    post_asignatura = request.POST['asignatura']
    post_fecha = request.POST['fecha']
    
    post_tarea = tareas(ROL_id=rol, titulo=post_titulo,asignatura_id=post_asignatura, fecha=post_fecha)
    post_tarea.save()
    
    return HttpResponseRedirect(reverse('horario', kwargs={'rol':rol}))
  except:
    return HttpResponseRedirect(reverse('horario', kwargs={'rol':rol}))

def borrarTarea(request, rol):
  titulo = request.POST['titulo']
  
  var = tareas.objects.get(titulo=titulo, ROL_id=rol, asignatura_id=request.POST['asignatura'])
  var.delete()
  
  return HttpResponseRedirect(reverse('horario', kwargs={'rol':rol}))  
#endregion

#region Asignaturas
def ramos(request,rol):
  usuario = user.objects.get(ROL=rol)
  if not checkLogin(rol):
    return HttpResponseRedirect(reverse('Login'))
  
  a_t = asignaturasTomadas.objects.filter(ROL=rol)
  
  asignatura = []
  for i in a_t:
    var = asignaturas.objects.get(clave_asignatura = i.clave_asignatura.clave_asignatura)
    asignatura.append(var)
  
  cantidad = len(a_t)
  # search two integers that multiplied give "cantidad"
  divisores = []
  for i in range(1,cantidad):
    if cantidad % (i + 1) == 0:
      filas = i + 1
      columnas = cantidad // (i + 1)
      divisores.append([filas,columnas])
      
  filas = divisores[int(len(divisores)/2) - 1][0]
  columnas = divisores[int(len(divisores)/2) - 1][1]
  
  context = {'usuario': usuario, 'asignaturasTomadas': asignatura, 'filas': filas, 'columnas': columnas}
  template = loader.get_template('tus_ramos.html')
  return HttpResponse(template.render(context, request))

def pestana_ramo(request,rol,ramo):
  g_usuario = user.objects.get(ROL=rol)
  if not checkLogin(rol):
    return HttpResponseRedirect(reverse('Login'))
  
  g_asignatura = asignaturasTomadas.objects.get(clave_asignatura=ramo, ROL_id=rol)
  g_temas = temas.objects.filter(ROL_id=rol,asignatura_id=ramo)
  g_tareas = tareas.objects.filter(ROL_id=rol, asignatura_id=ramo).order_by('fecha')[:4]
  g_links = links.objects.filter(ROL_id=rol, asignatura_id=ramo)
  
  context = {'usuario': g_usuario,
             'asignatura': g_asignatura,
             'temas': g_temas,
             'tareas': g_tareas,
             'links': g_links}
  
  template = loader.get_template('ramo.html')
  return HttpResponse(template.render(context, request))

def pestana_ramo_add(request,rol,ramo):
  try:
    tipo = request.POST['tipo']
    
    if tipo == 'temas':
      nombre_tema = request.POST['titulo-tema']
      
      tema_POST = temas(ROL_id=rol,asignatura_id=ramo,titulo=nombre_tema)
      tema_POST.save()

    if tipo == 'tareas':
      titulo_tarea = request.POST['titulo-tarea']
      fecha = request.POST['date']
      tarea_POST = tareas(ROL_id=rol,asignatura_id=ramo,titulo=titulo_tarea,fecha=fecha)
      tarea_POST.save()
      
    if tipo == 'links':
      list_links = links.objects.filter(ROL_id=rol,asignatura_id=ramo)

      if len(list_links) < 12:    
        link = request.POST['enlace']
        titulo_link = request.POST['titulo-link']
        
        link_POST = links(ROL_id=rol,asignatura_id=ramo,titulo=titulo_link,link=link)
        link_POST.save()
        
    return HttpResponseRedirect(reverse('ramo', kwargs={'rol':rol,'ramo':ramo}))
  except:
    HttpResponseRedirect(reverse('ramo', kwargs={'rol':rol,'ramo':ramo}))

def pestana_ramo_quitar(request,rol,ramo):
  tipo = request.POST['tipo']
  key = request.POST['key']
  
  print(tipo)
  print(key)
  
  if tipo == 'temas':
    tema_POST = temas.objects.get(ROL_id=rol,asignatura_id=ramo,titulo=key)
    tema_POST.delete()

  if tipo == 'tareas':
    tarea_POST = tareas.objects.get(ROL_id=rol,asignatura_id=ramo,titulo=key)
    tarea_POST.delete()
    
  if tipo == 'links':
    hora_POST = links.objects.get(ROL_id=rol,asignatura_id=ramo, link=key)
    hora_POST.delete()
      
  return HttpResponseRedirect(reverse('ramo', kwargs={'rol':rol,'ramo':ramo}))
#endregion

#region Zona estudio
def estudiando(request,rol,ramo):
  g_usuario = user.objects.get(ROL=rol)
  if not checkLogin(rol):
    return HttpResponseRedirect(reverse('Login'))
  g_asignatura = asignaturas.objects.get(clave_asignatura=ramo)
  g_temas = temas.objects.filter(ROL_id=rol, asignatura_id=ramo)
  g_links = links.objects.filter(ROL_id=rol, asignatura_id=ramo)
  l_tareas = tareas.objects.filter(ROL_id=rol, asignatura_id=ramo).order_by('fecha')[:3]
  
  
  list = []
  for i in g_temas:
    list.append([i.dominio + 0.067 * i.veces_estudiado, i.titulo])
  
  list.sort()
  
  for i in range(len(list)):
    list[i] = temas.objects.get(ROL_id=rol, titulo=list[i][1])
    
  context = {'usuario': g_usuario,
             'asignatura': g_asignatura,
             'links' : g_links,
             'temas': list,
             'tareas': l_tareas}
  
  template = loader.get_template('estudiando.html')
  return HttpResponse(template.render(context, request))

def retroalimentacion(request,rol,ramo):
  g_temas = request.POST['tema']
  g_tareas = request.POST['tarea']
  
  if g_temas == '' and g_tareas == '':
    return HttpResponseRedirect(reverse('horario', kwargs={'rol':rol}))
  
  g_usuario = user.objects.get(ROL=rol)
  g_asignatura = asignaturas.objects.get(clave_asignatura=ramo)
  
  if g_temas != '':
    g_temas = g_temas.split(',')
    for i in range(len(g_temas)):
      #remove first and last character
      g_temas[i] = g_temas[i][1:]
      g_temas[i] = g_temas[i][:-1]
    
  if g_tareas != '':
    g_tareas = g_tareas.split(',')
    
    for i in range(len(g_tareas)):
      #remove first and last character
      g_tareas[i] = g_tareas[i][1:]
      g_tareas[i] = g_tareas[i][:-1]

  context = {'usuario': g_usuario,
             'asignatura': g_asignatura,
             'temas': g_temas,
             'tareas': g_tareas}
  
  template = loader.get_template('retroalimentacion.html')
  return HttpResponse(template.render(context, request))

def p_retroalimentacion(request,rol,ramo):
  g_usuario = user.objects.get(ROL=rol)
  g_asignatura = asignaturas.objects.get(clave_asignatura=ramo)
  
  #region temas
  l_temas = []
  val_temas = []
  for tema in request.POST.getlist('tema_n'):
    l_temas.append(temas.objects.get(ROL_id=rol, asignatura_id=ramo, titulo=tema))
    val_temas.append(float(request.POST[tema]))
  
  for i in range(len(l_temas)):
    l_temas[i].dominio += val_temas[i] * 0.15
    
    l_temas[i].ultima_vez = datetime.now()
    l_temas[i].veces_estudiado += 1
    l_temas[i].color = Gen_color(l_temas[i].dominio)
    l_temas[i].save()  
  #endregion
  
  #region tareas
  val_tareas = []
  for tarea in request.POST.getlist('tarea_n'):
    val = True if (int(request.POST[tarea]) == 1) else False
    val_tareas.append(val)
    
  for i in range(len(val_tareas)):
    if val_tareas[i]:
      tareas.objects.get(ROL_id=rol, asignatura_id=ramo, titulo=tarea).delete()
  #endregion
  
  return HttpResponseRedirect(reverse('ramo', kwargs={'rol':rol, 'ramo':ramo}))
#endregion