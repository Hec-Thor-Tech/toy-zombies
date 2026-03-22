import tkinter as tk
from tkinter import messagebox
import os
import re

# --- Variables Globales y Configuración ---
RUTA_BESTIARIO = os.path.join("docs", "bestiario.md")
RUTA_IMG = "../img/" 
entidades_cargadas = [] 

# --- Funciones de Lógica y Procesamiento ---

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
    
    if not os.path.exists(RUTA_BESTIARIO):
        return []

    try:
        with open(RUTA_BESTIARIO, "r", encoding="utf-8") as file:
            content = file.read()

        bloques = re.split(r'(?=<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 40px;">)', content)
        bloques = [b for b in bloques if b.strip().startswith('<div style="display: flex;')]

        for bloque in bloques:
            datos = {}
            # Extraer Nombre e Imagen
            nombre_match = re.search(r'alt="(.*?)"', bloque)
            datos['nombre'] = nombre_match.group(1) if nombre_match else "Sin Nombre"

            img_match = re.search(r'src="\.\.\/img\/(.*?)"', bloque)
            datos['imagen'] = img_match.group(1) if img_match else ""

            # Extraer campos técnicos nuevos
            def extraer_campo(label):
                match = re.search(f'<b>{label}:</b> (.*?)</p>', bloque)
                if match:
                    return match.group(1).replace('<br>', ' ').strip()
                return ""

            datos['especie'] = extraer_campo("Especie")
            datos['habilidades'] = extraer_campo("Habilidades")
            datos['debilidades'] = extraer_campo("Debilidades")
            
            re_hr = re.compile(r'<hr style="border-color: #444; margin: 40px 0;">')
            if re_hr.search(bloque):
                datos['bloque_completo'] = bloque
            else:
                 datos['bloque_completo'] = bloque + '\n<hr style="border-color: #444; margin: 40px 0;">\n'

            entidades_cargadas.append(datos)

    except Exception as e:
        messagebox.showerror("Error de Lectura", f"No se pudo leer bestiario.md\n{e}")

    return [e['nombre'] for e in entidades_cargadas]

def cargar_lista_entidades():
    listbox_entidades.delete(0, tk.END)
    nombres = extraer_datos_bestiario()
    if nombres:
        for i, nombre in enumerate(nombres):
            listbox_entidades.insert(tk.END, f"{i+1:02d}. {nombre}")
        lbl_total.config(text=f"Total de entidades: {len(nombres)}")
    else:
        lbl_total.config(text="Total de entidades: 0")

def cargar_entidad_seleccionada(event):
    seleccion = listbox_entidades.curselection()
    if not seleccion:
        return

    indice = seleccion[0]
    datos = entidades_cargadas[indice]

    limpiar_campos()
    entry_nombre.insert(0, datos['nombre'])
    entry_especie.insert(0, datos['especie'])
    entry_habilidades.insert(0, datos['habilidades'])
    entry_debilidades.insert(0, datos['debilidades'])
    entry_imagen.insert(0, datos['imagen'])

    btn_guardar_cambios.config(state=tk.NORMAL)
    btn_inyectar.config(state=tk.DISABLED)

def generar_html_template(nombre, especie, habilidades, debilidades, imagen):
    if not imagen.endswith((".webp", ".png", ".jpg", ".gif")):
        imagen += ".webp"

    return f"""<div style="display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 40px;">
  <div style="flex: 1; min-width: 300px; background-color: rgba(30, 30, 30, 0.6); padding: 10px; border-radius: 8px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(8px);">
    <img src="../img/{imagen}" alt="{nombre}" style="width: 100%; border-radius: 4px;">
  </div>
  <div style="flex: 1; min-width: 300px; background-color: rgba(30, 30, 30, 0.6); padding: 20px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); backdrop-filter: blur(8px);">
    <h3 style="text-align: center; margin-top: 0; color: #ff5252; font-weight: bold; margin-bottom: 15px;">Características</h3>
    <div style="border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; background-color: rgba(0, 0, 0, 0.4);">
      <div style="padding: 15px;">
        <p style="margin-bottom: 12px; color: #fff;"><b>Nombre:</b> {nombre}</p>        
        <p style="margin-bottom: 12px; color: #fff;"><b>Especie:</b> {especie}</p>
        <p style="margin-bottom: 12px; color: #fff;"><b>Habilidades:</b> {habilidades}</p>
        <p style="margin-bottom: 0; color: #fff;"><b>Debilidades:</b> {debilidades}</p>
      </div>
    </div>
  </div>
</div>
<hr style="border-color: #444; margin: 40px 0;">
"""

def guardar_como_nueva_entidad():
    nombre = entry_nombre.get()
    imagen = entry_imagen.get()

    if not nombre or not imagen:
        messagebox.showwarning("Faltan datos", "El nombre y el archivo de imagen son obligatorios.")
        return

    html_template = generar_html_template(nombre, entry_especie.get(), entry_habilidades.get(), entry_debilidades.get(), imagen)

    try:
        with open(RUTA_BESTIARIO, "a", encoding="utf-8") as file:
            file.write(html_template)
            
        messagebox.showinfo("¡Éxito!", f"¡{nombre} se ha añadido al bestiario!")
        limpiar_campos()
        cargar_lista_entidades() 
        
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar en bestiario.md\n{e}")

def guardar_cambios_entidad():
    seleccion = listbox_entidades.curselection()
    if not seleccion:
        messagebox.showwarning("Atención", "No hay ninguna entidad seleccionada para editar.")
        return

    indice = seleccion[0]
    entidad_vieja = entidades_cargadas[indice]
    
    nombre = entry_nombre.get()
    imagen = entry_imagen.get()

    if not nombre or not imagen:
        messagebox.showwarning("Faltan datos", "El nombre y el archivo de imagen son obligatorios.")
        return

    html_nuevo = generar_html_template(nombre, entry_especie.get(), entry_habilidades.get(), entry_debilidades.get(), imagen)

    try:
        with open(RUTA_BESTIARIO, "r", encoding="utf-8") as file:
            content = file.read()

        if entidad_vieja['bloque_completo'] in content:
            content_actualizado = content.replace(entidad_vieja['bloque_completo'], html_nuevo)
            
            with open(RUTA_BESTIARIO, "w", encoding="utf-8") as file:
                file.write(content_actualizado)
                
            messagebox.showinfo("¡Éxito!", f"¡Cambios guardados para {nombre}!")
            limpiar_campos()
            cargar_lista_entidades() 
        else:
            messagebox.showerror("Error Crítico", "No se pudo localizar el bloque original en el archivo.\nEs posible que el archivo haya sido modificado externamente.")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar bestiario.md\n{e}")

# --- Configuración de la Ventana ---
root = tk.Tk()
root.title("Terminal de Datos v3.0 - Toy Zombies")
root.geometry("850x550") 
root.configure(bg="#121212")

fuente_titulo = ("Consolas", 14, "bold")
fuente_label = ("Consolas", 10, "bold")
fuente_lista = ("Consolas", 10)
bg_color = "#121212"
fg_color = "#ff5252" 
entry_bg = "#1e1e1e"
entry_fg = "#ffffff"
btn_fg = "#ffffff"

frame_main = tk.Frame(root, bg=bg_color)
frame_main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

frame_lista = tk.Frame(frame_main, bg=bg_color, width=300)
frame_lista.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))

tk.Label(frame_lista, text="ENTIDADES CLASIFICADAS", font=fuente_titulo, bg=bg_color, fg=fg_color).pack(pady=(0, 15))

scrollbar = tk.Scrollbar(frame_lista)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

listbox_entidades = tk.Listbox(frame_lista, font=fuente_lista, bg="#1a1a1a", fg=fg_color, 
                                selectbackground="#440000", selectforeground="white",
                                yscrollcommand=scrollbar.set, relief="solid", bd=1)
listbox_entidades.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=listbox_entidades.yview)

listbox_entidades.bind('<<ListboxSelect>>', cargar_entidad_seleccionada)

lbl_total = tk.Label(frame_lista, text="Total de entidades: 0", bg=bg_color, fg="#888", font=("Consolas", 9))
lbl_total.pack(pady=10)

btn_limpiar = tk.Button(frame_lista, text="NUEVA FICHA (LIMPIAR)", bg="#333", fg=btn_fg, 
                        font=("Consolas", 9, "bold"), relief="flat", cursor="hand2", command=limpiar_campos)
btn_limpiar.pack(fill=tk.X, pady=5)


frame_form = tk.Frame(frame_main, bg=bg_color)
frame_form.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(frame_form, text="FORMULARIO DE DATOS", font=fuente_titulo, bg=bg_color, fg=fg_color).pack(pady=(0, 15))

def crear_campo(parent, texto):
    frame_campo = tk.Frame(parent, bg=bg_color)
    frame_campo.pack(fill=tk.X, pady=5)
    tk.Label(frame_campo, text=texto, bg=bg_color, fg="#aaaaaa", font=fuente_label, width=15, anchor="w").pack(side=tk.LEFT)
    entry = tk.Entry(frame_campo, bg=entry_bg, fg=entry_fg, insertbackground="white", relief="solid", bd=1)
    entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
    return entry

entry_nombre = crear_campo(frame_form, "Nombre:")
entry_especie = crear_campo(frame_form, "Especie:")
entry_habilidades = crear_campo(frame_form, "Habilidades:")
entry_debilidades = crear_campo(frame_form, "Debilidades:")
entry_imagen = crear_campo(frame_form, "Archivo Imagen:")

frame_botones = tk.Frame(frame_form, bg=bg_color)
frame_botones.pack(pady=30, fill=tk.X)

btn_guardar_cambios = tk.Button(frame_botones, text="GUARDAR CAMBIOS (EDITAR)", bg="#440000", fg=btn_fg, 
                                font=("Consolas", 10, "bold"), relief="flat", cursor="hand2", 
                                state=tk.DISABLED, command=guardar_cambios_entidad)
btn_guardar_cambios.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)

btn_inyectar = tk.Button(frame_botones, text="AÑADIR COMO NUEVA ENTIDAD", bg=fg_color, fg="#000", 
                        font=("Consolas", 10, "bold"), relief="flat", cursor="hand2", command=guardar_como_nueva_entidad)
btn_inyectar.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)

limpiar_campos()
cargar_lista_entidades() 

root.mainloop()