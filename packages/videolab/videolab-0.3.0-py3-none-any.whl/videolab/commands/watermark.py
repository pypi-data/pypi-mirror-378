import argparse
import logging
from pathlib import Path
from typing import Any, cast, Optional, Tuple

import av
from PIL import Image, ImageDraw, ImageFont


def _create_watermark_image(
    text: str,
    frame_width: int,
    frame_height: int,
    font_size_arg: Optional[int],
    font_color_str: str,
    position_str: str,
    margin: int,
) -> Tuple[Image.Image, Tuple[int, int]]:
    """Creates a transparent watermark image with text."""
    font_size = font_size_arg if font_size_arg is not None else int(frame_height * 0.05)
    font = ImageFont.load_default(size=font_size)

    # Parse font color
    try:
        r, g, b, a = map(int, font_color_str.split(","))
        font_color = (r, g, b, a)
    except ValueError:
        logging.warning(f"Invalid font color format '{font_color_str}'. Using default.")
        font_color = (255, 255, 255, 128)

    # use a dummy image to calculate text size
    dummy_img = Image.new("RGBA", (1, 1))
    draw = ImageDraw.Draw(dummy_img)
    left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
    text_width = int(right - left)
    text_height = int(bottom - top)

    # create the watermark image
    img = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text((-left, -top), text, font=font, fill=font_color)

    # calculate position
    if position_str == "top-left":
        x = margin
        y = margin
    elif position_str == "bottom-left":
        x = margin
        y = frame_height - text_height - margin
    elif position_str == "bottom-right":
        x = frame_width - text_width - margin
        y = frame_height - text_height - margin
    elif position_str == "center":
        x = (frame_width - text_width) // 2
        y = (frame_height - text_height) // 2
    else:  # top-right is the default
        x = frame_width - text_width - margin
        y = margin
    position = (x, y)

    return img, position


def _add_watermark(
    frame: av.VideoFrame, watermark_img: Image.Image, position: Tuple[int, int]
) -> av.VideoFrame:
    """Overlays a watermark image onto a video frame."""
    img = frame.to_image()
    img.paste(watermark_img, position, watermark_img)

    new_frame = cast(av.VideoFrame, av.VideoFrame.from_image(img))
    new_frame.pts = frame.pts
    new_frame.time_base = frame.time_base
    return new_frame


def watermark_command(args: argparse.Namespace) -> None:
    """Adds a text watermark to a video."""
    output_file = args.output_file
    if output_file is None:
        input_path = Path(args.input_file)
        output_file = str(input_path.with_stem(f"{input_path.stem}_watermarked"))

    try:
        with av.open(args.input_file, mode="r") as in_container:
            in_video_stream = next(
                (s for s in in_container.streams if s.type == "video"), None
            )
            if not in_video_stream:
                logging.error(f"No video stream found in '{args.input_file}'.")
                return

            watermark_img, position = _create_watermark_image(
                args.text,
                in_video_stream.width,
                in_video_stream.height,
                args.font_size,
                args.font_color,
                args.position,
                args.margin,
            )

            with av.open(output_file, mode="w") as out_container:
                out_video_stream = out_container.add_stream_from_template(
                    in_video_stream
                )

                for packet in in_container.demux(in_video_stream):
                    for frame in packet.decode():
                        new_frame = _add_watermark(frame, watermark_img, position)
                        for new_packet in out_video_stream.encode(new_frame):
                            out_container.mux(new_packet)

                # flush the encoder
                for new_packet in out_video_stream.encode():
                    out_container.mux(new_packet)
    except av.AVError as e:
        logging.error(f"Error processing video file: {e}")
    except FileNotFoundError:
        logging.error(f"Input file '{args.input_file}' not found.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def register_subcommand(subparsers: Any) -> None:
    """Register the 'watermark' subcommand."""
    parser = subparsers.add_parser(
        "watermark",
        help="Add a watermark to a video.",
        description="Adds a watermark to a video file.",
    )
    parser.add_argument("input_file", type=str, help="Path to the input video file")
    parser.add_argument(
        "output_file",
        type=str,
        nargs="?",
        default=None,
        help=(
            "Path to save the watermarked video file, "
            "defaults: '<input_file>_watermarked.<ext>'"
        ),
    )
    parser.add_argument(
        "--text", type=str, required=True, help="The text for the watermark"
    )
    parser.add_argument(
        "--font-size",
        type=int,
        default=None,
        help="Font size for the watermark text. Defaults to 5%% of video height.",
    )
    parser.add_argument(
        "--font-color",
        type=str,
        default="255,255,255,128",
        help="Font color in RGBA format (e.g., '255,255,255,128').",
    )
    parser.add_argument(
        "--position",
        type=str,
        default="top-right",
        choices=["top-left", "top-right", "bottom-left", "bottom-right", "center"],
        help="Position of the watermark.",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=20,
        help="Margin from the edges of the video in pixels.",
    )
    parser.set_defaults(func=watermark_command)
