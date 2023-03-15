FROM ubuntu:20.04
# Changed
COPY . /app/code

RUN chgrp -R 0 /app/code && chmod g=u /app/code
RUN chmod -R a+x /app/code

WORKDIR /app/code

USER 1234

CMD ./entry.sh
