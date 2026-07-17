# Temporary iPhone HTTPS capture proxy

Use only when the user explicitly authorises inspection of a named app/domain and wants the capture server-hosted.

## Design

- Use `mitmdump`, bind to the server’s **LAN address only**, never `0.0.0.0`.
- Add the proxy TCP port only to the LAN firewall interface, not global/Tailscale rules.
- Persist only a domain-filtered flow file, owned by a dedicated `StateDirectory` with `UMask = "0077"`.
- Make it a temporary service; tell the user to disable the iPhone proxy and remove the CA certificate after capture.
- Do not log credentials, cookies, or unrelated traffic. Inspect the saved flow locally; extract just request method, path, non-secret headers, and response schema.

## NixOS pattern

```nix
environment.systemPackages = [ pkgs.mitmproxy ];

networking.firewall.interfaces.br0.allowedTCPPorts = [ 8081 ];

systemd.services.app-capture-proxy = {
  description = "Temporary domain-limited iPhone capture proxy";
  wantedBy = [ "multi-user.target" ];
  serviceConfig = {
    ExecStart = "${pkgs.mitmproxy}/bin/mitmdump "
      + "--listen-host <LAN-IP> --listen-port <PORT> "
      + "--set block_global=false "
      + "--set save_stream_file=/var/lib/app-capture/app.flows "
      + "--set save_stream_filter=\"~d <app-domain>\"";
    Restart = "on-failure";
    StateDirectory = "app-capture";
    UMask = "0077";
  };
};
```

Apply with `sudo nixos-rebuild switch --flake /etc/nixos#alticcio-server`, then verify `systemctl status app-capture-proxy` and that the port is exposed only on LAN.

## iPhone setup

1. Set the current Wi-Fi connection’s HTTP proxy to Manual: server LAN IP + port.
2. Visit `http://mitm.it` and install the mitmproxy CA profile.
3. Explicitly trust it under **Settings → General → About → Certificate Trust Settings**.
4. Reproduce only the desired app view.
5. Disable the Wi-Fi proxy and remove the CA profile/trust immediately afterwards.

If the app certificate-pins and fails under interception, stop. Do not weaken system TLS protections or attempt bypasses; continue by inspecting public clients/protocols instead.
