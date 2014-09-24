#!/usr/bin/env python
# Copyright 2014 The Swarming Authors. All rights reserved.
# Use of this source code is governed by the Apache v2.0 license that can be
# found in the LICENSE file.

import datetime
import inspect
import logging
import os
import random
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

import test_env

test_env.setup_test_env()

from google.appengine.api import search
from google.appengine.ext import deferred
from google.appengine.ext import ndb

# From tools/third_party/
import webtest

from components import stats_framework
from server import bot_management
from server import stats
from server import task_common
from server import task_request
from server import task_result
from server import task_scheduler
from server import task_to_run
from support import test_case

from server.task_result import State

# pylint: disable=W0212,W0612


def _gen_request_data(name='Request name', properties=None, **kwargs):
  base_data = {
    'name': name,
    'user': 'Jesus',
    'properties': {
      'commands': [[u'command1']],
      'data': [],
      'dimensions': {},
      'env': {},
      'execution_timeout_secs': 24*60*60,
      'io_timeout_secs': None,
    },
    'priority': 50,
    'scheduling_expiration_secs': 60,
    'tags': [u'tag1'],
  }
  base_data.update(kwargs)
  base_data['properties'].update(properties or {})
  return base_data


def get_results(request_key):
  """Fetches all task results for a specified TaskRequest ndb.Key.

  Returns:
    tuple(TaskResultSummary, list of TaskRunResult that exist).
  """
  result_summary_key = task_result.request_key_to_result_summary_key(
      request_key)
  result_summary = result_summary_key.get()
  # There's two way to look at it, either use a DB query or fetch all the
  # entities that could exist, at most 255. In general, there will be <3
  # entities so just fetching them by key would be faster. This function is
  # exclusively used in unit tests so it's not performance critical.
  q = task_result.TaskRunResult.query(ancestor=result_summary_key)
  q = q.order(task_result.TaskRunResult.key)
  return result_summary, q.fetch()


def _quick_reap():
  """Reaps a task."""
  data = _gen_request_data(
      properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
  request, _result_summary = task_scheduler.make_request(data)
  reaped_request, run_result = task_scheduler.bot_reap_task(
      {'OS': 'Windows-3.1.1'}, 'localhost')
  return run_result


class TaskSchedulerApiTest(test_case.TestCase):
  APP_DIR = ROOT_DIR

  def setUp(self):
    super(TaskSchedulerApiTest, self).setUp()
    self.testbed.init_search_stub()

    self.now = datetime.datetime(2014, 1, 2, 3, 4, 5, 6)
    self.mock_now(self.now)
    self.app = webtest.TestApp(
        deferred.application,
        extra_environ={
          'REMOTE_ADDR': '1.0.1.2',
          'SERVER_SOFTWARE': os.environ['SERVER_SOFTWARE'],
        })
    self.mock(stats_framework, 'add_entry', self._parse_line)

  def _parse_line(self, line):
    # pylint: disable=W0212
    actual = stats._parse_line(line, stats._Snapshot(), {}, {})
    self.assertIs(True, actual, line)

  def test_all_apis_are_tested(self):
    # Ensures there's a test for each public API.
    # TODO(maruel): Remove this once coverage is asserted.
    module = task_scheduler
    expected = set(
        i for i in dir(module)
        if i[0] != '_' and hasattr(getattr(module, i), 'func_name'))
    missing = expected - set(i[5:] for i in dir(self) if i.startswith('test_'))
    self.assertFalse(missing)

  def test_bot_reap_task(self):
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    request, _result_summary = task_scheduler.make_request(data)
    bot_dimensions = {
      u'OS': [u'Windows', u'Windows-3.1.1'],
      u'hostname': u'localhost',
      u'foo': u'bar',
    }
    actual_request, run_result  = task_scheduler.bot_reap_task(
        bot_dimensions, 'localhost')
    self.assertEqual(request, actual_request)
    self.assertEqual('localhost', run_result.bot_id)
    self.assertEqual(None, task_to_run.TaskToRun.query().get().queue_number)

  def test_bot_reap_task_quarantined(self):
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    request, _result_summary = task_scheduler.make_request(data)
    bot_dimensions = {
      u'OS': [u'Windows', u'Windows-3.1.1'],
      u'hostname': u'localhost',
      u'foo': u'bar',
    }
    bot_management.tag_bot_seen(
        'localhost', 'hostname', 'internal_ip', 'external_ip', bot_dimensions,
        'version', True)
    actual_request, run_result  = task_scheduler.bot_reap_task(
        bot_dimensions, 'localhost')
    self.assertEqual(None, actual_request)
    self.assertEqual(None, run_result)

  def test_exponential_backoff(self):
    self.mock(
        task_scheduler.random, 'random',
        lambda: task_scheduler._PROBABILITY_OF_QUICK_COMEBACK)
    data = [
      (0, 2),
      (1, 2),
      (2, 3),
      (3, 5),
      (4, 8),
      (5, 11),
      (6, 17),
      (7, 26),
      (8, 38),
      (9, 58),
      (10, 60),
      (11, 60),
    ]
    for value, expected in data:
      actual = int(round(task_scheduler.exponential_backoff(value)))
      self.assertEqual(expected, actual, (value, expected, actual))

  def test_exponential_backoff_quick(self):
    self.mock(
        task_scheduler.random, 'random',
        lambda: task_scheduler._PROBABILITY_OF_QUICK_COMEBACK - 0.01)
    self.assertEqual(1.0, task_scheduler.exponential_backoff(235))

  def test_get_results(self):
    # TODO(maruel): Split in more focused tests.
    self.mock(random, 'getrandbits', lambda _: 0x88)
    created_ts = self.now
    self.mock_now(created_ts)
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    request, _result_summary = task_scheduler.make_request(data)

    # The TaskRequest was enqueued, the TaskResultSummary was created but no
    # TaskRunResult exist yet since the task was not scheduled on any bot.
    result_summary, run_results = get_results(request.key)
    expected = {
      'abandoned_ts': None,
      'bot_id': None,
      'created_ts': created_ts,
      'completed_ts': None,
      'durations': [],
      'exit_codes': [],
      'failure': False,
      'id': '14350e868888800',
      'internal_failure': False,
      'modified_ts': created_ts,
      'name': u'Request name',
      'started_ts': None,
      'state': State.PENDING,
      'try_number': None,
      'user': u'Jesus',
    }
    self.assertEqual(expected, result_summary.to_dict())
    self.assertEqual([], run_results)

    # A bot reaps the TaskToRun.
    reaped_ts = self.now + datetime.timedelta(seconds=60)
    self.mock_now(reaped_ts)
    reaped_request, run_result = task_scheduler.bot_reap_task(
        {'OS': 'Windows-3.1.1'}, 'localhost')
    self.assertEqual(request, reaped_request)
    self.assertTrue(run_result)
    result_summary, run_results = get_results(request.key)
    expected = {
      'abandoned_ts': None,
      'bot_id': u'localhost',
      'created_ts': created_ts,  # Time the TaskRequest was created.
      'completed_ts': None,
      'durations': [],
      'exit_codes': [],
      'failure': False,
      'id': '14350e868888800',
      'internal_failure': False,
      'modified_ts': reaped_ts,
      'name': u'Request name',
      'started_ts': reaped_ts,
      'state': State.RUNNING,
      'try_number': 1,
      'user': u'Jesus',
    }
    self.assertEqual(expected, result_summary.to_dict())
    expected = [
      {
        'abandoned_ts': None,
        'bot_id': u'localhost',
        'completed_ts': None,
        'durations': [],
        'exit_codes': [],
        'id': '14350e868888801',
        'internal_failure': False,
        'modified_ts': reaped_ts,
        'started_ts': reaped_ts,
        'failure': False,
        'state': State.RUNNING,
        'try_number': 1,
      },
    ]
    self.assertEqual(expected, [i.to_dict() for i in run_results])

    # The bot completes the task.
    done_ts = self.now + datetime.timedelta(seconds=120)
    self.mock_now(done_ts)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'Foo1', 0, 0, 0.1) as entities:
      ndb.put_multi(entities)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 1, 'Bar22', 0, 0, 0.2) as entities:
      ndb.put_multi(entities)
    result_summary, run_results = get_results(request.key)
    expected = {
      'abandoned_ts': None,
      'bot_id': u'localhost',
      'created_ts': created_ts,
      'completed_ts': done_ts,
      'durations': [0.1, 0.2],
      'exit_codes': [0, 0],
      'failure': False,
      'id': '14350e868888800',
      'internal_failure': False,
      'modified_ts': done_ts,
      'name': u'Request name',
      'started_ts': reaped_ts,
      'state': State.COMPLETED,
      'try_number': 1,
      'user': u'Jesus',
    }
    self.assertEqual(expected, result_summary.to_dict())
    expected = [
      {
        'abandoned_ts': None,
        'bot_id': u'localhost',
        'completed_ts': done_ts,
        'durations': [0.1, 0.2],
        'exit_codes': [0, 0],
        'failure': False,
        'id': '14350e868888801',
        'internal_failure': False,
        'modified_ts': done_ts,
        'started_ts': reaped_ts,
        'state': State.COMPLETED,
        'try_number': 1,
      },
    ]
    self.assertEqual(expected, [t.to_dict() for t in run_results])

  def test_exit_code_failure(self):
    self.mock(random, 'getrandbits', lambda _: 0x88)
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    request, _result_summary = task_scheduler.make_request(data)
    reaped_request, run_result = task_scheduler.bot_reap_task(
        {'OS': 'Windows-3.1.1'}, 'localhost')
    self.assertEqual(request, reaped_request)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'Foo1', 0, 0, 0.1) as entities:
      ndb.put_multi(entities)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 1, 'Bar22', 0, 1, 0.2) as entities:
      ndb.put_multi(entities)
    result_summary, run_results = get_results(request.key)

    expected = {
      'abandoned_ts': None,
      'bot_id': u'localhost',
      'created_ts': self.now,
      'completed_ts': self.now,
      'durations': [0.1, 0.2],
      'exit_codes': [0, 1],
      'failure': True,
      'id': '14350e868888800',
      'internal_failure': False,
      'modified_ts': self.now,
      'name': u'Request name',
      'started_ts': self.now,
      'state': State.COMPLETED,
      'try_number': 1,
      'user': u'Jesus',
    }
    self.assertEqual(expected, result_summary.to_dict())

    expected = [
      {
        'abandoned_ts': None,
        'bot_id': u'localhost',
        'completed_ts': self.now,
        'durations': [0.1, 0.2],
        'exit_codes': [0, 1],
        'failure': True,
        'id': '14350e868888801',
        'internal_failure': False,
        'modified_ts': self.now,
        'started_ts': self.now,
        'state': State.COMPLETED,
        'try_number': 1,
      },
    ]
    self.assertEqual(expected, [t.to_dict() for t in run_results])

  def test_make_request(self):
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    # It is tested indirectly in the other functions.
    self.assertTrue(task_scheduler.make_request(data))

  def test_unpack_result_summary_key(self):
    actual = task_scheduler.unpack_result_summary_key('bb80200')
    expected = (
        "Key('TaskRequestShard', '6f4236', 'TaskRequest', 196608512, "
        "'TaskResultSummary', 1)")
    self.assertEqual(expected, str(actual))

    with self.assertRaises(ValueError):
      task_scheduler.unpack_result_summary_key('0')
    with self.assertRaises(ValueError):
      task_scheduler.unpack_result_summary_key('g')
    with self.assertRaises(ValueError):
      task_scheduler.unpack_result_summary_key('bb80201')

  def test_unpack_run_result_key(self):
    for i in ('1', '2'):
      actual = task_scheduler.unpack_run_result_key('bb8020' + i)
      expected = (
          "Key('TaskRequestShard', '6f4236', 'TaskRequest', 196608512, "
          "'TaskResultSummary', 1, 'TaskRunResult', " + i + ")")
      self.assertEqual(expected, str(actual))

    with self.assertRaises(ValueError):
      task_scheduler.unpack_run_result_key('1')
    with self.assertRaises(ValueError):
      task_scheduler.unpack_run_result_key('g')
    with self.assertRaises(ValueError):
      task_scheduler.unpack_run_result_key('bb80200')
    with self.assertRaises(NotImplementedError):
      task_scheduler.unpack_run_result_key('bb80203')

  def test_bot_update_task(self):
    run_result = _quick_reap()
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'hi', 0, 0, 0.1) as entities:
      self.assertEqual(3, len(entities))
      ndb.put_multi(entities)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'hey', 2, 0, 0.1) as entities:
      self.assertEqual(3, len(entities))
      ndb.put_multi(entities)
    self.assertEqual(['hihey'], run_result.get_outputs())

  def test_bot_update_task_new_two_commands(self):
    run_result = _quick_reap()
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'hi', 0, 0, 0.1) as entities:
      self.assertEqual(3, len(entities))
      ndb.put_multi(entities)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 1, 'hey', 0, 0, 0.2) as entities:
      self.assertEqual(3, len(entities))
      ndb.put_multi(entities)
    self.assertEqual(['hi', 'hey'], run_result.get_outputs())
    self.assertEqual([0.1, 0.2], run_result.durations)

  def test_bot_update_task_new_overwrite(self):
    run_result = _quick_reap()
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'hi', 0, None, None) as entities:
      self.assertEqual(3, len(entities))
      ndb.put_multi(entities)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'hey', 1, None, None) as entities:
      self.assertEqual(3, len(entities))
      ndb.put_multi(entities)
    self.assertEqual(['hhey'], run_result.get_outputs())

  def _bot_update_task_partial_write(self, index, expected_length):
    """Tests that a partial write fails."""
    class Foo(Exception):
      pass

    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    request, _result_summary = task_scheduler.make_request(data)
    reaped_request, run_result = task_scheduler.bot_reap_task(
        {'OS': 'Windows-3.1.1'}, 'localhost')

    # Use a large amount of data to force multiple (3) TaskOutputChunk.
    stdout = 'f' * (task_result.TaskOutput.CHUNK_SIZE * 2 + 1)
    with self.assertRaises(Foo):
      with task_scheduler.bot_update_task(
          run_result.key, 'localhost', 0, stdout, 0, None, None) as entities:
        self.assertEqual(expected_length, len(entities))
        entities[index].put()
        raise Foo('Ahah, got ya')

    # The client retries, this time it works.
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, stdout, 0, None, None) as entities:
      self.assertEqual(expected_length, len(entities))
      ndb.put_multi(entities)

    self.assertEqual([stdout], run_result.get_outputs())

    # The client retried even if it shouldn't have. No difference.
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, stdout, 0, 0, 0.1) as entities:
      self.assertEqual(expected_length, len(entities))
      ndb.put_multi(entities)

    self.assertEqual([stdout], run_result.get_outputs())

  def test_bot_update_task_partial_write(self):
    # The ndb.put_multi() mocks in _bot_update_task_partial_write receives:
    #  1 * TaskRunResult, 1 * TaskResultSummary, 3 * TaskOutputChunk.
    # This test case ensures that the code is behaving correctly, independent of
    # which element was written to the DB.
    number_elements = 5
    for index in range(number_elements):
      self._bot_update_task_partial_write(index, number_elements)

  def test_bot_kill_task(self):
    self.mock(random, 'getrandbits', lambda _: 0x88)
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    request, result_summary = task_scheduler.make_request(data)
    reaped_request, run_result = task_scheduler.bot_reap_task(
        {'OS': 'Windows-3.1.1'}, 'localhost')

    task_scheduler.bot_kill_task(run_result)
    expected = {
      'abandoned_ts': self.now,
      'bot_id': u'localhost',
      'created_ts': self.now,
      'completed_ts': None,
      'durations': [],
      'exit_codes': [],
      'failure': False,
      'id': '14350e868888800',
      'internal_failure': True,
      'modified_ts': self.now,
      'name': u'Request name',
      'started_ts': self.now,
      'state': State.BOT_DIED,
      'try_number': 1,
      'user': u'Jesus',
    }
    self.assertEqual(expected, result_summary.to_dict())

  def test_cancel_task(self):
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    _request, result_summary = task_scheduler.make_request(data)
    ok, was_running = task_scheduler.cancel_task(result_summary.key)
    self.assertEqual(True, ok)
    self.assertEqual(False, was_running)
    result_summary = result_summary.key.get()
    self.assertEqual(task_result.State.CANCELED, result_summary.state)

  def test_cron_abort_expired_task_to_run(self):
    # Create two shards, one is properly reaped, the other is expired.
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    task_scheduler.make_request(data)
    bot_dimensions = {
      u'OS': [u'Windows', u'Windows-3.1.1'],
      u'hostname': u'localhost',
      u'foo': u'bar',
    }
    expiration = data['scheduling_expiration_secs']
    self.mock_now(self.now, expiration+1)
    self.assertEqual(1, task_scheduler.cron_abort_expired_task_to_run())

  def test_cron_handle_bot_died(self):
    # TODO(maruel): Test expired tasks.
    self.mock(random, 'getrandbits', lambda _: 0x88)
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}),
        scheduling_expiration_secs=600)
    task_scheduler.make_request(data)
    bot_dimensions = {
      u'OS': [u'Windows', u'Windows-3.1.1'],
      u'hostname': u'localhost',
      u'foo': u'bar',
    }
    _request, run_result = task_scheduler.bot_reap_task(
        bot_dimensions, 'localhost')
    self.assertEqual(1, run_result.try_number)
    self.mock_now(self.now + task_common.BOT_PING_TOLERANCE, 1)
    self.assertEqual((0, 1), task_scheduler.cron_handle_bot_died())

    # Refresh and compare:
    run_result = run_result.key.get()
    expected = {
      'abandoned_ts': datetime.datetime(2014, 1, 2, 3, 9, 6, 6),
      'bot_id': u'localhost',
      'completed_ts': None,
      'durations': [],
      'exit_codes': [],
      'failure': False,
      'id': '14350e868888801',
      'internal_failure': True,
      'modified_ts': datetime.datetime(2014, 1, 2, 3, 9, 6, 6),
      'started_ts': datetime.datetime(2014, 1, 2, 3, 4, 5, 6),
      'state': task_result.State.BOT_DIED,
      'try_number': 1,
    }
    self.assertEqual(expected, run_result.to_dict())
    result_summary = run_result.result_summary_key.get()
    expected = {
      'abandoned_ts': None,
      'bot_id': u'localhost',
      'completed_ts': None,
      'created_ts': datetime.datetime(2014, 1, 2, 3, 4, 5, 6),
      'durations': [],
      'exit_codes': [],
      'failure': False,
      'id': '14350e868888800',
      'internal_failure': False,
      'modified_ts': datetime.datetime(2014, 1, 2, 3, 9, 6, 6),
      'name': u'Request name',
      'started_ts': datetime.datetime(2014, 1, 2, 3, 4, 5, 6),
      'state': task_result.State.PENDING,
      'try_number': 1,
      'user': u'Jesus',
    }
    self.assertEqual(expected, result_summary.to_dict())

    # Task was retried.
    self.mock_now(self.now + task_common.BOT_PING_TOLERANCE, 2)
    _request, run_result = task_scheduler.bot_reap_task(
        bot_dimensions, 'localhost')
    logging.info('%s', [t.to_dict() for t in task_to_run.TaskToRun.query()])
    self.assertEqual(2, run_result.try_number)
    with task_scheduler.bot_update_task(
        run_result.key, 'localhost', 0, 'Foo1', 0, 0, 0.1) as entities:
      ndb.put_multi(entities)
    result_summary = run_result.result_summary_key.get()
    expected = {
      'abandoned_ts': None,
      'bot_id': u'localhost',
      'completed_ts': datetime.datetime(2014, 1, 2, 3, 9, 7, 6),
      'created_ts': datetime.datetime(2014, 1, 2, 3, 4, 5, 6),
      'durations': [0.1],
      'exit_codes': [0],
      'failure': False,
      'id': '14350e868888800',
      'internal_failure': False,
      'modified_ts': datetime.datetime(2014, 1, 2, 3, 9, 7, 6),
      'name': u'Request name',
      'started_ts': datetime.datetime(2014, 1, 2, 3, 9, 7, 6),
      'state': 112,
      'try_number': 2,
      'user': u'Jesus',
    }
    self.assertEqual(expected, result_summary.to_dict())

  def test_search_by_name(self):
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    _, result_summary = task_scheduler.make_request(data)

    # Assert that search is not case-sensitive by using unexpected casing.
    actual, _cursor = task_scheduler.search_by_name('requEST', None, 10)
    self.assertEqual([result_summary], actual)
    actual, _cursor = task_scheduler.search_by_name('name', None, 10)
    self.assertEqual([result_summary], actual)

  def test_search_by_name_failures(self):
    data = _gen_request_data(
        properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
    _, result_summary = task_scheduler.make_request(data)

    actual, _cursor = task_scheduler.search_by_name('foo', None, 10)
    self.assertEqual([], actual)
    # Partial match doesn't work.
    actual, _cursor = task_scheduler.search_by_name('nam', None, 10)
    self.assertEqual([], actual)

  def test_search_by_name_broken_tasks(self):
    # Create tasks where task_scheduler_make_request() fails in the middle. This
    # is done by mocking the functions to fail every SKIP call and running it in
    # a loop.
    class RandomFailure(Exception):
      pass

    # First call fails ndb.put_multi(), second call fails search.Index.put(),
    # third call work.
    index = [0]
    SKIP = 3
    def put_multi(*args, **kwargs):
      self.assertEqual('make_request', inspect.stack()[1][3])
      if (index[0] % SKIP) == 1:
        raise RandomFailure()
      return old_put_multi(*args, **kwargs)

    def put(*args, **kwargs):
      self.assertEqual('make_request', inspect.stack()[1][3])
      if (index[0] % SKIP) == 2:
        raise RandomFailure()
      return old_put(*args, **kwargs)

    old_put_multi = self.mock(ndb, 'put_multi', put_multi)
    old_put = self.mock(search.Index, 'put', put)

    saved = []

    for i in xrange(100):
      index[0] = i
      data = _gen_request_data(
          name='Request %d' % i,
          properties=dict(dimensions={u'OS': u'Windows-3.1.1'}))
      try:
        _, result_summary = task_scheduler.make_request(data)
        saved.append(result_summary)
      except RandomFailure:
        pass

    self.assertEqual(34, len(saved))
    # The mocking doesn't affect TaskRequest since it uses
    # datastore_utils.insert() which uses ndb.Model.put().
    self.assertEqual(100, task_request.TaskRequest.query().count())
    self.assertEqual(34, task_result.TaskResultSummary.query().count())

    # Now the DB is full of half-corrupted entities.
    cursor = None
    actual, cursor = task_scheduler.search_by_name('Request', cursor, 31)
    self.assertEqual(31, len(actual))
    actual, cursor = task_scheduler.search_by_name('Request', cursor, 31)
    self.assertEqual(3, len(actual))
    actual, cursor = task_scheduler.search_by_name('Request', cursor, 31)
    self.assertEqual(0, len(actual))


if __name__ == '__main__':
  if '-v' in sys.argv:
    unittest.TestCase.maxDiff = None
  logging.basicConfig(
      level=logging.DEBUG if '-v' in sys.argv else logging.ERROR)
  unittest.main()
