"""
Módulo para generar gráficos con Plotly
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional

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

    def _export_png(self, fig: go.Figure, output_path: Path) -> None:
        """
        Exporta una figura de Plotly a PNG usando el método nativo write_image.
        
        Args:
            fig: Figura de Plotly a exportar
            output_path: Ruta donde guardar el PNG
        """
        if not self.enable_png:
            return
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            # Usar el método nativo de Plotly (requiere kaleido instalado)
            fig.write_image(str(output_path), width=self.config.get("width", 1566), height=self.config.get("height", 365))
            logger.info("PNG guardado en: %s", output_path)
        except Exception as exc:
            logger.warning("Fallo al exportar PNG en %s: %s", output_path, exc)
    
    def create_portfolio_performance_chart(
        self, 
        performance_df: pd.DataFrame,
        output_html: Path,
        output_png: Optional[Path] = None
    ) -> str:
        """
        Crea el gráfico de rendimiento del portafolio
        
        Args:
            performance_df: DataFrame con el rendimiento
            output_html: Ruta para guardar el HTML
            output_png: Ruta opcional para guardar PNG
        
        Returns:
            Ruta del archivo HTML generado
        """
        try:
            if performance_df.empty:
                logger.warning("DataFrame vacío, no se puede generar gráfico")
                return ""
            
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
            
            # Guardar PNG si se especifica
            if output_png and self.enable_png:
                self._export_png(fig, Path(output_png))
            
            return str(output_html)
        
        except Exception as e:
            logger.error(f"Error generando gráfico de portafolio: {e}")
            return ""
    
    def create_asset_chart(
        self,
        symbol: str,
        intraday_data: Optional[pd.DataFrame],
        output_html: Path,
        output_png: Optional[Path] = None,
        daily_data: Optional[pd.DataFrame] = None,
        intraday_interval: Optional[str] = None,
    ) -> str:
        """
        Crea un gráfico individual para un activo
        
        Args:
            symbol: Símbolo del activo
            hist_data: DataFrame con datos históricos
            output_html: Ruta para guardar el HTML
            output_png: Ruta opcional para guardar PNG
        
        Returns:
            Ruta del archivo HTML generado
        """
        try:
            if (intraday_data is None or intraday_data.empty) and (daily_data is None or daily_data.empty):
                logger.warning(f"No hay datos para {symbol}")
                return ""

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
                return ""

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
            
            # Guardar PNG si se especifica
            if output_png and self.enable_png:
                self._export_png(fig, Path(output_png))
            
            return str(output_html)
        
        except Exception as e:
            logger.error(f"Error generando gráfico para {symbol}: {e}")
            return ""
    
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
    ) -> str:
        """
        Crea un gráfico de pastel con la distribución del portafolio
        
        Args:
            allocation_data: Lista con datos de distribución
            output_html: Ruta para guardar el HTML
            output_png: Ruta opcional para guardar PNG
        
        Returns:
            Ruta del archivo HTML generado
        """
        try:
            if not allocation_data:
                logger.warning("No hay datos de distribución")
                return ""
            
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
            
            # Guardar PNG si se especifica
            if output_png and self.enable_png:
                self._export_png(fig, Path(output_png))
            
            return str(output_html)
        
        except Exception as e:
            logger.error(f"Error generando gráfico de distribución: {e}")
            return ""
