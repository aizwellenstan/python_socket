import socket

from asyncio import _overlapped

import struct

listen_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=socket.IPPROTO_IP)

listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

listen_sock.bind(('0.0.0.0', 9000))

listen_sock.listen(0)

NULL = 0

concurrency=0xffffffff

_iocp = _overlapped.CreateIoCompletionPort(_overlapped.INVALID_HANDLE_VALUE, NULL, 0, concurrency)

_overlapped.CreateIoCompletionPort(listen_sock.fileno(), _iocp, 0, 0)

conn_sock = socket.socket(listen_sock.family)

conn_sock.settimeout(0)

ov = _overlapped.Overlapped(NULL)

ov.AcceptEx(listen_sock.fileno(), conn_sock.fileno())

def on_accepted():

buf = struct.pack('@P', listen_sock.fileno())

conn_sock.setsockopt(socket.SOL_SOCKET, _overlapped.SO_UPDATE_ACCEPT_CONTEXT, buf)

conn_sock.settimeout(listen_sock.gettimeout())

print('connected from %s:%s' % conn_sock.getpeername())

return conn_sock, conn_sock.getpeername()

callback_map = {}

if ov.pending:

callback_map[ov.address] = on_accepted

else:

on_accepted()

while True:

# wait maximum 1 second

status = _overlapped.GetQueuedCompletionStatus(_iocp, 1000)

if status is None:

continue # try again

err, transferred, key, address = status

callback = callback_map[address]

callback()

break
