FROM freeradius/freeradius-server:3.0.19

COPY src/clients.conf /etc/freeradius
COPY src/mods-config/files/authorize /etc/freeradius/mods-config/files/

RUN chgrp freerad /etc/freeradius/mods-config/files/authorize \
    && chgrp freerad /etc/freeradius/clients.conf
