# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: discord.proto

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
  name='discord.proto',
  package='discord',
  syntax='proto3',
  serialized_pb=_b('\n\rdiscord.proto\x12\x07\x64iscord\"3\n\x04User\x12\n\n\x02id\x18\x01 \x01(\x04\x12\x10\n\x08nickname\x18\x02 \x01(\t\x12\r\n\x05roles\x18\x03 \x03(\t\"?\n\x08\x42indCode\x12\x0c\n\x04\x63ode\x18\x01 \x01(\t\x12\x12\n\ncreated_at\x18\x02 \x01(\x01\x12\x11\n\texpire_at\x18\x03 \x01(\x01\"I\n\x12GetBindCodeRequest\x12\x1b\n\x04user\x18\x01 \x01(\x0b\x32\r.discord.User\x12\x16\n\x0e\x65xpire_timeout\x18\x02 \x01(\x01\"6\n\x13GetBindCodeResponse\x12\x1f\n\x04\x63ode\x18\x01 \x01(\x0b\x32\x11.discord.BindCode\"\x1a\n\x18\x44\x65\x62ugClearServiceRequest\"\x1b\n\x19\x44\x65\x62ugClearServiceResponseb\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_USER = _descriptor.Descriptor(
  name='User',
  full_name='discord.User',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='id', full_name='discord.User.id', index=0,
      number=1, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='nickname', full_name='discord.User.nickname', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='roles', full_name='discord.User.roles', index=2,
      number=3, type=9, cpp_type=9, label=3,
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
  serialized_start=26,
  serialized_end=77,
)


_BINDCODE = _descriptor.Descriptor(
  name='BindCode',
  full_name='discord.BindCode',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='discord.BindCode.code', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='created_at', full_name='discord.BindCode.created_at', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='expire_at', full_name='discord.BindCode.expire_at', index=2,
      number=3, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=79,
  serialized_end=142,
)


_GETBINDCODEREQUEST = _descriptor.Descriptor(
  name='GetBindCodeRequest',
  full_name='discord.GetBindCodeRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='user', full_name='discord.GetBindCodeRequest.user', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='expire_timeout', full_name='discord.GetBindCodeRequest.expire_timeout', index=1,
      number=2, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
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
  serialized_start=144,
  serialized_end=217,
)


_GETBINDCODERESPONSE = _descriptor.Descriptor(
  name='GetBindCodeResponse',
  full_name='discord.GetBindCodeResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='discord.GetBindCodeResponse.code', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
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
  serialized_start=219,
  serialized_end=273,
)


_DEBUGCLEARSERVICEREQUEST = _descriptor.Descriptor(
  name='DebugClearServiceRequest',
  full_name='discord.DebugClearServiceRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
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
  serialized_start=275,
  serialized_end=301,
)


_DEBUGCLEARSERVICERESPONSE = _descriptor.Descriptor(
  name='DebugClearServiceResponse',
  full_name='discord.DebugClearServiceResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
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
  serialized_start=303,
  serialized_end=330,
)

_GETBINDCODEREQUEST.fields_by_name['user'].message_type = _USER
_GETBINDCODERESPONSE.fields_by_name['code'].message_type = _BINDCODE
DESCRIPTOR.message_types_by_name['User'] = _USER
DESCRIPTOR.message_types_by_name['BindCode'] = _BINDCODE
DESCRIPTOR.message_types_by_name['GetBindCodeRequest'] = _GETBINDCODEREQUEST
DESCRIPTOR.message_types_by_name['GetBindCodeResponse'] = _GETBINDCODERESPONSE
DESCRIPTOR.message_types_by_name['DebugClearServiceRequest'] = _DEBUGCLEARSERVICEREQUEST
DESCRIPTOR.message_types_by_name['DebugClearServiceResponse'] = _DEBUGCLEARSERVICERESPONSE

User = _reflection.GeneratedProtocolMessageType('User', (_message.Message,), dict(
  DESCRIPTOR = _USER,
  __module__ = 'discord_pb2'
  # @@protoc_insertion_point(class_scope:discord.User)
  ))
_sym_db.RegisterMessage(User)

BindCode = _reflection.GeneratedProtocolMessageType('BindCode', (_message.Message,), dict(
  DESCRIPTOR = _BINDCODE,
  __module__ = 'discord_pb2'
  # @@protoc_insertion_point(class_scope:discord.BindCode)
  ))
_sym_db.RegisterMessage(BindCode)

GetBindCodeRequest = _reflection.GeneratedProtocolMessageType('GetBindCodeRequest', (_message.Message,), dict(
  DESCRIPTOR = _GETBINDCODEREQUEST,
  __module__ = 'discord_pb2'
  # @@protoc_insertion_point(class_scope:discord.GetBindCodeRequest)
  ))
_sym_db.RegisterMessage(GetBindCodeRequest)

GetBindCodeResponse = _reflection.GeneratedProtocolMessageType('GetBindCodeResponse', (_message.Message,), dict(
  DESCRIPTOR = _GETBINDCODERESPONSE,
  __module__ = 'discord_pb2'
  # @@protoc_insertion_point(class_scope:discord.GetBindCodeResponse)
  ))
_sym_db.RegisterMessage(GetBindCodeResponse)

DebugClearServiceRequest = _reflection.GeneratedProtocolMessageType('DebugClearServiceRequest', (_message.Message,), dict(
  DESCRIPTOR = _DEBUGCLEARSERVICEREQUEST,
  __module__ = 'discord_pb2'
  # @@protoc_insertion_point(class_scope:discord.DebugClearServiceRequest)
  ))
_sym_db.RegisterMessage(DebugClearServiceRequest)

DebugClearServiceResponse = _reflection.GeneratedProtocolMessageType('DebugClearServiceResponse', (_message.Message,), dict(
  DESCRIPTOR = _DEBUGCLEARSERVICERESPONSE,
  __module__ = 'discord_pb2'
  # @@protoc_insertion_point(class_scope:discord.DebugClearServiceResponse)
  ))
_sym_db.RegisterMessage(DebugClearServiceResponse)


# @@protoc_insertion_point(module_scope)
