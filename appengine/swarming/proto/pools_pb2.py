# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pools.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pools.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x0bpools.proto\"\xc6\x01\n\x08PoolsCfg\x12\x13\n\x04pool\x18\x01 \x03(\x0b\x32\x05.Pool\x12\x1c\n\x14\x66orbid_unknown_pools\x18\x02 \x01(\x08\x12$\n\rtask_template\x18\x03 \x03(\x0b\x32\r.TaskTemplate\x12\x39\n\x18task_template_deployment\x18\x04 \x03(\x0b\x32\x17.TaskTemplateDeployment\x12&\n\x0e\x62ot_monitoring\x18\x05 \x03(\x0b\x32\x0e.BotMonitoring\"\xa7\x02\n\x04Pool\x12\x0c\n\x04name\x18\x01 \x03(\t\x12\x0e\n\x06owners\x18\x02 \x03(\t\x12\x1f\n\nschedulers\x18\x03 \x01(\x0b\x32\x0b.Schedulers\x12\x1f\n\x17\x61llowed_service_account\x18\x04 \x03(\t\x12%\n\x1d\x61llowed_service_account_group\x18\x05 \x03(\t\x12\"\n\x18task_template_deployment\x18\x06 \x01(\tH\x00\x12\x42\n\x1ftask_template_deployment_inline\x18\x07 \x01(\x0b\x32\x17.TaskTemplateDeploymentH\x00\x12\x16\n\x0e\x62ot_monitoring\x18\x08 \x01(\tB\x18\n\x16task_deployment_scheme\"Y\n\nSchedulers\x12\x0c\n\x04user\x18\x01 \x03(\t\x12\r\n\x05group\x18\x02 \x03(\t\x12.\n\x12trusted_delegation\x18\x03 \x03(\x0b\x32\x12.TrustedDelegation\"p\n\x11TrustedDelegation\x12\x0f\n\x07peer_id\x18\x01 \x01(\t\x12\x32\n\x0erequire_any_of\x18\x02 \x01(\x0b\x32\x1a.TrustedDelegation.TagList\x1a\x16\n\x07TagList\x12\x0b\n\x03tag\x18\x01 \x03(\t\"\xcd\x02\n\x0cTaskTemplate\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07include\x18\x02 \x03(\t\x12\'\n\x05\x63\x61\x63he\x18\x03 \x03(\x0b\x32\x18.TaskTemplate.CacheEntry\x12/\n\x0c\x63ipd_package\x18\x04 \x03(\x0b\x32\x19.TaskTemplate.CipdPackage\x12\x1e\n\x03\x65nv\x18\x05 \x03(\x0b\x32\x11.TaskTemplate.Env\x1a(\n\nCacheEntry\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0c\n\x04path\x18\x02 \x01(\t\x1a\x39\n\x0b\x43ipdPackage\x12\x0c\n\x04path\x18\x01 \x01(\t\x12\x0b\n\x03pkg\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\x1a?\n\x03\x45nv\x12\x0b\n\x03var\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\x12\x0e\n\x06prefix\x18\x03 \x03(\t\x12\x0c\n\x04soft\x18\x04 \x01(\x08\"y\n\x16TaskTemplateDeployment\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x1b\n\x04prod\x18\x02 \x01(\x0b\x32\r.TaskTemplate\x12\x1d\n\x06\x63\x61nary\x18\x03 \x01(\x0b\x32\r.TaskTemplate\x12\x15\n\rcanary_chance\x18\x04 \x01(\x05\"4\n\rBotMonitoring\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x15\n\rdimension_key\x18\x02 \x03(\tb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_POOLSCFG = _descriptor.Descriptor(
  name='PoolsCfg',
  full_name='PoolsCfg',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pool', full_name='PoolsCfg.pool', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='forbid_unknown_pools', full_name='PoolsCfg.forbid_unknown_pools', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template', full_name='PoolsCfg.task_template', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template_deployment', full_name='PoolsCfg.task_template_deployment', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_monitoring', full_name='PoolsCfg.bot_monitoring', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=16,
  serialized_end=214,
)


_POOL = _descriptor.Descriptor(
  name='Pool',
  full_name='Pool',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='Pool.name', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='owners', full_name='Pool.owners', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='schedulers', full_name='Pool.schedulers', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='allowed_service_account', full_name='Pool.allowed_service_account', index=3,
      number=4, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='allowed_service_account_group', full_name='Pool.allowed_service_account_group', index=4,
      number=5, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template_deployment', full_name='Pool.task_template_deployment', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='task_template_deployment_inline', full_name='Pool.task_template_deployment_inline', index=6,
      number=7, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='bot_monitoring', full_name='Pool.bot_monitoring', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='task_deployment_scheme', full_name='Pool.task_deployment_scheme',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=217,
  serialized_end=512,
)


_SCHEDULERS = _descriptor.Descriptor(
  name='Schedulers',
  full_name='Schedulers',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user', full_name='Schedulers.user', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='group', full_name='Schedulers.group', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='trusted_delegation', full_name='Schedulers.trusted_delegation', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=514,
  serialized_end=603,
)


_TRUSTEDDELEGATION_TAGLIST = _descriptor.Descriptor(
  name='TagList',
  full_name='TrustedDelegation.TagList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tag', full_name='TrustedDelegation.TagList.tag', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=695,
  serialized_end=717,
)

_TRUSTEDDELEGATION = _descriptor.Descriptor(
  name='TrustedDelegation',
  full_name='TrustedDelegation',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='peer_id', full_name='TrustedDelegation.peer_id', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='require_any_of', full_name='TrustedDelegation.require_any_of', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TRUSTEDDELEGATION_TAGLIST, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=605,
  serialized_end=717,
)


_TASKTEMPLATE_CACHEENTRY = _descriptor.Descriptor(
  name='CacheEntry',
  full_name='TaskTemplate.CacheEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='TaskTemplate.CacheEntry.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='path', full_name='TaskTemplate.CacheEntry.path', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=889,
  serialized_end=929,
)

_TASKTEMPLATE_CIPDPACKAGE = _descriptor.Descriptor(
  name='CipdPackage',
  full_name='TaskTemplate.CipdPackage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='path', full_name='TaskTemplate.CipdPackage.path', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pkg', full_name='TaskTemplate.CipdPackage.pkg', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='version', full_name='TaskTemplate.CipdPackage.version', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=931,
  serialized_end=988,
)

_TASKTEMPLATE_ENV = _descriptor.Descriptor(
  name='Env',
  full_name='TaskTemplate.Env',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='var', full_name='TaskTemplate.Env.var', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='TaskTemplate.Env.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='prefix', full_name='TaskTemplate.Env.prefix', index=2,
      number=3, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='soft', full_name='TaskTemplate.Env.soft', index=3,
      number=4, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=990,
  serialized_end=1053,
)

_TASKTEMPLATE = _descriptor.Descriptor(
  name='TaskTemplate',
  full_name='TaskTemplate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='TaskTemplate.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='include', full_name='TaskTemplate.include', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cache', full_name='TaskTemplate.cache', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='cipd_package', full_name='TaskTemplate.cipd_package', index=3,
      number=4, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='env', full_name='TaskTemplate.env', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TASKTEMPLATE_CACHEENTRY, _TASKTEMPLATE_CIPDPACKAGE, _TASKTEMPLATE_ENV, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=720,
  serialized_end=1053,
)


_TASKTEMPLATEDEPLOYMENT = _descriptor.Descriptor(
  name='TaskTemplateDeployment',
  full_name='TaskTemplateDeployment',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='TaskTemplateDeployment.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='prod', full_name='TaskTemplateDeployment.prod', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='canary', full_name='TaskTemplateDeployment.canary', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='canary_chance', full_name='TaskTemplateDeployment.canary_chance', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1055,
  serialized_end=1176,
)


_BOTMONITORING = _descriptor.Descriptor(
  name='BotMonitoring',
  full_name='BotMonitoring',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='BotMonitoring.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='dimension_key', full_name='BotMonitoring.dimension_key', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1178,
  serialized_end=1230,
)

_POOLSCFG.fields_by_name['pool'].message_type = _POOL
_POOLSCFG.fields_by_name['task_template'].message_type = _TASKTEMPLATE
_POOLSCFG.fields_by_name['task_template_deployment'].message_type = _TASKTEMPLATEDEPLOYMENT
_POOLSCFG.fields_by_name['bot_monitoring'].message_type = _BOTMONITORING
_POOL.fields_by_name['schedulers'].message_type = _SCHEDULERS
_POOL.fields_by_name['task_template_deployment_inline'].message_type = _TASKTEMPLATEDEPLOYMENT
_POOL.oneofs_by_name['task_deployment_scheme'].fields.append(
  _POOL.fields_by_name['task_template_deployment'])
_POOL.fields_by_name['task_template_deployment'].containing_oneof = _POOL.oneofs_by_name['task_deployment_scheme']
_POOL.oneofs_by_name['task_deployment_scheme'].fields.append(
  _POOL.fields_by_name['task_template_deployment_inline'])
_POOL.fields_by_name['task_template_deployment_inline'].containing_oneof = _POOL.oneofs_by_name['task_deployment_scheme']
_SCHEDULERS.fields_by_name['trusted_delegation'].message_type = _TRUSTEDDELEGATION
_TRUSTEDDELEGATION_TAGLIST.containing_type = _TRUSTEDDELEGATION
_TRUSTEDDELEGATION.fields_by_name['require_any_of'].message_type = _TRUSTEDDELEGATION_TAGLIST
_TASKTEMPLATE_CACHEENTRY.containing_type = _TASKTEMPLATE
_TASKTEMPLATE_CIPDPACKAGE.containing_type = _TASKTEMPLATE
_TASKTEMPLATE_ENV.containing_type = _TASKTEMPLATE
_TASKTEMPLATE.fields_by_name['cache'].message_type = _TASKTEMPLATE_CACHEENTRY
_TASKTEMPLATE.fields_by_name['cipd_package'].message_type = _TASKTEMPLATE_CIPDPACKAGE
_TASKTEMPLATE.fields_by_name['env'].message_type = _TASKTEMPLATE_ENV
_TASKTEMPLATEDEPLOYMENT.fields_by_name['prod'].message_type = _TASKTEMPLATE
_TASKTEMPLATEDEPLOYMENT.fields_by_name['canary'].message_type = _TASKTEMPLATE
DESCRIPTOR.message_types_by_name['PoolsCfg'] = _POOLSCFG
DESCRIPTOR.message_types_by_name['Pool'] = _POOL
DESCRIPTOR.message_types_by_name['Schedulers'] = _SCHEDULERS
DESCRIPTOR.message_types_by_name['TrustedDelegation'] = _TRUSTEDDELEGATION
DESCRIPTOR.message_types_by_name['TaskTemplate'] = _TASKTEMPLATE
DESCRIPTOR.message_types_by_name['TaskTemplateDeployment'] = _TASKTEMPLATEDEPLOYMENT
DESCRIPTOR.message_types_by_name['BotMonitoring'] = _BOTMONITORING

PoolsCfg = _reflection.GeneratedProtocolMessageType('PoolsCfg', (_message.Message,), dict(
  DESCRIPTOR = _POOLSCFG,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:PoolsCfg)
  ))
_sym_db.RegisterMessage(PoolsCfg)

Pool = _reflection.GeneratedProtocolMessageType('Pool', (_message.Message,), dict(
  DESCRIPTOR = _POOL,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:Pool)
  ))
_sym_db.RegisterMessage(Pool)

Schedulers = _reflection.GeneratedProtocolMessageType('Schedulers', (_message.Message,), dict(
  DESCRIPTOR = _SCHEDULERS,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:Schedulers)
  ))
_sym_db.RegisterMessage(Schedulers)

TrustedDelegation = _reflection.GeneratedProtocolMessageType('TrustedDelegation', (_message.Message,), dict(

  TagList = _reflection.GeneratedProtocolMessageType('TagList', (_message.Message,), dict(
    DESCRIPTOR = _TRUSTEDDELEGATION_TAGLIST,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:TrustedDelegation.TagList)
    ))
  ,
  DESCRIPTOR = _TRUSTEDDELEGATION,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:TrustedDelegation)
  ))
_sym_db.RegisterMessage(TrustedDelegation)
_sym_db.RegisterMessage(TrustedDelegation.TagList)

TaskTemplate = _reflection.GeneratedProtocolMessageType('TaskTemplate', (_message.Message,), dict(

  CacheEntry = _reflection.GeneratedProtocolMessageType('CacheEntry', (_message.Message,), dict(
    DESCRIPTOR = _TASKTEMPLATE_CACHEENTRY,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:TaskTemplate.CacheEntry)
    ))
  ,

  CipdPackage = _reflection.GeneratedProtocolMessageType('CipdPackage', (_message.Message,), dict(
    DESCRIPTOR = _TASKTEMPLATE_CIPDPACKAGE,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:TaskTemplate.CipdPackage)
    ))
  ,

  Env = _reflection.GeneratedProtocolMessageType('Env', (_message.Message,), dict(
    DESCRIPTOR = _TASKTEMPLATE_ENV,
    __module__ = 'pools_pb2'
    # @@protoc_insertion_point(class_scope:TaskTemplate.Env)
    ))
  ,
  DESCRIPTOR = _TASKTEMPLATE,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:TaskTemplate)
  ))
_sym_db.RegisterMessage(TaskTemplate)
_sym_db.RegisterMessage(TaskTemplate.CacheEntry)
_sym_db.RegisterMessage(TaskTemplate.CipdPackage)
_sym_db.RegisterMessage(TaskTemplate.Env)

TaskTemplateDeployment = _reflection.GeneratedProtocolMessageType('TaskTemplateDeployment', (_message.Message,), dict(
  DESCRIPTOR = _TASKTEMPLATEDEPLOYMENT,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:TaskTemplateDeployment)
  ))
_sym_db.RegisterMessage(TaskTemplateDeployment)

BotMonitoring = _reflection.GeneratedProtocolMessageType('BotMonitoring', (_message.Message,), dict(
  DESCRIPTOR = _BOTMONITORING,
  __module__ = 'pools_pb2'
  # @@protoc_insertion_point(class_scope:BotMonitoring)
  ))
_sym_db.RegisterMessage(BotMonitoring)


# @@protoc_insertion_point(module_scope)