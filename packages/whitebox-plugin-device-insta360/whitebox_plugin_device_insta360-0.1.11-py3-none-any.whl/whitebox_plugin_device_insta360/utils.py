import os
import time
import logging
import subprocess
import queue
from pathlib import Path

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from utils.functional import wrapped_partial


logger = logging.getLogger(__name__)

channel_layer = get_channel_layer()


# region handling


def _prepare_ffmpeg_command(
    input_file=None,
    input_stdin=False,
    output_file=None,
    output_stdout=False,
    width=1440,
    height=720,
):
    if not input_file and not input_stdin:
        raise ValueError("Either input_file or input_stdin must be provided")

    if input_file and input_stdin:
        raise ValueError("Provide only one of input_file or input_stdin")

    if not output_file and not output_stdout:
        raise ValueError("Either output_file or output_stdout must be provided")

    ffmpeg_input = input_file if input_file else "pipe:0"

    command = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-threads",
        "1",
        "-filter_complex_threads",
        "8",
        # Input side
        "-fflags",
        "+nobuffer",  # lower latency
        "-f",
        "h264",  # raw Annex-B H.264 input
        "-i",
        ffmpeg_input,
        # Processing
        # "-vf",
        "-filter_complex",
        f"[0:v]scale={width}:{height},v360=dfisheye:e:ih_fov=193:iv_fov=193[out]",
        # Output side: fragmented MP4 for MSE (init segment + moof/mdat fragments)
        "-map",
        "[out]",
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-tune",
        "zerolatency",
        "-pix_fmt",
        "yuv420p",
        "-profile:v",
        "baseline",
        "-level",
        "3.1",
        "-x264-params",
        "bframes=0:keyint=60:min-keyint=60:scenecut=0",
        "-movflags",
        "+frag_keyframe+empty_moov+default_base_moof+separate_moof",
        "-frag_duration",
        "500000",  # ~0.5s
        "-an",
        "-f",
        "mp4",
        "pipe:1",
    ]

    return command


def start_ffmpeg_process(
    input_file=None,
    input_stdin=False,
    output_file=None,
    output_stdout=False,
    width=1440,
    height=720,
):
    command = _prepare_ffmpeg_command(
        input_file=input_file,
        input_stdin=input_stdin,
        output_file=output_file,
        output_stdout=output_stdout,
        width=width,
        height=height,
    )

    print(f"Running ffmpeg command:\n{' '.join(command)}")
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE if input_stdin else None,
        stdout=subprocess.PIPE if output_stdout else None,
        stderr=subprocess.PIPE,
    )
    return process


# endregion handling


# region streaming


async def _base_video_stream_handler(
    content: bytes,
    queue: "queue.Queue[bytes]",
    **kwargs,
):
    queue.put(content)


def prepare_stream_handler(queue):
    return wrapped_partial(
        _base_video_stream_handler,
        queue=queue,
    )


# endregion streaming


# region processing


def _send_to_frontend(type_, content: bytes):
    # Use the channel layer to send the content
    send_coro = channel_layer.group_send
    wrapped_send = async_to_sync(send_coro)
    # print('Sending content to frontend')
    wrapped_send(
        "video_stream",
        {
            "type": type_,
            "content": content,
        },
    )


def _readable(fp):
    import select

    try:
        r, _, _ = select.select([fp], [], [], 0)
        return bool(r)
    except Exception:
        return False


def _parse_box_len(b: memoryview, off: int):
    import struct

    if off + 8 > len(b):
        return None
    size = struct.unpack_from(">I", b, off)[0]
    typ = bytes(b[off + 4 : off + 8]).decode("ascii", "ignore")
    if size == 1:
        if off + 16 > len(b):
            return None
        size = struct.unpack_from(">Q", b, off + 8)[0]
        hdr = 16
    else:
        hdr = 8
    if size < hdr:
        return None
    if off + size > len(b):
        return None
    return size, typ


def _maybe_resend_init_segment(state):
    init_segment = state["init_segment"]

    if not init_segment:
        return

    now = time.time()
    last_init_sent = state["last_init_sent"] or 0

    if (now - last_init_sent) >= 2.0:
        _send_to_frontend(
            "stream.init",
            state["init_segment"],
        )
        state["last_init_sent"] = now


def emit(type_, data: bytes):
    _send_to_frontend(type_, data)


def _drain_fmp4(ffmpeg_process, state):
    if _readable(ffmpeg_process.stdout):
        fd = ffmpeg_process.stdout.fileno()
        while True:
            try:
                chunk = os.read(fd, 64 * 1024)
                if not chunk:
                    break
                state["buf"].extend(chunk)
            except BlockingIOError:
                break

    # Always drain stderr to avoid blocking
    if _readable(ffmpeg_process.stderr):
        try:
            _ = ffmpeg_process.stderr.read()
        except Exception:
            pass

    mv = memoryview(state["buf"])  # zero-copy slicing for parsing
    off = 0

    if not state["init_segment"]:
        # Expect ftyp + moov at the start
        parts = []
        cur = off
        for expected in ("ftyp", "moov"):
            box = _parse_box_len(mv, cur)
            if not box:
                return  # need more bytes
            size, typ = box
            if typ != expected:
                # Unexpected; drop until a plausible ftyp
                off = 0
                # try to resync by discarding one byte
                state["buf"] = bytearray(mv[1:].tobytes())
                return
            parts.append(mv[cur : cur + size].tobytes())
            cur += size

        # We have both boxes fully
        init_segment = b"".join(parts)

        emit("stream.init", init_segment)
        off = cur

        state["init_segment"] = init_segment
    else:
        _maybe_resend_init_segment(state)

        # Emit moof+mdat pairs
        while True:
            box = _parse_box_len(mv, off)
            if not box:
                break
            size, typ = box
            if typ != "moof":
                # Skip unexpected box types until moof
                off += size
                continue
            moof_off = off
            moof_end = off + size
            off = moof_end
            box2 = _parse_box_len(mv, off)
            if not box2:
                # need more for the following box
                off = moof_off
                break
            size2, typ2 = box2
            if typ2 != "mdat":
                # Not a fragment; skip moof
                off = moof_end
                continue
            mdat_end = off + size2
            if mdat_end > len(mv):
                # partial mdat; wait for more
                off = moof_off
                break
            # Emit moof+mdat together
            emit("stream.data", mv[moof_off:mdat_end].tobytes())
            off = mdat_end

    if off > 0:
        # Discard consumed bytes
        state["buf"] = bytearray(mv[off:].tobytes())


def process_stream(
    process_queue: "queue.Queue[bytes]",
    stop_event: "threading.Event",
    output_file: Path,
    socket_passthrough: bool = False,
):
    import os

    ffmpeg_process = None
    if socket_passthrough:
        # These should match the dimensions in _prepare_ffmpeg_command output
        out_width = 1440
        out_height = 720
        ffmpeg_process = start_ffmpeg_process(
            input_stdin=True,
            output_stdout=True,
            width=out_width,
            height=out_height,
        )
        os.set_blocking(ffmpeg_process.stdout.fileno(), False)
        os.set_blocking(ffmpeg_process.stderr.fileno(), False)
        fmp4_state = {
            "buf": bytearray(),
            "init_segment": None,
            "last_init_sent": None,
        }

    # Make sure that the directory structure exists
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        while not stop_event.is_set():
            if socket_passthrough and ffmpeg_process.poll() is not None:
                print("FFMPEG DIED")
                raise SystemExit

            try:
                content = process_queue.get(timeout=0.05)
            except queue.Empty:
                # Periodically drain encoder output even if no new input
                if socket_passthrough:
                    _drain_fmp4(ffmpeg_process, fmp4_state)
                continue

            if output_file:
                with open(output_file, "ab") as f:
                    f.write(content)

            if socket_passthrough:
                # Feed raw Annex-B into ffmpeg; drain its TS output
                try:
                    ffmpeg_process.stdin.write(content)
                except (BrokenPipeError, ValueError):
                    pass
                _drain_fmp4(ffmpeg_process, fmp4_state)

        # Final drain on shutdown
        if socket_passthrough:
            try:
                ffmpeg_process.stdin.close()
            except Exception:
                pass

            # Drain any remaining output
            _drain_fmp4(ffmpeg_process, fmp4_state)

            ffmpeg_process.stdout.close()
            ffmpeg_process.stderr.close()

            ffmpeg_process.wait(timeout=2)
    finally:
        print("  Done")


# endregion processing
