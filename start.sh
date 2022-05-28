gunicorn \
--workers=${GUNICORN_WORKERS} \
--threads=${GUNICORN_THREADS} \
--worker-tmp-dir=/dev/shm \
-b 0.0.0.0:8080 \
"server:run_server()"
