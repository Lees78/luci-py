# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: infra_libs/ts_mon/protos/timestamp.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='infra_libs/ts_mon/protos/timestamp.proto',
  package='ts_mon.proto',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=b'\n(infra_libs/ts_mon/protos/timestamp.proto\x12\x0cts_mon.proto\"+\n\tTimestamp\x12\x0f\n\x07seconds\x18\x01 \x01(\x03\x12\r\n\x05nanos\x18\x02 \x01(\x05'
)




_TIMESTAMP = _descriptor.Descriptor(
  name='Timestamp',
  full_name='ts_mon.proto.Timestamp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='seconds', full_name='ts_mon.proto.Timestamp.seconds', index=0,
      number=1, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nanos', full_name='ts_mon.proto.Timestamp.nanos', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=58,
  serialized_end=101,
)

DESCRIPTOR.message_types_by_name['Timestamp'] = _TIMESTAMP
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Timestamp = _reflection.GeneratedProtocolMessageType('Timestamp', (_message.Message,), {
  'DESCRIPTOR' : _TIMESTAMP,
  '__module__' : 'infra_libs.ts_mon.protos.timestamp_pb2'
  # @@protoc_insertion_point(class_scope:ts_mon.proto.Timestamp)
  })
_sym_db.RegisterMessage(Timestamp)


# @@protoc_insertion_point(module_scope)
