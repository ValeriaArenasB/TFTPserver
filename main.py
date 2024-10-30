##Código servidor versión 17.11.23

#coding=utf-8
# Aplicación servidor TFTP - Grupo x


import socket
import os


OP_RRQ = 1
OP_WRQ = 2
OP_DATA = 3
OP_ACK = 4
OP_ERROR = 5
DIRECTORIO = r"C:\Users\Sonyvideo1\Downloads\tftp"



def iniciar_servidor_tftp():


   puerto_tftp = 69


   servidor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   servidor.bind(('', puerto_tftp))
   print(f"El servidor TFTP ha sido iniciado en el puerto {puerto_tftp}")


   nombres_de_archivos = listar_archivos_en_string(DIRECTORIO)
   print(nombres_de_archivos)


   while True:

       mensaje, direccion_cliente = servidor.recvfrom(512)
       print(f"Petición de cliente recibida - Dirección IPv4: {direccion_cliente}")
       print(f"Mensaje enviado:{mensaje}")
       procesar_solicitud(servidor,mensaje,direccion_cliente)


#  servidor.close()


def procesar_solicitud(servidor, mensaje, direccion_cliente):

   op_code = int.from_bytes(mensaje[0:2], 'big')
   detalles = mensaje[2:].split(b'\0')
   nombre_archivo = detalles[0].decode('ascii')
   modo = detalles[1].decode('ascii')


   if op_code == OP_RRQ:
       manejar_rrq(servidor, nombre_archivo, direccion_cliente, modo)
   elif op_code == OP_WRQ:
       manejar_wrq(servidor, nombre_archivo, direccion_cliente, modo)
   else:
       enviar_error(servidor, direccion_cliente, 4, "Operación no soportada")








def manejar_rrq(servidor, nombre_archivo, direccion_cliente, modo):
   ruta_completa = os.path.join(DIRECTORIO, nombre_archivo)


   if nombre_archivo == "LIST_FILES":
       nombres_de_archivos = listar_archivos_en_string(DIRECTORIO).encode('ascii')
       servidor.sendto(nombres_de_archivos, direccion_cliente)
       return


   if not os.path.exists(ruta_completa):
       enviar_error(servidor, direccion_cliente, 1, "Archivo no encontrado")
       return




   with open(ruta_completa, 'rb') as archivo:
       bloque = 1
       data = archivo.read(512)


       while data:
           mensaje = OP_DATA.to_bytes(2, 'big') + bloque.to_bytes(2, 'big') + data
           servidor.sendto(mensaje, direccion_cliente)


           # Esperar ACK
           try:
               servidor.settimeout(10)  # Timeout para esperar el ACK
               while True:
                   ack, _ = servidor.recvfrom(4)
                   ack_bloque = int.from_bytes(ack[2:4], 'big')
                   if ack_bloque == bloque:
                       break
           except socket.timeout:
               print("Timeout esperando ACK para el bloque", bloque)
               return  # o reintentar enviar el mismo bloque


           bloque += 1
           data = archivo.read(512)


   if modo == 'netascii':
       data = data.replace(b'\n', b'\r\n')

def manejar_wrq(servidor, nombre_archivo, direccion_cliente, modo):
   ruta_completa = os.path.join(DIRECTORIO, nombre_archivo)
   mensaje = OP_ACK.to_bytes(2, 'big') + (0).to_bytes(2, 'big')
   servidor.sendto(mensaje, direccion_cliente)
   try:
       with open(ruta_completa, 'wb') as archivo:
           while True:
               data, _ = servidor.recvfrom(512 + 4)  # Recibir bloque de datos
               print(data)
               if modo == 'netascii':
                   data = data.replace(b'\n', b'\r\n')
               bloque = int.from_bytes(data[2:4], 'big')
               contenido = data[4:]
               print(data)



               # Escribir datos en el archivo
               archivo.write(contenido)


               # Enviar ACK por el bloque recibido
               mensaje_ack = OP_ACK.to_bytes(2, 'big') + bloque.to_bytes(2, 'big')
               servidor.sendto(mensaje_ack, direccion_cliente)


               # Verificar si es el último bloque
               if len(contenido) < 512:
                   break
   except IOError:
       enviar_error(servidor, direccion_cliente, 2, "No se puede escribir el archivo")




def enviar_error(servidor, direccion_cliente, codigo_error, mensaje_error):
   mensaje = OP_ERROR.to_bytes(2, 'big') + codigo_error.to_bytes(2, 'big') + mensaje_error.encode('ascii') + b'\0'
   servidor.sendto(mensaje, direccion_cliente)


def listar_archivos_en_string(DIRECTORIO):
   archivos = []
   for archivo in os.listdir(DIRECTORIO):
       if os.path.isfile(os.path.join(DIRECTORIO, archivo)):
           archivos.append(archivo)
   return ', '.join(archivos)




def main_menu():


   while True:
       print("┌────────────────────────────────────────────────┐")
       print("│                Menú Principal                  │")
       print("├────────────────────────────────────────────────┤")
       print("│ 1. Menú Consultas Adicionales                  │")
       print("│ 2. Menú Datos                                  │")
       print("│ 3. Menú Consulas Entrega 3                     │")
       print("│ 4. Salir                                       │")
       print("└────────────────────────────────────────────────┘")
       option = input("Selecciona una opción: ")


       ##if option == "1":
       ##    menuConsultasAdicionales()
       ##elif option == "2":
       ##    menuData()
       ##elif option == "3":
       ##    menuConsultasE3()
       ##elif option == "4":
       ##    connection.close()
       ##    break
       ##else:
       ##    print("Opción no válida. Por favor, seleccione una opción válida.")


       ##input("Presiona ENTER para continuar...")




# Inicio del programa principal


if __name__ == '__main__':


   iniciar_servidor_tftp()



