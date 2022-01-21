# OpenTelemetry Log Parser

This Python framework will help you to:
- Read of Standard OpenTelemetry collector Logs (JSON format)
- Process and filter of the elements received (for Boomi but can be adapted to any other Platform)
- Generate Logs with simple format (one line per traceId) easily readable by tools like Promtail/Loki

![Alt text](resources/overview.png?raw=true "otel-log-parser")

## Sample Input

```json lines
{
    "resourceSpans": [
        {
            "instrumentationLibrarySpans": [
                {
                    "instrumentationLibrary": {
                        "name": "io.opentelemetry.servlet-2.2",
                        "version": "1.4.1"
                    },
                    "spans": [
                        {
                            "attributes": [
                                {
                                    "key": "http.user_agent",
                                    "value": {
                                        "stringValue": "synthetic-monitoring-agent/v0.4.1-0-g49cdae8 (linux amd64; 49cdae8ec92d1bd404ffb3183795b5ed83cccd3f; 2021-12-02 14:23:54+00:00; +https://github.com/grafana/synthetic-monitoring-agent)"
                                    }
                                },
                                {
                                    "key": "http.flavor",
                                    "value": {
                                        "stringValue": "1.1"
                                    }
                                },
                                {
                                    "key": "enduser.id",
                                    "value": {
                                        "stringValue": "boomi_anthonyrabiaza-XXXXXX"
                                    }
                                },
                                {
                                    "key": "thread.id",
                                    "value": {
                                        "intValue": "123"
                                    }
                                },
                                {
                                    "key": "net.peer.ip",
                                    "value": {
                                        "stringValue": "127.0.0.1"
                                    }
                                },
                                {
                                    "key": "thread.name",
                                    "value": {
                                        "stringValue": "1649569546@qtp-599887337-2"
                                    }
                                },
                                {
                                    "key": "http.status_code",
                                    "value": {
                                        "intValue": "200"
                                    }
                                },
                                {
                                    "key": "http.method",
                                    "value": {
                                        "stringValue": "POST"
                                    }
                                },
                                {
                                    "key": "http.client_ip",
                                    "value": {
                                        "stringValue": "17X.1XX.1XX.8"
                                    }
                                },
                                {
                                    "key": "http.url",
                                    "value": {
                                        "stringValue": "http://localhost:9999/ws/rest/apm/test/MQ/?instrument=true"
                                    }
                                }
                            ],
                            "endTimeUnixNano": "1642773532825710376",
                            "kind": "SPAN_KIND_SERVER",
                            "name": "/ws/rest",
                            "parentSpanId": "",
                            "spanId": "8da3cb333857dbe2",
                            "startTimeUnixNano": "1642773532616862371",
                            "status": {},
                            "traceId": "cee6c79e0273f8f8fd92b5dd9f1055df"
                        }
                    ]
                },
              {
                "instrumentationLibrary": {
                  "name": "io.opentelemetry.http-url-connection",
                  "version": "1.4.1"
                },
                "spans": [
                ]
              }
            ]
        }
    ]
}
```
## Sample Output

```text
2022-01-21T21:58:55.546512 traceID=cee6c79e0273f8f8fd92b5dd9f1055df span_number=9 operations="/ws/rest,HTTP GET,SELECT centos7_vmware_dev,SELECT centos7_vmware_dev,JMS_centos7_vmware_dev_myqueue send,DatabaseSend.send,JMSSend.send,ExecutionTask.call,DatabaseSend.send"
```

## Getting Started

### Prerequisites

Install the following dependencies:

```shell
pip install jsonpath-ng
pip install tqdm
```

### Configure OpenTelemetry Collector

Please check the elements wrapped between HERE and ABOVE

```yaml
exporters:
  otlp:
    endpoint: abcdefg.antsoftware.org:55680
    insecure: true
  logging:
    loglevel: info
  # HERE
  file:
    path: /opt/opentelemetry/logs/traces.log
  # ABOVE
  prometheusremotewrite:
    endpoint: "https://****@prometheus-us-central1.grafana.net/api/prom/push"
service:
  extensions: [health_check, zpages]
  pipelines:
    traces/1:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [otlp]
    # HERE
    traces/2:
      receivers: [otlp]
      processors: [memory_limiter, batch]
      exporters: [file]
    # ABOVE
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheusremotewrite]
(...)
```

### Execute the Framework

```shell
python3 -u main.py
```

```shell
----------------------------------------------------------------
OpenTelemetry Log Parser
  https://github.com/anthonyrabiaza/opentelemetry-log-parser
  Press Ctrl+C to stop the process
----------------------------------------------------------------
Opening traces.log
Writing to traces.log
2022-01-21 21:14:57.833536: Receiving and processing traces...
 64%|███████████████████████████████████████████████████████████████████████████████████████████████████████████▌                                                            | 64/100 [06:10<04:13,  7.04s/it]
```

### Execute the Framework in background

```shell
./otel-log-parser.sh
```

### Promtail configuration 

```yaml
server:
  http_listen_port: 0
  grpc_listen_port: 0
positions:
  filename: /tmp/positions.yaml
client:
  url: https://****@logs-prod-us-central1.grafana.net/api/prom/push
scrape_configs:
- job_name: otelcol-parsed
  static_configs:
  - targets:
      - localhost
    labels:
      job: otelcol-parsed-logs
      __path__: /opt/opentelemetry/logs/traces_parsed*.log
  pipeline_stages:
  - match:
      selector: '{job="otelcol-parsed"}'
      stages:
      - regex:
          expression: '.*traceID=(?P<traceID>[0-9a-zA-Z]+) spanNumber=(?P<spanNumber>[0-9]+) operations=(?P<operations>.+)'
      - labels:
          traceID:
          spanNumber:
          operations:

```
## Example of View in Grafana Loki and Tempo

![Alt text](resources/otel_loki_tempo.png?raw=true "otel-log-parser")