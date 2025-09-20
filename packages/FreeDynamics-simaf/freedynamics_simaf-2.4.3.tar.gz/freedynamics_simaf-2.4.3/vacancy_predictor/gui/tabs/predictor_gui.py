import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import pandas as pd
import joblib
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class PredictorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Predictor de Vacancies")
        self.root.geometry("900x700")
        
        # Variables para almacenar paths
        self.csv_path = None
        self.model_path = None
        self.predictions_df = None
        self.predict_btn = None  # Referencia al botón de predicción
        
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = ttk.Label(main_frame, text="🔮 Predictor de Vacancies", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Frame de controles
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        control_frame.pack(fill="x", pady=(0, 10))
        
        # Botones de carga
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=5)
        
        ttk.Button(btn_frame, text="📁 Cargar CSV", 
                  command=self.load_csv, width=15).pack(side="left", padx=(0, 10))
        ttk.Button(btn_frame, text="🤖 Cargar Modelo (.joblib)", 
                  command=self.load_model, width=20).pack(side="left", padx=(0, 10))
        
        # Botón de predicción - GUARDAR REFERENCIA
        self.predict_btn = ttk.Button(btn_frame, text="🔮 Predecir", 
                                     command=self.predict, width=15, state="disabled")
        self.predict_btn.pack(side="left", padx=(0, 10))
        
        ttk.Button(btn_frame, text="💾 Guardar Resultados", 
                  command=self.save_results, width=20, state="disabled").pack(side="left")
        self.save_btn = ttk.Button(btn_frame, text="💾 Guardar Resultados", 
                                  command=self.save_results, width=20, state="disabled")
        self.save_btn.pack(side="left")
        
        # Info de archivos cargados
        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill="x", pady=5)
        
        self.csv_label = ttk.Label(info_frame, text="CSV: No cargado", foreground="red")
        self.csv_label.pack(anchor="w")
        
        self.model_label = ttk.Label(info_frame, text="Modelo: No cargado", foreground="red")
        self.model_label.pack(anchor="w")
        
        # Pestañas para resultados
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill="both", expand=True)
        
        # Pestaña de datos
        data_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(data_frame, text="📊 Datos")
        
        self.data_text = scrolledtext.ScrolledText(data_frame, height=15, wrap='word')
        self.data_text.pack(fill="both", expand=True)
        
        # Pestaña de resultados
        results_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(results_frame, text="📈 Resultados")
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=15, wrap='word')
        self.results_text.pack(fill="both", expand=True)
        
        # Pestaña de visualización
        viz_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(viz_frame, text="📉 Gráficos")
        
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, viz_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def load_csv(self):
        """Cargar archivo CSV"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("CSV files", "*.csv"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                self.csv_path = file_path
                self.df = pd.read_csv(file_path)
                self.csv_label.config(text=f"CSV: {file_path.split('/')[-1]} ({len(self.df)} filas)", 
                                    foreground="green")
                
                # Mostrar información del CSV
                info = f"""Archivo CSV cargado: {file_path.split('/')[-1]}
                
Filas: {len(self.df):,}
Columnas: {len(self.df.columns)}
                
Columnas disponibles:
{', '.join(self.df.columns.tolist())}

Primeras 5 filas:
{self.df.head().to_string()}
"""
                self.data_text.delete(1.0, tk.END)
                self.data_text.insert(1.0, info)
                
                self.check_ready()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando CSV: {str(e)}")
    
    def load_model(self):
        """Cargar modelo .joblib"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar modelo",
            filetypes=[("Joblib files", "*.joblib"), ("Todos los archivos", "*.*")]
        )
        
        if file_path:
            try:
                self.model_path = file_path
                self.model_data = joblib.load(file_path)
                self.model = self.model_data["model"]
                self.feature_columns = self.model_data["feature_columns"]
                self.scaler = self.model_data.get("scaler", None)
                
                self.model_label.config(text=f"Modelo: {file_path.split('/')[-1]}", 
                                      foreground="green")
                
                # Mostrar información del modelo
                model_info = f"""Modelo cargado: {file_path.split('/')[-1]}
                
Tipo: {type(self.model).__name__}
Features requeridas: {len(self.feature_columns)}
                
Features:
{', '.join(self.feature_columns)}

Parámetros del modelo:
"""
                if hasattr(self.model, 'get_params'):
                    params = self.model.get_params()
                    for key, value in list(params.items())[:10]:  # Mostrar primeros 10
                        model_info += f"{key}: {value}\n"
                    if len(params) > 10:
                        model_info += f"... y {len(params) - 10} parámetros más\n"
                
                self.data_text.insert(tk.END, "\n\n" + "="*50 + "\n" + model_info)
                
                self.check_ready()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando modelo: {str(e)}")
    
    def check_ready(self):
        """Verificar si se puede predecir - CORREGIDO"""
        if self.csv_path and self.model_path and hasattr(self, 'df') and hasattr(self, 'feature_columns'):
            # Verificar que todas las features estén en el CSV
            missing_features = [feat for feat in self.feature_columns if feat not in self.df.columns]
            if missing_features:
                messagebox.showwarning("Advertencia", 
                    f"Faltan features en el CSV:\n{', '.join(missing_features)}")
                self.predict_btn.config(state="disabled")
            else:
                # Habilitar botón de predicción
                self.predict_btn.config(state="normal")
        else:
            self.predict_btn.config(state="disabled")
    
    def predict(self):
        """Realizar predicciones"""
        try:
            # Preparar datos
            X_new = self.df[self.feature_columns].copy()
            
            if self.scaler is not None:
                X_new = pd.DataFrame(
                    self.scaler.transform(X_new),
                    columns=self.feature_columns,
                    index=self.df.index
                )
            
            # Hacer predicciones
            predictions = np.round(self.model.predict(X_new))
            self.df["vacancies_predicted"] = predictions
            
            # Calcular estadísticas
            if "vacancies" in self.df.columns:
                actual = self.df["vacancies"]
                mae = np.mean(np.abs(predictions - actual))
                rmse = np.sqrt(np.mean((predictions - actual)**2))
                accuracy = np.mean(predictions == actual)
                
                stats_text = f"""📊 ESTADÍSTICAS DE PREDICCIÓN:

MAE (Error Absoluto Medio): {mae:.2f}
RMSE (Raíz del Error Cuadrático Medio): {rmse:.2f}
Precisión (exactitud): {accuracy:.2%}

Distribución de predicciones:
{predictions.value_counts().to_string()}
"""
            else:
                stats_text = "📊 Predicciones completadas (sin valores reales para comparar)"
            
            # Mostrar resultados
            results_text = f"""✅ PREDICCIONES COMPLETADAS

Total de predicciones: {len(predictions):,}
Rango de predicciones: {int(predictions.min())} - {int(predictions.max())}

{stats_text}

Primeras 10 predicciones:
{self.df[['vacancies_predicted'] + (['vacancies'] if 'vacancies' in self.df.columns else [])].head(10).to_string()}
"""
            
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, results_text)
            
            # Habilitar botón de guardar
            self.save_btn.config(state="normal")
            
            # Crear visualización
            self.create_visualization()
            
            # Cambiar a pestaña de resultados
            self.notebook.select(1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en predicción: {str(e)}")
    
    def create_visualization(self):
        """Crear gráficos de resultados"""
        self.ax.clear()
        
        if "vacancies" in self.df.columns:
            # Scatter plot de predicciones vs reales
            self.ax.scatter(self.df["vacancies"], self.df["vacancies_predicted"], alpha=0.6)
            max_val = max(self.df["vacancies"].max(), self.df["vacancies_predicted"].max())
            self.ax.plot([0, max_val], [0, max_val], 'r--', label='Predicción perfecta')
            self.ax.set_xlabel('Valores Reales')
            self.ax.set_ylabel('Predicciones')
            self.ax.set_title('Predicciones vs Valores Reales')
            self.ax.legend()
        else:
            # Histograma de predicciones
            self.df["vacancies_predicted"].hist(bins=20, ax=self.ax, alpha=0.7)
            self.ax.set_xlabel('Vacancies Predichas')
            self.ax.set_ylabel('Frecuencia')
            self.ax.set_title('Distribución de Predicciones')
        
        self.ax.grid(True, alpha=0.3)
        self.canvas.draw()
    
    def save_results(self):
        """Guardar resultados en CSV"""
        file_path = filedialog.asksaveasfilename(
            title="Guardar resultados",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                messagebox.showinfo("Éxito", f"Resultados guardados en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Error guardando: {str(e)}")

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = PredictorGUI(root)
    root.mainloop()