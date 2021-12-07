FROM python:3.7.3

WORKDIR usr/src/dash_app
COPY ./dash_app .
RUN pip install --no-cache-dir -r requirements.txt \
    && chmod +x ./entrypoint.sh
ENTRYPOINT ["sh", "entrypoint.sh"]