FROM balenalib/amd64-python:3.9-run

RUN install_packages libnm0 python3-gi python3-yaml gir1.2-nm-1.0

COPY nm-dbus.py nm-dbus.py

CMD bash -c "python3 nm-dbus.py; sleep infinity"
