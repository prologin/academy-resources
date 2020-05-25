#!/usr/bin/env python3

# pip install requests
import requests

PROMPT = '>>> '


class Voter:
    def __init__(self, endpoint):
        """
        Constructeur
        endpoint: URL string
        data: dictionnaire contenant les projets, avec leur index, leur
              description, et le nombre de votes actuels
        """
        self.endpoint = endpoint
        self.data = {}


    def fetch(self):
        """
        Recupere les donnees contenues sur le serveur, sous la forme d'un json.
        """
        req = requests.get(url=self.endpoint)
        self.data = req.json()['projects']


    def display(self):
        """
        Affiche les informations de chaque projet
        """
        for item in self.data:
            print(f'{item["index"]}. {item["project_name"]}:', end='')
            print(f'{item["description"]} ({item["votes"]})')


    def vote(self, index):
        """
        Envoie le vote au serveur sous la forme d'un dictionnaire
        """
        dic = {}
        dic['vote'] = index
        response = requests.post(url=self.endpoint, json=dic)
        print(f'Response: {response.text}')


#
#   M A I N
#

if __name__ == '__main__':
    allowed_cmds = ['fetch', 'display', 'vote', 'quit', 'help']
    url = input('Requested endpoint? ')
    voter = Voter(url)
    while True:
        cmd = input(PROMPT)
        if cmd not in allowed_cmds:
            print('Invalid command')
        else:
            if cmd == 'fetch':
                voter.fetch()
            elif cmd == 'display':
                voter.display()
            elif cmd == 'vote':
                v = input('Input the project index you want to vote for: ')
                voter.vote(v)
            elif cmd == 'help':
                print('Allowed commands: ', end='')
                for cmd in allowed_cmds:
                    print(f'{cmd}  ', end='')
                print()
            else: # if cmd == 'quit'
                exit(0)
