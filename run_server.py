from wraith.server import start_http_server


if __name__ == "__main__":
    start_http_server(
        host="127.0.0.1",
        port=8080,
        telemetry_dir="wraith_logs"
    )
