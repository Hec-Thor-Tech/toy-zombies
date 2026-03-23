import tkinter as tk
from tkinter import messagebox
import os
import re

RUTA_BESTIARIO = os.path.join("docs", "bestiario.md")
entidades_cargadas = [] 

def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_especie.delete(0, tk.END)
    entry_habilidades.delete(0, tk.END)
    entry_debilidades.delete(0, tk.END)
    entry_imagen.delete(0, tk.END)
    entry_info.delete(0, tk.END) # Nuevo campo limpiado
    btn_guardar_cambios.config(state=tk.DISABLED)
    btn_inyectar.config(state=tk.NORMAL)

def extraer_datos_bestiario():
    global entidades_cargadas
    entidades_cargadas = []
    if not os.path.exists(RUTA_BESTIARIO): return []

    with open(RUTA_BESTIARIO, "r", encoding="utf-8") as file: content = file.read()
    
    # Dividimos el documento buscando las etiquetas cyber-container
    bloques = re.split(r'(?=<div[^>]*class="cyber-container")', content)
    bloques = [b for b in bloques if '<div' in b and 'cyber-container' in b]

    for bloque in bloques:
        datos = {}
        
        # Extraer Nombre e Imagen
        nombre_match = re.search(r'alt="(.*?)"', bloque)
        datos['nombre'] = nombre_match.group(1) if nombre_match else "Sin Nombre"
        img_match = re.search(r'src="\.\.\/img\/(.*?)"', bloque)
        datos['imagen'] = img_match.group(1) if img_match else ""

        # Extraer Información del juego (Todo lo que está después de la imagen y antes de cerrar el panel)
        info_match = re.search(r'<img[^>]*class="cyber-img">\s*(.*?)\s*</div>\s*<div class="cyber-data-panel">', bloque, re.DOTALL)
        datos['info'] = info_match.group(1).strip() if info_match else ""

        # Extraer campos de la tabla de datos
        def extraer_campo(label):
            match = re.search(f'<b>{label}:</b>\\s*(.*?)</p>', bloque)
            return match.group(1).replace('<br>', ' ').strip() if match else ""

        datos['especie'] = extraer_campo("Especie")
        datos['habilidades'] = extraer_campo("Habilidades")
        datos['debilidades'] = extraer_campo("Debilidades")
        datos['bloque_completo'] = bloque
        
        entidades_cargadas.append(datos)

    return [e['nombre'] for e in entidades_cargadas]

def cargar_lista_entidades():
    listbox_entidades.delete(0, tk.END)
    nombres = extraer_datos_bestiario()
    for i, nombre in enumerate(nombres): listbox_entidades.insert(tk.END, f"{i+1:02d}. {nombre}")
    lbl_total.config(text=f"Total de entidades: {len(nombres)}")

def cargar_entidad_seleccionada(event):
    seleccion = listbox_entidades.curselection()
    if not seleccion: return
    datos = entidades_cargadas[seleccion[0]]
    limpiar_campos()
    entry_nombre.insert(0, datos['nombre'])
    entry_especie.insert(0, datos['especie'])
    entry_habilidades.insert(0, datos['habilidades'])
    entry_debilidades.insert(0, datos['debilidades'])
    entry_imagen.insert(0, datos['imagen'])
    entry_info.insert(0, datos['info']) # Cargar la info
    btn_guardar_cambios.config(state=tk.NORMAL)
    btn_inyectar.config(state=tk.DISABLED)

def generar_html_cyberpunk(nombre, especie, habilidades, debilidades, imagen, info):
    if not imagen.endswith((".webp", ".png", ".jpg", ".gif")): imagen += ".webp"
    return f"""<div class="cyber-container">
  <div class="cyber-img-panel">
    <img src="../img/{imagen}" alt="{nombre}" class="cyber-img">
    {info}
  </div>
  <div class="cyber-data-panel">
    <h3 class="cyber-title">CARACTERÍSTICAS:</h3>
    <p class="cyber-text"><b>Nombre:</b> {nombre}</p>        
    <p class="cyber-text"><b>Especie:</b> {especie}</p>
    <p class="cyber-text"><b>Habilidades:</b> {habilidades}</p>
    <p class="cyber-text"><b>Debilidades:</b> {debilidades}</p>
  </div>
</div>
<hr class="cyber-hr">
"""

def guardar_como_nueva_entidad():
    nombre, imagen = entry_nombre.get(), entry_imagen.get()
    if not nombre or not imagen: return messagebox.showwarning("Faltan datos", "Falta nombre o imagen.")
    try:
        with open(RUTA_BESTIARIO, "a", encoding="utf-8") as file:
            file.write(generar_html_cyberpunk(nombre, entry_especie.get(), entry_habilidades.get(), entry_debilidades.get(), imagen, entry_info.get()))
        limpiar_campos()
        cargar_lista_entidades()
    except Exception as e: messagebox.showerror("Error", str(e))

def guardar_cambios_entidad():
    seleccion = listbox_entidades.curselection()
    if not seleccion: return
    entidad_vieja = entidades_cargadas[seleccion[0]]
    html_nuevo = generar_html_cyberpunk(entry_nombre.get(), entry_especie.get(), entry_habilidades.get(), entry_debilidades.get(), entry_imagen.get(), entry_info.get())
    try:
        with open(RUTA_BESTIARIO, "r", encoding="utf-8") as file: content = file.read()
        if entidad_vieja['bloque_completo'] in content:
            with open(RUTA_BESTIARIO, "w", encoding="utf-8") as file: file.write(content.replace(entidad_vieja['bloque_completo'], html_nuevo))
            
            # Mantenemos la selección después de guardar
            index = seleccion[0]
            limpiar_campos()
            cargar_lista_entidades()
            listbox_entidades.selection_set(index)
            listbox_entidades.event_generate("<<ListboxSelect>>")
    except Exception as e: messagebox.showerror("Error", str(e))

# --- Interfaz ---
root = tk.Tk()
root.title("Terminal Toy Zombies v4.2")
root.geometry("850x650") # Un poco más alto para acomodar el nuevo campo
root.configure(bg="#050505")

frame_main = tk.Frame(root, bg="#050505")
frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
frame_lista = tk.Frame(frame_main, bg="#050505", width=300); frame_lista.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
tk.Label(frame_lista, text="ENTIDADES", font=("Consolas", 14, "bold"), bg="#050505", fg="#00f0ff").pack(pady=(0, 15))

# SOLUCIÓN PROBLEMA 2: exportselection=False añadido aquí
listbox_entidades = tk.Listbox(frame_lista, font=("Consolas", 10), bg="#0a0a0f", fg="#00f0ff", selectbackground="#ff003c", selectforeground="white", relief="solid", bd=1, exportselection=False)
listbox_entidades.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
listbox_entidades.bind('<<ListboxSelect>>', cargar_entidad_seleccionada)

lbl_total = tk.Label(frame_lista, text="Total: 0", bg="#050505", fg="#888", font=("Consolas", 9))
lbl_total.pack(pady=5)
btn_limpiar = tk.Button(frame_lista, text="NUEVA FICHA", bg="#111", fg="#fff", font=("Consolas", 9, "bold"), relief="flat", command=limpiar_campos)
btn_limpiar.pack(fill=tk.X, pady=5)

frame_form = tk.Frame(frame_main, bg="#050505")
frame_form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
tk.Label(frame_form, text="DATOS DE SISTEMA", font=("Consolas", 14, "bold"), bg="#050505", fg="#ff003c").pack(pady=(0, 15))

def crear_campo(texto):
    f = tk.Frame(frame_form, bg="#050505")
    f.pack(fill=tk.X, pady=5)
    tk.Label(f, text=texto, bg="#050505", fg="#00f0ff", font=("Consolas", 10, "bold"), width=15, anchor="w").pack(side=tk.LEFT)
    e = tk.Entry(f, bg="#0a0a0f", fg="#fff", insertbackground="#00f0ff", relief="solid", bd=1)
    e.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    return e

entry_nombre = crear_campo("Nombre:")
entry_especie = crear_campo("Especie:")
entry_habilidades = crear_campo("Habilidades:")
entry_debilidades = crear_campo("Debilidades:")
entry_imagen = crear_campo("Imagen:")
entry_info = crear_campo("Info del Juego:") # NUEVO CAMPO AGREGADO

frame_botones = tk.Frame(frame_form, bg="#050505")
frame_botones.pack(pady=30, fill=tk.X)
btn_guardar_cambios = tk.Button(frame_botones, text="GUARDAR EDICIÓN", bg="#ff003c", fg="#fff", font=("Consolas", 10, "bold"), relief="flat", state=tk.DISABLED, command=guardar_cambios_entidad)
btn_guardar_cambios.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
btn_inyectar = tk.Button(frame_botones, text="AGREGAR NUEVA", bg="#00f0ff", fg="#000", font=("Consolas", 10, "bold"), relief="flat", command=guardar_como_nueva_entidad)
btn_inyectar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

limpiar_campos()
cargar_lista_entidades()
root.mainloop()