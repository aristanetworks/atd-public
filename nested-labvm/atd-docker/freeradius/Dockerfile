FROM freeradius/freeradius-server:3.0.19

COPY src/clients.conf /etc/freeradius

RUN chgrp freerad /etc/freeradius/clients.conf
