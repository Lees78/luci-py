# Copyright 2014 The LUCI Authors. All rights reserved.
# Use of this source code is governed by the Apache v2.0 license that can be
# found in the LICENSE file.

"""Integration with Cloud Endpoints.

This module is used only when 'endpoints' is importable (see auth/__init__.py).
"""

import functools
import logging

import endpoints

from protorpc import message_types
from protorpc import util

from . import api
from . import config
from . import delegation
from . import ipaddr
from . import model

from components import utils

# Part of public API of 'auth' component, exposed by this module.
__all__ = [
  'endpoints_api',
  'endpoints_method',
]


# TODO(vadimsh): id_token auth (used when talking to Cloud Endpoints from
# Android for example) is not supported yet, since this module talks to
# OAuth API directly to validate client_ids to simplify usage of Cloud Endpoints
# APIs by service accounts. Otherwise, each service account (or rather it's
# client_id) has to be hardcoded into the application source code.


# Cloud Endpoints auth library likes to spam logging.debug(...) messages: four
# messages per _every_ authenticated request. Monkey patch it.
from endpoints import users_id_token
users_id_token.logging = logging.getLogger('endpoints.users_id_token')
users_id_token.logging.setLevel(logging.INFO)


# Reduce the verbosity of messages dumped by _ah/spi/BackendService.logMessages.
# Otherwise ereporter2 catches them one by one, generating email for each
# individual error. See endpoints.api_backend_service.BackendServiceImpl.
def monkey_patch_endpoints_logger():
  logger = logging.getLogger('endpoints.api_backend_service')
  original = logger.handle
  def patched_handle(record):
    if record.levelno >= logging.ERROR:
      record.levelno = logging.WARNING
      record.levelname = logging.getLevelName(record.levelno)
    return original(record)
  logger.handle = patched_handle
monkey_patch_endpoints_logger()


@util.positional(2)
def endpoints_api(
    name, version,
    auth_level=endpoints.AUTH_LEVEL.OPTIONAL,
    allowed_client_ids=None,
    **kwargs):
  """Same as @endpoints.api but tweaks default auth related properties.

  By default API marked with this decorator will use same authentication scheme
  as non-endpoints request handlers (i.e. fetch a whitelist of OAuth client_id's
  from the datastore, recognize service accounts, etc.), disabling client_id
  checks performed by Cloud Endpoints frontend (and doing them on the backend,
  see 'initialize_auth' below).

  Using service accounts with vanilla Cloud Endpoints auth is somewhat painful:
  every service account should be whitelisted in the 'allowed_client_ids' list
  in the source code of the application (when calling @endpoints.api). By moving
  client_id checks to the backend we can support saner logic.
  """
  # 'audiences' is used with id_token auth, it's not supported yet.
  assert 'audiences' not in kwargs, 'Not supported'

  # We love authentication.
  if auth_level == endpoints.AUTH_LEVEL.NONE:
    raise ValueError('Authentication is required')

  # We love API Explorer.
  if allowed_client_ids is None:
    allowed_client_ids = endpoints.SKIP_CLIENT_ID_CHECK
  if allowed_client_ids != endpoints.SKIP_CLIENT_ID_CHECK:
    allowed_client_ids = sorted(
        set(allowed_client_ids) | set([endpoints.API_EXPLORER_CLIENT_ID]))

  # Someone was looking for job security here:
  # - api() returns _ApiDecorator class instance.
  # - One of the following is done:
  #   - _ApiDecorator.__call__() is called with the remote.Service class as
  #     argument.
  #   - api_class() is explicitly called which returns a function, which is then
  #     called with the  remote.Service class as argument.
  api_decorator = endpoints.api(
      name, version,
      auth_level=auth_level,
      allowed_client_ids=allowed_client_ids,
      **kwargs)

  def fn(cls):
    if not cls.all_remote_methods():
      raise TypeError(
          'Service %s must have at least one auth.endpoints_method method' %
          name)
    for method, func in cls.all_remote_methods().iteritems():
      if func and not api.is_decorated(func.remote._RemoteMethodInfo__method):
        raise TypeError(
            'Method \'%s\' of \'%s\' is not protected by @require or @public '
            'decorator' % (method, name))
    return cls

  # Monkey patch api_decorator to make 'api_class' to return wrapped decorator.
  orig = api_decorator.api_class
  def patched_api_class(*args, **kwargs):
    wrapper = orig(*args, **kwargs)
    return lambda cls: fn(wrapper(cls))
  api_decorator.api_class = patched_api_class

  return api_decorator


def endpoints_method(
    request_message=message_types.VoidMessage,
    response_message=message_types.VoidMessage,
    **kwargs):
  """Same as @endpoints.method but also adds auth state initialization code.

  Also forbids changing auth parameters on per-method basis, since it
  unnecessary complicates authentication code. All methods inherit properties
  set on the service level.
  """
  assert 'audiences' not in kwargs, 'Not supported'
  assert 'allowed_client_ids' not in kwargs, 'Not supported'

  # @endpoints.method wraps a method with a call that sets up state for
  # endpoints.get_current_user(). It does a bunch of checks and eventually calls
  # oauth.get_client_id(). oauth.get_client_id() times out a lot and we want to
  # retry RPC on deadline exceptions a bunch of times. To do so we rely on the
  # fact that oauth.get_client_id() (and other functions in oauth module)
  # essentially caches a result of RPC call to OAuth service in os.environ. So
  # we call it ourselves (with retries) to cache the state in os.environ before
  # giving up control to @endpoints.method. That's what @initialize_oauth
  # decorator does.

  def new_decorator(func):
    @initialize_oauth
    @endpoints.method(request_message, response_message, **kwargs)
    @functools.wraps(func)
    def wrapper(service, *args, **kwargs):
      try:
        initialize_request_auth(
            service.request_state.remote_address, service.request_state.headers)
        return func(service, *args, **kwargs)
      except api.AuthenticationError as ex:
        logging.warning(
            'Authentication error.\n%s\nPeer: %s\nIP: %s',
            ex.message, api.get_peer_identity().to_bytes(),
            service.request_state.remote_address)
        raise endpoints.UnauthorizedException()
      except api.AuthorizationError as ex:
        logging.warning(
            'Authorization error.\n%s\nPeer: %s\nIP: %s',
            ex.message, api.get_peer_identity().to_bytes(),
            service.request_state.remote_address)
        raise endpoints.ForbiddenException()
    return wrapper
  return new_decorator


def initialize_oauth(method):
  """Initializes OAuth2 state before calling wrapped @endpoints.method.

  Used to retry deadlines in GetOAuthUser RPCs before diving into Endpoints code
  that doesn't care about retries.

  TODO(vadimsh): This call is unnecessary if id_token is used instead of
  access_token. We do not use id_tokens currently.
  """
  @functools.wraps(method)
  def wrapper(service, *args, **kwargs):
    if service.request_state.headers.get('Authorization'):
      # See _maybe_set_current_user_vars in endpoints/users_id_token.py.
      scopes = (
          method.method_info.scopes
          if method.method_info.scopes is not None
          else service.api_info.scopes)
      # GAE OAuth module uses internal cache for OAuth RCP responses. The cache
      # key, unfortunately, is basically str(scopes), and a single scope passed
      # as a string (Endpoints lib does that) and a list with one scope only
      # have different cache keys (even though RCPs are identical). So do what
      # Endpoints lib does to warm the cache for it.
      scopes = scopes[0] if len(scopes) == 1 else scopes
      api.attempt_oauth_initialization(scopes)
    return method(service, *args, **kwargs)
  return wrapper


def initialize_request_auth(remote_address, headers):
  """Grabs caller identity and initializes request local authentication context.

  Called before executing a cloud endpoints method. May raise AuthorizationError
  or AuthenticationError exceptions.
  """
  config.ensure_configured()
  auth_context = api.reinitialize_request_cache()

  # Endpoints library always does authentication before invoking a method. Just
  # grab the result of that authentication: it's doesn't make any RPCs.
  current_user = endpoints.get_current_user()

  # Cloud Endpoints auth on local dev server works much better compared to OAuth
  # library since endpoints is using real authentication backend, while oauth.*
  # API is mocked. It makes API Explorer work with local apps. Always use Cloud
  # Endpoints auth on the dev server. It has a side effect: client_id whitelist
  # is ignored, there's no way to get client_id on dev server via endpoints API.
  identity = None
  if utils.is_local_dev_server():
    if current_user:
      identity = model.Identity(model.IDENTITY_USER, current_user.email())
    else:
      identity = model.Anonymous
  else:
    # Use OAuth API directly to grab both client_id and email and validate them.
    # endpoints.get_current_user() itself is implemented in terms of OAuth API,
    # with some additional code to handle id_token that we currently skip (see
    # TODO at the top of this file). OAuth API calls below will just reuse
    # cached values without making any additional RPCs.
    if headers.get('Authorization'):
      # Raises error for forbidden client_id, never returns None or Anonymous.
      identity = api.extract_oauth_caller_identity(
          extra_client_ids=[endpoints.API_EXPLORER_CLIENT_ID])
      # Double check that we used same cached values as endpoints did.
      assert identity and not identity.is_anonymous, identity
      assert current_user is not None
      assert identity.name == current_user.email(), (
          identity.name, current_user.email())
    else:
      # 'Authorization' header is missing. Endpoints still could have found
      # id_token in GET request parameters. Ignore it for now, the code is
      # complicated without it already.
      if current_user is not None:
        raise api.AuthenticationError('Unsupported authentication method')
      identity = model.Anonymous

  # Verify IP is whitelisted and authenticate requests from bots. It raises
  # AuthorizationError if IP is not allowed.
  assert identity is not None
  assert remote_address
  ip = ipaddr.ip_from_string(remote_address)
  auth_context.peer_ip = ip

  # verify_ip_whitelisted may change identity for bots, store new one.
  identity = api.verify_ip_whitelisted(identity, ip, headers)
  auth_context.peer_identity = identity

  # Parse delegation token, if given, to deduce end-user identity.
  delegation_tok = headers.get(delegation.HTTP_HEADER)
  if delegation_tok:
    try:
      auth_context.current_identity = delegation.check_delegation_token(
          delegation_tok, auth_context.peer_identity)
    except delegation.BadTokenError as exc:
      raise api.AuthorizationError('Bad delegation token: %s' % exc)
    except delegation.TransientError as exc:
      msg = 'Transient error while validating delegation token.\n%s' % exc
      logging.error(msg)
      raise endpoints.InternalServerErrorException(msg)
  else:
    auth_context.current_identity = auth_context.peer_identity
