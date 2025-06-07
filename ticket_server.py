import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from datetime import datetime

TICKETS_FILE = 'tickets.json'

CANNED_RESPONSES = {
    'bug report': 'Thank you for reporting this bug. Our team will investigate.',
    'feature request': 'Thank you for your feature suggestion! We\'ll consider it.',
    'support': 'Thank you for reaching out. We\'ll get back to you soon.',
}


def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, 'r') as f:
            return json.load(f)
    return []


def save_tickets(tickets):
    with open(TICKETS_FILE, 'w') as f:
        json.dump(tickets, f, indent=2)


def classify_issue(description):
    lower = description.lower()
    if 'error' in lower or 'bug' in lower:
        return 'bug report'
    if 'feature' in lower or 'enhancement' in lower:
        return 'feature request'
    return 'support'


class TicketHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('/', '/index.html'):
            try:
                with open('index.html', 'rb') as f:
                    content = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self._send_json({'error': 'UI not found'}, status=404)
        elif parsed.path == '/tickets':
            tickets = load_tickets()
            self._send_json(tickets)
        elif parsed.path.startswith('/tickets/'):
            ticket_id = parsed.path[len('/tickets/') :]
            tickets = load_tickets()
            for t in tickets:
                if str(t['id']) == ticket_id:
                    self._send_json(t)
                    return
            self._send_json({'error': 'Not found'}, status=404)
        else:
            self._send_json({'error': 'Invalid endpoint'}, status=404)

    def do_POST(self):
        if self.path != '/tickets':
            self._send_json({'error': 'Invalid endpoint'}, status=404)
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body)
            description = data.get('description', '')
            user = data.get('user', 'anonymous')
        except json.JSONDecodeError:
            self._send_json({'error': 'Invalid JSON'}, status=400)
            return
        issue_type = classify_issue(description)
        response_text = CANNED_RESPONSES[issue_type]
        tickets = load_tickets()
        ticket_id = len(tickets) + 1
        ticket = {
            'id': ticket_id,
            'user': user,
            'description': description,
            'issue_type': issue_type,
            'response': response_text,
            'status': 'open',
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        tickets.append(ticket)
        save_tickets(tickets)
        self._send_json(ticket, status=201)


def run(server_class=HTTPServer, handler_class=TicketHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}')
    httpd.serve_forever()


if __name__ == '__main__':
    run()
