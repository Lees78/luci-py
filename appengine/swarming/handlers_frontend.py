# Copyright 2013 The LUCI Authors. All rights reserved.
# Use of this source code is governed under the Apache License, Version 2.0
# that can be found in the LICENSE file.

"""Main entry point for Swarming service.

This file contains the URL handlers for all the Swarming service URLs,
implemented using the webapp2 framework.
"""

import collections
import datetime
import itertools
import os

import webapp2

from google.appengine import runtime
from google.appengine.api import users
from google.appengine.datastore import datastore_query
from google.appengine.ext import ndb

import handlers_bot
import handlers_backend
import handlers_endpoints
import mapreduce_jobs
import template
from components import auth
from components import datastore_utils
from components import utils
from server import acl
from server import bot_code
from server import bot_management
from server import config
from server import stats_gviz
from server import task_pack
from server import task_request
from server import task_result
from server import task_scheduler


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


# Helper class for displaying the sort options in html templates.
SortOptions = collections.namedtuple('SortOptions', ['key', 'name'])


### is_admin pages.


class RestrictedConfigHandler(auth.AuthenticatingHandler):
  @auth.autologin
  @auth.require(acl.is_admin)
  def get(self):
    # Template parameters schema matches settings_info() return value.
    self.response.write(template.render(
        'swarming/restricted_config.html', config.settings_info()))


class RestrictedCancelPendingHandler(auth.AuthenticatingHandler):
  """Cancels all pending tasks."""
  @auth.require(acl.is_admin)
  def post(self):
    # There's two ways to query, either with TaskToRun.queue_number or with
    # TaskResultSummary.state.
    canceled = 0
    was_running = 0
    q = task_result.TaskResultSummary.query(
        task_result.TaskResultSummary.state == task_result.State.PENDING)
    status = ''
    try:
      for result_key in q.iter(keys_only=True):
        request_obj = task_pack.result_summary_key_to_request_key(
            result_key).get()
        ok, wr = task_scheduler.cancel_task(request_obj, result_key)
        if ok:
          canceled += 1
        if wr:
          was_running += 1
      status = 'Success'
    except runtime.DeadlineExceededError:
      status = 'Deadline exceeded'
    self.response.write(
        'Canceled %d tasks.\n%d tasks were running.\n%s' %
        (canceled, was_running, status))


class UploadBotConfigHandler(auth.AuthenticatingHandler):
  """Stores a new bot_config.py script."""

  @auth.autologin
  @auth.require(acl.is_admin)
  def get(self):
    bot_config = bot_code.get_bot_config()
    params = {
      'content': bot_config.content.decode('utf-8'),
      'path': self.request.path,
      'when': bot_config.when,
      'who': bot_config.who,
      'xsrf_token': self.generate_xsrf_token(),
    }
    self.response.write(
        template.render('swarming/restricted_upload_bot_config.html', params))

  @auth.require(acl.is_admin)
  def post(self):
    script = self.request.get('script', '')
    if not script:
      self.abort(400, 'No script uploaded')

    # Make sure the script is valid utf-8. For some odd reason, the script
    # instead may or may not be an unicode instance. This depends if it is on
    # AppEngine production or not.
    if isinstance(script, str):
      script = script.decode('utf-8', 'replace')
    script = script.encode('utf-8')
    bot_code.store_bot_config(script)
    self.get()


class UploadBootstrapHandler(auth.AuthenticatingHandler):
  """Stores a new bootstrap.py script."""

  @auth.autologin
  @auth.require(acl.is_admin)
  def get(self):
    bootstrap = bot_code.get_bootstrap(self.request.host_url)
    params = {
      'content': bootstrap.content.decode('utf-8'),
      'path': self.request.path,
      'when': bootstrap.when,
      'who': bootstrap.who,
      'xsrf_token': self.generate_xsrf_token(),
    }
    self.response.write(
        template.render('swarming/restricted_upload_bootstrap.html', params))

  @auth.require(acl.is_admin)
  def post(self):
    script = self.request.get('script', '')
    if not script:
      self.abort(400, 'No script uploaded')

    # Make sure the script is valid utf-8. For some odd reason, the script
    # instead may or may not be an unicode instance. This depends if it is on
    # AppEngine production or not.
    if isinstance(script, str):
      script = script.decode('utf-8', 'replace')
    script = script.encode('utf-8')
    bot_code.store_bootstrap(script)
    self.get()


### Mapreduce related handlers


class RestrictedLaunchMapReduceJob(auth.AuthenticatingHandler):
  """Enqueues a task to start a map reduce job on the backend module.

  A tree of map reduce jobs inherits module and version of a handler that
  launched it. All UI handlers are executes by 'default' module. So to run a
  map reduce on a backend module one needs to pass a request to a task running
  on backend module.
  """

  @auth.require(acl.is_admin)
  def post(self):
    job_id = self.request.get('job_id')
    assert job_id in mapreduce_jobs.MAPREDUCE_JOBS
    success = utils.enqueue_task(
        url='/internal/taskqueue/mapreduce/launch/%s' % job_id,
        queue_name=mapreduce_jobs.MAPREDUCE_TASK_QUEUE,
        use_dedicated_module=False)
    # New tasks should show up on the status page.
    if success:
      self.redirect('/restricted/mapreduce/status')
    else:
      self.abort(500, 'Failed to launch the job')


### acl.is_privileged_user pages.


class OldBotsListHandler(auth.AuthenticatingHandler):
  """Presents the list of known bots."""
  ACCEPTABLE_BOTS_SORTS = {
    'last_seen_ts': 'Last Seen',
    '-quarantined': 'Quarantined',
    '__key__': 'ID',
  }
  SORT_OPTIONS = [
    SortOptions(k, v) for k, v in sorted(ACCEPTABLE_BOTS_SORTS.iteritems())
  ]

  @auth.autologin
  @auth.require(acl.is_privileged_user)
  def get(self):
    limit = int(self.request.get('limit', 100))
    cursor = datastore_query.Cursor(urlsafe=self.request.get('cursor'))
    sort_by = self.request.get('sort_by', '__key__')
    if sort_by not in self.ACCEPTABLE_BOTS_SORTS:
      self.abort(400, 'Invalid sort_by query parameter')

    if sort_by[0] == '-':
      order = datastore_query.PropertyOrder(
          sort_by[1:], datastore_query.PropertyOrder.DESCENDING)
    else:
      order = datastore_query.PropertyOrder(
          sort_by, datastore_query.PropertyOrder.ASCENDING)

    dimensions = (
      l.strip() for l in self.request.get('dimensions', '').splitlines()
    )
    dimensions = [i for i in dimensions if i]

    now = utils.utcnow()
    cutoff = now - datetime.timedelta(
        seconds=config.settings().bot_death_timeout_secs)

    # TODO(maruel): Counting becomes an issue at the 10k range, at that point it
    # should be prepopulated in an entity and updated via a cron job.
    num_bots_busy_future = (bot_management.BotInfo.query(
        bot_management.BotInfo.composite == bot_management.BotInfo.BUSY)
        .count_async())
    num_bots_dead_future = bot_management.BotInfo.query(
        bot_management.BotInfo.last_seen_ts < cutoff).count_async()
    num_bots_quarantined_future = bot_management.BotInfo.query(
        bot_management.BotInfo.quarantined == True).count_async()
    num_bots_total_future = bot_management.BotInfo.query().count_async()
    q = bot_management.BotInfo.query().order(order)
    for d in dimensions:
      q = q.filter(bot_management.BotInfo.dimensions_flat == d)
    fetch_future = q.fetch_page_async(limit, start_cursor=cursor)

    # TODO(maruel): self.request.host_url should be the default AppEngine url
    # version and not the current one. It is only an issue when
    # version-dot-appid.appspot.com urls are used to access this page.
    # TODO(aludwin): Display both gRPC and non-gRPC versions
    version = bot_code.get_bot_version(self.request.host_url)
    bots, cursor, more = fetch_future.get_result()
    # Prefetch the tasks. We don't actually use the value here, it'll be
    # implicitly used by ndb local's cache when refetched by the html template.
    tasks = filter(None, (b.task for b in bots))
    ndb.get_multi(tasks)
    num_bots_busy = num_bots_busy_future.get_result()
    num_bots_dead = num_bots_dead_future.get_result()
    num_bots_quarantined = num_bots_quarantined_future.get_result()
    num_bots_total = num_bots_total_future.get_result()
    try_link = '/botlist?l=%d' % limit
    if dimensions:
      try_link += '&f=' + '&f='.join(dimensions)
    params = {
      'bots': bots,
      'current_version': version,
      'cursor': cursor.urlsafe() if cursor and more else '',
      'dimensions': '\n'.join(dimensions),
      'is_admin': acl.is_admin(),
      'is_privileged_user': acl.is_privileged_user(),
      'limit': limit,
      'now': now,
      'num_bots_alive': num_bots_total - num_bots_dead,
      'num_bots_busy': num_bots_busy,
      'num_bots_dead': num_bots_dead,
      'num_bots_quarantined': num_bots_quarantined,
      'try_link': try_link,
      'sort_by': sort_by,
      'sort_options': self.SORT_OPTIONS,
      'xsrf_token': self.generate_xsrf_token(),
    }
    self.response.write(
        template.render('swarming/restricted_botslist.html', params))


class OldBotHandler(auth.AuthenticatingHandler):
  """Returns data about the bot, including last tasks and events."""

  @auth.autologin
  @auth.require(acl.is_privileged_user)
  def get(self, bot_id):
    # pagination is currently for tasks, not events.
    limit = int(self.request.get('limit', 100))
    cursor = datastore_query.Cursor(urlsafe=self.request.get('cursor'))
    run_results_future = task_result.TaskRunResult.query(
        task_result.TaskRunResult.bot_id == bot_id).order(
            -task_result.TaskRunResult.started_ts).fetch_page_async(
                limit, start_cursor=cursor)
    bot_future = bot_management.get_info_key(bot_id).get_async()
    events_future = bot_management.get_events_query(
        bot_id, True).fetch_async(100)

    now = utils.utcnow()

    # Calculate the time this bot was idle.
    idle_time = datetime.timedelta()
    run_time = datetime.timedelta()
    run_results, cursor, more = run_results_future.get_result()
    if run_results:
      run_time = run_results[0].duration_now(now) or datetime.timedelta()
      if not cursor and run_results[0].state != task_result.State.RUNNING:
        # Add idle time since last task completed. Do not do this when a cursor
        # is used since it's not representative.
        idle_time = now - run_results[0].ended_ts
      for index in xrange(1, len(run_results)):
        # .started_ts will always be set by definition but .ended_ts may be None
        # if the task was abandoned. We can't count idle time since the bot may
        # have been busy running *another task*.
        # TODO(maruel): One option is to add a third value "broken_time".
        # Looking at timestamps specifically could help too, e.g. comparing
        # ended_ts of this task vs the next one to see if the bot was assigned
        # two tasks simultaneously.
        if run_results[index].ended_ts:
          idle_time += (
              run_results[index-1].started_ts - run_results[index].ended_ts)
          # We are taking the whole time the bot was doing work, not just the
          # duration associated with the task.
          duration = run_results[index].duration_as_seen_by_server
          if duration:
            run_time += duration

    events = events_future.get_result()
    bot = bot_future.get_result()
    if not bot and events:
      # If there is not BotInfo, look if there are BotEvent child of this
      # entity. If this is the case, it means the bot was deleted but it's
      # useful to show information about it to the user even if the bot was
      # deleted. For example, it could be an auto-scaled bot.
      bot = bot_management.BotInfo(
          key=bot_management.get_info_key(bot_id),
          dimensions_flat=bot_management.dimensions_to_flat(
              events[0].dimensions),
          state=events[0].state,
          external_ip=events[0].external_ip,
          authenticated_as=events[0].authenticated_as,
          version=events[0].version,
          quarantined=events[0].quarantined,
          task_id=events[0].task_id,
          last_seen_ts=events[0].ts)

    params = {
      'bot': bot,
      'bot_id': bot_id,
      # TODO(aludwin): Use the bot's correct gRPC status to determine the
      # version
      'current_version': bot_code.get_bot_version(self.request.host_url),
      'cursor': cursor.urlsafe() if cursor and more else None,
      'events': events,
      'idle_time': idle_time,
      'is_admin': acl.is_admin(),
      'limit': limit,
      'now': now,
      'run_results': run_results,
      'run_time': run_time,
      'try_link': '/bot?id=%s' % bot_id,
      'xsrf_token': self.generate_xsrf_token(),
    }
    self.response.write(
        template.render('swarming/restricted_bot.html', params))


class OldBotDeleteHandler(auth.AuthenticatingHandler):
  """Deletes a known bot.

  This only deletes the BotInfo, not BotRoot, BotEvent's nor BotSettings.

  This is sufficient so the bot doesn't show up on the Bots page while keeping
  historical data.
  """

  @auth.require(acl.is_admin)
  def post(self, bot_id):
    bot_key = bot_management.get_info_key(bot_id)
    if bot_key.get():
      bot_key.delete()
    self.redirect('/restricted/bots')


### User accessible pages.


class OldTasksHandler(auth.AuthenticatingHandler):
  """Lists all requests and allows callers to manage them."""
  # Each entry is an item in the Sort column.
  # Each entry is (key, text, hover)
  SORT_CHOICES = [
    ('created_ts', 'Created', 'Most recently created tasks are shown first.'),
    ('modified_ts', 'Active',
      'Shows the most recently active tasks first. Using this order resets '
      'state to \'All\'.'),
    ('completed_ts', 'Completed',
      'Shows the most recently completed tasks first. Using this order resets '
      'state to \'All\'.'),
    ('abandoned_ts', 'Abandoned',
      'Shows the most recently abandoned tasks first. Using this order resets '
      'state to \'All\'.'),
  ]

  # Each list is one column in the Task state filtering column.
  # Each sublist is the checkbox item in this column.
  # Each entry is (key, text, hover)
  # TODO(maruel): Evaluate what the categories the users would like for
  # diagnosis, then adapt the DB to enable efficient queries.
  STATE_CHOICES = [
    [
      ('all', 'All', 'All tasks ever requested independent of their state.'),
      ('pending', 'Pending',
        'Tasks that are still ready to be assigned to a bot. Using this order '
        'resets order to \'Created\'.'),
      ('running', 'Running',
        'Tasks being currently executed by a bot. Using this order resets '
        'order to \'Created\'.'),
      ('pending_running', 'Pending|running',
        'Tasks either \'pending\' or \'running\'. Using this order resets '
        'order to \'Created\'.'),
    ],
    [
      ('completed', 'Completed',
        'All tasks that are completed, independent if the task itself '
        'succeeded or failed. This excludes tasks that had an infrastructure '
        'failure. Using this order resets order to \'Created\'.'),
      ('completed_success', 'Successes',
        'Tasks that completed successfully. Using this order resets order to '
        '\'Created\'.'),
      ('completed_failure', 'Failures',
        'Tasks that were executed successfully but failed, e.g. exit code is '
        'non-zero. Using this order resets order to \'Created\'.'),
      ('timed_out', 'Timed out',
        'The execution timed out, so it was forcibly killed.'),
    ],
    [
      ('bot_died', 'Bot died',
        'The bot stopped sending updates while running the task, causing the '
        'task execution to time out. This is considered an infrastructure '
        'failure and the usual reason is that the bot BSOD\'ed or '
        'spontaneously rebooted. Using this order resets order to '
        '\'Created\'.'),
      ('expired', 'Expired',
        'The task was not assigned a bot until its expiration timeout, causing '
        'the task to never being assigned to a bot. This can happen when the '
        'dimension filter was not available or overloaded with a low priority. '
        'Either fix the priority or bring up more bots with these dimensions. '
        'Using this order resets order to \'Created\'.'),
      ('canceled', 'Canceled',
        'The task was explictly canceled by a user before it started '
        'executing. Using this order resets order to \'Created\'.'),
    ],
  ]

  @auth.autologin
  @auth.require(acl.is_user)
  def get(self):
    cursor_str = self.request.get('cursor')
    limit = int(self.request.get('limit', 100))
    sort = self.request.get('sort', self.SORT_CHOICES[0][0])
    state = self.request.get('state', self.STATE_CHOICES[0][0][0])
    counts = self.request.get('counts', '').strip()
    task_tags = [
      line for line in self.request.get('task_tag', '').splitlines() if line
    ]

    if not any(sort == i[0] for i in self.SORT_CHOICES):
      self.abort(400, 'Invalid sort')
    if not any(any(state == i[0] for i in j) for j in self.STATE_CHOICES):
      self.abort(400, 'Invalid state')

    if sort != 'created_ts':
      # Zap all filters in this case to reduce the number of required indexes.
      # Revisit according to the user requests.
      state = 'all'

    now = utils.utcnow()
    # "Temporarily" disable the count. This is too slow on the prod server
    # (>10s). The fix is to have the web page do a XHR query to get the values
    # asynchronously.
    counts_future = None
    if counts == 'true':
      counts_future = self._get_counts_future(now)

    try:
      if task_tags:
        # Enforce created_ts when tags are used.
        sort = 'created_ts'
      query = task_result.get_result_summaries_query(
          None, None, sort, state, task_tags)
      tasks, cursor_str = datastore_utils.fetch_page(query, limit, cursor_str)

      # Prefetch the TaskRequest all at once, so that ndb's in-process cache has
      # it instead of fetching them one at a time indirectly when using
      # TaskResultSummary.request_key.get().
      futures = ndb.get_multi_async(t.request_key for t in tasks)

      # Evaluate the counts to print the filtering columns with the associated
      # numbers.
      state_choices = self._get_state_choices(counts_future)
    except ValueError as e:
      self.abort(400, str(e))

    def safe_sum(items):
      return sum(items, datetime.timedelta())

    def avg(items):
      if not items:
        return 0.
      return safe_sum(items) / len(items)

    def median(items):
      if not items:
        return 0.
      middle = len(items) / 2
      if len(items) % 2:
        return items[middle]
      return (items[middle-1]+items[middle]) / 2

    gen = (t.duration_now(now) for t in tasks)
    durations = sorted(t for t in gen if t is not None)
    gen = (t.pending_now(now) for t in tasks)
    pendings = sorted(t for t in gen if t is not None)
    total_cost_usd = sum(t.cost_usd for t in tasks)
    total_cost_saved_usd = sum(
        t.cost_saved_usd for t in tasks if t.cost_saved_usd)
    # Include the overhead in the total amount of time saved, since it's
    # overhead saved.
    # In theory, t.duration_as_seen_by_server should always be set when
    # t.deduped_from is set but there has some broken entities in the datastore.
    total_saved = safe_sum(
        t.duration_as_seen_by_server for t in tasks
        if t.deduped_from and t.duration_as_seen_by_server)
    duration_sum = safe_sum(durations)
    total_saved_percent = (
        (100. * total_saved.total_seconds() / duration_sum.total_seconds())
        if duration_sum else 0.)

    try_link = '/tasklist?l=%d' % limit
    if task_tags:
      try_link += '&f=' + '&f='.join(task_tags)
    params = {
      'cursor': cursor_str,
      'duration_average': avg(durations),
      'duration_median': median(durations),
      'duration_sum': duration_sum,
      'has_pending': any(t.is_pending for t in tasks),
      'has_running': any(t.is_running for t in tasks),
      'is_admin': acl.is_admin(),
      'is_privileged_user': acl.is_privileged_user(),
      'limit': limit,
      'now': now,
      'pending_average': avg(pendings),
      'pending_median': median(pendings),
      'pending_sum': safe_sum(pendings),
      'show_footer': bool(pendings or durations),
      'sort': sort,
      'sort_choices': self.SORT_CHOICES,
      'state': state,
      'state_choices': state_choices,
      'task_tag': '\n'.join(task_tags),
      'tasks': tasks,
      'total_cost_usd': total_cost_usd,
      'total_cost_saved_usd': total_cost_saved_usd,
      'total_saved': total_saved,
      'total_saved_percent': total_saved_percent,
      'try_link': try_link,
      'xsrf_token': self.generate_xsrf_token(),
    }
    # TODO(maruel): If admin or if the user is task's .user, show the Cancel
    # button. Do not show otherwise.
    self.response.write(template.render('swarming/user_tasks.html', params))

    # Do not let dangling futures linger around.
    ndb.Future.wait_all(futures)

  def _get_counts_future(self, now):
    """Returns all the counting futures in parallel."""
    counts_future = {}
    last_24h = now - datetime.timedelta(days=1)
    for state_key, _, _ in itertools.chain.from_iterable(self.STATE_CHOICES):
      query = task_result.get_result_summaries_query(
          last_24h, None, 'created_ts', state_key, None)
      counts_future[state_key] = query.count_async()
    return counts_future

  def _get_state_choices(self, counts_future):
    """Converts STATE_CHOICES with _get_counts_future() into nice text."""
    # Appends the number of tasks for each filter. It gives a sense of how much
    # things are going on.
    if counts_future:
      counts = {k: v.get_result() for k, v in counts_future.iteritems()}
    state_choices = []
    for choice_list in self.STATE_CHOICES:
      state_choices.append([])
      for state_key, name, title in choice_list:
        if counts_future:
          name += ' (%d)' % counts[state_key]
        state_choices[-1].append((state_key, name, title))
    return state_choices


class BaseOldTaskHandler(auth.AuthenticatingHandler):
  """Handler that acts on a single task.

  Ensures that the user has access to the task.
  """
  def get_request_and_result(self, task_id, with_secret_bytes=False):
    """Retrieves the TaskRequest for 'task_id' and enforces the ACL.

    Supports both TaskResultSummary (ends with 0) or TaskRunResult (ends with 1
    or 2).

    Returns:
      tuple(TaskRequest, SecretBytes, result): result can be either for
          a TaskRunResult or a TaskResultSummay.
    """
    try:
      key = task_pack.unpack_result_summary_key(task_id)
      request_key = task_pack.result_summary_key_to_request_key(key)
    except ValueError:
      try:
        key = task_pack.unpack_run_result_key(task_id)
        request_key = task_pack.result_summary_key_to_request_key(
            task_pack.run_result_key_to_result_summary_key(key))
      except ValueError:
        self.abort(404, 'Invalid key format.')
    if with_secret_bytes:
      sb_key = task_pack.request_key_to_secret_bytes_key(request_key)
      request, result, secret_bytes = ndb.get_multi((request_key, key, sb_key))
    else:
      request, result = ndb.get_multi((request_key, key))
      secret_bytes = None
    if not request or not result:
      self.abort(404, '%s not found.' % key.id())
    if not request.has_access:
      self.abort(403, '%s is not accessible.' % key.id())
    return request, secret_bytes, result


class OldTaskHandler(BaseOldTaskHandler):
  """Show the full text of a task request and its result."""

  @staticmethod
  def packages_grouped_by_path(flat_packages):
    """Returns sorted [(path, [PinInfo, ...])].

    Used by user_task.html.
    """
    retval = collections.defaultdict(list)
    for pkg in flat_packages:
      retval[pkg.path].append(pkg)
    return sorted(retval.iteritems())

  @auth.autologin
  @auth.require(acl.is_user)
  def get(self, task_id):
    request, _, result = self.get_request_and_result(task_id)
    parent_task_future = None
    if request.parent_task_id:
      parent_key = task_pack.unpack_run_result_key(request.parent_task_id)
      parent_task_future = parent_key.get_async()
    children_tasks_futures = [
      task_pack.unpack_result_summary_key(c).get_async()
      for c in result.children_task_ids
    ]

    bot_id = result.bot_id
    following_task_future = None
    previous_task_future = None
    if result.started_ts:
      # Use a shortcut name because it becomes unwieldy otherwise.
      cls = task_result.TaskRunResult

      # Note that the links will be to the TaskRunResult, not to
      # TaskResultSummary.
      following_task_future = cls.query(
          cls.bot_id == bot_id,
          cls.started_ts > result.started_ts,
          ).order(cls.started_ts).get_async()
      previous_task_future = cls.query(
          cls.bot_id == bot_id,
          cls.started_ts < result.started_ts,
          ).order(-cls.started_ts).get_async()

    bot_future = (
        bot_management.get_info_key(bot_id).get_async() if bot_id else None)

    following_task = None
    if following_task_future:
      following_task = following_task_future.get_result()

    previous_task = None
    if previous_task_future:
      previous_task = previous_task_future.get_result()

    parent_task = None
    if parent_task_future:
      parent_task = parent_task_future.get_result()
    children_tasks = [c.get_result() for c in children_tasks_futures]

    cipd = None
    if request.properties.cipd_input:
      cipd = {
        'server': request.properties.cipd_input.server,
        'client_package': request.properties.cipd_input.client_package,
        'packages': self.packages_grouped_by_path(
            request.properties.cipd_input.packages),
      }

    cipd_pins = None
    if result.cipd_pins:
      cipd_pins = {
        'client_package': result.cipd_pins.client_package,
        'packages': self.packages_grouped_by_path(result.cipd_pins.packages),
      }

    params = {
      'bot': bot_future.get_result() if bot_future else None,
      'children_tasks': children_tasks,
      'cipd': cipd,
      'cipd_pins': cipd_pins,
      'is_admin': acl.is_admin(),
      'is_gae_admin': users.is_current_user_admin(),
      'is_privileged_user': acl.is_privileged_user(),
      'following_task': following_task,
      'full_appid': os.environ['APPLICATION_ID'],
      'host_url': self.request.host_url,
      'is_running': result.state == task_result.State.RUNNING,
      'parent_task': parent_task,
      'previous_task': previous_task,
      'request': request,
      'task': result,
      'try_link': '/task?id=%s' % task_id,
      'xsrf_token': self.generate_xsrf_token(),
    }
    self.response.write(template.render('swarming/user_task.html', params))


class OldTaskCancelHandler(BaseOldTaskHandler):
  """Cancel a task."""

  @auth.require(acl.is_user)
  def post(self, task_id):
    request, _, result = self.get_request_and_result(task_id)
    if not task_scheduler.cancel_task(request, result.key)[0]:
      self.abort(400, 'Task cancelation error')
    # The cancel button appears at both the /tasks and /task pages. Redirect to
    # the right place.
    if self.request.get('redirect_to', '') == 'listing':
      self.redirect('/user/tasks')
    else:
      self.redirect('/user/task/%s' % task_id)


class OldTaskRetryHandler(BaseOldTaskHandler):
  """Retries the same task but with new metadata.

  Retrying a task forcibly make it not idempotent so the task is unconditionally
  scheduled.
  """

  @auth.require(acl.is_user)
  def post(self, task_id):
    original_request, secret_bytes, _ = self.get_request_and_result(
        task_id, with_secret_bytes=True)
    # Retrying a task is essentially reusing the same task request as the
    # original one, but with new parameters.
    new_request = task_request.new_request_clone(
        original_request, secret_bytes,
        allow_high_priority=acl.can_schedule_high_priority_tasks())
    result_summary = task_scheduler.schedule_request(
      new_request, secret_bytes)
    self.redirect('/user/task/%s' % result_summary.task_id)


### Public pages.


class OldUIHandler(auth.AuthenticatingHandler):
  @auth.public
  def get(self):
    params = {
      'host_url': self.request.host_url,
      'is_admin': acl.is_admin(),
      'is_privileged_user': acl.is_privileged_user(),
      'is_user': acl.is_user(),
      'is_bootstrapper': acl.is_bootstrapper(),
      'bootstrap_token': '...',
      'mapreduce_jobs': [],
      'user_type': acl.get_user_type(),
      'xsrf_token': '',
    }
    if acl.is_admin():
      params['mapreduce_jobs'] = [
        {'id': job_id, 'name': job_def['job_name']}
        for job_id, job_def in mapreduce_jobs.MAPREDUCE_JOBS.iteritems()
      ]
      params['xsrf_token'] = self.generate_xsrf_token()
    if acl.is_bootstrapper():
      params['bootstrap_token'] = bot_code.generate_bootstrap_token()
    self.response.write(template.render('swarming/root.html', params))


class BotsListHandler(auth.AuthenticatingHandler):
  """Redirects to a list of known bots."""

  @auth.public
  def get(self):
    limit = int(self.request.get('limit', 100))

    dimensions = (
      l.strip() for l in self.request.get('dimensions', '').splitlines()
    )
    dimensions = [i for i in dimensions if i]

    new_ui_link = '/botlist?l=%d' % limit
    if dimensions:
      new_ui_link += '&f=' + '&f='.join(dimensions)

    self.redirect(new_ui_link)


class BotHandler(auth.AuthenticatingHandler):
  """Redirects to a page about the bot, including last tasks and events."""

  @auth.public
  def get(self, bot_id):
    self.redirect('/bot?id=%s' % bot_id)


### User accessible pages.


class TasksHandler(auth.AuthenticatingHandler):
  """Redirects to a list of all task requests."""

  @auth.public
  def get(self):
    limit = int(self.request.get('limit', 100))
    task_tags = [
      line for line in self.request.get('task_tag', '').splitlines() if line
    ]

    new_ui_link = '/tasklist?l=%d' % limit
    if task_tags:
      new_ui_link += '&f=' + '&f='.join(task_tags)

    self.redirect(new_ui_link)


class TaskHandler(auth.AuthenticatingHandler):
  """Redirects to a page containing task request and result."""

  @auth.public
  def get(self, task_id):
    self.redirect('/task?id=%s' % task_id)


class UIHandler(auth.AuthenticatingHandler):
  """Serves the landing page for the new UI of the requested page.

  This landing page is stamped with the OAuth 2.0 client id from the
  configuration."""
  @auth.public
  def get(self, page):
    if not page:
      page = 'swarming'

    params = {
      'client_id': config.settings().ui_client_id,
    }
    # Can cache for 1 week, because the only thing that would change in this
    # template is the oauth client id, which changes very infrequently.
    self.response.cache_control.no_cache = None
    self.response.cache_control.public = True
    self.response.cache_control.max_age = 604800
    try:
      self.response.write(template.render(
        'swarming/public_%s_index.html' % page, params))
    except template.TemplateNotFound:
      self.abort(404, 'Page not found.')


class WarmupHandler(webapp2.RequestHandler):
  def get(self):
    auth.warmup()
    bot_code.get_swarming_bot_zip(self.request.host_url)
    utils.get_module_version_list(None, None)
    self.response.headers['Content-Type'] = 'text/plain; charset=utf-8'
    self.response.write('ok')


class EmailHandler(webapp2.RequestHandler):
  """Blackhole any email sent."""
  def post(self, to):
    pass


def create_application(debug):
  template.bootstrap()
  utils.set_task_queue_module('default')

  routes = [
      # Frontend pages. They return HTML.
      # Public pages.
      ('/oldui', OldUIHandler),
      ('/stats', stats_gviz.StatsSummaryHandler),
      ('/<page:(bot|botlist|task|tasklist|)>', UIHandler),

      # Task pages. Redirects to Polymer UI
      ('/user/tasks', TasksHandler),
      ('/user/task/<task_id:[0-9a-fA-F]+>', TaskHandler),

      # Bot pages. Redirects to Polymer UI
      ('/restricted/bots', BotsListHandler),
      ('/restricted/bot/<bot_id:[^/]+>', BotHandler),

      # User pages. TODO(kjlubick): Remove on January 1, 2017
      ('/oldui/user/tasks', OldTasksHandler),
      ('/oldui/user/task/<task_id:[0-9a-fA-F]+>', OldTaskHandler),
      ('/oldui/user/task/<task_id:[0-9a-fA-F]+>/cancel', OldTaskCancelHandler),
      ('/oldui/user/task/<task_id:[0-9a-fA-F]+>/retry', OldTaskRetryHandler),

      # Privileged user pages. TODO(kjlubick): Remove on January 1, 2017
      ('/oldui/restricted/bots', OldBotsListHandler),
      ('/oldui/restricted/bot/<bot_id:[^/]+>', OldBotHandler),
      ('/oldui/restricted/bot/<bot_id:[^/]+>/delete', OldBotDeleteHandler),

      # Admin pages.
      ('/restricted/config', RestrictedConfigHandler),
      ('/restricted/cancel_pending', RestrictedCancelPendingHandler),
      ('/restricted/upload/bot_config', UploadBotConfigHandler),
      ('/restricted/upload/bootstrap', UploadBootstrapHandler),

      # Mapreduce related urls.
      (r'/restricted/launch_mapreduce', RestrictedLaunchMapReduceJob),

      # The new APIs:
      ('/swarming/api/v1/stats/summary/<resolution:[a-z]+>',
        stats_gviz.StatsGvizSummaryHandler),
      ('/swarming/api/v1/stats/dimensions/<dimensions:.+>/<resolution:[a-z]+>',
        stats_gviz.StatsGvizDimensionsHandler),

      ('/_ah/mail/<to:.+>', EmailHandler),
      ('/_ah/warmup', WarmupHandler),
  ]
  routes = [webapp2.Route(*i) for i in routes]

  # If running on a local dev server, allow bots to connect without prior
  # groups configuration. Useful when running smoke test.
  if utils.is_local_dev_server():
    acl.bootstrap_dev_server_acls()

  routes.extend(handlers_backend.get_routes())
  routes.extend(handlers_bot.get_routes())
  routes.extend(handlers_endpoints.get_routes())
  return webapp2.WSGIApplication(routes, debug=debug)
