import tkinter as tk
from tkinter import messagebox
import json
from pathlib import Path

class CyberEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Terminal de Archivos - Toy Zombies")
        self.root.geometry("900x650")
        self.root.configure(bg="#050505") # Fondo oscuro principal

        # Carpetas donde buscaremos
        self.target_dirs = ["docs", "overrides"]
        self.current_file_path = None
        self.file_paths = []

        # Lista de extensiones de imagen que NO queremos abrir
        self.excluir_extensiones = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico"}

        self.setup_ui()
        self.load_files()

    def setup_ui(self):
        """Construye la interfaz gráfica con el estilo cyberpunk."""
        
        # --- LADO IZQUIERDO: Lista de archivos ---
        frame_lista = tk.Frame(self.root, bg="#050505", width=300)
        frame_lista.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

        tk.Label(frame_lista, text="SISTEMA DE ARCHIVOS", font=("Consolas", 14, "bold"), bg="#050505", fg="#00f0ff").pack(pady=(0, 15))

        # Lista con el estilo del bestiario
        self.listbox_archivos = tk.Listbox(frame_lista, font=("Consolas", 10), bg="#0a0a0f", fg="#00f0ff", 
                                           selectbackground="#ff003c", selectforeground="white", 
                                           relief="solid", bd=1, exportselection=False)
        self.listbox_archivos.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.listbox_archivos.bind('<<ListboxSelect>>', self.cargar_archivo_seleccionado)

        # Contador de archivos
        self.lbl_total = tk.Label(frame_lista, text="Total: 0", bg="#050505", fg="#888", font=("Consolas", 9))
        self.lbl_total.pack(pady=5)

        # Botón para exportar a JSON
        btn_exportar = tk.Button(frame_lista, text="EXPORTAR A JSON", bg="#111", fg="#fff", 
                                 font=("Consolas", 10, "bold"), relief="flat", command=self.exportar_a_json)
        btn_exportar.pack(fill=tk.X, pady=5, ipady=5)


        # --- LADO DERECHO: Editor de texto ---
        frame_editor = tk.Frame(self.root, bg="#050505")
        frame_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)

        tk.Label(frame_editor, text="EDITOR DE CONTENIDO", font=("Consolas", 14, "bold"), bg="#050505", fg="#ff003c").pack(pady=(0, 15))

        # Caja de texto grande para editar el documento
        self.text_editor = tk.Text(frame_editor, font=("Consolas", 11), bg="#0a0a0f", fg="#fff", 
                                   insertbackground="#00f0ff", relief="solid", bd=1, wrap=tk.WORD)
        self.text_editor.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Botón para guardar cambios en el archivo actual
        self.btn_guardar = tk.Button(frame_editor, text="GUARDAR CAMBIOS DEL ARCHIVO", bg="#ff003c", fg="#fff", 
                                     font=("Consolas", 10, "bold"), relief="flat", state=tk.DISABLED, 
                                     command=self.guardar_archivo_actual)
        self.btn_guardar.pack(fill=tk.X, ipady=5)

    def load_files(self):
        """Busca en las carpetas e ignora las imágenes."""
        self.file_paths = []
        self.listbox_archivos.delete(0, tk.END)

        for dir_name in self.target_dirs:
            dir_path = Path(dir_name)
            if dir_path.exists() and dir_path.is_dir():
                for file_path in dir_path.rglob('*'):
                    # Si es un archivo y su extensión NO está en la lista de excluidos
                    if file_path.is_file() and file_path.suffix.lower() not in self.excluir_extensiones:
                        self.file_paths.append(file_path)
                        # Mostramos la ruta relativa en la lista para que sea fácil de leer
                        self.listbox_archivos.insert(tk.END, str(file_path))
        
        # Actualizamos el contador visual
        self.lbl_total.config(text=f"Total: {len(self.file_paths)}")

    def cargar_archivo_seleccionado(self, event):
        """Lee el archivo seleccionado y lo muestra en la caja de texto."""
        seleccion = self.listbox_archivos.curselection()
        if not seleccion: return
        
        index = seleccion[0]
        self.current_file_path = self.file_paths[index]

        try:
            # Leemos el archivo
            contenido = self.current_file_path.read_text(encoding='utf-8')
            self.text_editor.delete(1.0, tk.END) # Limpiamos pantalla
            self.text_editor.insert(tk.END, contenido) # Pegamos texto nuevo
            
            # Activamos el botón de guardar
            self.btn_guardar.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error de Sistema", f"No se pudo leer:\n{e}")

    def guardar_archivo_actual(self):
        """Sobrescribe el archivo con el texto que editaste."""
        if not self.current_file_path: return

        nuevo_contenido = self.text_editor.get(1.0, tk.END)
        if nuevo_contenido.endswith('\n'):
            nuevo_contenido = nuevo_contenido[:-1]

        try:
            self.current_file_path.write_text(nuevo_contenido, encoding='utf-8')
            messagebox.showinfo("Sistema", "Archivo actualizado con éxito.")
        except Exception as e:
            messagebox.showerror("Error de Sistema", f"Fallo al guardar:\n{e}")

    def exportar_a_json(self):
        """Recopila todos los archivos de texto y crea el JSON."""
        datos_json = []
        
        for file_path in self.file_paths:
            try:
                contenido = file_path.read_text(encoding='utf-8')
                datos_json.append({
                    "directorio del archivo": str(file_path.parent),
                    "nombre del archivo": file_path.name,
                    "contenido": contenido
                })
            except Exception:
                # Si algún archivo da un error raro, lo ignoramos y seguimos
                pass 

        try:
            ruta_salida = Path("documentacion_toyzombies.json")
            with ruta_salida.open('w', encoding='utf-8') as f:
                json.dump(datos_json, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Extracción Completa", f"Se exportaron {len(datos_json)} archivos a documentacion_toyzombies.json")
        except Exception as e:
            messagebox.showerror("Error Crítico", f"No se pudo crear el JSON:\n{e}")

# Arrancamos la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = CyberEditorApp(root)
    root.mainloop()