#!/usr/bin/env python3

"""Ce module correspond au serveur HTTP avec lequel vous allez interagir.

Il permet de repondre a 2 types de requetes: les GET et les POST.

En reponse a une requete GET, il va envoyer l'etat actuel des votes dans le format de serialization JSON.

Lorsqu'il recoit une requete POST, il va traiter les donnees de celle-ci et repondre un statut en fonction de la
reussite ou l'echec de l'operation."""

import argparse
import http.server
import json

FILENAME = "/data/votes.json"

class VoteServer(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        with open(FILENAME, "r") as fp:
            self.data = json.load(fp)

        super().__init__(*args, **kwargs)

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.data).encode())

    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))

        try:
            data = json.loads(self.rfile.read(content_length))

        except:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(
                "Votre requête n'est pas du JSON valide.".encode()
            )
            return

        if "vote" not in data:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(
                "Le JSON ne contient pas de champ 'vote'.".encode()
            )
            return

        try:
            self.data['projects'][data['vote']]['votes'] += 1
        except:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(
                "Une erreur interne s'est produite.".encode()
            )
            return

        with open(FILENAME, "w") as fp:
            json.dump(self.data, fp)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(
            f"Bonjour {data['name']} votre vote pour {data['vote']} a bien été pris en compte.".encode()
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port", type=int, default=80, help="the port to listen on"
    )
    args = parser.parse_args()
    httpd = http.server.HTTPServer(("", args.port), VoteServer)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()
