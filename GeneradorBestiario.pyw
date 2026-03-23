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
        nombre_match = re.search(r'alt="(.*?)"', bloque)
        datos['nombre'] = nombre_match.group(1) if nombre_match else "Sin Nombre"
        img_match = re.search(r'src="\.\.\/img\/(.*?)"', bloque)
        datos['imagen'] = img_match.group(1) if img_match else ""

        def extraer_campo(label):
            # Se añade \s* para tolerar espacios extra accidentales
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
    btn_guardar_cambios.config(state=tk.NORMAL)
    btn_inyectar.config(state=tk.DISABLED)

def generar_html_cyberpunk(nombre, especie, habilidades, debilidades, imagen):
    if not imagen.endswith((".webp", ".png", ".jpg", ".gif")): imagen += ".webp"
    # ¡AQUÍ ESTÁ EL CAMBIO PRINCIPAL! Ahora inyecta CARACTERÍSTICAS:
    return f"""<div class="cyber-container">
  <div class="cyber-img-panel">
    <img src="../img/{imagen}" alt="{nombre}" class="cyber-img">
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
            file.write(generar_html_cyberpunk(nombre, entry_especie.get(), entry_habilidades.get(), entry_debilidades.get(), imagen))
        limpiar_campos()
        cargar_lista_entidades()
    except Exception as e: messagebox.showerror("Error", str(e))

def guardar_cambios_entidad():
    seleccion = listbox_entidades.curselection()
    if not seleccion: return
    entidad_vieja = entidades_cargadas[seleccion[0]]
    html_nuevo = generar_html_cyberpunk(entry_nombre.get(), entry_especie.get(), entry_habilidades.get(), entry_debilidades.get(), entry_imagen.get())
    try:
        with open(RUTA_BESTIARIO, "r", encoding="utf-8") as file: content = file.read()
        if entidad_vieja['bloque_completo'] in content:
            with open(RUTA_BESTIARIO, "w", encoding="utf-8") as file: file.write(content.replace(entidad_vieja['bloque_completo'], html_nuevo))
            limpiar_campos()
            cargar_lista_entidades()
    except Exception as e: messagebox.showerror("Error", str(e))

def migrar_todo_al_nuevo_estilo():
    if not entidades_cargadas: return
    respuesta = messagebox.askyesno("Migración", "¿Actualizar todo el bestiario a la nueva cabecera de CARACTERÍSTICAS?")
    if respuesta:
        nuevo_contenido = ""
        for datos in entidades_cargadas:
            nuevo_contenido += generar_html_cyberpunk(datos['nombre'], datos['especie'], datos['habilidades'], datos['debilidades'], datos['imagen'])
        with open(RUTA_BESTIARIO, "w", encoding="utf-8") as file: file.write(nuevo_contenido)
        cargar_lista_entidades()
        messagebox.showinfo("Éxito", "¡Todo el bestiario ha sido actualizado!")

# --- Interfaz ---
root = tk.Tk()
root.title("Terminal Toy Zombies v4.1")
root.geometry("850x600") 
root.configure(bg="#050505")

frame_main = tk.Frame(root, bg="#050505")
frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
frame_lista = tk.Frame(frame_main, bg="#050505", width=300); frame_lista.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
tk.Label(frame_lista, text="ENTIDADES", font=("Consolas", 14, "bold"), bg="#050505", fg="#00f0ff").pack(pady=(0, 15))

listbox_entidades = tk.Listbox(frame_lista, font=("Consolas", 10), bg="#0a0a0f", fg="#00f0ff", selectbackground="#ff003c", selectforeground="white", relief="solid", bd=1)
listbox_entidades.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
listbox_entidades.bind('<<ListboxSelect>>', cargar_entidad_seleccionada)

lbl_total = tk.Label(frame_lista, text="Total: 0", bg="#050505", fg="#888", font=("Consolas", 9))
lbl_total.pack(pady=5)
btn_limpiar = tk.Button(frame_lista, text="NUEVA FICHA", bg="#111", fg="#fff", font=("Consolas", 9, "bold"), relief="flat", command=limpiar_campos)
btn_limpiar.pack(fill=tk.X, pady=5)

btn_migrar = tk.Button(frame_lista, text="MIGRAR TODO AL NUEVO ESTILO", bg="#00f0ff", fg="#000", font=("Consolas", 9, "bold"), relief="flat", command=migrar_todo_al_nuevo_estilo)
btn_migrar.pack(fill=tk.X, pady=5)

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

entry_nombre, entry_especie, entry_habilidades, entry_debilidades, entry_imagen = crear_campo("Nombre:"), crear_campo("Especie:"), crear_campo("Habilidades:"), crear_campo("Debilidades:"), crear_campo("Imagen:")

frame_botones = tk.Frame(frame_form, bg="#050505")
frame_botones.pack(pady=30, fill=tk.X)
btn_guardar_cambios = tk.Button(frame_botones, text="GUARDAR EDICIÓN", bg="#ff003c", fg="#fff", font=("Consolas", 10, "bold"), relief="flat", state=tk.DISABLED, command=guardar_cambios_entidad)
btn_guardar_cambios.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
btn_inyectar = tk.Button(frame_botones, text="AGREGAR NUEVA", bg="#00f0ff", fg="#000", font=("Consolas", 10, "bold"), relief="flat", command=guardar_como_nueva_entidad)
btn_inyectar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

limpiar_campos()
cargar_lista_entidades()
root.mainloop()