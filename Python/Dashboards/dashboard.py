import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

# =========================================
# 1. Configuración inicial con tema oscuro completo
# =========================================
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.DARKLY,
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css",
    ],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Mi Dashboard Profesional - Dark Mode"
server = app.server

# =================================================================================
# 2. Datos de ejemplo
# =================================================================================
np.random.seed(42)
dates = pd.date_range(start="2023-01-01", end="2023-12-31", freq="D")
categories = ["Electrónicos", "Ropa", "Alimentos", "Hogar"]
regions = ["Norte", "Sur", "Este", "Oeste"]

data = {
    "Fecha": np.tile(dates, len(categories)),
    "Categoría": np.repeat(categories, len(dates)),
    "Ventas": np.random.randint(50, 500, len(dates) * len(categories)).cumsum(),
    "Beneficios": np.random.uniform(0.1, 0.3, len(dates) * len(categories)),
    "Región": np.random.choice(regions, len(dates) * len(categories)),
    "Satisfacción": np.random.uniform(3.5, 5.0, len(dates) * len(categories)),
}
df = pd.DataFrame(data)

# Datos resumidos para las cards
summary_data = {
    "Total Ventas": f"${df['Ventas'].sum():,.0f}",
    "Beneficio Promedio": f"{df['Beneficios'].mean() * 100:.1f}%",
    "Satisfacción": f"{df['Satisfacción'].mean():.1f}/5.0",
    "Clientes Únicos": "1,248",
}

# =================================================================================
# 3. Configuración de tema oscuro para los gráficos
# =================================================================================
dark_template = {
    "layout": {
        "paper_bgcolor": "#222",
        "plot_bgcolor": "#222",
        "font": {"color": "#EEE"},
        "xaxis": {"gridcolor": "#444", "linecolor": "#666", "zerolinecolor": "#444"},
        "yaxis": {"gridcolor": "#444", "linecolor": "#666", "zerolinecolor": "#444"},
        "hoverlabel": {"bgcolor": "#333", "font": {"color": "white"}},
        "colorway": ["#00bc8c", "#3498db", "#f39c12", "#e74c3c"],
    }
}


# =================================================================================
# 4. Creación de componentes visuales
# =================================================================================
def create_dark_card(title, value, icon_name, color):
    return dbc.Card(
        dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className=f"fas fa-{icon_name} fa-2x me-2"),
                        html.H5(title, className="card-title mb-0"),
                    ],
                    className="d-flex align-items-center",
                ),
                html.H2(value, className="mt-2 mb-0"),
            ]
        ),
        className=f"border-0 mb-3 h-100 bg-{color}",  # Usamos las clases de color originales
        style={
            "border-left": f"4px solid {get_border_color(color)}"
        },  # Borde lateral para contraste
    )


# Paleta de colores
def get_border_color(color):
    return {
        "primary": "#3498db",
        "success": "#00bc8c",
        "info": "#17a2b8",
        "warning": "#f39c12",
        "danger": "#e74c3c",
    }.get(color, "#555")


def create_light_dropdown(id, label, options, value, multi=False):
    return html.Div(
        [
            dbc.Label(
                label, className="mb-2 fw-bold text-light"
            ),  # Label claro sobre fondo oscuro
            dcc.Dropdown(
                id=id,
                options=[{"label": opt, "value": opt} for opt in options],
                value=value,
                multi=multi,
                clearable=False,
                className="light-dropdown",
                style={
                    "backgroundColor": "white",  # Fondo blanco
                    "color": "#333",  # Texto oscuro
                    "borderRadius": "6px",
                },
            ),
        ],
        className="mb-4",
    )


# Gráfico de tendencia interactivo
def create_trend_chart():
    fig = px.line(
        df.groupby(["Fecha", "Categoría"]).sum().reset_index(),
        x="Fecha",
        y="Ventas",
        color="Categoría",
        template=dark_template,
    )
    fig.update_layout(
        title="Tendencia de Ventas por Categoría",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    return fig


# Gráfico de barras apiladas
def create_stacked_bar_chart():
    monthly = (
        df.groupby([pd.Grouper(key="Fecha", freq="M"), "Región"])["Ventas"]
        .sum()
        .reset_index()
    )
    monthly["Mes"] = monthly["Fecha"].dt.strftime("%b")

    fig = px.bar(
        monthly,
        x="Mes",
        y="Ventas",
        color="Región",
        barmode="stack",
        template=dark_template,
        color_discrete_sequence=px.colors.qualitative.Dark24,
    )
    fig.update_layout(title="Ventas Mensuales por Región")
    return fig


# Gráfico circular interactivo
def create_pie_chart():
    cat_sales = df.groupby("Categoría")["Ventas"].sum().reset_index()
    fig = px.pie(
        cat_sales, values="Ventas", names="Categoría", hole=0.4, template=dark_template
    )
    fig.update_layout(
        title="Distribución de Ventas",
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        marker=dict(line=dict(color="#222", width=1)),
    )
    return fig


# =================================================================================
# 5. Layout del dashboard
# =================================================================================
app.layout = dbc.Container(
    fluid=True,
    className="dark-theme",
    children=[
        # Header con logo y título
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.I(className="fas fa-chart-line fa-2x me-2"),
                                html.H1("Dashboard de Ventas", className="mb-0"),
                            ],
                            className="d-flex align-items-center py-3",
                        )
                    ],
                    width=12,
                )
            ],
            className="border-bottom  mb-4",
        ),
        # Filtros y controles
        dbc.Row(
            [
                dbc.Col(
                    create_light_dropdown(
                        "category-dropdown",
                        "Categoría",
                        ["Electrónicos", "Ropa", "Alimentos", "Hogar"],
                        "Electrónicos",
                    ),
                    md=4,
                ),
                dbc.Col(
                    create_light_dropdown(
                        "region-dropdown",
                        "Región",
                        ["Norte", "Sur", "Este", "Oeste"],
                        ["Norte"],
                        multi=True,
                    ),
                    md=4,
                ),
                dbc.Col(
                    dcc.DatePickerRange(
                        id="date-range",
                        min_date_allowed=df["Fecha"].min(),
                        max_date_allowed=df["Fecha"].max(),
                        start_date=df["Fecha"].min(),
                        end_date=df["Fecha"].max(),
                        className="dark-datepicker",
                    ),
                    md=4,
                    className="d-flex align-items-end",
                ),
            ],
            className="border-bottom mb-4",
        ),
        # Tarjetas
        dbc.Row(
            [
                dbc.Col(
                    create_dark_card(
                        "Ventas Totales",
                        summary_data["Total Ventas"],
                        "dollar-sign",
                        "success",
                    ),
                    md=3,
                ),
                dbc.Col(
                    create_dark_card(
                        "Beneficio",
                        summary_data["Beneficio Promedio"],
                        "chart-line",
                        "info",
                    ),
                    md=3,
                ),
                dbc.Col(
                    create_dark_card(
                        "Satisfacción", summary_data["Satisfacción"], "smile", "warning"
                    ),
                    md=3,
                ),
                dbc.Col(
                    create_dark_card(
                        "Clientes", summary_data["Clientes Únicos"], "users", "danger"
                    ),
                    md=3,
                ),
            ],
            className="mb-4 g-3",
        ),
        # Gráficos
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="trend-chart",
                        figure=create_trend_chart(),
                        className="dark-graph",
                    ),
                    lg=8,
                    className="mb-3",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="pie-chart",
                        figure=create_pie_chart(),
                        className="dark-graph",
                    ),
                    lg=4,
                    className="mb-3",
                ),
            ],
            className="g-3",
        ),
        # Segunda fila de gráficos
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id="bar-chart",
                        figure=create_stacked_bar_chart(),
                        className="dark-graph",
                    ),
                    lg=6,
                    className="mb-3",
                ),
                dbc.Col(
                    dcc.Graph(
                        id="scatter-plot",
                        figure=px.scatter(
                            df.sample(100),
                            x="Ventas",
                            y="Satisfacción",
                            color="Categoría",
                            size="Beneficios",
                            template=dark_template,
                            title="Relación Ventas vs Satisfacción",
                        ),
                        className="dark-graph",
                    ),
                    lg=6,
                    className="mb-3",
                ),
            ],
            className="g-3",
        ),
        # Footer
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        [
                            html.P(
                                [
                                    html.Span(
                                        "© 2025 Nombre estudiantes", className="me-2"
                                    ),
                                    html.A(
                                        html.I(className="fab fa-github me-2"),
                                        href="#asdf",
                                    ),
                                    html.A(
                                        html.I(className="fab fa-linkedin me-2"),
                                        href="#",
                                    ),
                                    html.A(
                                        html.I(className="fa-brands fa-instagram"),
                                        href="#asdf",
                                    ),
                                ],
                                className="text-muted text-center py-3 mb-0",
                            )
                        ]
                    ),
                    width=12,
                )
            ],
            className="mt-4 border-top border-dark",
        ),
    ],
    style={
        "backgroundColor": "#1a1a1a",
        "color": "#EEE",
        "minHeight": "100vh",
        "padding": "20px",
    },
)


# =========================================
# 6. Callbacks para interactividad
# =========================================
@callback(
    Output("trend-chart", "figure"),
    [
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
        Input("region-dropdown", "value"),
    ],
)
def update_trend_chart(start_date, end_date, regions):
    if not isinstance(regions, list):
        regions = [regions]

    filtered_df = df[
        (df["Fecha"] >= start_date)
        & (df["Fecha"] <= end_date)
        & (df["Región"].isin(regions))
    ]

    if filtered_df.empty:
        return go.Figure(layout=dark_template["layout"])

    fig = px.line(
        filtered_df.groupby(["Fecha", "Categoría"]).sum().reset_index(),
        x="Fecha",
        y="Ventas",
        color="Categoría",
        template=dark_template,
    )
    fig.update_layout(title="Tendencia de Ventas por Categoría", hovermode="x unified")
    return fig


# =========================================
# 7. Estilos CSS personalizados
# =========================================
app.css.append_css(
    {
        "external_url": [
            {
                "selector": ".light-dropdown .Select-menu-outer",
                "rule": """
            background-color: white !important;
            color: #333 !important;
            border: 1px solid #ddd !important;
        """,
            },
            {
                "selector": ".light-dropdown .Select-control",
                "rule": "border: 1px solid #ddd !important;",
            },
            {
                "selector": ".light-dropdown .Select-value-label",
                "rule": "color: #333 !important;",
            },
        ]
    }
)

# =========================================
# 8. Ejecutar la aplicación
# =========================================
if __name__ == "__main__":
    app.run(debug=True)
