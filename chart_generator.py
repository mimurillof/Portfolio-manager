"""
Módulo para generar gráficos con Plotly
"""
import io
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChartGenerator:
    """Clase para generar gráficos del portafolio"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.colors = config.get("colors", {})
        self.enable_png = bool(config.get("enable_png_export", True))

    def _export_png_to_bytes(self, fig: go.Figure) -> Optional[bytes]:
        """
        Exporta una figura de Plotly a PNG en memoria como bytes.
        Método robusto basado en write_image con manejo de errores mejorado.
        
        Args:
            fig: Figura de Plotly a exportar
        
        Returns:
            Bytes del archivo PNG o None si falla
        """
        if not self.enable_png:
            logger.debug("Exportación PNG deshabilitada en configuración")
            return None

        try:
            # Configurar dimensiones
            width = self.config.get("width", 1200)
            height = self.config.get("height", 600)
            
            logger.debug(f"Intentando exportar PNG con dimensiones {width}x{height}")
            
            # Método directo: usar write_image que internamente maneja el buffer
            # Este es el método que funciona correctamente en Heroku
            img_bytes = fig.to_image(format="png", width=width, height=height)
            
            if img_bytes and len(img_bytes) > 0:
                logger.info(f"✅ PNG generado correctamente ({len(img_bytes)} bytes)")
                return img_bytes
            else:
                logger.warning("⚠️ Se generó PNG pero está vacío")
                return None
            
        except ImportError as exc:
            logger.error(f"⚠️ kaleido no está instalado: {exc}")
            logger.info("💡 Instala kaleido con: pip install kaleido")
            return None
        except Exception as exc:
            logger.exception("❌ Error al exportar PNG con to_image")
            return None
    
    def _save_chart_robustly(
        self,
        fig: go.Figure,
        filepath: str,
        width: int = 1200,
        height: int = 600
    ) -> Optional[str]:
        """
        Guarda un gráfico de forma robusta con manejo de errores mejorado.
        Implementación basada en el código funcional que sí trabaja en Heroku.
        
        Args:
            fig: Figura de Plotly a guardar
            filepath: Ruta completa donde guardar
            width: Ancho de la imagen
            height: Alto de la imagen
            
        Returns:
            Ruta del archivo guardado o None si falla
        """
        try:
            # Crear directorio si no existe
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            # Determinar el formato según la extensión
            ext = Path(filepath).suffix.lower()
            
            if ext == '.png':
                try:
                    # Intentar guardar como PNG directamente
                    fig.write_image(filepath, width=width, height=height)
                    logger.info(f"✅ Gráfico guardado como PNG: {filepath}")
                    return filepath
                except Exception as png_error:
                    logger.exception("⚠️ No se pudo guardar como PNG usando write_image")
                    logger.info("💡 Guardando como HTML interactivo en su lugar...")
                    
                    # Fallback a HTML
                    html_filepath = filepath.replace('.png', '.html')
                    fig.write_html(html_filepath)
                    logger.info(f"✅ Gráfico guardado como HTML: {html_filepath}")
                    return html_filepath
            else:
                # Guardar como HTML directamente
                fig.write_html(filepath)
                logger.info(f"✅ Gráfico guardado como HTML: {filepath}")
                return filepath
                
        except Exception as e:
            logger.exception("❌ Error inesperado al guardar gráfico")
            return None
    
    
    def create_portfolio_performance_chart(
        self, 
        performance_df: pd.DataFrame,
        output_html: Path,
        output_png: Optional[Path] = None
    ) -> Tuple[str, Optional[bytes]]:
        """
        Crea el gráfico de rendimiento del portafolio
        
        Args:
            performance_df: DataFrame con el rendimiento
            output_html: Ruta para guardar el HTML
            output_png: Ruta opcional para guardar PNG (se mantiene por compatibilidad)
        
        Returns:
            Tupla con (ruta del HTML generado, bytes del PNG o None)
        """
        try:
            if performance_df.empty:
                logger.warning("DataFrame vacío, no se puede generar gráfico")
                return "", None
            
            # Crear figura
            fig = go.Figure()
            
            # Agregar línea de rendimiento
            fig.add_trace(go.Scatter(
                x=performance_df['date'],
                y=performance_df['portfolio_value'],
                mode='lines',
                name='Portfolio Value',
                line=dict(color=self.colors.get("neutral", "#3b82f6"), width=2),
                fill='tozeroy',
                fillcolor=f'rgba(59, 130, 246, 0.1)',
            ))
            
            # Configurar layout
            fig.update_layout(
                title={
                    'text': 'Rendimiento del Portafolio',
                    'x': 0.5,
                    'xanchor': 'center',
                    'font': {'size': 20, 'color': self.colors.get("text", "#1f2937")}
                },
                xaxis_title='Fecha',
                yaxis_title='Valor del Portafolio ($)',
                template=self.config.get("template", "plotly_white"),
                hovermode='x unified',
                showlegend=False,
                height=self.config.get("height", 365),
                width=self.config.get("width", 1566),
                margin=dict(l=60, r=30, t=60, b=60),
                plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)',
                ),
                yaxis=dict(
                    showgrid=True,
                    gridcolor='rgba(0,0,0,0.05)',
                    tickformat='$,.2f',
                ),
            )
            
            # Guardar HTML
            fig.write_html(str(output_html))
            logger.info(f"Gráfico HTML guardado en: {output_html}")
            
            # Generar PNG (primero intentando vía archivo para reproducir comportamiento funcional existente)
            png_bytes = None
            if self.enable_png:
                saved_path = None
                if output_png is not None:
                    saved_path = self._save_chart_robustly(
                        fig,
                        str(output_png),
                        width=self.config.get("width", 1200),
                        height=self.config.get("height", 600)
                    )
                    if saved_path and saved_path.lower().endswith(".png"):
                        try:
                            with open(saved_path, "rb") as png_file:
                                png_bytes = png_file.read()
                            logger.info(f"PNG cargado desde disco: {saved_path}")
                        except Exception as file_error:
                            logger.error(f"No se pudo leer PNG generado ({saved_path}): {file_error}")
                            png_bytes = None
                
                # Fallback a generación in-memory si no obtuvimos bytes desde archivo
                if png_bytes is None:
                    logger.debug("Intentando exportación PNG en memoria para gráfico de portafolio")
                    png_bytes = self._export_png_to_bytes(fig)

                if png_bytes is None:
                    logger.warning("No se pudo generar PNG del gráfico de portafolio (disco ni memoria)")
            
            return str(output_html), png_bytes
        
        except Exception as e:
            logger.error(f"Error generando gráfico de portafolio: {e}")
            return "", None
    
    def create_asset_chart(
        self,
        symbol: str,
        intraday_data: Optional[pd.DataFrame],
        output_html: Path,
        output_png: Optional[Path] = None,
        daily_data: Optional[pd.DataFrame] = None,
        intraday_interval: Optional[str] = None,
    ) -> Tuple[str, Optional[bytes]]:
        """
        Crea un gráfico individual para un activo
        
        Args:
            symbol: Símbolo del activo
            hist_data: DataFrame con datos históricos
            output_html: Ruta para guardar el HTML
            output_png: Ruta opcional para guardar PNG (se mantiene por compatibilidad)
            daily_data: Datos diarios
            intraday_interval: Intervalo intradiario
        
        Returns:
            Tupla con (ruta del HTML generado, bytes del PNG o None)
        """
        try:
            if (intraday_data is None or intraday_data.empty) and (daily_data is None or daily_data.empty):
                logger.warning(f"No hay datos para {symbol}")
                return "", None

            traces = []
            buttons = []

            base_color = self.colors.get("neutral", "#3b82f6")
            fill_color = 'rgba(59, 130, 246, 0.12)'

            def add_trace_from_df(df: pd.DataFrame, label: str, visible: bool) -> None:
                if df is None or df.empty:
                    return
                sorted_df = df.sort_index()
                has_time_component = True
                if len(sorted_df.index) > 1:
                    first_delta = sorted_df.index[1] - sorted_df.index[0]
                    has_time_component = first_delta < pd.Timedelta(days=1)

                hovertemplate = (
                    "%{x|%Y-%m-%d %H:%M}<br>$%{y:,.2f}<extra></extra>"
                    if has_time_component
                    else "%{x|%Y-%m-%d}<br>$%{y:,.2f}<extra></extra>"
                )
                traces.append(go.Scatter(
                    x=sorted_df.index,
                    y=sorted_df['Close'],
                    mode='lines',
                    name=label,
                    visible=visible,
                    line=dict(color=base_color, width=2),
                    fill='tozeroy',
                    fillcolor=fill_color,
                    hovertemplate=hovertemplate,
                ))

            interval_key = (intraday_interval or "15m").lower()
            frequency_plan = {
                "15m": [
                    ("15 minutos", None),
                    ("1 hora", "1h"),
                    ("Diario (60d)", "1d"),
                ],
                "30m": [
                    ("30 minutos", None),
                    ("2 horas", "2h"),
                    ("Diario (60d)", "1d"),
                ],
                "60m": [
                    ("1 hora", None),
                    ("4 horas", "4h"),
                    ("Diario (60d)", "1d"),
                ],
                "1h": [
                    ("1 hora", None),
                    ("4 horas", "4h"),
                    ("Diario (60d)", "1d"),
                ],
            }.get(interval_key, [
                ("Intraday", None),
                ("Diario", "1d"),
            ])

            if intraday_data is not None and not intraday_data.empty:
                intraday_df = intraday_data.copy()
                intraday_df.index = pd.to_datetime(intraday_df.index)
                for label, rule in frequency_plan:
                    if rule is None:
                        source_df = intraday_df
                    else:
                        source_df = intraday_df.resample(rule).agg({'Close': 'last'}).dropna()

                        if source_df.empty and daily_data is not None and not daily_data.empty:
                            source_df = daily_data

                    add_trace_from_df(source_df, label, visible=not traces)

            if daily_data is not None and not daily_data.empty:
                daily_df = daily_data.copy()
                daily_df.index = pd.to_datetime(daily_df.index)
                add_trace_from_df(daily_df, 'Histórico 6M', visible=not traces)

            if not traces:
                logger.warning(f"No se pudieron crear trazas para {symbol}")
                return "", None

            fig = go.Figure(data=traces)

            # Configurar botones según número de trazas
            visibility_matrix = []
            for idx in range(len(traces)):
                visible_flags = [False] * len(traces)
                visible_flags[idx] = True
                visibility_matrix.append(visible_flags)

            button_labels = [trace.name for trace in traces]
            for label, visibility in zip(button_labels, visibility_matrix):
                buttons.append(dict(
                    label=label,
                    method="update",
                    args=[{"visible": visibility}],
                ))

            # Configurar layout
            fig.update_layout(
                title=f'{symbol} - Precio Histórico',
                xaxis_title='Fecha',
                yaxis_title='Precio ($)',
                template=self.config.get("template", "plotly_white"),
                height=420,
                margin=dict(l=60, r=30, t=60, b=60),
                xaxis_rangeslider_visible=False,
                hovermode='x unified',
                showlegend=False,
                updatemenus=[
                    dict(
                        type="buttons",
                        direction="right",
                        x=0.5,
                        y=1.15,
                        xanchor='center',
                        buttons=buttons,
                    )
                ] if len(buttons) > 1 else [],
            )
            fig.update_xaxes(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)'
            )
            fig.update_yaxes(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                tickformat='$,.2f'
            )
            
            # Guardar HTML
            fig.write_html(str(output_html))
            logger.info(f"Gráfico de {symbol} guardado en: {output_html}")
            
            # Generar PNG (intentar primero guardando a archivo, luego fallback en memoria)
            png_bytes = None
            if self.enable_png:
                saved_path = None
                if output_png is not None:
                    saved_path = self._save_chart_robustly(
                        fig,
                        str(output_png),
                        width=self.config.get("width", 1200),
                        height=self.config.get("height", 600)
                    )
                    if saved_path and saved_path.lower().endswith(".png"):
                        try:
                            with open(saved_path, "rb") as png_file:
                                png_bytes = png_file.read()
                            logger.info(f"PNG de {symbol} cargado desde disco: {saved_path}")
                        except Exception as file_error:
                            logger.error(f"No se pudo leer PNG de {symbol} en {saved_path}: {file_error}")
                            png_bytes = None
                
                if png_bytes is None:
                    logger.debug(f"Intentando exportación PNG en memoria para {symbol}")
                    png_bytes = self._export_png_to_bytes(fig)

                if png_bytes is None:
                    logger.warning(f"No se pudo generar PNG para {symbol} (disco ni memoria)")
            
            return str(output_html), png_bytes
        
        except Exception as e:
            logger.error(f"Error generando gráfico para {symbol}: {e}")
            return "", None
    
    def create_mini_sparkline(self, data: List[float]) -> str:
        """
        Crea un mini gráfico sparkline
        
        Args:
            data: Lista de valores
        
        Returns:
            HTML del gráfico embebido como string
        """
        try:
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                y=data,
                mode='lines',
                line=dict(
                    color=self.colors.get("positive" if data[-1] > data[0] else "negative", "#3b82f6"),
                    width=2
                ),
                showlegend=False,
            ))
            
            fig.update_layout(
                height=30,
                width=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                plot_bgcolor='transparent',
                paper_bgcolor='transparent',
            )
            
            return fig.to_html(include_plotlyjs=False, div_id=f"sparkline_{id(data)}")
        
        except Exception as e:
            logger.error(f"Error generando sparkline: {e}")
            return ""
    
    def create_allocation_pie_chart(
        self,
        allocation_data: List[Dict],
        output_html: Path,
        output_png: Optional[Path] = None
    ) -> Tuple[str, Optional[bytes]]:
        """
        Crea un gráfico de pastel con la distribución del portafolio
        
        Args:
            allocation_data: Lista con datos de distribución
            output_html: Ruta para guardar el HTML
            output_png: Ruta opcional para guardar PNG (se mantiene por compatibilidad)
        
        Returns:
            Tupla con (ruta del HTML generado, bytes del PNG o None)
        """
        try:
            if not allocation_data:
                logger.warning("No hay datos de distribución")
                return "", None
            
            labels = [asset["symbol"] for asset in allocation_data]
            values = [asset["allocation_percent"] for asset in allocation_data]
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                textinfo='label+percent',
                marker=dict(
                    colors=px.colors.qualitative.Set3[:len(labels)]
                ),
            )])
            
            fig.update_layout(
                title='Distribución del Portafolio',
                template=self.config.get("template", "plotly_white"),
                height=400,
                showlegend=True,
            )
            
            # Guardar HTML
            fig.write_html(str(output_html))
            logger.info(f"Gráfico de distribución guardado en: {output_html}")
            
            png_bytes = None
            if self.enable_png:
                saved_path = None
                if output_png is not None:
                    saved_path = self._save_chart_robustly(
                        fig,
                        str(output_png),
                        width=self.config.get("width", 1200),
                        height=self.config.get("height", 600)
                    )
                    if saved_path and saved_path.lower().endswith(".png"):
                        try:
                            with open(saved_path, "rb") as png_file:
                                png_bytes = png_file.read()
                            logger.info(f"PNG de distribución cargado desde disco: {saved_path}")
                        except Exception as file_error:
                            logger.error(f"No se pudo leer PNG de distribución en {saved_path}: {file_error}")
                            png_bytes = None
                
                if png_bytes is None:
                    logger.debug("Intentando exportación PNG en memoria para gráfico de distribución")
                    png_bytes = self._export_png_to_bytes(fig)

                if png_bytes is None:
                    logger.warning("No se pudo generar PNG del gráfico de distribución (disco ni memoria)")
            
            return str(output_html), png_bytes
        
        except Exception as e:
            logger.error(f"Error generando gráfico de distribución: {e}")
            return "", None
