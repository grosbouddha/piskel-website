from base import BaseHandler
from models import Framesheet, Piskel
from google.appengine.ext import db
from handlers import image as image_handler
from types import *
import logging

import random
import os

class StubHandler(BaseHandler):
  fake_user_configs = [
    {
      'user_id': None,
      'auth_id': '111',
      'user_name': 'user_1',
      'public_piskel_count': 4,
      'private_piskel_count': 5,
      'deleted_piskel_count': 3
    },
    {
      'user_id': None,
      'auth_id': '222',
      'user_name': 'user_2',
      'public_piskel_count': 9,
      'private_piskel_count': 2,
      'deleted_piskel_count': 2
    }
  ]

  # Creates a bunch of piskels for the logged-in user.
  # Creates a bunch of fake users with fake piskels
  #
  # To clear this fake data:
  # <project_root>/dev_appserver.py app.yaml --clear_datastore 
  #
  # This entry point only works on localhost.
  def create(self):
    logging.info(dir(self.auth.store.user_model))
    
    if not self._isLocal():
      return

    for user_config in self.fake_user_configs:
      auth_id = user_config['auth_id']
      user = self.auth.store.user_model.get_by_auth_id(auth_id)
      if not user:
        ok, user = self.auth.store.user_model.create_user(auth_id)
        assert ok, "Not able to create fake user with auth_id %s" % auth_id
      
      user_id = self.auth.store.user_to_dict(user)['user_id']
      user_config['user_id'] = user_id

    values = {
      'user_configs': []
    }

    # Create the list of user configs.
    logged_in_user_config = self._get_logged_in_user_config()
    all_user_configs = self.fake_user_configs
    if logged_in_user_config:
        all_user_configs = [logged_in_user_config] + all_user_configs

    # Generate fake piskels fir each user.
    for user_config in all_user_configs:
        self._assert_config(user_config)
        self._create_fake_piskels_for_user(user_config)
        values['user_configs'].append(user_config)

    self.render('stub.html', values)

  def _isLocal(self):
    return os.environ["SERVER_NAME"] in ("localhost")

  def _get_logged_in_user_config(self):
    if not self.session_user or not self.current_user:
      return None

    return {
      'user_id': self.session_user['user_id'],
      'user_name': self.current_user.name,
      'public_piskel_count': 6,
      'private_piskel_count': 3,
      'deleted_piskel_count': 2
    }

  def _create_fake_piskels_for_user(self, user_conf):
    user_id = user_conf['user_id']

    for idx, _ in enumerate(xrange(user_conf['private_piskel_count'])):
      ui_id = str(idx) + '_' + user_conf['user_name']
      self._create_piskel(user_id, ui_id, True, False)

    for idx, _ in enumerate(xrange(user_conf['public_piskel_count'])):
      ui_id = str(idx) + '_' + user_conf['user_name']
      self._create_piskel(user_id, ui_id, False, False)

    for idx, _ in enumerate(xrange(user_conf['deleted_piskel_count'])):
      ui_id = str(idx) + '_' + user_conf['user_name']
      self._create_piskel(user_id, ui_id, False, True)


  def _assert_config(self, config):
    logging.info(config)
    assert type(config['user_id']) is LongType, "invalid user_id: %r" % config['user_id']
    assert type(config['user_name']) is StringType, "invalid user_name: %r" % config['user_name']
    assert type(config['public_piskel_count']) is IntType
    assert type(config['private_piskel_count']) is IntType
    assert type(config['deleted_piskel_count']) is IntType

  def _create_piskel(self, user_id, ui_id, is_private, is_deleted):
    #logging.info('Adding fake piskel')
    piskel = Piskel(owner=user_id)
    piskel.garbage = False
    piskel.deleted = is_deleted
    piskel.name = ui_id + ' name'
    piskel.description = 'desc ' + ui_id
    piskel.private = is_private

    piskel.put()

    piskel_id=str(piskel.key())
    content = '{"modelVersion":2,"piskel":{"name":"zizi","description":"","fps":12,"height":32,"width":32,"layers":["{\"name\":\"Layer 1\",\"opacity\":1,\"frameCount\":1,\"chunks\":[{\"layout\":[[0]],\"base64PNG\":\"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAfklEQVRYR+2W4QqAEQxF5/0fmqZW+krTrty+uv4yzg5GM3Jr5PVNADKAGuhm2DmqAvjC0apzzPhqcGRONeDwFIDQTwH4ZvzMwJr1Wr2fAeyeDDqAg0EQ1Wt4bRsEIAO/N7ArUMdfTdQAVAOQ5/g4w2wgaiCbP+0XgAzIAN3AAHXHFiEe0qtCAAAAAElFTkSuQmCC\"}]}"]}}'
    preview_link_data = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAfklEQVRYR+2W4QqAEQxF5/0fmqZW+krTrty+uv4yzg5GM3Jr5PVNADKAGuhm2DmqAvjC0apzzPhqcGRONeDwFIDQTwH4ZvzMwJr1Wr2fAeyeDDqAg0EQ1Wt4bRsEIAO/N7ArUMdfTdQAVAOQ5/g4w2wgaiCbP+0XgAzIAN3AAHXHFiEe0qtCAAAAAElFTkSuQmCC'
    framesheet_link_data = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAfklEQVRYR+2W4QqAEQxF5/0fmqZW+krTrty+uv4yzg5GM3Jr5PVNADKAGuhm2DmqAvjC0apzzPhqcGRONeDwFIDQTwH4ZvzMwJr1Wr2fAeyeDDqAg0EQ1Wt4bRsEIAO/N7ArUMdfTdQAVAOQ5/g4w2wgaiCbP+0XgAzIAN3AAHXHFiEe0qtCAAAAAElFTkSuQmCC'
    framesheet = Framesheet(
        piskel_id=piskel_id,
        fps=str(10),
        content=content,
        frames=1,
        preview_link=image_handler.create_link(preview_link_data),
        framesheet_link=image_handler.create_link(framesheet_link_data),
        active=False
    )
    piskel.set_current_framesheet(framesheet)
    piskel.put()

