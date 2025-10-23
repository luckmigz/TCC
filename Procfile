web: uvicorn main:app --host=0.0.0.0 --port=${PORT}
worker: python backend/detection_service/run_worker.py
dashboard: streamlit run backend/detection_service/dashboard.py --server.port $PORT