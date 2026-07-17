# iPhone TLS traffic capture on alticcio-server

Use only for a user-authorised, short-lived inspection of a specific app/API. Bind to the LAN IP, open the firewall only on `br0`, persist only a domain-filtered flow file, and use `UMask = "0077"` / `StateDirectory`.

## NixOS service pattern

```nix
networking.firewall.interfaces.br0.allowedTCPPorts = [ 53 80 8384 8081 ];
environment.systemPackages = [ pkgs.mitmproxy ];

systemd.services.app-capture-proxy = {
  wantedBy = [ "multi-user.target" ];
  serviceConfig = {
    ExecStart = "${pkgs.mitmproxy}/bin/mitmdump --listen-host <LAN_IP> --listen-port <PORT> --set block_global=false --set save_stream_file=/var/lib/app-capture/app.flows --set save_stream_filter=\"~d <target-domain>\"";
    Restart = "on-failure";
    StateDirectory = "app-capture";
    UMask = "0077";
  };
};
```

Do not add a second top-level assignment for `networking.firewall.interfaces.br0.allowedTCPPorts`; merge the port into the existing `interfaces.br0` block. Rebuild with `sudo nixos-rebuild switch --flake /etc/nixos#alticcio-server`.

## iPhone procedure

1. Set the current Wi-Fi connection to a manual proxy at `<LAN_IP>:<PORT>`.
2. Visit `http://mitm.it`; install the Apple profile.
3. Install the profile under **Settings → General → VPN & Device Management**, then trust its root certificate under **Settings → General → About → Certificate Trust Settings**.
4. Exercise only the target app screen.
5. Disable the iPhone proxy immediately. Disable the server capture service after extracting the needed flow.

If TLS pinning prevents the connection, do not weaken iPhone security further; pivot to static/client protocol analysis.

## Safe extraction

The captured flow file is root-private. Use a root-run mitmdump addon to extract only the necessary header names/values directly into the local secrets store; never print tokens to chat or make the flow file broadly readable. For an API reproduction, capture headers such as client type/version, facility/tenant group, app auth token, and user agent, then test the equivalent server request with a credential stored locally.
