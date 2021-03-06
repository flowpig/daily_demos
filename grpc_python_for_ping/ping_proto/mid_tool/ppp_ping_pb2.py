# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: ppp_ping.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='ppp_ping.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n\x0eppp_ping.proto\"?\n\rDoPingRequest\x12\x0e\n\x06schema\x18\x01 \x01(\x05\x12\r\n\x05users\x18\x02 \x01(\x05\x12\x0f\n\x07hostids\x18\x03 \x03(\x03\"\x1a\n\x0b\x44oPingReply\x12\x0b\n\x03key\x18\x01 \x01(\x05\x32\x43\n\x0fPPPsubPingServe\x12\x30\n\x0eSubmitWillPing\x12\x0e.DoPingRequest\x1a\x0c.DoPingReply\"\x00\x62\x06proto3')
)




_DOPINGREQUEST = _descriptor.Descriptor(
  name='DoPingRequest',
  full_name='DoPingRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='schema', full_name='DoPingRequest.schema', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='users', full_name='DoPingRequest.users', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hostids', full_name='DoPingRequest.hostids', index=2,
      number=3, type=3, cpp_type=2, label=3,
      has_default_value=False, default_value=[],
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=18,
  serialized_end=81,
)


_DOPINGREPLY = _descriptor.Descriptor(
  name='DoPingReply',
  full_name='DoPingReply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='DoPingReply.key', index=0,
      number=1, type=5, cpp_type=1, label=1,
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
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=83,
  serialized_end=109,
)

DESCRIPTOR.message_types_by_name['DoPingRequest'] = _DOPINGREQUEST
DESCRIPTOR.message_types_by_name['DoPingReply'] = _DOPINGREPLY
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

DoPingRequest = _reflection.GeneratedProtocolMessageType('DoPingRequest', (_message.Message,), dict(
  DESCRIPTOR = _DOPINGREQUEST,
  __module__ = 'ppp_ping_pb2'
  # @@protoc_insertion_point(class_scope:DoPingRequest)
  ))
_sym_db.RegisterMessage(DoPingRequest)

DoPingReply = _reflection.GeneratedProtocolMessageType('DoPingReply', (_message.Message,), dict(
  DESCRIPTOR = _DOPINGREPLY,
  __module__ = 'ppp_ping_pb2'
  # @@protoc_insertion_point(class_scope:DoPingReply)
  ))
_sym_db.RegisterMessage(DoPingReply)



_PPPSUBPINGSERVE = _descriptor.ServiceDescriptor(
  name='PPPsubPingServe',
  full_name='PPPsubPingServe',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=111,
  serialized_end=178,
  methods=[
  _descriptor.MethodDescriptor(
    name='SubmitWillPing',
    full_name='PPPsubPingServe.SubmitWillPing',
    index=0,
    containing_service=None,
    input_type=_DOPINGREQUEST,
    output_type=_DOPINGREPLY,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_PPPSUBPINGSERVE)

DESCRIPTOR.services_by_name['PPPsubPingServe'] = _PPPSUBPINGSERVE

# @@protoc_insertion_point(module_scope)
