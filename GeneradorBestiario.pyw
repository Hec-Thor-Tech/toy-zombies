import tkinter as tk
from tkinter import messagebox
import os
import re

entidades_cargadas = [] 

# --- FUNCIONES DE ENRUTAMIENTO BILINGÜE ---
def get_ruta_bestiario():
    if idioma_actual.get() == "es":
        return os.path.join("docs", "bestiario.md")
    else:
        return os.path.join("docs", "en", "bestiario.md")

def get_img_prefix():
    return "../img/" if idioma_actual.get() == "es" else "../../img/"

def get_labels():
    if idioma_actual.get() == "es":
        return {"title": "CARACTERÍSTICAS:", "nombre": "Nombre", "especie": "Especie", "habilidades": "Habilidades", "debilidades": "Debilidades"}
    else:
        return {"title": "FEATURES:", "nombre": "Name", "especie": "Species", "habilidades": "Abilities", "debilidades": "Weaknesses"}

# --- LÓGICA PRINCIPAL ---
def limpiar_campos():
    entry_nombre.delete(0, tk.END)
    entry_especie.delete(0, tk.END)
    entry_habilidades.delete(0, tk.END)
    entry_debilidades.delete(0, tk.END)
    entry_imagen.delete(0, tk.END)
    entry_info.delete(0, tk.END)
    btn_guardar_cambios.config(state=tk.DISABLED)
    btn_inyectar.config(state=tk.NORMAL)

def extraer_datos_bestiario():
    global entidades_cargadas
    entidades_cargadas = []
    ruta = get_ruta_bestiario()
    if not os.path.exists(ruta): return []

    with open(ruta, "r", encoding="utf-8") as file: content = file.read()
    
    bloques = re.split(r'(?=<div[^>]*class="cyber-container")', content)
    bloques = [b for b in bloques if '<div' in b and 'cyber-container' in b]

    for bloque in bloques:
        datos = {}
        
        # Extraer Nombre
        nombre_match = re.search(r'alt="(.*?)"', bloque)
        datos['nombre'] = nombre_match.group(1) if nombre_match else "Sin Nombre"
        
        # Extraer Imagen (soporta dinámicamente ../img/ y ../../img/)
        img_match = re.search(r'src="\.\./(?:\.\./)?img\/(.*?)"', bloque)
        datos['imagen'] = img_match.group(1) if img_match else ""

        # Extraer Información del juego
        info_match = re.search(r'<img[^>]*class="cyber-img">\s*(.*?)\s*</div>\s*<div class="cyber-data-panel">', bloque, re.DOTALL)
        datos['info'] = info_match.group(1).strip() if info_match else ""

        # Extraer campos bilingües
        def extraer_campo(label_es, label_en):
            match = re.search(f'<b>(?:{label_es}|{label_en}):</b>\\s*(.*?)</p>', bloque)
            return match.group(1).replace('<br>', ' ').strip() if match else ""

        datos['especie'] = extraer_campo("Especie", "Species")
        datos['habilidades'] = extraer_campo("Habilidades", "Abilities")
        datos['debilidades'] = extraer_campo("Debilidades", "Weaknesses")
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
    entry_info.insert(0, datos['info'])
    btn_guardar_cambios.config(state=tk.NORMAL)
    btn_inyectar.config(state=tk.DISABLED)

def generar_html_cyberpunk(nombre, especie, habilidades, debilidades, imagen, info):
    if not imagen.endswith((".webp", ".png", ".jpg", ".gif")): imagen += ".webp"
    prefix = get_img_prefix()
    labels = get_labels()
    
    return f"""<div class="cyber-container">
  <div class="cyber-img-panel">
    <img src="{prefix}{imagen}" alt="{nombre}" class="cyber-img">
    {info}
  </div>
  <div class="cyber-data-panel">
    <h3 class="cyber-title">{labels['title']}</h3>
    <p class="cyber-text"><b>{labels['nombre']}:</b> {nombre}</p>        
    <p class="cyber-text"><b>{labels['especie']}:</b> {especie}</p>
    <p class="cyber-text"><b>{labels['habilidades']}:</b> {habilidades}</p>
    <p class="cyber-text"><b>{labels['debilidades']}:</b> {debilidades}</p>
  </div>
</div>
<hr class="cyber-hr">
"""

def guardar_como_nueva_entidad():
    nombre, imagen = entry_nombre.get(), entry_imagen.get()
    if not nombre or not imagen: return messagebox.showwarning("Faltan datos", "Falta nombre o imagen.")
    try:
        ruta = get_ruta_bestiario()
        # Crear directorio /en/ si no existe por alguna razón
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "a", encoding="utf-8") as file:
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
        ruta = get_ruta_bestiario()
        with open(ruta, "r", encoding="utf-8") as file: content = file.read()
        if entidad_vieja['bloque_completo'] in content:
            with open(ruta, "w", encoding="utf-8") as file: file.write(content.replace(entidad_vieja['bloque_completo'], html_nuevo))
            
            index = seleccion[0]
            limpiar_campos()
            cargar_lista_entidades()
            listbox_entidades.selection_set(index)
            listbox_entidades.event_generate("<<ListboxSelect>>")
    except Exception as e: messagebox.showerror("Error", str(e))

# --- INTERFAZ GRÁFICA ---
root = tk.Tk()
root.title("Terminal Toy Zombies v5.0 (Bilingüe)")
root.geometry("850x650")
root.configure(bg="#050505")

# Variable global para el idioma
idioma_actual = tk.StringVar(value="es")

frame_main = tk.Frame(root, bg="#050505")
frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
frame_lista = tk.Frame(frame_main, bg="#050505", width=300)
frame_lista.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

tk.Label(frame_lista, text="ENTIDADES", font=("Consolas", 14, "bold"), bg="#050505", fg="#00f0ff").pack(pady=(0, 10))

# --- NUEVO: SELECTOR DE IDIOMA ---
def al_cambiar_idioma():
    limpiar_campos()
    cargar_lista_entidades()

frame_idioma = tk.Frame(frame_lista, bg="#050505")
frame_idioma.pack(fill=tk.X, pady=(0, 10))
tk.Radiobutton(frame_idioma, text="ESPAÑOL", variable=idioma_actual, value="es", bg="#050505", fg="#ff003c", selectcolor="#111", command=al_cambiar_idioma, font=("Consolas", 10, "bold")).pack(side=tk.LEFT, expand=True)
tk.Radiobutton(frame_idioma, text="ENGLISH", variable=idioma_actual, value="en", bg="#050505", fg="#00f0ff", selectcolor="#111", command=al_cambiar_idioma, font=("Consolas", 10, "bold")).pack(side=tk.LEFT, expand=True)

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

entry_nombre = crear_campo("Nombre/Name:")
entry_especie = crear_campo("Especie/Species:")
entry_habilidades = crear_campo("Habilidad/Ability:")
entry_debilidades = crear_campo("Debilidad/Weakness:")
entry_imagen = crear_campo("Imagen:")
entry_info = crear_campo("Info del Juego:")

frame_botones = tk.Frame(frame_form, bg="#050505")
frame_botones.pack(pady=30, fill=tk.X)
btn_guardar_cambios = tk.Button(frame_botones, text="GUARDAR EDICIÓN", bg="#ff003c", fg="#fff", font=("Consolas", 10, "bold"), relief="flat", state=tk.DISABLED, command=guardar_cambios_entidad)
btn_guardar_cambios.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
btn_inyectar = tk.Button(frame_botones, text="AGREGAR NUEVA", bg="#00f0ff", fg="#000", font=("Consolas", 10, "bold"), relief="flat", command=guardar_como_nueva_entidad)
btn_inyectar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

limpiar_campos()
cargar_lista_entidades()
root.mainloop()