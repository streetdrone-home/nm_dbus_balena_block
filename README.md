# nm_dbus_balena_block
Configure networks with NetworkManager through D-BUS.

The network connections to be configured can be specified in two ways, in order of precedence:

1. **Environment Variable**

    Set the `NM_DBUS_CONFIG` variable.
    Its value should be a YAML list of dictionaries, with each dictionary providing the configuration for a connection.
    Each dictionary can have these fiels:
    
    - `name`: name if the connection, e.g. 'Wired Connection', 'Sensor 1', etc. *Required*
    - `iface`: the network interface device to activate the connection on, e.g. 'enp4s0f2'. *Required*
    - `method`: IPv4 configuration method. One of `auto`, `link-local`, `manual`, `shared` or `disabled`. *Required*
    - `ipv4`: IP address to assign to connection. *Optional; required when `method` is `manual`*
    
    The configuration would most typically be provided in YAML's 'flow' format, such as:
    
    ```yaml
    [{name: TestConn, iface: enxa0cec8ed8e19, method: manual, ipv4: 192.168.0.1}, {name: "Wired Conn", iface: 'enp4s0f2, method: auto}]
    ```
    
1. **YAML configuration file**

    Extend this image or use volumes to place a file at `/nm-dbus.yaml`.
    Its contents should be the same as described above, but would more typically use YAML's indented block style.
