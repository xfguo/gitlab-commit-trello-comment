#!/usr/bin/python -tt
#
# Copyright (C) 2012 Shawn Sterling <shawn@systemtemplar.org>
# Copyright (C) 2013 Xiongfei(Alex) Guo <xfguo@credosemi.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# gitlab-commit-trello-comment: a script which push gitlab commit to trello card comment.
# modify from gitlab-webhook-receiver: a script for gitlab & puppet integration
#
# The latest version of git will be found on:
# https://github.com/xfguo/gitlab-commit-trello-comment
#
# The latest version of gitlab-webhook-receiver will be found on shawn-sterling's github page:
# https://github.com/shawn-sterling/gitlab-webhook-receiver

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import re
import json
import logging
import logging.handlers

from trolly import client as trolly_client
from trolly import board as trolly_board
from urlparse import urlsplit
from trolly import card

import config

import pprint

log = logging.getLogger('log')
log.setLevel(config.log_level)
log_handler = logging.handlers.RotatingFileHandler(config.log_file,
                                                   maxBytes=config.log_max_size,
                                                   backupCount=4)
f = logging.Formatter("%(asctime)s %(filename)s %(levelname)s %(message)s",
                      "%B %d %H:%M:%S")
log_handler.setFormatter(f)
log.addHandler(log_handler)

class webhookReceiver(BaseHTTPRequestHandler):
    def comment_to_trello(self, card_short_id, comment):
        log.debug("Try comment on card #%d, [\n%s\n]" % (card_short_id, comment))
        trello_key = config.trello_key
        trello_token = config.trello_token
        board_id = config.board_id
        
        client = trolly_client.Client(trello_key, user_auth_token = trello_token)
        board = trolly_board.Board(client, board_id)
        card = board.getCard(str(card_short_id))
        card.addComments(comment)

    def do_POST(self):
        """
            receives post, handles it
        """
        log.debug('got post')
        self.rfile._sock.settimeout(5)
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        message = 'OK'
        self.send_response(200)
        self.send_header("Content-type", "text")
        self.send_header("Content-length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)
        log.debug('gitlab connection should be closed now.')

        #parse data
        post = json.loads(data_string)
        repo = post['repository']['name']
        #got namespace
        namespace = urlsplit(post['repository']['homepage'])[2]
        namespace = ''.join(('/', namespace)) if namespace else namespace
        repo_url = ''.join((config.gitlab_url, namespace, '/', repo))
        branch = re.split('/', post['ref'])[-1]
        branch_url = repo_url + '/commits/%s' % branch
        log.debug(pprint.pformat(post))
        
        for commit in post['commits']:
            card_short_id_list = map(int, re.findall('#([1-9]+)', commit['message']))
            git_hash = commit['id'][:7]
            git_hash_url = repo_url + '/commit/%s' % git_hash
            author = commit['author']['name']
            comment = commit['message']
            trello_comment = '''\[**%s** has a new commit about this card\]
\[repo: [%s](%s) | branch: [%s](%s) | hash: [%s](%s)\]
----
%s''' % (author, repo, repo_url, branch, branch_url, git_hash, git_hash_url, comment)
            for card_short_id in card_short_id_list:
                self.comment_to_trello(card_short_id, trello_comment)

def main():
    """
        the main event.
    """
    try:
        server = HTTPServer(('', 9000), webhookReceiver)
        log.info('started web server...')
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('ctrl-c pressed, shutting down.')
        server.socket.close()

if __name__ == '__main__':
    main()
