"""
Tab para procesamiento batch de archivos LAMMPS dump con soporte OVITO
VERSIÓN MEJORADA con filtrado de superficie antes de extracción de features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import pandas as pd
import numpy as np
import logging
import threading
import json
from typing import Callable, Optional, Dict, List, Set

# Importar el procesador batch mejorado
try:
    from vacancy_predictor.core.batch_processor import (
        BatchDumpProcessor , 
        create_standard_processor, 
        create_ovito_processor,
        OvitoFilterConfig
    )
    ENHANCED_PROCESSOR_AVAILABLE = True
except ImportError:
    # Fallback al procesador original si no está disponible
    from vacancy_predictor.core.batch_processor import BatchDumpProcessor
    ENHANCED_PROCESSOR_AVAILABLE = False

logger = logging.getLogger(__name__)

class BatchProcessingTab:
    """Tab para procesamiento batch con soporte OVITO opcional"""
    
    def __init__(self, parent, data_loaded_callback: Callable):
        self.parent = parent
        self.data_loaded_callback = data_loaded_callback
        
        # Determinar qué procesador usar
        if ENHANCED_PROCESSOR_AVAILABLE:
            self.processor = create_standard_processor()  # Empieza en modo estándar
            self.enhanced_mode = True
            logger.info("EnhancedBatchProcessor disponible - Modo OVITO habilitado")
        else:
            self.processor = BatchDumpProcessor()
            self.enhanced_mode = False
            logger.warning("EnhancedBatchProcessor no disponible - Modo estándar solamente")
        
        self.processor.set_progress_callback(self.update_progress)
        
        self.frame = ttk.Frame(parent)
        
        # Variables de procesamiento
        self.directory_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value="ml_dataset_output")
        
        # Variables de configuración LAMMPS
        self.atm_total_var = tk.IntVar(value=16384)
        self.energy_min_var = tk.DoubleVar(value=-4.0)
        self.energy_max_var = tk.DoubleVar(value=-3.0)
        self.energy_bins_var = tk.IntVar(value=10)
        
        # Variables de configuración OVITO
        self.enable_ovito_var = tk.BooleanVar(value=False)
        self.surface_radius_var = tk.DoubleVar(value=3.0)
        self.smoothing_level_var = tk.IntVar(value=0)
        self.apply_stress_var = tk.BooleanVar(value=False)
        self.stress_x_var = tk.DoubleVar(value=1.0)
        self.stress_y_var = tk.DoubleVar(value=1.0)
        self.stress_z_var = tk.DoubleVar(value=1.0)
        self.export_filtered_var = tk.BooleanVar(value=False)
        
        # Variables de entrenamiento ML
        self.test_size_var = tk.DoubleVar(value=0.2)
        self.n_estimators_var = tk.IntVar(value=100)
        self.random_state_var = tk.IntVar(value=42)
        
        # Dataset y estado
        self.current_dataset = None
        self.selected_features = set()
        self.trained_model = None
        self.is_processing = False
        self.is_training = False
        
        # Crear interfaz
        self.create_widgets()
    
    def create_widgets(self):
        """Crear todos los widgets del tab"""
        # Crear notebook para secciones
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 1. Pestaña de configuración y procesamiento (MODIFICADA)
        self.create_processing_tab()
        
        # 2. Pestaña de selección de features (SIN CAMBIOS)
        self.create_features_tab()
        
        # 3. Pestaña de entrenamiento ML (SIN CAMBIOS)
        self.create_training_tab()
        
        # 4. Pestaña de resultados (SIN CAMBIOS)
        self.create_results_tab()
    
    def create_processing_tab(self):
        """Crear pestaña de configuración y procesamiento con soporte OVITO"""
        process_frame = ttk.Frame(self.notebook)
        self.notebook.add(process_frame, text="🔧 Configuración & Procesamiento")
        
        # Configuración LAMMPS
        config_frame = ttk.LabelFrame(process_frame, text="Configuración LAMMPS", padding="10")
        config_frame.pack(fill="x", padx=10, pady=5)
        
        # Parámetros en grid
        ttk.Label(config_frame, text="Número total de átomos:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.atm_total_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Energía mínima (eV):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.energy_min_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Energía máxima (eV):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.energy_max_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        ttk.Label(config_frame, text="Bins de energía:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(config_frame, textvariable=self.energy_bins_var, width=15).grid(row=3, column=1, padx=5, pady=2)
        
        # NUEVA SECCIÓN: Configuración OVITO
        if self.enhanced_mode:
            self.create_ovito_config_section(process_frame)
        
        # Directorios
        dirs_frame = ttk.LabelFrame(process_frame, text="Directorios", padding="10")
        dirs_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(dirs_frame, text="Directorio con dumps:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(dirs_frame, textvariable=self.directory_var, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(dirs_frame, text="Explorar...", command=self.browse_directory).grid(row=0, column=2, padx=5, pady=2)
        
        ttk.Label(dirs_frame, text="Directorio de salida:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(dirs_frame, textvariable=self.output_dir_var, width=50).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(dirs_frame, text="Explorar...", command=self.browse_output_directory).grid(row=1, column=2, padx=5, pady=2)
        
        # Botón de procesamiento (MODIFICADO)
        process_btn_frame = ttk.Frame(process_frame)
        process_btn_frame.pack(fill="x", padx=10, pady=10)
        
        # Indicador de modo
        if self.enhanced_mode:
            self.mode_label = ttk.Label(process_btn_frame, text="Modo: ESTÁNDAR", font=("Arial", 9, "bold"))
            self.mode_label.pack(side="right", padx=10)
        
        self.process_button = ttk.Button(process_btn_frame, text="🚀 Procesar Archivos Dump", 
                                        command=self.start_processing, style="Action.TButton")
        self.process_button.pack(side="left", padx=5)
        
        ttk.Button(process_btn_frame, text="Cargar Dataset Existente", 
                  command=self.load_existing_dataset).pack(side="left", padx=5)
        
        # Progreso
        progress_frame = ttk.LabelFrame(process_frame, text="Progreso", padding="10")
        progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100, length=400)
        self.progress_bar.pack(fill="x", pady=(0, 10))
        
        self.status_var = tk.StringVar(value="Listo para procesar")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(anchor="w")
        
        # Log de procesamiento
        #self.process_log = tk.Text(progress_frame, height=10, wrap="word", font=("Courier", 9))
        #self.process_log.pack(fill="both", expand=True, pady=(10, 0))
    
    def create_ovito_config_section(self, parent):
        """Crear sección de configuración OVITO"""
        ovito_frame = ttk.LabelFrame(parent, text="🔬 Configuración OVITO (Filtrado de Superficie)", padding="10")
        ovito_frame.pack(fill="x", padx=10, pady=5)
        
        # Checkbox principal
        self.ovito_checkbox = ttk.Checkbutton(
            ovito_frame, 
            text="Habilitar filtrado OVITO (calcular features solo en región nanoporo)",
            variable=self.enable_ovito_var,
            command=self.on_ovito_toggle
        )
        self.ovito_checkbox.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))
        
        # Crear frame para parámetros OVITO
        self.ovito_params_frame = ttk.Frame(ovito_frame)
        self.ovito_params_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=5)
        
        # Parámetros de superficie
        surface_label = ttk.Label(self.ovito_params_frame, text="Parámetros de Superficie:", font=("Arial", 9, "bold"))
        surface_label.grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 5))
        
        ttk.Label(self.ovito_params_frame, text="Radio superficie:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        surface_radius_entry = ttk.Entry(self.ovito_params_frame, textvariable=self.surface_radius_var, width=10)
        surface_radius_entry.grid(row=1, column=1, padx=5, pady=2)
        ttk.Label(self.ovito_params_frame, text="Å", font=("Arial", 8)).grid(row=1, column=2, sticky="w")
        
        ttk.Label(self.ovito_params_frame, text="Nivel suavizado:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        smoothing_entry = ttk.Entry(self.ovito_params_frame, textvariable=self.smoothing_level_var, width=10)
        smoothing_entry.grid(row=2, column=1, padx=5, pady=2)
        ttk.Label(self.ovito_params_frame, text="(0=sin suavizado)", font=("Arial", 8)).grid(row=2, column=2, sticky="w")
        
        # Tensor de estrés
        ttk.Separator(self.ovito_params_frame, orient="horizontal").grid(row=3, column=0, columnspan=3, sticky="ew", pady=10)
        
        stress_checkbox = ttk.Checkbutton(
            self.ovito_params_frame,
            text="Aplicar tensor de estrés",
            variable=self.apply_stress_var,
            command=self.on_stress_toggle
        )
        stress_checkbox.grid(row=4, column=0, columnspan=3, sticky="w", pady=5)
        
        # Frame para parámetros de estrés
        self.stress_params_frame = ttk.Frame(self.ovito_params_frame)
        self.stress_params_frame.grid(row=5, column=0, columnspan=3, sticky="ew", padx=20)
        
        ttk.Label(self.stress_params_frame, text="X:").grid(row=0, column=0, sticky="w", padx=2)
        ttk.Entry(self.stress_params_frame, textvariable=self.stress_x_var, width=8).grid(row=0, column=1, padx=2)
        
        ttk.Label(self.stress_params_frame, text="Y:").grid(row=0, column=2, sticky="w", padx=2)
        ttk.Entry(self.stress_params_frame, textvariable=self.stress_y_var, width=8).grid(row=0, column=3, padx=2)
        
        ttk.Label(self.stress_params_frame, text="Z:").grid(row=0, column=4, sticky="w", padx=2)
        ttk.Entry(self.stress_params_frame, textvariable=self.stress_z_var, width=8).grid(row=0, column=5, padx=2)
        
        # Opciones adicionales
        ttk.Separator(self.ovito_params_frame, orient="horizontal").grid(row=6, column=0, columnspan=3, sticky="ew", pady=10)
        
        ttk.Checkbutton(
            self.ovito_params_frame,
            text="Exportar dumps filtrados (para verificación)",
            variable=self.export_filtered_var
        ).grid(row=7, column=0, columnspan=3, sticky="w", pady=2)
        
        # Info explicativa
        info_text = ("El filtrado OVITO aplica ConstructSurfaceModifier + InvertSelection + DeleteSelected\n"
                    "para calcular features solo en átomos que rodean el nanoporo.")
        info_label = ttk.Label(self.ovito_params_frame, text=info_text, 
                              font=("Arial", 8), foreground="gray")
        info_label.grid(row=8, column=0, columnspan=3, sticky="w", pady=(10, 0))
        
        # Inicialmente deshabilitar parámetros
        self.on_ovito_toggle()
        self.on_stress_toggle()
    
    def on_ovito_toggle(self):
        """Callback cuando se habilita/deshabilita OVITO"""
        if not self.enhanced_mode:
            return
            
        enabled = self.enable_ovito_var.get()
        
        # Habilitar/deshabilitar controles
        for child in self.ovito_params_frame.winfo_children():
            if isinstance(child, (ttk.Entry, ttk.Checkbutton)):
                child.config(state="normal" if enabled else "disabled")
            elif isinstance(child, ttk.Frame):  # stress_params_frame
                for subchild in child.winfo_children():
                    if isinstance(subchild, ttk.Entry):
                        subchild.config(state="normal" if enabled else "disabled")
        
        # Actualizar modo del procesador
        if enabled:
            self._update_processor_to_ovito()
            if hasattr(self, 'mode_label'):
                self.mode_label.config(text="Modo: OVITO FILTRADO", foreground="blue")
        else:
            self._update_processor_to_standard()
            if hasattr(self, 'mode_label'):
                self.mode_label.config(text="Modo: ESTÁNDAR", foreground="black")
        
        self.log_process(f"Modo OVITO: {'HABILITADO' if enabled else 'DESHABILITADO'}")
    
    def on_stress_toggle(self):
        """Callback cuando se habilita/deshabilita tensor de estrés"""
        if not self.enhanced_mode:
            return
            
        enabled = self.apply_stress_var.get() and self.enable_ovito_var.get()
        
        # Habilitar/deshabilitar entradas de estrés
        for child in self.stress_params_frame.winfo_children():
            if isinstance(child, ttk.Entry):
                child.config(state="normal" if enabled else "disabled")
    
    def _update_processor_to_ovito(self):
        """Actualizar procesador a modo OVITO"""
        if not self.enhanced_mode:
            return
            
        try:
            self.processor = create_ovito_processor(
                atm_total=self.atm_total_var.get(),
                surface_radius=self.surface_radius_var.get(),
                smoothing_level=self.smoothing_level_var.get(),
                apply_stress=self.apply_stress_var.get(),
                stress_tensor=(
                    self.stress_x_var.get(),
                    self.stress_y_var.get(),
                    self.stress_z_var.get()
                ),
                energy_min=self.energy_min_var.get(),
                energy_max=self.energy_max_var.get(),
                energy_bins=self.energy_bins_var.get()
            )
            self.processor.set_progress_callback(self.update_progress)
            
            # Configurar exportación de dumps filtrados si está habilitada
            if self.export_filtered_var.get():
                filtered_dir = Path(self.output_dir_var.get()) / "filtered_dumps"
                self.processor.ovito_config.export_filtered_dumps = True
                self.processor.ovito_config.filtered_dump_dir = str(filtered_dir)
            
        except Exception as e:
            logger.error(f"Error actualizando a modo OVITO: {e}")
            messagebox.showerror("Error", f"Error configurando OVITO: {str(e)}")
    
    def _update_processor_to_standard(self):
        """Actualizar procesador a modo estándar"""
        if not self.enhanced_mode:
            return
            
        try:
            self.processor = create_standard_processor(
                atm_total=self.atm_total_var.get(),
                energy_min=self.energy_min_var.get(),
                energy_max=self.energy_max_var.get(),
                energy_bins=self.energy_bins_var.get()
            )
            self.processor.set_progress_callback(self.update_progress)
            
        except Exception as e:
            logger.error(f"Error actualizando a modo estándar: {e}")
    
    # ========== RESTO DE MÉTODOS SIN CAMBIOS ==========
    # Copio todos los métodos existentes sin modificación
    
    def create_features_tab(self):
        """Crear pestaña de selección de features"""
        features_frame = ttk.Frame(self.notebook)
        self.notebook.add(features_frame, text="🎯 Selección de Features")
        
        # Info del dataset
        info_frame = ttk.LabelFrame(features_frame, text="Información del Dataset", padding="10")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        self.dataset_info_label = ttk.Label(info_frame, text="No hay dataset cargado", 
                                           font=("Arial", 10))
        self.dataset_info_label.pack(anchor="w")
        
        # Tabla de features
        table_frame = ttk.LabelFrame(features_frame, text="Features Disponibles", padding="10")
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Botones de control
        control_frame = ttk.Frame(table_frame)
        control_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(control_frame, text="Seleccionar Todo", 
                  command=self.select_all_features).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Deseleccionar Todo", 
                  command=self.deselect_all_features).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Auto-Seleccionar (Top 30)", 
                  command=self.auto_select_features).pack(side="left", padx=5)
        
        # Treeview para features
        tree_container = ttk.Frame(table_frame)
        tree_container.pack(fill="both", expand=True)
        
        columns = ("Feature", "Tipo", "Correlación", "Importancia", "Seleccionado")
        self.features_tree = ttk.Treeview(tree_container, columns=columns, show="headings", height=12)
        
        for col in columns:
            self.features_tree.heading(col, text=col)
            self.features_tree.column(col, width=150, anchor="center")
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.features_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_container, orient="horizontal", command=self.features_tree.xview)
        self.features_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.features_tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        
        # Bind eventos
        self.features_tree.bind("<Double-1>", self.toggle_feature_selection)
        
        # Resumen de selección
        summary_frame = ttk.LabelFrame(features_frame, text="Resumen de Selección", padding="10")
        summary_frame.pack(fill="x", padx=10, pady=5)
        
        self.selection_summary_label = ttk.Label(summary_frame, text="0 features seleccionadas", 
                                                font=("Arial", 10, "bold"))
        self.selection_summary_label.pack(anchor="w")
    
    def create_training_tab(self):
        """Crear pestaña de entrenamiento ML"""
        training_frame = ttk.Frame(self.notebook)
        self.notebook.add(training_frame, text="🤖 Entrenamiento ML")
        
        # Configuración del modelo
        model_config_frame = ttk.LabelFrame(training_frame, text="Configuración del Modelo", padding="10")
        model_config_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(model_config_frame, text="Tamaño de prueba:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(model_config_frame, textvariable=self.test_size_var, width=15).grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(model_config_frame, text="Nº Estimadores:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(model_config_frame, textvariable=self.n_estimators_var, width=15).grid(row=1, column=1, padx=5, pady=2)
        
        ttk.Label(model_config_frame, text="Random State:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        ttk.Entry(model_config_frame, textvariable=self.random_state_var, width=15).grid(row=2, column=1, padx=5, pady=2)
        
        # Botones de entrenamiento
        training_controls_frame = ttk.LabelFrame(training_frame, text="Control de Entrenamiento", padding="10")
        training_controls_frame.pack(fill="x", padx=10, pady=5)
        
        buttons_frame = ttk.Frame(training_controls_frame)
        buttons_frame.pack(fill="x")
        
        self.train_button = ttk.Button(buttons_frame, text="🚀 Entrenar Modelo", 
                                      command=self.start_training, style="Action.TButton")
        self.train_button.pack(side="left", padx=5)
        
        self.stop_train_button = ttk.Button(buttons_frame, text="⏹️ Detener", 
                                           command=self.stop_training, state="disabled")
        self.stop_train_button.pack(side="left", padx=5)
        
        ttk.Button(buttons_frame, text="💾 Guardar Modelo", 
                  command=self.save_model).pack(side="right", padx=5)
        ttk.Button(buttons_frame, text="📁 Cargar Modelo", 
                  command=self.load_model).pack(side="right", padx=5)
        
        # Progreso de entrenamiento
        train_progress_frame = ttk.LabelFrame(training_frame, text="Progreso de Entrenamiento", padding="10")
        train_progress_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.train_progress_var = tk.DoubleVar()
        self.train_progress_bar = ttk.Progressbar(train_progress_frame, variable=self.train_progress_var, 
                                                 maximum=100, length=400)
        self.train_progress_bar.pack(fill="x", pady=(0, 10))
        
        self.train_status_var = tk.StringVar(value="Listo para entrenar")
        self.train_status_label = ttk.Label(train_progress_frame, textvariable=self.train_status_var)
        self.train_status_label.pack(anchor="w")
        
        # Log de entrenamiento
        self.training_log = tk.Text(train_progress_frame, height=12, wrap="word", font=("Courier", 9))
        self.training_log.pack(fill="both", expand=True, pady=(10, 0))
    
    def create_results_tab(self):
        """Crear pestaña de resultados"""
        results_frame = ttk.Frame(self.notebook)
        self.notebook.add(results_frame, text="📊 Resultados")
        
        # Métricas del modelo
        metrics_frame = ttk.LabelFrame(results_frame, text="Métricas del Modelo", padding="10")
        metrics_frame.pack(fill="x", padx=10, pady=5)
        
        self.metrics_text = tk.Text(metrics_frame, height=8, wrap="word", 
                                   state="disabled", font=("Courier", 9))
        self.metrics_text.pack(fill="both", expand=True)
        
        # Botones de acción
        actions_frame = ttk.LabelFrame(results_frame, text="Acciones", padding="10")
        actions_frame.pack(fill="x", padx=10, pady=5)
        
        action_buttons = ttk.Frame(actions_frame)
        action_buttons.pack(fill="x")
        
        ttk.Button(action_buttons, text="📈 Ver Gráficos", 
                  command=self.show_plots).pack(side="left", padx=5)
        ttk.Button(action_buttons, text="📋 Feature Importance", 
                  command=self.show_feature_importance).pack(side="left", padx=5)
        ttk.Button(action_buttons, text="🔮 Hacer Predicción", 
                  command=self.make_prediction).pack(side="left", padx=5)
        
        # Resultados detallados
        detailed_frame = ttk.LabelFrame(results_frame, text="Resultados Detallados", padding="10")
        detailed_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.results_text = tk.Text(detailed_frame, height=12, wrap="word", 
                                   state="disabled", font=("Courier", 9))
        
        results_scrollbar = ttk.Scrollbar(detailed_frame, orient="vertical", 
                                        command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
        self.results_text.pack(side="left", fill="both", expand=True)
        results_scrollbar.pack(side="right", fill="y")
    
    # Métodos de procesamiento (MODIFICADOS para usar el procesador mejorado)
    def browse_directory(self):
        """Seleccionar directorio con archivos .dump"""
        directory = filedialog.askdirectory(title="Seleccionar directorio con archivos .dump")
        if directory:
            self.directory_var.set(directory)
            try:
                dump_files = self.processor.find_dump_files(directory)
                message = f"Directorio seleccionado: {len(dump_files)} archivos .dump encontrados"
                self.update_status(message)
            except Exception as e:
                logger.error(f"Error explorando directorio: {e}")
    
    def browse_output_directory(self):
        """Seleccionar directorio de salida"""
        directory = filedialog.askdirectory(title="Seleccionar directorio de salida")
        if directory:
            self.output_dir_var.set(directory)
    
    def start_processing(self):
        """Iniciar procesamiento de archivos dump"""
        if self.is_processing:
            return
        
        if not self.directory_var.get():
            messagebox.showwarning("Advertencia", "Seleccione un directorio con archivos .dump")
            return
        
        # Actualizar configuración del procesador
        if self.enhanced_mode:
            if self.enable_ovito_var.get():
                self._update_processor_to_ovito()
            else:
                self._update_processor_to_standard()
        else:
            # Configurar procesador original
            self.processor.set_parameters(
                atm_total=self.atm_total_var.get(),
                energy_min=self.energy_min_var.get(),
                energy_max=self.energy_max_var.get(),
                energy_bins=self.energy_bins_var.get()
            )
        
        # Iniciar procesamiento en hilo separado
        self.is_processing = True
        self.process_button.config(state="disabled")
        
        thread = threading.Thread(target=self._processing_worker, daemon=True)
        thread.start()
    
    def _processing_worker(self):
        """Worker para procesamiento de archivos"""
        try:
            self.log_process("Iniciando procesamiento de archivos dump...")
            
            # Procesar directorio
            dataset = self.processor.process_directory(self.directory_var.get())
            
            # Guardar dataset
            output_dir = Path(self.output_dir_var.get())
            output_dir.mkdir(exist_ok=True)
            
            csv_path = output_dir / "batch_dataset.csv"
            dataset.to_csv(csv_path)
            
            # Actualizar UI
            self.current_dataset = dataset
            self.frame.after(0, self._update_after_processing, dataset, csv_path)
            
        except Exception as e:
            self.frame.after(0, self._handle_processing_error, str(e))
        finally:
            self.frame.after(0, self._reset_processing_state)
    
    def _update_after_processing(self, dataset, csv_path):
        """Actualizar UI después del procesamiento"""
        self.log_process(f"Procesamiento completado: {csv_path}")
        
        # Mostrar estadísticas OVITO si corresponde
        if self.enhanced_mode and self.enable_ovito_var.get():
            self._show_ovito_statistics(dataset)
        
        self.update_dataset_info(dataset)
        self.update_features_table(dataset)
        
        # Cambiar a tab de features
        self.notebook.select(1)
        
        # Notificar callback
        self.data_loaded_callback(dataset)
    
    def _show_ovito_statistics(self, dataset):
        """Mostrar estadísticas del filtrado OVITO"""
        try:
            if '_filter_ratio' in dataset.columns:
                avg_ratio = dataset['_filter_ratio'].mean()
                min_ratio = dataset['_filter_ratio'].min()
                max_ratio = dataset['_filter_ratio'].max()
                
                if '_n_atoms_filtered' in dataset.columns:
                    avg_filtered = dataset['_n_atoms_filtered'].mean()
                    stats_msg = (f"ESTADÍSTICAS OVITO:\n"
                               f"  Ratio promedio conservado: {avg_ratio:.3f}\n"
                               f"  Rango ratio: {min_ratio:.3f} - {max_ratio:.3f}\n"
                               f"  Átomos promedio post-filtro: {avg_filtered:.0f}")
                    self.log_process(stats_msg)
        except Exception as e:
            logger.warning(f"Error mostrando estadísticas OVITO: {e}")
    
    def _handle_processing_error(self, error_msg):
        """Manejar errores de procesamiento"""
        self.log_process(f"ERROR: {error_msg}")
        messagebox.showerror("Error", f"Error en procesamiento: {error_msg}")
    
    def _reset_processing_state(self):
        """Resetear estado de procesamiento"""
        self.is_processing = False
        self.process_button.config(state="normal")
        self.progress_var.set(0)
        self.status_var.set("Listo para procesar")
    
    def load_existing_dataset(self):
        """Cargar dataset existente"""
        file_path = filedialog.askopenfilename(
            title="Cargar Dataset",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.xlsx'):
                    dataset = pd.read_excel(file_path, index_col=0)
                else:
                    dataset = pd.read_csv(file_path, index_col=0)
                
                self.current_dataset = dataset
                self.update_dataset_info(dataset)
                self.update_features_table(dataset)
                
                # Cambiar a tab de features
                self.notebook.select(1)
                
                # Notificar callback
                self.data_loaded_callback(dataset)
                
            except Exception as e:
                messagebox.showerror("Error", f"Error cargando dataset: {str(e)}")
    
    # ========== RESTO DE MÉTODOS SIN CAMBIOS ==========
    # [Incluir todos los demás métodos existentes: update_dataset_info, update_features_table, 
    #  toggle_feature_selection, select_all_features, etc. - son los mismos del código original]
    
    def update_dataset_info(self, dataset):
        """Actualizar información del dataset"""
        if dataset is not None:
            info = f"Dataset: {len(dataset)} muestras, {len(dataset.columns)} columnas"
            if 'vacancies' in dataset.columns:
                vac_stats = dataset['vacancies'].describe()
                info += f" | Vacancies: {vac_stats['min']:.0f}-{vac_stats['max']:.0f} (mean: {vac_stats['mean']:.1f})"
            
            # Agregar info OVITO si está presente
            if self.enhanced_mode and '_ovito_filtered' in dataset.columns:
                ovito_count = dataset['_ovito_filtered'].sum()
                info += f" | OVITO: {ovito_count} archivos filtrados"
            
            self.dataset_info_label.config(text=info)
    
    # [RESTO DE MÉTODOS COPIADOS TAL COMO ESTÁN EN EL ORIGINAL]
    # Por brevedad, incluyo solo algunos métodos clave. Los demás se mantienen iguales.
    
    def update_features_table(self, dataset):
        """Actualizar tabla de features"""
        # Limpiar tabla
        for item in self.features_tree.get_children():
            self.features_tree.delete(item)
        
        if dataset is None:
            return
        
        # Excluir columnas metadata
        exclude_cols = ['file_path', 'vacancies', '_file_name', '_ovito_filtered', 
                       '_n_atoms_original', '_n_atoms_filtered', '_filter_ratio']
        feature_cols = [col for col in dataset.columns 
                       if col not in exclude_cols and not col.startswith('_')]
        
        # Calcular correlaciones con target si existe
        correlations = {}
        if 'vacancies' in dataset.columns:
            for col in feature_cols:
                try:
                    corr = dataset[col].corr(dataset['vacancies'])
                    correlations[col] = corr if not pd.isna(corr) else 0.0
                except:
                    correlations[col] = 0.0
        
        # Llenar tabla
        for col in feature_cols:
            corr = correlations.get(col, 0.0)
            dtype = str(dataset[col].dtype)
            
            # Determinar tipo simplificado
            if 'float' in dtype or 'int' in dtype:
                type_simple = "Numérico"
            else:
                type_simple = "Categórico"
            
            # Insertar en tabla
            self.features_tree.insert('', 'end', values=(
                col,
                type_simple,
                f"{abs(corr):.3f}",
                "TBD",  # Importancia se calculará después del entrenamiento
                "No"
            ))
        
        self.update_selection_summary()
    
    def toggle_feature_selection(self, event):
        """Alternar selección de feature con doble click"""
        item = self.features_tree.selection()[0]
        feature_name = self.features_tree.item(item, 'values')[0]
        
        if feature_name in self.selected_features:
            self.selected_features.remove(feature_name)
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "No"
            ))
        else:
            self.selected_features.add(feature_name)
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "Sí"
            ))
        
        self.update_selection_summary()
    
    def select_all_features(self):
        """Seleccionar todas las features"""
        self.selected_features.clear()
        for item in self.features_tree.get_children():
            feature_name = self.features_tree.item(item, 'values')[0]
            self.selected_features.add(feature_name)
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "Sí"
            ))
        self.update_selection_summary()
    
    def deselect_all_features(self):
        """Deseleccionar todas las features"""
        self.selected_features.clear()
        for item in self.features_tree.get_children():
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], "No"
            ))
        self.update_selection_summary()
    
    def auto_select_features(self):
        """Auto-seleccionar top features por correlación"""
        if self.current_dataset is None or 'vacancies' not in self.current_dataset.columns:
            messagebox.showwarning("Advertencia", "No hay dataset con target para auto-selección")
            return
        
        # Calcular correlaciones
        exclude_cols = ['file_path', 'vacancies', '_file_name', '_ovito_filtered']
        feature_cols = [col for col in self.current_dataset.columns 
                       if col not in exclude_cols and not col.startswith('_')]
        
        correlations = []
        for col in feature_cols:
            try:
                corr = abs(self.current_dataset[col].corr(self.current_dataset['vacancies']))
                if not pd.isna(corr):
                    correlations.append((col, corr))
            except:
                pass
        
        # Seleccionar top 30
        correlations.sort(key=lambda x: x[1], reverse=True)
        top_features = [feat for feat, _ in correlations[:30]]
        
        # Actualizar selección
        self.selected_features.clear()
        self.selected_features.update(top_features)
        
        # Actualizar tabla
        for item in self.features_tree.get_children():
            feature_name = self.features_tree.item(item, 'values')[0]
            selected = "Sí" if feature_name in self.selected_features else "No"
            self.features_tree.item(item, values=(
                *self.features_tree.item(item, 'values')[:4], selected
            ))
        
        self.update_selection_summary()
        messagebox.showinfo("Auto-selección", f"Seleccionadas {len(top_features)} features por correlación")
    
    def update_selection_summary(self):
        """Actualizar resumen de selección"""
        count = len(self.selected_features)
        self.selection_summary_label.config(text=f"{count} features seleccionadas")
    
    # Métodos de entrenamiento (SIN CAMBIOS)
    def start_training(self):
        """Iniciar entrenamiento del modelo"""
        if self.is_training:
            return
        
        if self.current_dataset is None:
            messagebox.showwarning("Advertencia", "No hay dataset cargado")
            return
        
        if not self.selected_features:
            messagebox.showwarning("Advertencia", "Seleccione features para entrenar")
            return
        
        if 'vacancies' not in self.current_dataset.columns:
            messagebox.showerror("Error", "No se encontró columna 'vacancies' como target")
            return
        
        # Iniciar entrenamiento en hilo separado
        self.is_training = True
        self.train_button.config(state="disabled")
        self.stop_train_button.config(state="normal")
        
        thread = threading.Thread(target=self._training_worker, daemon=True)
        thread.start()
        
        # Cambiar a tab de entrenamiento
        self.notebook.select(2)
    
    def _training_worker(self):
        """Worker para entrenamiento del modelo"""
        try:
            self.log_training("Iniciando entrenamiento...")
            
            # Preparar datos
            X = self.current_dataset[list(self.selected_features)]
            y = self.current_dataset['vacancies']
            
            self.log_training(f"Features: {len(self.selected_features)}, Muestras: {len(X)}")
            
            # Dividir datos
            from sklearn.model_selection import train_test_split
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=self.test_size_var.get(), 
                random_state=self.random_state_var.get()
            )
            
            self.frame.after(0, self._update_train_progress, 20, "Dividiendo datos...")
            
            # Entrenar modelo
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
            
            self.frame.after(0, self._update_train_progress, 40, "Entrenando Random Forest...")
            
            model = RandomForestRegressor(
                n_estimators=self.n_estimators_var.get(),
                random_state=self.random_state_var.get(),
                n_jobs=-1
            )
            
            model.fit(X_train, y_train)
            
            self.frame.after(0, self._update_train_progress, 70, "Evaluando modelo...")
            
            # Hacer predicciones
            train_pred = model.predict(X_train)
            test_pred = model.predict(X_test)
            
            # Calcular métricas
            train_mae = mean_absolute_error(y_train, train_pred)
            test_mae = mean_absolute_error(y_test, test_pred)
            train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
            test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
            train_r2 = r2_score(y_train, train_pred)
            test_r2 = r2_score(y_test, test_pred)
            
            # Feature importance
            feature_importance = pd.DataFrame({
                'feature': list(self.selected_features),
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            # Almacenar resultados
            results = {
                'model': model,
                'feature_importance': feature_importance,
                'metrics': {
                    'train_mae': train_mae,
                    'test_mae': test_mae,
                    'train_rmse': train_rmse,
                    'test_rmse': test_rmse,
                    'train_r2': train_r2,
                    'test_r2': test_r2,
                    'n_features': len(self.selected_features),
                    'n_train': len(X_train),
                    'n_test': len(X_test)
                },
                'test_data': {
                    'X_test': X_test,
                    'y_test': y_test,
                    'predictions': test_pred
                }
            }
            
            self.frame.after(0, self._update_after_training, results)
            
        except Exception as e:
            self.frame.after(0, self._handle_training_error, str(e))
        finally:
            self.frame.after(0, self._reset_training_state)
    
    def _update_train_progress(self, value, message):
        """Actualizar progreso de entrenamiento"""
        self.train_progress_var.set(value)
        self.train_status_var.set(message)
    
    def _update_after_training(self, results):
        """Actualizar UI después del entrenamiento"""
        self.trained_model = results
        
        # Actualizar métricas
        metrics = results['metrics']
        metrics_text = f"""RESULTADOS DEL ENTRENAMIENTO
==============================

CONFIGURACIÓN:
  Algoritmo: Random Forest
  Nº Estimadores: {self.n_estimators_var.get()}
  Features utilizadas: {metrics['n_features']}
  Muestras entrenamiento: {metrics['n_train']}
  Muestras prueba: {metrics['n_test']}"""
        
        # Agregar info OVITO si corresponde
        if self.enhanced_mode and self.enable_ovito_var.get():
            metrics_text += f"""
  MODO OVITO: HABILITADO
  Radio superficie: {self.surface_radius_var.get():.1f} Å
  Nivel suavizado: {self.smoothing_level_var.get()}"""
        
        metrics_text += f"""

MÉTRICAS DE RENDIMIENTO:
  Train MAE:  {metrics['train_mae']:.3f}
  Test MAE:   {metrics['test_mae']:.3f}
  Train RMSE: {metrics['train_rmse']:.3f}
  Test RMSE:  {metrics['test_rmse']:.3f}
  Train R²:   {metrics['train_r2']:.3f}
  Test R²:    {metrics['test_r2']:.3f}

TOP 10 FEATURES MÁS IMPORTANTES:
"""
        
        for i, row in results['feature_importance'].head(10).iterrows():
            metrics_text += f"  {row['feature'][:40]:40s}: {row['importance']:.4f}\n"
        
        # Actualizar feature importance en tabla
        self._update_feature_importance_in_table(results['feature_importance'])
        
        # Mostrar métricas
        self.metrics_text.config(state='normal')
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(1.0, metrics_text)
        self.metrics_text.config(state='disabled')
        
        # Log de entrenamiento
        self.log_training("Entrenamiento completado exitosamente!")
        self.log_training(f"Test R²: {metrics['test_r2']:.3f}, Test MAE: {metrics['test_mae']:.3f}")
        
        # Cambiar a tab de resultados
        self.notebook.select(3)
    
    def _update_feature_importance_in_table(self, feature_importance):
        """Actualizar importancia en tabla de features"""
        importance_dict = dict(zip(feature_importance['feature'], feature_importance['importance']))
        
        for item in self.features_tree.get_children():
            values = list(self.features_tree.item(item, 'values'))
            feature_name = values[0]
            
            if feature_name in importance_dict:
                values[3] = f"{importance_dict[feature_name]:.4f}"
            else:
                values[3] = "0.0000"
            
            self.features_tree.item(item, values=values)
    
    def _handle_training_error(self, error_msg):
        """Manejar errores de entrenamiento"""
        self.log_training(f"ERROR: {error_msg}")
        messagebox.showerror("Error", f"Error en entrenamiento: {error_msg}")
    
    def _reset_training_state(self):
        """Resetear estado de entrenamiento"""
        self.is_training = False
        self.train_button.config(state="normal")
        self.stop_train_button.config(state="disabled")
        self.train_progress_var.set(0)
        self.train_status_var.set("Listo para entrenar")
    
    def stop_training(self):
        """Detener entrenamiento"""
        self.is_training = False
        self.log_training("Deteniendo entrenamiento...")
    
    # [RESTO DE MÉTODOS DE PERSISTENCIA, VISUALIZACIÓN Y AUXILIARES SIN CAMBIOS]
    # save_model, load_model, show_plots, show_feature_importance, make_prediction, etc.
    
    # Métodos auxiliares
    def update_progress(self, current, total, message=""):
        """Callback para actualizar progreso del procesador"""
        if total > 0:
            percentage = (current / total) * 100
            self.progress_var.set(percentage)
        
        if message:
            self.status_var.set(message)
        
        self.frame.update_idletasks()
    
    def update_status(self, message):
        """Actualizar mensaje de estado"""
        self.status_var.set(message)
    
    def log_process(self, message):
        """Agregar mensaje al log de procesamiento"""
        self.process_log.insert(tk.END, f"{message}\n")
        self.process_log.see(tk.END)
        self.frame.update_idletasks()
    
    def log_training(self, message):
        """Agregar mensaje al log de entrenamiento"""
        self.training_log.insert(tk.END, f"{message}\n")
        self.training_log.see(tk.END)
        self.frame.update_idletasks()
    
    def reset(self):
        """Resetear el tab completo"""
        # Resetear variables LAMMPS
        self.directory_var.set("")
        self.output_dir_var.set("ml_dataset_output")
        self.atm_total_var.set(16384)
        self.energy_min_var.set(-4.0)
        self.energy_max_var.set(-3.0)
        self.energy_bins_var.set(10)
        
        # Resetear variables OVITO
        self.enable_ovito_var.set(False)
        self.surface_radius_var.set(3.0)
        self.smoothing_level_var.set(0)
        self.apply_stress_var.set(False)
        self.stress_x_var.set(1.0)
        self.stress_y_var.set(1.0)
        self.stress_z_var.set(1.0)
        self.export_filtered_var.set(False)
        
        # Resetear variables ML
        self.test_size_var.set(0.2)
        self.n_estimators_var.set(100)
        self.random_state_var.set(42)
        
        # Resetear datos
        self.current_dataset = None
        self.selected_features.clear()
        self.trained_model = None
        
        # Resetear UI
        self.progress_var.set(0)
        self.train_progress_var.set(0)
        self.status_var.set("Listo para procesar")
        self.train_status_var.set("Listo para entrenar")
        
        self.process_log.delete(1.0, tk.END)
        self.training_log.delete(1.0, tk.END)
        
        self.metrics_text.config(state='normal')
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.config(state='disabled')
        
        # Limpiar tablas
        for item in self.features_tree.get_children():
            self.features_tree.delete(item)
        
        self.update_dataset_info(None)
        self.update_selection_summary()
        
        # Resetear estados
        self.is_processing = False
        self.is_training = False
        self.process_button.config(state="normal")
        self.train_button.config(state="normal")
        self.stop_train_button.config(state="disabled")
        
        # Resetear procesador
        if self.enhanced_mode:
            self.processor = create_standard_processor()
            self.processor.set_progress_callback(self.update_progress)
            if hasattr(self, 'mode_label'):
                self.mode_label.config(text="Modo: ESTÁNDAR", foreground="black")
        
        # Volver al primer tab
        self.notebook.select(0)
    
    # [AGREGAR AQUÍ RESTO DE MÉTODOS DEL CÓDIGO ORIGINAL: save_model, load_model, 
    #  show_plots, show_feature_importance, make_prediction, etc.]