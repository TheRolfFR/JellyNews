FROM python:3.12-alpine

RUN pip install -e .

ENV SIGNAL_SMTP_PORT=8025
ENV SIGNAL_SMTP_HOST=0.0.0.0
ENV SIGNAL_SMTP_USER=smtp2signal

RUN adduser --disabled-password --no-create-home --gecos "" --h /home -s /bin/bash ${SIGNAL_SMTP_USER} \
            && chown -R ${SIGNAL_SMTP_USER}:${SIGNAL_SMTP_USER} /home && ln -s /usr/local/bin/python3 /usr/bin/python3 \
            && apk --no-cache add su-exec
WORKDIR /home

COPY --from=builder /install /usr/local

VOLUME /home
EXPOSE ${SIGNAL_SMTP_PORT}
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

