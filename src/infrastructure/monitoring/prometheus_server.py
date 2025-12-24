# -*- coding: utf-8 -*-

"""
PROMETHEUS SERVER - HTTP Server for Metrics Exposition
Servidor HTTP para exposição de métricas Prometheus
"""

import asyncio
import threading
import time
from typing import Optional, Dict, Any
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import urllib.parse

from .metrics_collector import metrics_collector
from ...shared.utils.logger import get_logger


class MetricsHandler(BaseHTTPRequestHandler):
    """Handler HTTP para métricas Prometheus"""

    def do_GET(self):
        """Processa requisições GET"""
        try:
            parsed_path = urllib.parse.urlparse(self.path)

            if parsed_path.path == '/metrics':
                self._handle_metrics()
            elif parsed_path.path == '/health':
                self._handle_health()
            elif parsed_path.path == '/':
                self._handle_root()
            else:
                self._handle_not_found()

        except Exception as e:
            logger.error(f"Erro no handler HTTP: {e}")
            self._send_error(500, f"Internal Server Error: {e}")

    def _handle_metrics(self):
        """Retorna métricas no formato Prometheus"""
        try:
            metrics_text = metrics_collector.get_metrics_text()
            self._send_response(200, metrics_text, 'text/plain; version=0.0.4; charset=utf-8')

        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            self._send_error(500, f"Error getting metrics: {e}")

    def _handle_health(self):
        """Endpoint de health check"""
        try:
            health = metrics_collector.health_check()
            status_code = 200 if health['status'] == 'healthy' else 503

            import json
            response = json.dumps(health, indent=2, ensure_ascii=False)
            self._send_response(status_code, response, 'application/json')

        except Exception as e:
            logger.error(f"Erro no health check: {e}")
            self._send_error(500, f"Health check failed: {e}")

    def _handle_root(self):
        """Página inicial com informações"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Automator Web IA - Metrics Server</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .endpoint {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-left: 4px solid #007acc; }}
                .status {{ color: green; }}
            </style>
        </head>
        <body>
            <h1>🚀 Automator Web IA v8.0 - Metrics Server</h1>
            <p class="status">✅ Server running on port {self.server.server_address[1]}</p>

            <h2>📊 Available Endpoints</h2>

            <div class="endpoint">
                <strong>GET /metrics</strong><br>
                Prometheus metrics exposition endpoint<br>
                <em>Content-Type: text/plain</em>
            </div>

            <div class="endpoint">
                <strong>GET /health</strong><br>
                Health check endpoint<br>
                <em>Content-Type: application/json</em>
            </div>

            <div class="endpoint">
                <strong>GET /</strong><br>
                This information page<br>
                <em>Content-Type: text/html</em>
            </div>

            <h2>📈 Metrics Information</h2>
            <ul>
                <li><strong>System Metrics:</strong> CPU, Memory, Disk, Network</li>
                <li><strong>Application Metrics:</strong> Tasks, Workflows, API calls</li>
                <li><strong>Security Metrics:</strong> Auth attempts, Security incidents</li>
                <li><strong>Performance Metrics:</strong> Response times, Error rates</li>
            </ul>

            <h2>🔗 Integration</h2>
            <p>Add the following to your <code>prometheus.yml</code>:</p>
            <pre>
  - job_name: 'automator-webia'
    static_configs:
      - targets: ['localhost:{self.server.server_address[1]}']
    scrape_interval: 15s
            </pre>
        </body>
        </html>
        """

        self._send_response(200, html, 'text/html')

    def _handle_not_found(self):
        """Página não encontrada"""
        self._send_error(404, "Endpoint not found")

    def _send_response(self, status_code: int, content: str, content_type: str):
        """Envia resposta HTTP"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(content.encode('utf-8'))))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def _send_error(self, status_code: int, message: str):
        """Envia erro HTTP"""
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error {status_code}</title></head>
        <body>
            <h1>Error {status_code}</h1>
            <p>{message}</p>
        </body>
        </html>
        """

        self._send_response(status_code, error_html, 'text/html')

    def log_message(self, format, *args):
        """Override para usar nosso logger"""
        logger.info(f"HTTP {format % args}")


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """Servidor HTTP com threading"""
    daemon_threads = True


class PrometheusMetricsServer:
    """Servidor de métricas Prometheus"""

    def __init__(self, host: str = '0.0.0.0', port: int = 8001):
        self.host = host
        self.port = port
        self.server = None
        self.thread = None
        self.running = False

        global logger
        logger = get_logger(__name__)

        logger.info(f"PrometheusMetricsServer inicializado - {host}:{port}")

    def start(self):
        """Inicia o servidor em background"""
        if self.running:
            logger.warning("Servidor já está rodando")
            return

        def run_server():
            try:
                self.server = ThreadingHTTPServer((self.host, self.port), MetricsHandler)
                logger.info(f"🚀 Servidor de métricas iniciado em http://{self.host}:{self.port}")

                self.running = True
                self.server.serve_forever()

            except Exception as e:
                logger.error(f"Erro ao iniciar servidor de métricas: {e}")
                self.running = False

        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()

        # Aguarda o servidor iniciar
        time.sleep(0.1)

    def stop(self):
        """Para o servidor"""
        if not self.running:
            return

        logger.info("Parando servidor de métricas...")
        if self.server:
            self.server.shutdown()
            self.server.server_close()

        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5.0)

        logger.info("✅ Servidor de métricas parado")

    def is_running(self) -> bool:
        """Verifica se o servidor está rodando"""
        return self.running

    def get_status(self) -> Dict[str, Any]:
        """Retorna status do servidor"""
        return {
            'running': self.running,
            'host': self.host,
            'port': self.port,
            'metrics_collector_status': metrics_collector.health_check()
        }

    def restart(self):
        """Reinicia o servidor"""
        self.stop()
        time.sleep(1.0)
        self.start()


# Instância global do servidor
metrics_server = PrometheusMetricsServer()


# ===== MÉTODOS DE CONTROLE =====

def start_metrics_server(host: str = '0.0.0.0', port: int = 8001):
    """Inicia servidor de métricas"""
    global metrics_server
    if metrics_server.is_running():
        logger.warning("Servidor de métricas já está rodando")
        return

    metrics_server = PrometheusMetricsServer(host, port)
    metrics_server.start()


def stop_metrics_server():
    """Para servidor de métricas"""
    global metrics_server
    metrics_server.stop()


def get_metrics_server_status() -> Dict[str, Any]:
    """Retorna status do servidor de métricas"""
    global metrics_server
    return metrics_server.get_status()


# ===== FUNÇÕES UTILITÁRIAS =====

def collect_and_expose_metrics():
    """Coleta métricas e mantém servidor rodando"""
    try:
        while True:
            # Coleta métricas a cada 15 segundos
            metrics_collector.collect_all_metrics()
            time.sleep(15)

    except KeyboardInterrupt:
        logger.info("Coleta de métricas interrompida")
    except Exception as e:
        logger.error(f"Erro na coleta de métricas: {e}")


def start_background_collection():
    """Inicia coleta de métricas em background"""
    thread = threading.Thread(target=collect_and_expose_metrics, daemon=True)
    thread.start()
    logger.info("Coleta de métricas em background iniciada")


# Inicialização automática se executado diretamente
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Prometheus Metrics Server for Automator Web IA')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind server')
    parser.add_argument('--port', type=int, default=8001, help='Port to bind server')
    parser.add_argument('--collect-interval', type=int, default=15, help='Metrics collection interval in seconds')

    args = parser.parse_args()

    # Inicia coleta em background
    start_background_collection()

    # Inicia servidor
    start_metrics_server(args.host, args.port)

    try:
        # Mantém rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário")
        stop_metrics_server()
