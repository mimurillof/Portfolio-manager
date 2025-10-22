PS C:\Users\mikia\mi-proyecto> heroku logs --tail --app portofolio-manager-horizon
2025-10-22T15:51:38.695792+00:00 app[worker.1]: INFO:portfolio_processor:Total de usuarios a procesar: 1
2025-10-22T15:51:38.695792+00:00 app[worker.1]: 
2025-10-22T15:51:38.695818+00:00 app[worker.1]: 2025-10-22 15:51:38 - portfolio_processor - INFO -
2025-10-22T15:51:38.695820+00:00 app[worker.1]: [1/1] Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985...
2025-10-22T15:51:38.695820+00:00 app[worker.1]: INFO:portfolio_processor:
2025-10-22T15:51:38.695821+00:00 app[worker.1]: [1/1] Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985...
2025-10-22T15:51:38.695847+00:00 app[worker.1]: 2025-10-22 15:51:38 - portfolio_processor - INFO - === Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 ===
2025-10-22T15:51:38.695847+00:00 app[worker.1]: INFO:portfolio_processor:=== Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 ===
2025-10-22T15:51:38.760737+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/rest/v1/users?select=%2A&user_id=eq.048adfcc-fe6e-4608-9b74-fc5608eed985 "HTTP/2 200 OK"
2025-10-22T15:51:38.863280+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/rest/v1/portfolios?select=%2A&user_id=eq.048adfcc-fe6e-4608-9b74-fc5608eed985 "HTTP/2 200 OK"
2025-10-22T15:51:38.863847+00:00 app[worker.1]: INFO:supabase_client:Usuario 048adfcc-fe6e-4608-9b74-fc5608eed985: 1 portfolio(s) encontrado(s).
2025-10-22T15:51:38.925258+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/rest/v1/assets?select=%2A&portfolio_id=eq.5 "HTTP/2 200 OK"
2025-10-22T15:51:38.925830+00:00 app[worker.1]: INFO:supabase_client:Portfolio 5: 4 asset(s) encontrado(s).
2025-10-22T15:51:38.925858+00:00 app[worker.1]: INFO:supabase_client:Datos completos obtenidos para usuario 048adfcc-fe6e-4608-9b74-fc5608eed985: 1 portfolio(s).
2025-10-22T15:51:38.925905+00:00 app[worker.1]: 2025-10-22 15:51:38 - portfolio_processor - INFO - Usuario: Miguel Angel Murillo Frias (murillofrias.miguel@gmail.com)
2025-10-22T15:51:38.925907+00:00 app[worker.1]: INFO:portfolio_processor:Usuario: Miguel Angel Murillo Frias (murillofrias.miguel@gmail.com)
2025-10-22T15:51:38.925937+00:00 app[worker.1]: 2025-10-22 15:51:38 - portfolio_processor - INFO -   Portfolio: mki (4 assets)     
2025-10-22T15:51:38.925938+00:00 app[worker.1]: INFO:portfolio_processor:  Portfolio: mki (4 assets)
2025-10-22T15:51:39.064449+00:00 app[worker.1]: 2025-10-22 15:51:39 - portfolio_processor - INFO - Ticker validado en yfinance: ^SPX
2025-10-22T15:51:39.064488+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: ^SPX
2025-10-22T15:51:39.195832+00:00 app[worker.1]: 2025-10-22 15:51:39 - portfolio_processor - INFO - Ticker validado en yfinance: BTC-USD
2025-10-22T15:51:39.195840+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: BTC-USD
2025-10-22T15:51:39.330667+00:00 app[worker.1]: 2025-10-22 15:51:39 - portfolio_processor - INFO - Ticker validado en yfinance: PAXG-USD
2025-10-22T15:51:39.330680+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: PAXG-USD
2025-10-22T15:51:39.464889+00:00 app[worker.1]: 2025-10-22 15:51:39 - portfolio_processor - INFO - Ticker validado en yfinance: NVDA
2025-10-22T15:51:39.464905+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: NVDA
2025-10-22T15:51:39.464928+00:00 app[worker.1]: 2025-10-22 15:51:39 - portfolio_processor - INFO - Generando reporte con 4 assets únicos...
2025-10-22T15:51:39.464929+00:00 app[worker.1]: INFO:portfolio_processor:Generando reporte con 4 assets únicos...
2025-10-22T15:51:39.464959+00:00 app[worker.1]: INFO:portfolio_manager:Iniciando generación de reporte completo...
2025-10-22T15:51:39.464976+00:00 app[worker.1]: INFO:portfolio_manager:Usando assets dinámicos desde base de datos (4 assets)      
2025-10-22T15:51:40.006494+00:00 app[worker.1]: INFO:portfolio_manager:Valor del portafolio: $150.67
2025-10-22T15:51:40.395500+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/bucket/portfolio-files "HTTP/2 200 OK"
2025-10-22T15:51:40.395990+00:00 app[worker.1]: INFO:supabase_storage:Descargando portafolio desde Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json
2025-10-22T15:51:40.511961+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json "HTTP/2 200 OK"
2025-10-22T15:52:07.309108+00:00 app[worker.1]: INFO:portfolio_manager:Generando gráficos...
2025-10-22T15:52:07.385762+00:00 app[worker.1]: INFO:chart_generator:Gráfico HTML guardado en: /app/charts/portfolio_chart.html    
2025-10-22T15:52:07.385932+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_chart.html
2025-10-22T15:52:08.100375+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_chart.html "HTTP/2 200 OK"
2025-10-22T15:52:08.100853+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/portfolio_chart.png
2025-10-22T15:52:08.372282+00:00 app[worker.1]: INFO:chart_generator:Gráfico de ^SPX guardado en: /app/charts/assets/^SPX_chart.html
2025-10-22T15:52:08.372488+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/_CARET_SPX_chart.html
2025-10-22T15:52:09.085643+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/_CARET_SPX_chart.html "HTTP/2 200 OK"
2025-10-22T15:52:09.086186+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/^SPX_chart.png
2025-10-22T15:52:09.521648+00:00 app[worker.1]: INFO:chart_generator:Gráfico de BTC-USD guardado en: /app/charts/assets/BTC-USD_chart.html
2025-10-22T15:52:09.521861+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/BTC-USD_chart.html
2025-10-22T15:52:09.879693+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/BTC-USD_chart.html "HTTP/2 200 OK"
2025-10-22T15:52:09.880182+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/BTC-USD_chart.png
2025-10-22T15:52:10.362498+00:00 app[worker.1]: INFO:chart_generator:Gráfico de PAXG-USD guardado en: /app/charts/assets/PAXG-USD_chart.html
2025-10-22T15:52:10.362685+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/PAXG-USD_chart.html
2025-10-22T15:52:11.391693+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/PAXG-USD_chart.html "HTTP/2 200 OK"
2025-10-22T15:52:11.392365+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/PAXG-USD_chart.png
2025-10-22T15:52:11.705205+00:00 app[worker.1]: INFO:chart_generator:Gráfico de NVDA guardado en: /app/charts/assets/NVDA_chart.html
2025-10-22T15:52:11.705392+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/NVDA_chart.html
2025-10-22T15:52:12.077264+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/NVDA_chart.html "HTTP/2 200 OK"
2025-10-22T15:52:12.077795+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/NVDA_chart.png
2025-10-22T15:52:12.113795+00:00 app[worker.1]: INFO:chart_generator:Gráfico de distribución guardado en: /app/charts/allocation_chart.html
2025-10-22T15:52:12.113923+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/allocation_chart.html
2025-10-22T15:52:12.768711+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/allocation_chart.html "HTTP/2 200 OK"
2025-10-22T15:52:12.769398+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/allocation_chart.png
2025-10-22T15:52:12.769439+00:00 app[worker.1]: INFO:portfolio_manager:Gráficos generados exitosamente
2025-10-22T15:52:12.774954+00:00 app[worker.1]: INFO:supabase_storage:Subiendo JSON del portafolio a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json
2025-10-22T15:52:13.044948+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json "HTTP/2 200 OK"
2025-10-22T15:52:13.045443+00:00 app[worker.1]: INFO:portfolio_manager:Datos guardados en Supabase
2025-10-22T15:52:13.045513+00:00 app[worker.1]: INFO:portfolio_manager:Reporte completo generado exitosamente
2025-10-22T15:52:13.045615+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - ✓ Usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 procesado exitosamente: 1 portfolio(s), 4 asset(s)
2025-10-22T15:52:13.045626+00:00 app[worker.1]: INFO:portfolio_processor:✓ Usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 procesado exitosamente: 1 portfolio(s), 4 asset(s)
2025-10-22T15:52:13.045673+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO -
2025-10-22T15:52:13.045674+00:00 app[worker.1]: ======================================================================
2025-10-22T15:52:13.045682+00:00 app[worker.1]: INFO:portfolio_processor:
2025-10-22T15:52:13.045683+00:00 app[worker.1]: ======================================================================
2025-10-22T15:52:13.045705+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - RESUMEN DE EJECUCIÓN
2025-10-22T15:52:13.045713+00:00 app[worker.1]: INFO:portfolio_processor:RESUMEN DE EJECUCIÓN
2025-10-22T15:52:13.045733+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - ======================================================================
2025-10-22T15:52:13.045741+00:00 app[worker.1]: INFO:portfolio_processor:======================================================================
2025-10-22T15:52:13.045761+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - Total usuarios: 1
2025-10-22T15:52:13.045769+00:00 app[worker.1]: INFO:portfolio_processor:Total usuarios: 1
2025-10-22T15:52:13.045789+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - Exitosos:       1
2025-10-22T15:52:13.045797+00:00 app[worker.1]: INFO:portfolio_processor:Exitosos:       1
2025-10-22T15:52:13.045817+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - Errores:        0
2025-10-22T15:52:13.045825+00:00 app[worker.1]: INFO:portfolio_processor:Errores:        0
2025-10-22T15:52:13.045843+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - Omitidos:       0
2025-10-22T15:52:13.045844+00:00 app[worker.1]: INFO:portfolio_processor:Omitidos:       0
2025-10-22T15:52:13.045870+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - Duración:       34.66 segundos  
2025-10-22T15:52:13.045878+00:00 app[worker.1]: INFO:portfolio_processor:Duración:       34.66 segundos
2025-10-22T15:52:13.045896+00:00 app[worker.1]: 2025-10-22 15:52:13 - portfolio_processor - INFO - ======================================================================
2025-10-22T15:52:13.045904+00:00 app[worker.1]: INFO:portfolio_processor:======================================================================
2025-10-22T15:52:13.045912+00:00 app[worker.1]:
2025-10-22T15:52:13.045913+00:00 app[worker.1]: ================================================================================   
2025-10-22T15:52:13.045914+00:00 app[worker.1]: RESUMEN DE GENERACIÓN
2025-10-22T15:52:13.045922+00:00 app[worker.1]: ================================================================================   
2025-10-22T15:52:13.045922+00:00 app[worker.1]:
2025-10-22T15:52:13.045923+00:00 app[worker.1]: Total usuarios:  1
2025-10-22T15:52:13.045930+00:00 app[worker.1]: Exitosos:        1
2025-10-22T15:52:13.045931+00:00 app[worker.1]: Errores:         0
2025-10-22T15:52:13.045941+00:00 app[worker.1]: Omitidos:        0
2025-10-22T15:52:13.045941+00:00 app[worker.1]:
2025-10-22T15:52:13.045941+00:00 app[worker.1]: Detalles:
2025-10-22T15:52:13.045951+00:00 app[worker.1]: ✓ Usuario 048adfcc... : 1 portfolio(s), 4 asset(s)
2025-10-22T15:52:13.045968+00:00 app[worker.1]:
2025-10-22T15:52:13.045968+00:00 app[worker.1]: Reporte generado a las 15:52:13