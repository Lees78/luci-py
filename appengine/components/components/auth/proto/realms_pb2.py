# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: components/auth/proto/realms.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='components/auth/proto/realms.proto',
  package='components.auth.realms',
  syntax='proto3',
  serialized_options=b'Z:go.chromium.org/luci/server/auth/service/protocol;protocol',
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\"components/auth/proto/realms.proto\x12\x16\x63omponents.auth.realms\"\x85\x01\n\x06Realms\x12\x13\n\x0b\x61pi_version\x18\x01 \x01(\x03\x12\x37\n\x0bpermissions\x18\x02 \x03(\x0b\x32\".components.auth.realms.Permission\x12-\n\x06realms\x18\x03 \x03(\x0b\x32\x1d.components.auth.realms.Realm\",\n\nPermission\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x10\n\x08internal\x18\x02 \x01(\x08\"y\n\x05Realm\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x31\n\x08\x62indings\x18\x02 \x03(\x0b\x32\x1f.components.auth.realms.Binding\x12/\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32!.components.auth.realms.RealmData\"2\n\x07\x42inding\x12\x13\n\x0bpermissions\x18\x01 \x03(\r\x12\x12\n\nprincipals\x18\x02 \x03(\t\"\'\n\tRealmData\x12\x1a\n\x12\x65nforce_in_service\x18\x01 \x03(\tB<Z:go.chromium.org/luci/server/auth/service/protocol;protocolb\x06proto3'
)




_REALMS = _descriptor.Descriptor(
  name='Realms',
  full_name='components.auth.realms.Realms',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='api_version', full_name='components.auth.realms.Realms.api_version', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='permissions', full_name='components.auth.realms.Realms.permissions', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='realms', full_name='components.auth.realms.Realms.realms', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=63,
  serialized_end=196,
)


_PERMISSION = _descriptor.Descriptor(
  name='Permission',
  full_name='components.auth.realms.Permission',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='components.auth.realms.Permission.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='internal', full_name='components.auth.realms.Permission.internal', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=198,
  serialized_end=242,
)


_REALM = _descriptor.Descriptor(
  name='Realm',
  full_name='components.auth.realms.Realm',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='components.auth.realms.Realm.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='bindings', full_name='components.auth.realms.Realm.bindings', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='data', full_name='components.auth.realms.Realm.data', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=244,
  serialized_end=365,
)


_BINDING = _descriptor.Descriptor(
  name='Binding',
  full_name='components.auth.realms.Binding',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='permissions', full_name='components.auth.realms.Binding.permissions', index=0,
      number=1, type=13, cpp_type=3, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='principals', full_name='components.auth.realms.Binding.principals', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=367,
  serialized_end=417,
)


_REALMDATA = _descriptor.Descriptor(
  name='RealmData',
  full_name='components.auth.realms.RealmData',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='enforce_in_service', full_name='components.auth.realms.RealmData.enforce_in_service', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=419,
  serialized_end=458,
)

_REALMS.fields_by_name['permissions'].message_type = _PERMISSION
_REALMS.fields_by_name['realms'].message_type = _REALM
_REALM.fields_by_name['bindings'].message_type = _BINDING
_REALM.fields_by_name['data'].message_type = _REALMDATA
DESCRIPTOR.message_types_by_name['Realms'] = _REALMS
DESCRIPTOR.message_types_by_name['Permission'] = _PERMISSION
DESCRIPTOR.message_types_by_name['Realm'] = _REALM
DESCRIPTOR.message_types_by_name['Binding'] = _BINDING
DESCRIPTOR.message_types_by_name['RealmData'] = _REALMDATA
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Realms = _reflection.GeneratedProtocolMessageType('Realms', (_message.Message,), {
  'DESCRIPTOR' : _REALMS,
  '__module__' : 'components.auth.proto.realms_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.realms.Realms)
  })
_sym_db.RegisterMessage(Realms)

Permission = _reflection.GeneratedProtocolMessageType('Permission', (_message.Message,), {
  'DESCRIPTOR' : _PERMISSION,
  '__module__' : 'components.auth.proto.realms_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.realms.Permission)
  })
_sym_db.RegisterMessage(Permission)

Realm = _reflection.GeneratedProtocolMessageType('Realm', (_message.Message,), {
  'DESCRIPTOR' : _REALM,
  '__module__' : 'components.auth.proto.realms_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.realms.Realm)
  })
_sym_db.RegisterMessage(Realm)

Binding = _reflection.GeneratedProtocolMessageType('Binding', (_message.Message,), {
  'DESCRIPTOR' : _BINDING,
  '__module__' : 'components.auth.proto.realms_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.realms.Binding)
  })
_sym_db.RegisterMessage(Binding)

RealmData = _reflection.GeneratedProtocolMessageType('RealmData', (_message.Message,), {
  'DESCRIPTOR' : _REALMDATA,
  '__module__' : 'components.auth.proto.realms_pb2'
  # @@protoc_insertion_point(class_scope:components.auth.realms.RealmData)
  })
_sym_db.RegisterMessage(RealmData)


DESCRIPTOR._options = None
# @@protoc_insertion_point(module_scope)
