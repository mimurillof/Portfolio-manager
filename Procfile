# Heroku Procfile para Portfolio Manager Multi-Cliente
# Worker que ejecuta cada 15 minutos durante horario de mercado (NYSE)

# Opción 1: Usar el nuevo sistema multi-cliente (RECOMENDADO)
worker: python generate_report.py --worker --period 6mo --skip-empty

# Opción 2: Usar batch_process_portfolios.py directamente (sin scheduler)
# worker: python batch_process_portfolios.py --period 6mo --skip-empty


