PS C:\Users\mikia\mi-proyecto> heroku logs --tail --app portofolio-manager-horizon
2025-10-22T14:35:24.925299+00:00 app[worker.1]: INFO:portfolio_processor:Total de usuarios a procesar: 1
2025-10-22T14:35:24.925299+00:00 app[worker.1]: 
2025-10-22T14:35:24.925326+00:00 app[worker.1]: 2025-10-22 14:35:24 - portfolio_processor - INFO -
2025-10-22T14:35:24.925327+00:00 app[worker.1]: [1/1] Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985...
2025-10-22T14:35:24.925329+00:00 app[worker.1]: INFO:portfolio_processor:
2025-10-22T14:35:24.925329+00:00 app[worker.1]: [1/1] Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985...
2025-10-22T14:35:24.925353+00:00 app[worker.1]: 2025-10-22 14:35:24 - portfolio_processor - INFO - === Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 ===
2025-10-22T14:35:24.925354+00:00 app[worker.1]: INFO:portfolio_processor:=== Procesando usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 ===
2025-10-22T14:35:24.967369+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/rest/v1/users?select=%2A&user_id=eq.048adfcc-fe6e-4608-9b74-fc5608eed985 "HTTP/2 200 OK"
2025-10-22T14:35:25.014744+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/rest/v1/portfolios?select=%2A&user_id=eq.048adfcc-fe6e-4608-9b74-fc5608eed985 "HTTP/2 200 OK"
2025-10-22T14:35:25.015295+00:00 app[worker.1]: INFO:supabase_client:Usuario 048adfcc-fe6e-4608-9b74-fc5608eed985: 1 portfolio(s) encontrado(s).  
2025-10-22T14:35:25.072919+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/rest/v1/assets?select=%2A&portfolio_id=eq.5 "HTTP/2 200 OK"
2025-10-22T14:35:25.073519+00:00 app[worker.1]: INFO:supabase_client:Portfolio 5: 4 asset(s) encontrado(s).
2025-10-22T14:35:25.073545+00:00 app[worker.1]: INFO:supabase_client:Datos completos obtenidos para usuario 048adfcc-fe6e-4608-9b74-fc5608eed985: 1 portfolio(s).
2025-10-22T14:35:25.073589+00:00 app[worker.1]: 2025-10-22 14:35:25 - portfolio_processor - INFO - Usuario: Miguel Angel Murillo Frias (murillofrias.miguel@gmail.com)
2025-10-22T14:35:25.073591+00:00 app[worker.1]: INFO:portfolio_processor:Usuario: Miguel Angel Murillo Frias (murillofrias.miguel@gmail.com)      
2025-10-22T14:35:25.073619+00:00 app[worker.1]: 2025-10-22 14:35:25 - portfolio_processor - INFO -   Portfolio: mki (4 assets)
2025-10-22T14:35:25.073619+00:00 app[worker.1]: INFO:portfolio_processor:  Portfolio: mki (4 assets)
2025-10-22T14:35:25.175220+00:00 app[worker.1]: 2025-10-22 14:35:25 - portfolio_processor - INFO - Ticker validado en yfinance: ^SPX
2025-10-22T14:35:25.175236+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: ^SPX
2025-10-22T14:35:25.317074+00:00 app[worker.1]: 2025-10-22 14:35:25 - portfolio_processor - INFO - Ticker validado en yfinance: BTC-USD
2025-10-22T14:35:25.317115+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: BTC-USD
2025-10-22T14:35:25.481829+00:00 app[worker.1]: 2025-10-22 14:35:25 - portfolio_processor - INFO - Ticker validado en yfinance: PAXG-USD
2025-10-22T14:35:25.481844+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: PAXG-USD
2025-10-22T14:35:25.623532+00:00 app[worker.1]: 2025-10-22 14:35:25 - portfolio_processor - INFO - Ticker validado en yfinance: NVDA
2025-10-22T14:35:25.623538+00:00 app[worker.1]: INFO:portfolio_processor:Ticker validado en yfinance: NVDA
2025-10-22T14:35:25.623575+00:00 app[worker.1]: 2025-10-22 14:35:25 - portfolio_processor - INFO - Generando reporte con 4 assets únicos...       
2025-10-22T14:35:25.623576+00:00 app[worker.1]: INFO:portfolio_processor:Generando reporte con 4 assets únicos...
2025-10-22T14:35:25.623606+00:00 app[worker.1]: INFO:portfolio_manager:Iniciando generación de reporte completo...
2025-10-22T14:35:25.623625+00:00 app[worker.1]: INFO:portfolio_manager:Usando assets dinámicos desde base de datos (4 assets)
2025-10-22T14:35:26.115351+00:00 app[worker.1]: INFO:portfolio_manager:Valor del portafolio: $150.83
2025-10-22T14:35:26.502793+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/bucket/portfolio-files "HTTP/2 200 OK"
2025-10-22T14:35:26.503225+00:00 app[worker.1]: INFO:supabase_storage:Descargando portafolio desde Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json
2025-10-22T14:35:26.835998+00:00 app[worker.1]: INFO:httpx:HTTP Request: GET https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json "HTTP/2 200 OK"
2025-10-22T14:35:52.198519+00:00 app[worker.1]: INFO:portfolio_manager:Generando gráficos...
2025-10-22T14:35:52.237475+00:00 app[worker.1]: INFO:chart_generator:Gráfico HTML guardado en: /app/charts/portfolio_chart.html
2025-10-22T14:35:52.237585+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_chart.html
2025-10-22T14:35:52.925909+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_chart.html "HTTP/2 200 OK"
2025-10-22T14:35:52.926400+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/portfolio_chart.png
2025-10-22T14:35:53.162977+00:00 app[worker.1]: INFO:chart_generator:Gráfico de ^SPX guardado en: /app/charts/assets/^SPX_chart.html
2025-10-22T14:35:53.163229+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/_CARET_SPX_chart.html
2025-10-22T14:35:53.875637+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/_CARET_SPX_chart.html "HTTP/2 200 OK"
2025-10-22T14:35:53.876135+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/^SPX_chart.png
2025-10-22T14:35:54.318831+00:00 app[worker.1]: INFO:chart_generator:Gráfico de BTC-USD guardado en: /app/charts/assets/BTC-USD_chart.html        
2025-10-22T14:35:54.319014+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/BTC-USD_chart.html
2025-10-22T14:35:54.705360+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/BTC-USD_chart.html "HTTP/2 200 OK"
2025-10-22T14:35:54.705818+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/BTC-USD_chart.png
2025-10-22T14:35:55.139227+00:00 app[worker.1]: INFO:chart_generator:Gráfico de PAXG-USD guardado en: /app/charts/assets/PAXG-USD_chart.html      
2025-10-22T14:35:55.139241+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/PAXG-USD_chart.html
2025-10-22T14:35:55.713044+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/PAXG-USD_chart.html "HTTP/2 200 OK"
2025-10-22T14:35:55.713561+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/PAXG-USD_chart.png
2025-10-22T14:35:56.035052+00:00 app[worker.1]: INFO:chart_generator:Gráfico de NVDA guardado en: /app/charts/assets/NVDA_chart.html
2025-10-22T14:35:56.035224+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/NVDA_chart.html
2025-10-22T14:35:56.473969+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/NVDA_chart.html "HTTP/2 200 OK"
2025-10-22T14:35:56.474599+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/assets/NVDA_chart.png
2025-10-22T14:35:56.512667+00:00 app[worker.1]: INFO:chart_generator:Gráfico de distribución guardado en: /app/charts/allocation_chart.html       
2025-10-22T14:35:56.512788+00:00 app[worker.1]: INFO:supabase_storage:Subiendo gráfico a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/allocation_chart.html
2025-10-22T14:35:57.042300+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/allocation_chart.html "HTTP/2 200 OK"
2025-10-22T14:35:57.042766+00:00 app[worker.1]: WARNING:portfolio_manager:Archivo de gráfico no existe, omitiendo subida: /app/charts/allocation_chart.png
2025-10-22T14:35:57.042792+00:00 app[worker.1]: INFO:portfolio_manager:Gráficos generados exitosamente
2025-10-22T14:35:57.046353+00:00 app[worker.1]: INFO:supabase_storage:Subiendo JSON del portafolio a Supabase: portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json
2025-10-22T14:35:57.199144+00:00 app[worker.1]: INFO:httpx:HTTP Request: POST https://tlmdrkthueicqnvbjmie.supabase.co/storage/v1/object/portfolio-files/048adfcc-fe6e-4608-9b74-fc5608eed985/portfolio_data.json "HTTP/2 200 OK"
2025-10-22T14:35:57.199606+00:00 app[worker.1]: INFO:portfolio_manager:Datos guardados en Supabase
2025-10-22T14:35:57.199676+00:00 app[worker.1]: INFO:portfolio_manager:Reporte completo generado exitosamente
2025-10-22T14:35:57.199793+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - ✓ Usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 procesado exitosamente: 1 portfolio(s), 4 asset(s)
2025-10-22T14:35:57.199795+00:00 app[worker.1]: INFO:portfolio_processor:✓ Usuario 048adfcc-fe6e-4608-9b74-fc5608eed985 procesado exitosamente: 1 portfolio(s), 4 asset(s)
2025-10-22T14:35:57.199844+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO -
2025-10-22T14:35:57.199844+00:00 app[worker.1]: ======================================================================
2025-10-22T14:35:57.199847+00:00 app[worker.1]: INFO:portfolio_processor:
2025-10-22T14:35:57.199847+00:00 app[worker.1]: ======================================================================
2025-10-22T14:35:57.199870+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - RESUMEN DE EJECUCIÓN
2025-10-22T14:35:57.199872+00:00 app[worker.1]: INFO:portfolio_processor:RESUMEN DE EJECUCIÓN
2025-10-22T14:35:57.199894+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - ======================================================================
2025-10-22T14:35:57.199896+00:00 app[worker.1]: INFO:portfolio_processor:======================================================================   
2025-10-22T14:35:57.199918+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - Total usuarios: 1
2025-10-22T14:35:57.199919+00:00 app[worker.1]: INFO:portfolio_processor:Total usuarios: 1
2025-10-22T14:35:57.199942+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - Exitosos:       1
2025-10-22T14:35:57.199942+00:00 app[worker.1]: INFO:portfolio_processor:Exitosos:       1
2025-10-22T14:35:57.199964+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - Errores:        0
2025-10-22T14:35:57.199965+00:00 app[worker.1]: INFO:portfolio_processor:Errores:        0
2025-10-22T14:35:57.199986+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - Omitidos:       0
2025-10-22T14:35:57.199986+00:00 app[worker.1]: INFO:portfolio_processor:Omitidos:       0
2025-10-22T14:35:57.200012+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - Duración:       32.68 segundos
2025-10-22T14:35:57.200013+00:00 app[worker.1]: INFO:portfolio_processor:Duración:       32.68 segundos
2025-10-22T14:35:57.200035+00:00 app[worker.1]: 2025-10-22 14:35:57 - portfolio_processor - INFO - ======================================================================
2025-10-22T14:35:57.200035+00:00 app[worker.1]: INFO:portfolio_processor:======================================================================   
2025-10-22T14:35:57.200049+00:00 app[worker.1]:
2025-10-22T14:35:57.200049+00:00 app[worker.1]: ================================================================================
2025-10-22T14:35:57.200050+00:00 app[worker.1]: RESUMEN DE GENERACIÓN
2025-10-22T14:35:57.200051+00:00 app[worker.1]: ================================================================================
2025-10-22T14:35:57.200061+00:00 app[worker.1]:
2025-10-22T14:35:57.200061+00:00 app[worker.1]: Total usuarios:  1
2025-10-22T14:35:57.200061+00:00 app[worker.1]: Exitosos:        1
2025-10-22T14:35:57.200064+00:00 app[worker.1]: Errores:         0
2025-10-22T14:35:57.200066+00:00 app[worker.1]: Omitidos:        0
2025-10-22T14:35:57.200076+00:00 app[worker.1]:
2025-10-22T14:35:57.200077+00:00 app[worker.1]: Detalles:
2025-10-22T14:35:57.200078+00:00 app[worker.1]: ✓ Usuario 048adfcc... : 1 portfolio(s), 4 asset(s)
2025-10-22T14:35:57.200102+00:00 app[worker.1]:
2025-10-22T14:35:57.200102+00:00 app[worker.1]: Reporte generado a las 14:35:57