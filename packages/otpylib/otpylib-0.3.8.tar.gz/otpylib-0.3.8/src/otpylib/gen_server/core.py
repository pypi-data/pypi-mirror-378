"""
A generic server is an abstraction of a server loop built on top of the mailbox
module.

It is best used to build components that accept request from other components in
your application such as:

 - an in-memory key-value store
 - a TCP server handler
 - a finite state machine

There are 3 ways of sending messages to a generic server:

 - **cast:** send a message
 - **call:** send a message an wait for a response
 - directly to the mailbox

> **NB:** If a call returns an exception to the caller, the exception will be
> raised on the caller side.

.. code-block:: python
   :caption: Example

   from otpylib import gen_server, mailbox
   import types


   # Create module-like object for callbacks
   callbacks = types.SimpleNamespace()


   async def start():
       await gen_server.start(callbacks, name='kvstore')


   async def get(key):
       return await gen_server.call('kvstore', ('get', key))


   async def set(key, val):
       return await gen_server.call('kvstore', ('set', key, val))


   async def stop():
       await gen_server.cast('kvstore', 'stop')


   async def printstate():
       await mailbox.send('kvstore', 'printstate')

   # gen_server callbacks

   async def init(_init_arg):
       state = {}
       return state

   callbacks.init = init


   # optional
   async def terminate(reason, state):
       if reason is not None:
           print('An error occured:', reason)

       print('Exited with state:', state)

   callbacks.terminate = terminate


   # if not defined, the gen_server will stop with a NotImplementedError when
   # receiving a call
   async def handle_call(message, _caller, state):
       match message:
           case ('get', key):
               val = state.get(key, None)
               return (gen_server.Reply(payload=val), state)

           case ('set', key, val):
               prev = state.get(key, None)
               state[key] = val
               return (gen_server.Reply(payload=prev), state)

           case _:
               exc = NotImplementedError('unknown request')
               return (gen_server.Reply(payload=exc), state)

   callbacks.handle_call = handle_call


   # if not defined, the gen_server will stop with a NotImplementedError when
   # receiving a cast
   async def handle_cast(message, state):
       match message:
           case 'stop':
               return (gen_server.Stop(), state)

           case _:
               print('unknown request')
               return (gen_server.NoReply(), state)

   callbacks.handle_cast = handle_cast


   # optional
   async def handle_info(message, state):
       match message:
           case 'printstate':
               print(state)

           case _:
               pass

       return (gen_server.NoReply(), state)

   callbacks.handle_info = handle_info
"""

from typing import TypeVar, Union, Optional, Any, Tuple, Dict, Set
from types import ModuleType
import logging
import time
import uuid
from dataclasses import dataclass

import anyio
import anyio.abc

from otpylib import mailbox


State = TypeVar("State")

# Global registries for transparent restart support
_PENDING_CALLS: Dict[str, Dict[str, Any]] = {}  # Survives GenServer death
_GENSERVER_STATES: Dict[str, Dict[str, Any]] = {}  # State preservation by unique key
_CALL_COUNTER = 0  # For unique call IDs


class GenServerExited(Exception):
    """
    Raised when the generic server exited during a call.
    """


@dataclass
class _Loop:
    yes: bool


@dataclass
class _Raise:
    exc: BaseException


Continuation = Union[_Loop, _Raise]


@dataclass
class Reply:
    """
    Return an instance of this class to send a reply to the caller.
    """

    payload: Any  #: The response to send back


@dataclass
class NoReply:
    """
    Return an instance of this class to not send a reply to the caller.
    """


@dataclass
class Stop:
    """
    Return an instance of this class to stop the generic server.
    """

    reason: Optional[BaseException] = (
        None  #: Eventual exception that caused the gen_server to stop
    )


@dataclass
class _CallMessage:
    source: anyio.abc.ObjectSendStream
    payload: Any
    call_id: Optional[str] = None  # Optional for enhanced tracking


@dataclass
class _CastMessage:
    payload: Any


def _generate_state_key(name: Optional[str], supervisor_context: Optional[str] = None) -> Optional[str]:
    """
    Generate a unique state storage key.
    
    Returns None if state recovery should not be enabled (no name and no context).
    """
    if supervisor_context:
        # For supervised gen_servers, include supervisor context
        if name:
            return f"{supervisor_context}:{name}"
        else:
            return f"{supervisor_context}:anonymous"
    elif name:
        # Standalone gen_server with name
        return f"standalone:{name}"
    else:
        # Anonymous gen_server without supervisor - no state recovery
        return None


async def start(
    module: ModuleType,
    init_arg: Optional[Any] = None,
    name: Optional[str] = None,
    _recovered_state: Optional[Dict[str, Any]] = None,  # For direct state injection
    _supervisor_context: Optional[str] = None,  # For unique state key generation
    *,
    task_status: anyio.abc.TaskStatus,
) -> None:
    """
    Starts the generic server loop.

    :param module: Module containing the generic server's callbacks
    :param init_arg: Optional argument passed to the `init` callback
    :param name: Optional name to use to register the generic server's mailbox
    :param _recovered_state: Internal parameter for direct state recovery
    :param _supervisor_context: Internal parameter for supervisor-based state recovery
    :param task_status: Task status for structured concurrency coordination

    :raises otpylib.mailbox.NameAlreadyExist: If the `name` was already registered
    :raises Exception: If the generic server terminated with a non-null reason
    """

    await _loop(module, init_arg, name, _recovered_state, _supervisor_context, task_status)


async def call(
    name_or_mid: Union[str, mailbox.MailboxID],
    payload: Any,
    timeout: Optional[float] = None,
) -> Any:
    """
    Send a request to the generic server and wait for a response.

    This function creates a temporary bi-directional channel. The writer is
    passed to the `handle_call` function and is used to send the response back
    to the caller.

    :param name_or_mid: The generic server's mailbox identifier
    :param payload: The message to send to the generic server
    :param timeout: Optional timeout after which this function fails
    :returns: The response from the generic server
    :raises GenServerExited: If the generic server exited after handling the call
    :raises Exception: If the response is an exception

    """
    global _CALL_COUNTER
    
    # Generate unique call ID for tracking
    _CALL_COUNTER += 1
    call_id = f"call_{_CALL_COUNTER}_{uuid.uuid4().hex[:8]}"
    
    # Create response channel with buffer to avoid immediate closure issues
    send_stream, receive_stream = anyio.create_memory_object_stream[Union[Exception, Any]](1)
    
    # Register call for potential recovery
    _PENDING_CALLS[call_id] = {
        'send_stream': send_stream,
        'payload': payload,
        'name_or_mid': name_or_mid,
        'timestamp': time.time(),
    }
    
    # Send message with both stream and call ID
    message = _CallMessage(source=send_stream, payload=payload, call_id=call_id)
    await mailbox.send(name_or_mid, message)

    try:
        if timeout is not None:
            with anyio.move_on_after(timeout) as cancel_scope:
                val = await receive_stream.receive()
                
            if cancel_scope.cancelled_caught:
                raise TimeoutError("Gen server call timed out")
        else:
            val = await receive_stream.receive()

        if isinstance(val, Exception):
            raise val

        return val

    finally:
        # Clean up registration
        _PENDING_CALLS.pop(call_id, None)
        await send_stream.aclose()
        await receive_stream.aclose()


async def cast(
    name_or_mid: Union[str, mailbox.MailboxID],
    payload: Any,
) -> None:
    """
    Send a message to the generic server without expecting a response.

    :param name_or_mid: The generic server's mailbox identifier
    :param payload: The message to send
    """

    message = _CastMessage(payload=payload)
    await mailbox.send(name_or_mid, message)


async def reply(caller: anyio.abc.ObjectSendStream, response: Any) -> None:
    """
    The `handle_call` callback can start a background task to handle a slow
    request and return a `NoReply` instance. Use this function in the background
    task to send the response to the caller at a later time.

    :param caller: The caller SendStream to use to send the response
    :param response: The response to send back to the caller

    .. code-block:: python
       :caption: Example

       from otpylib import gen_server, supervisor, dynamic_supervisor
       import anyio


       async def slow_task(message, caller):
           # do stuff with message
           await gen_server.reply(caller, response)


       async def handle_call(message, caller, state):
           await dynamic_supervisor.start_child(
               'slow-task-pool',
               supervisor.child_spec(
                   id='some-slow-task',
                   task=slow_task,
                   args=[message, caller],
                   restart=supervisor.restart_strategy.TEMPORARY,
               ),
           )

           return (gen_server.NoReply(), state)
    """
    
    try:
        await caller.send(response)
    except (anyio.ClosedResourceError, anyio.BrokenResourceError):
        # Caller timed out or disconnected, that's OK
        pass


async def _loop(
    module: ModuleType,
    init_arg: Optional[Any],
    name: Optional[str],
    _recovered_state: Optional[Dict[str, Any]],
    _supervisor_context: Optional[str],
    task_status: anyio.abc.TaskStatus,
) -> None:
    # Generate unique state key if applicable
    state_key = _generate_state_key(name, _supervisor_context)
    
    async with mailbox.open(name) as mid:
        processing_calls: Set[str] = set()  # Track in-flight calls
        
        try:
            # Initialize or recover state
            if _recovered_state is not None:
                # Direct state injection provided
                state = _recovered_state['state']
                pending_calls = _recovered_state.get('pending_calls', [])
                
                # Re-inject pending calls into mailbox for reprocessing
                for call_id in pending_calls:
                    if call_id in _PENDING_CALLS:
                        call_info = _PENDING_CALLS[call_id]
                        # Re-send the original message
                        message = _CallMessage(
                            source=call_info['send_stream'],
                            payload=call_info['payload'],
                            call_id=call_id
                        )
                        await mailbox.send(mid, message)
                
                # Optional: notify module of recovery
                if hasattr(module, 'on_recovery'):
                    state = await module.on_recovery(state)
                    
            elif state_key and state_key in _GENSERVER_STATES:
                # Check for auto-saved state
                saved = _GENSERVER_STATES[state_key]
                state = saved['state']
                pending_calls = saved.get('pending_calls', [])
                
                # Re-inject pending calls
                for call_id in pending_calls:
                    if call_id in _PENDING_CALLS:
                        call_info = _PENDING_CALLS[call_id]
                        message = _CallMessage(
                            source=call_info['send_stream'],
                            payload=call_info['payload'],
                            call_id=call_id
                        )
                        await mailbox.send(mid, message)
                
                # Clear the saved state now that we've recovered
                del _GENSERVER_STATES[state_key]
                
                # Optional recovery callback
                if hasattr(module, 'on_recovery'):
                    state = await module.on_recovery(state)
            else:
                # Normal initialization
                state = await _init(module, init_arg)
            
            # Signal that the gen_server is ready to handle messages
            task_status.started()
            
            looping = True

            while looping:
                message = await mailbox.receive(mid)

                match message:
                    case _CallMessage(source, payload, call_id):
                        if call_id:
                            processing_calls.add(call_id)
                        continuation, state = await _handle_call(
                            module, payload, source, state
                        )
                        if call_id:
                            processing_calls.discard(call_id)

                    case _CastMessage(payload):
                        continuation, state = await _handle_cast(module, payload, state)

                    case _:
                        continuation, state = await _handle_info(module, message, state)

                match continuation:
                    case _Loop(yes=False):
                        looping = False

                    case _Loop(yes=True):
                        looping = True

                    case _Raise(exc=err):
                        raise err

        except Exception as err:
            # Save state for potential restart if we have a state key
            if state_key:
                _GENSERVER_STATES[state_key] = {
                    'state': state,
                    'pending_calls': list(processing_calls),
                    'timestamp': time.time(),
                }
            await _terminate(module, err, state)
            raise err from None

        else:
            # Clean shutdown - clear saved state if exists
            if state_key and state_key in _GENSERVER_STATES:
                del _GENSERVER_STATES[state_key]
            await _terminate(module, None, state)


async def _init(module: ModuleType, init_arg: Any) -> State:
    return await module.init(init_arg)


async def _terminate(
    module: ModuleType,
    reason: Optional[BaseException],
    state: State,
) -> None:
    handler = getattr(module, "terminate", None)
    if handler is not None:
        await handler(reason, state)

    elif reason is not None:
        logger = logging.getLogger(f"otpylib.gen_server.{module.__name__}")
        logger.exception("Gen server terminated with exception", exc_info=reason)


async def _handle_call(
    module: ModuleType,
    message: Any,
    source: anyio.abc.ObjectSendStream,
    state: State,
) -> Tuple[Continuation, State]:
    handler = getattr(module, "handle_call", None)
    if handler is None:
        raise NotImplementedError(f"{module.__name__}.handle_call")

    result = await handler(message, source, state)
    continuation: Union[_Loop, _Raise]

    match result:
        case (Reply(payload), new_state):
            state = new_state
            await reply(source, payload)
            continuation = _Loop(yes=True)

        case (NoReply(), new_state):
            state = new_state
            continuation = _Loop(yes=True)

        case (Stop(reason), new_state):
            state = new_state
            await reply(source, GenServerExited())

            if reason is not None:
                continuation = _Raise(reason)
            else:
                continuation = _Loop(yes=False)

        case _:
            raise TypeError(
                f"{module.__name__}.handle_call did not return a valid value"
            )

    return continuation, state


async def _handle_cast(
    module: ModuleType,
    message: Any,
    state: State,
) -> Tuple[Continuation, State]:
    handler = getattr(module, "handle_cast", None)
    if handler is None:
        raise NotImplementedError(f"{module.__name__}.handle_cast")

    result = await handler(message, state)
    continuation: Union[_Loop, _Raise]

    match result:
        case (NoReply(), new_state):
            state = new_state
            continuation = _Loop(yes=True)

        case (Stop(reason), new_state):
            state = new_state

            if reason is not None:
                continuation = _Raise(reason)
            else:
                continuation = _Loop(yes=False)

        case _:
            raise TypeError(
                f"{module.__name__}.handle_cast did not return a valid value"
            )

    return continuation, state


async def _handle_info(
    module: ModuleType,
    message: Any,
    state: State,
) -> Tuple[Continuation, State]:
    handler = getattr(module, "handle_info", None)
    if handler is None:
        return _Loop(yes=True), state

    result = await handler(message, state)
    continuation: Union[_Loop, _Raise]

    match result:
        case (NoReply(), new_state):
            state = new_state
            continuation = _Loop(yes=True)

        case (Stop(reason), new_state):
            state = new_state

            if reason is not None:
                continuation = _Raise(reason)
            else:
                continuation = _Loop(yes=False)

        case _:
            raise TypeError(
                f"{module.__name__}.handle_info did not return a valid value"
            )

    return continuation, state


# Public function to enable supervisor integration
def get_saved_state(state_key: str) -> Optional[Dict[str, Any]]:
    """
    Get saved state for a GenServer by its unique state key.
    
    :param state_key: The unique state key
    :returns: Saved state dict or None if not found
    """
    return _GENSERVER_STATES.get(state_key)


def clear_saved_state(state_key: str) -> None:
    """
    Clear saved state for a GenServer.
    
    :param state_key: The unique state key
    """
    if state_key in _GENSERVER_STATES:
        del _GENSERVER_STATES[state_key]
